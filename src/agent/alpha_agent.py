import ast
import difflib
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import httpx  # for ReadTimeout detection
import torch.cuda
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

from src.tools.quantitative_tool import QuantitativeTool
from src.tools.rag_pipeline import RAGTool
from src.utils import config
from src.utils.logger_config import logger

os.environ["LLAMA_INDEX_USE_INSTRUMENTATION"] = (
    "0"  # best-effort; harmless if unsupported
)

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

if torch.backends.mps.is_available():
    device = "mps"
elif torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2", device=device
)


# ---------- helpers ----------
def _safe_ascii(s: str) -> str:
    """
    Converts a string to ASCII-only characters for safe Windows console logging.

    Parameters:
        s (str): The input string.

    Returns:
        str: The ASCII-only string, or '<non-ascii omitted>' if conversion fails.
    """
    try:
        return s.encode("ascii", "ignore").decode("ascii")
    except Exception:
        return "<non-ascii omitted>"


@dataclass
class RunResult:
    text: str
    pipeline: str  # 'react'
    tools: List[str]


# ======================== ReAct instructions (tightened) ========================
REACT_INSTRUCTIONS = """You are AlphaAgent. Use tools when helpful and finish with a concise answer.

Tools you can call (one per Action):
- qualitative_financial_analyzer: filings/news/10-K analysis via RAG.
- key_financial_ratios_fetcher: valuation metrics (P/E, P/B, dividend yield).
- daily_stock_performance_fetcher: latest OHLCV.

Rules:
- Use at most 2 tool calls.
- Use exactly one tool per Action.
- If the user asks about risks AND a valuation metric, use BOTH qualitative_financial_analyzer and key_financial_ratios_fetcher.
- When answering "risks from the latest 10-K", you MUST target Item 1A (Risk Factors) and, if relevant, Item 1C (Cybersecurity) of the latest filing. Do NOT summarize Item 7 (MD&A) or Notes to Financials for risks.
- Do NOT log.info "Observation:" yourself; I will insert it.
- Do NOT answer without using at least one tool.
- Do NOT use daily_stock_performance_fetcher for valuation metrics; if P/E/valuation is requested, you MUST use key_financial_ratios_fetcher.

Follow EXACTLY this format for each step:
Thought: <brief reasoning>
Action: <one of [qualitative_financial_analyzer, key_financial_ratios_fetcher, daily_stock_performance_fetcher]>
Action Input: <valid JSON>

After I provide the Observation(s), you may do another Thought/Action or finish.

YOUR LAST LINE MUST START WITH EXACTLY:
Final Answer:
"""


# =============================== Runtime Setup ===============================
def setup_runtime():
    """
    Initializes LLM and tool instances (no LlamaIndex agent runtime).
    Returns (llm, rag_tool, qtool).
    """
    logger.info("Configuring the LLM (mistral:7b-instruct-q4_0, MVP)…")

    Settings.llm = Ollama(
        model="mistral:7b-instruct-q4_0",
        request_timeout=600.0,  # avoid read timeouts on CPU
        temperature=0.0,  # deterministic
        additional_kwargs={
            # Ollama expects options nested under "options"
            "options": {
                "num_ctx": 768,  # big RAM saver
                "num_predict": 128,  # keep answers short to reduce work
                "num_batch": 8,  # lower peak memory during generation
                "num_gpu": 0,  # force CPU path
            }
        },
    )

    logger.info("Instantiating tools…")
    rag_tool = RAGTool()  # uses Settings.embed_model
    quantitative_tool = QuantitativeTool()
    logger.info("Runtime initialization complete.")
    return Settings.llm, rag_tool, quantitative_tool


# =================== Intent routing (synonym + fuzzy + semantic) ===================
_INTENT_SYNONYMS: Dict[str, List[str]] = {
    "risks": [
        "risk factor",
        "risk",
        "risks",
        "threat",
        "vulnerability",
        "cybersecurity",
        "cyber security",
        "breach",
        "data breach",
        "security risk",
        "item 1a",
        "item 1c",
    ],
    "mdna": [
        "margin",
        "margins",
        "gross margin",
        "operating margin",
        "profitability",
        "driver",
        "drivers",
        "headwind",
        "tailwind",
        "pricing",
        "price/mix",
        "mix",
        "cost of goods",
        "cogs",
        "opex",
        "expenses",
        "r&d",
        "sg&a",
        "sga",
        "operating expenses",
        "unit economics",
    ],
    "liquidity": [
        "liquidity",
        "cash flow",
        "operating cash flow",
        "free cash flow",
        "fcf",
        "capex",
        "capital expenditures",
        "working capital",
        "debt",
        "leverage",
        "buyback",
        "repurchase",
        "dividend",
        "capital resources",
    ],
    "legal": [
        "litigation",
        "lawsuit",
        "legal proceeding",
        "proceeding",
        "antitrust",
        "doj",
        "ftc",
        "ec investigation",
        "settlement",
        "item 3",
    ],
    "business": [
        "business model",
        "segments",
        "segment",
        "products",
        "services",
        "competition",
        "competitors",
        "go-to-market",
        "tam",
        "total addressable market",
        "item 1",
    ],
    "controls": [
        "internal control",
        "icfr",
        "disclosure controls",
        "material weakness",
        "sox 404",
        "item 9a",
    ],
}

_INTENT_DESC: Dict[str, str] = {
    "risks": "10-K Item 1A risk factors and Item 1C cybersecurity threats",
    "mdna": "10-K Item 7 MD&A results of operations margin and cost drivers",
    "liquidity": "10-K Item 7 MD&A liquidity and capital resources cash flow capex",
    "legal": "10-K Item 3 legal proceedings and litigation",
    "business": "10-K Item 1 business segments products competition",
    "controls": "10-K Item 9A internal control over financial reporting disclosure controls",
}


def _normalize_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").lower()).strip()


def _tokenize(s: str) -> List[str]:
    return re.findall(r"[a-z]+", s.lower())


def _fuzzy_hit(query_tokens: List[str], vocab: List[str], thr: float = 0.86) -> bool:
    """Catch typos (margn→margin)."""
    vocab_tokens = set(t for phrase in vocab for t in _tokenize(phrase))
    for qt in query_tokens:
        if len(qt) < 5:  # avoid noise
            continue
        best = difflib.get_close_matches(qt, vocab_tokens, n=1, cutoff=thr)
        if best:
            return True
    return False


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return 0.0 if na == 0 or nb == 0 else dot / (na * nb)


def _embed(text: str) -> List[float]:
    m = Settings.embed_model
    try:
        return m.get_query_embedding(text)
    except Exception:
        return m.get_text_embedding(text)


def _semantic_intent(query: str) -> Tuple[str, float]:
    """
    Determines the nearest intent label for a given query using sentence embeddings and cosine similarity.

    Args:
        query (str): The user query to classify.

    Returns:
        Tuple[str, float]: A tuple containing the best-matching intent label and its cosine similarity score.
                           Returns ("default", 0.0) if embedding or scoring fails.
    """
    try:
        qv = _embed(query)
        scores = {k: _cosine(qv, _embed(v)) for k, v in _INTENT_DESC.items()}
        intent, score = max(scores.items(), key=lambda kv: kv[1])
        return intent, float(score)
    except Exception:
        return "default", 0.0


def _infer_10k_intent(q: str) -> Tuple[str, float]:
    """
    Returns (intent, confidence). Confidence is:
      - 1.0 if keyword/synonym matched
      - semantic cosine if semantic fallback used
      - 0.0 default otherwise
    """
    qn = _normalize_text(q)
    tokens = _tokenize(qn)

    # 1) synonym/phrase match (strong)
    for intent, phrases in _INTENT_SYNONYMS.items():
        if any(p in qn for p in phrases) or _fuzzy_hit(tokens, phrases):
            return intent, 1.0

    # 2) semantic fallback (soft)
    intent, score = _semantic_intent(qn)
    if score >= 0.48:
        return intent, score

    # 3) default unknown
    return "default", 0.0


@lru_cache(maxsize=1)
def _get_ticker_name_mapping() -> Dict[str, str]:
    """
    Loads the SEC's ticker-to-company-name mapping from the JSON file.
    The result is cached in memory to avoid re-reading the file.
    """
    mapping_file = config.RAW_DATA_DIR / "company_tickers.json"
    if not mapping_file.exists():
        logger.warning("company_tickers.json not found. Cannot map tickers to names.")
        return {}

    with open(mapping_file, "r") as f:
        all_tickers_data = json.load(f)

    # Create a mapping from ticker to title (company name)
    ticker_to_name = {
        value["ticker"]: value["title"] for key, value in all_tickers_data.items()
    }
    return ticker_to_name


def _build_rag_query(
    user_query: str, ticker: str, intent: str, confidence: float
) -> str:
    """
    Constructs a retrieval query for the RAG pipeline based on user input, ticker, detected intent, and confidence.

    Args:
        user_query (str): The original user question or context.
        ticker (str): The stock ticker symbol (e.g., 'MSFT').
        intent (str): The inferred 10-K section intent (e.g., 'risks', 'mdna', etc.).
        confidence (float): Confidence score for the intent (0.0 to 1.0).

    Returns:
        str: A formatted query string guiding the retriever to the relevant 10-K section(s).
             If confidence is low, the query allows broader context.
    """
    uq = (user_query or "").strip()

    if intent == "risks":
        base = (
            f"{ticker} latest Form 10-K. Focus on Item 1A (Risk Factors) and Item 1C (Cybersecurity). "
            f"Return a concise list of key risks from the most recent filing."
        )
    elif intent == "mdna":
        base = (
            f"{ticker} latest Form 10-K. Focus on Item 7 MD&A — Results of Operations. "
            f"Extract margin drivers (gross & operating), price/mix, COGS, and opex."
        )
    elif intent == "liquidity":
        base = (
            f"{ticker} latest Form 10-K. Focus on Item 7 MD&A — Liquidity and Capital Resources. "
            f"Summarize cash flow drivers, capex, debt/leverage, and buybacks/dividends."
        )
    elif intent == "legal":
        base = (
            f"{ticker} latest Form 10-K. Focus on Item 3 (Legal Proceedings). "
            f"Summarize material litigation disclosed."
        )
    elif intent == "business":
        base = (
            f"{ticker} latest Form 10-K. Focus on Item 1 (Business). "
            f"Summarize segments, products, and competition."
        )
    elif intent == "controls":
        base = (
            f"{ticker} latest Form 10-K. Focus on Item 9A (Controls and Procedures). "
            f"Summarize conclusions on ICFR and disclosure controls."
        )
    else:
        # low/unknown confidence: allow retriever to roam
        base = f"{ticker} latest Form 10-K. Answer using the most relevant sections."

    # Allow adjacent context when we're not fully confident
    if 0.0 < confidence < 0.48:
        base += " If needed, consult adjacent sections (Item 1, Item 1A, Item 7) for context."

    return base if not uq else f"{base} Context: {uq}"


# =================== Manual ReAct (no fallback, no handlers) ===================
_ACTION_RE = re.compile(
    r"Thought\s*:\s*(?P<thought>.*?)[\r\n]+Action\s*:\s*(?P<tool>[a-zA-Z0-9_]+)[\r\n]+Action Input\s*:\s*(?P<input>.+)",
    re.IGNORECASE | re.DOTALL,
)


def _strip_code_fences(s: str) -> str:
    """
    Removes Markdown code fences (triple backticks) from a string.

    Parameters:
        s (str): The input string, possibly containing code fences.

    Returns:
        str: The string with code fences removed. If code fences are present,
    """
    s = s.strip()
    if s.startswith("```"):
        s = s.strip("`")
        parts = s.splitlines()
        s = "\n".join(parts[1:]) if parts else ""
    return s.strip()


def _parse_action_block(
    text: str,
) -> Tuple[Optional[str], Optional[str], Optional[dict]]:
    """
    Parses a model output block to extract the reasoning (`Thought`), tool name (`Action`), and tool input (`Action Input`).

    Args:
        text (str): The model output containing the action block.

    Returns:
        Tuple[Optional[str], Optional[str], Optional[dict]]:
            - thought: The extracted reasoning string.
            - tool: The tool name as a string.
            - input_dict: The parsed input as a dictionary (from JSON or Python literal), or a fallback dict if parsing fails.

    Notes:
        - Accepts both JSON and Python-literal dicts for the input.
        - Strips Markdown code fences if present.
        - Uses a heuristic to cut at the last closing brace or bracket for robust parsing.
        - If parsing fails, returns a dict with the raw string or query.
    """
    m = _ACTION_RE.search(text or "")
    if not m:
        return None, None, None
    thought = (m.group("thought") or "").strip()
    tool = (m.group("tool") or "").strip()
    raw = _strip_code_fences((m.group("input") or "").strip())

    # Heuristic: cut at the last '}' or ']'
    cut = max(raw.rfind("}"), raw.rfind("]"))
    candidate = raw[: cut + 1].strip() if cut != -1 else raw

    parsed = None
    try:
        parsed = json.loads(candidate)
    except Exception:
        try:
            parsed = ast.literal_eval(candidate)
        except Exception:
            pass

    if not isinstance(parsed, dict):
        if isinstance(parsed, str):
            parsed = {"query": parsed}
        else:
            parsed = {"raw": candidate}

    return thought, tool, parsed


def _try_parse_json(s: str):
    """
    Attempts to parse a string as JSON.

    Args:
        s (str): The string to parse.

    Returns:
        Any: The parsed JSON object if successful, otherwise None.
    """
    try:
        return json.loads(s)
    except Exception:
        return None


def _sanitize_final_text(s: str) -> str:
    """
    Removes any chain-of-thought or tool scaffolding lines from the model output
    if the required "Final Answer:" prefix is missing.

    Args:
        s (str): The model output string to sanitize.

    Returns:
        str: The cleaned string with only the final answer, excluding lines that
             start with "Thought:", "Action:", "Action Input:", or "Observation:".
    """
    lines = []
    for line in (s or "").splitlines():
        if re.match(
            r"^\s*(Thought|Action|Action Input|Observation)\s*:", line, re.IGNORECASE
        ):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def _format_metrics_line(r: dict) -> Tuple[str, Optional[float]]:
    """
    Builds a canonical metrics summary line from the payload returned by key_financial_ratios_fetcher.

    Args:
        r (dict): Dictionary containing financial metrics, such as price, P/E ratios, dividend yield, timestamp, and timezone.

    Returns:
        Tuple[str, Optional[float]]:
            - A formatted string summarizing available metrics (trailing P/E, forward P/E, price, dividend yield, timestamp, exchange timezone).
            - The trailing P/E value as a float, or None if not present.
    """

    def _get(d, keys):
        for k in keys:
            if k in d and d[k] is not None:
                return d[k]
        return None

    price = _get(r, ["price", "regularMarketPrice", "currentPrice"])
    trailing_pe = _get(r, ["trailingPE", "trailing_pe", "trailingPe"])
    forward_pe = _get(r, ["forwardPE", "forward_pe", "forwardPe"])
    div_yield = _get(r, ["dividendYield", "trailingAnnualDividendYield", "yield"])
    ts = _get(r, ["marketTime", "regularMarketTime"])
    tz = r.get("tz") or r.get("exchangeTimezoneName")

    parts = []
    if trailing_pe is not None:
        parts.append(f"Trailing P/E = {float(trailing_pe):.2f}")
    if forward_pe is not None:
        parts.append(f"Forward P/E = {float(forward_pe):.2f}")
    if price is not None:
        parts.append(f"Price = {price}")
    if div_yield is not None:
        dy = float(div_yield)
        if dy < 1:  # convert fraction to %
            dy *= 100.0
        parts.append(f"Dividend yield = {dy:.2f}%")
    if ts is not None:
        parts.append(f"As-of (UTC epoch) = {ts}")
    if tz:
        parts.append(f"Exchange TZ = {tz}")

    return " | ".join(parts), trailing_pe


def _is_on_topic(text: str, ticker: str) -> bool:
    """
    Dynamically checks if the response text is on-topic for the given ticker
    by looking up the company name from the master ticker list.
    """
    t = (text or "").lower()
    ticker_lower = ticker.lower()

    mapping = _get_ticker_name_mapping()
    company_name = mapping.get(ticker.upper(), "").lower()

    # Get the primary name, e.g., "Apple Inc." -> "apple"
    company_name_base = ""
    if company_name:
        company_name_base = re.split(r"[,.\s(]", company_name)[0]

    # Check for the ticker OR the primary company name
    need_any = (ticker_lower in t) or (company_name_base and company_name_base in t)

    need_one = any(
        k in t
        for k in ["10-k", "risk", "risk factor", "p/e", "pe ratio", "price/earnings"]
    )
    bad = any(
        b in t for b in ["patient", "surgery", "post-operative", "medical regimen"]
    )
    return need_any and need_one and not bad


async def _llm_complete(prompt: str) -> str:
    """Single-turn completion via Ollama (async) with one retry on ReadTimeout."""
    try:
        resp = await Settings.llm.acomplete(prompt)
        text = (
            getattr(resp, "text", None) or getattr(resp, "message", None) or str(resp)
        )
        return (text or "").strip()
    except Exception as e:
        # Retry once on read timeout with longer timeout and trimmed prompt
        is_timeout = (
            isinstance(e, httpx.ReadTimeout)
            or "ReadTimeout" in e.__class__.__name__
            or "ReadTimeout" in str(e)
        )
        if not is_timeout:
            raise
        try:
            # bump timeout defensively if the wrapper exposes it
            if hasattr(Settings.llm, "request_timeout"):
                Settings.llm.request_timeout = max(
                    getattr(Settings.llm, "request_timeout", 600.0), 900.0
                )
        except Exception:
            pass
        trimmed = prompt[-12000:]  # keep the tail (observations + latest instructions)
        resp = await Settings.llm.acomplete(trimmed)
        text = (
            getattr(resp, "text", None) or getattr(resp, "message", None) or str(resp)
        )
        return (text or "").strip()


async def run_manual_react(
    user_query: str, rag_tool: RAGTool, qtool: QuantitativeTool
) -> RunResult:
    """
    Deterministic ReAct harness with enforcement:
    - Try up to 2 tool calls driven by the model.
    - Duplicate-tool guards (qual once + ratios once when both are needed).
    - If the model fails to emit a valid Action, nudge once.
    - Post-loop enforcement: call missing required tools (keeping at most 2 calls).
    - Final synthesis guard: on-topic validator + one repair pass.
    """

    def _infer_intent_flags(q: str):
        ql = (q or "").lower()
        wants_risks = any(
            k in ql for k in ["risk", "risk factor", "10-k", "10k", "filing"]
        )
        wants_pe = any(
            k in ql
            for k in [
                "p/e",
                "pe ",
                "pe-ratio",
                "pe ratio",
                "price/earnings",
                "valuation",
            ]
        )
        return wants_risks, wants_pe

    def _extract_ticker(q: str) -> str:
        """
        Extracts a stock ticker symbol from a user query string.

        The function searches for ticker symbols in two formats:
        - Standalone uppercase letters (1-5 characters), e.g., 'TSLA'
        - Uppercase letters within parentheses, e.g., '(TSLA)'

        If no ticker is found, defaults to 'MSFT'.

        Args:
            q (str): The input query string.

        Returns:
            str: The extracted ticker symbol, or 'MSFT' if none found.
        """
        # Improved regex to find tickers like (TSLA) or TSLA without parentheses
        m = re.search(r"\b([A-Z]{1,5})\b", q or "")
        # Fallback for parenthesized tickers
        if not m:
            m = re.search(r"\(([A-Z]{1,5})\)", q or "")
        return m.group(1) if m else "MSFT"  # Default remains for safety

    wants_risks, wants_pe = _infer_intent_flags(user_query)
    item_intent, intent_conf = _infer_10k_intent(user_query)

    # Helper: choose the qualitative query safely
    def _qual_query_from(payload: dict) -> str:
        explicit = (payload or {}).get("query") or (payload or {}).get("question")
        if explicit:
            return explicit
        # Route based on inferred 10-K intent (risks, mdna, liquidity, etc.)
        return _build_rag_query(
            user_query=user_query,
            ticker=_extract_ticker(user_query),
            intent=item_intent,
            confidence=intent_conf,
        )

    tools = {
        "qualitative_financial_analyzer": lambda payload: rag_tool.query(
            _qual_query_from(payload)
        ),
        "key_financial_ratios_fetcher": lambda payload: qtool.get_key_financial_ratios(
            (payload or {}).get("ticker")
            or (payload or {}).get("symbol")
            or _extract_ticker(user_query)
        ),
        "daily_stock_performance_fetcher": lambda payload: qtool.get_daily_stock_performance(
            (payload or {}).get("ticker")
            or (payload or {}).get("symbol")
            or _extract_ticker(user_query)
        ),
    }

    transcript: List[str] = []
    observations: List[str] = []  # strings "tool_name => result"
    used_tools: List[str] = []  # tool names, in order
    ratios_payload = None  # dict with trailingPE/forwardPE/price/timestamp if available

    transcript.append(REACT_INSTRUCTIONS)
    transcript.append("USER QUESTION:\n" + user_query)

    max_steps = 2
    attempted_retry = False
    step = 0

    while step < max_steps:
        prompt_parts = transcript[:]
        if observations:
            prompt_parts.append("\n".join(f"Observation: {o}" for o in observations))
        prompt = "\n\n".join(prompt_parts)

        model_out = await _llm_complete(prompt)
        thought, tool_name, action_input = _parse_action_block(model_out)

        # Guard: don't use OHLCV for valuation when P/E requested
        if tool_name == "daily_stock_performance_fetcher" and wants_pe:
            transcript.append(
                "System: The user asked for a valuation metric (P/E). "
                "Do NOT use daily_stock_performance_fetcher. You MUST call key_financial_ratios_fetcher. "
                "Emit the Action again."
            )
            if not attempted_retry:
                attempted_retry = True
                continue

        # Guard: avoid duplicate qualitative call if ratios still missing (when both required)
        if (
            step > 0
            and tool_name == "qualitative_financial_analyzer"
            and wants_pe
            and "key_financial_ratios_fetcher" not in used_tools
        ):
            transcript.append(
                "System: You've already used the qualitative tool. The user also asked for P/E. "
                "Now you MUST call key_financial_ratios_fetcher. Emit the Action again."
            )
            if not attempted_retry:
                attempted_retry = True
                continue

        # Guard: avoid duplicate ratios call if qualitative still missing (when both required)
        if (
            step > 0
            and tool_name == "key_financial_ratios_fetcher"
            and wants_risks
            and "qualitative_financial_analyzer" not in used_tools
        ):
            transcript.append(
                "System: You've already called the ratios tool. The user also asked for risks. "
                "Now you MUST call qualitative_financial_analyzer. Emit the Action again."
            )
            if not attempted_retry:
                attempted_retry = True
                continue

        if tool_name in tools:
            # Execute tool
            try:
                result = tools[tool_name](action_input or {})
                if tool_name == "key_financial_ratios_fetcher":
                    # Try to keep a structured copy for enforcement
                    if isinstance(result, dict):
                        ratios_payload = result
                    else:
                        parsed = (
                            _try_parse_json(result) if isinstance(result, str) else None
                        )
                        if isinstance(parsed, dict):
                            ratios_payload = parsed
                if not isinstance(result, str):
                    try:
                        result_str = json.dumps(result, ensure_ascii=False)
                    except Exception:
                        result_str = str(result)
                else:
                    result_str = result
                result_str = result_str[:2000]
            except Exception as e:
                result_str = f"[TOOL ERROR: {e}]"

            used_tools.append(tool_name)
            observations.append(f"{tool_name} => {result_str}")

            # Add step + observation to context
            step_block = f"""Thought: {thought or "(omitted)"}
Action: {tool_name}
Action Input: {json.dumps(action_input, ensure_ascii=False) if isinstance(action_input, dict) else str(action_input)}"""
            transcript.append(step_block.strip())
            transcript.append(f"Observation: {result_str}")

            step += 1
            continue

        # No valid Action parsed → nudge once
        if not attempted_retry:
            attempted_retry = True
            transcript.append(
                "System: You must call at least one tool before answering. "
                "If valuation (P/E) is requested, you MUST call key_financial_ratios_fetcher. "
                "Do NOT write a Final Answer yet. Emit the Action now."
            )
            continue

        # After retry still no Action → break and enforce intent
        break

    # ---- Intent enforcement (post-loop) ----
    # Ensure qualitative tool if needed for risks or any 10-K analysis intent
    if "qualitative_financial_analyzer" not in used_tools and item_intent != "default":
        try:
            r = rag_tool.query(
                _build_rag_query(
                    user_query, _extract_ticker(user_query), item_intent, intent_conf
                )
            )
            observations.append(f"qualitative_financial_analyzer => {str(r)[:2000]}")
        except Exception as e:
            observations.append(f"qualitative_financial_analyzer => [TOOL ERROR: {e}]")
        used_tools.append("qualitative_financial_analyzer")

    # Ensure ratios tool if P/E requested
    if wants_pe and "key_financial_ratios_fetcher" not in used_tools:
        # Keep max 2 tool calls: if OHLCV was used, swap it out
        if "daily_stock_performance_fetcher" in used_tools and len(used_tools) >= 2:
            # remove the last OHLCV observation
            try:
                last_idx = (
                    len(observations)
                    - 1
                    - observations[::-1].index(
                        next(
                            o
                            for o in observations[::-1]
                            if o.startswith("daily_stock_performance_fetcher =>")
                        )
                    )
                )
                observations.pop(last_idx)
            except Exception:
                if observations:
                    observations.pop()
            # remove the tool entry (last occurrence)
            for i in range(len(used_tools) - 1, -1, -1):
                if used_tools[i] == "daily_stock_performance_fetcher":
                    used_tools.pop(i)
                    break

        # now add ratios
        try:
            r = qtool.get_key_financial_ratios(_extract_ticker(user_query))
            if isinstance(r, dict):
                ratios_payload = r
            observations.append(
                f"key_financial_ratios_fetcher => {json.dumps(r, ensure_ascii=False)[:2000]}"
            )
        except Exception as e:
            observations.append(f"key_financial_ratios_fetcher => [TOOL ERROR: {e}]")
        used_tools.append("key_financial_ratios_fetcher")

    # ---- Build enforcement hint for final numbers ----
    must_include_line = ""
    if ratios_payload:
        price = (
            ratios_payload.get("price")
            or ratios_payload.get("regularMarketPrice")
            or ratios_payload.get("currentPrice")
        )
        trailing_pe = (
            ratios_payload.get("trailingPE")
            or ratios_payload.get("trailing_pe")
            or ratios_payload.get("trailingPe")
        )
        market_time = ratios_payload.get("marketTime") or ratios_payload.get(
            "regularMarketTime"
        )
        tz = ratios_payload.get("tz") or ratios_payload.get("exchangeTimezoneName")
        if trailing_pe is not None:
            must_include_line = (
                f"Required numbers to include verbatim: Trailing P/E = {float(trailing_pe):.2f}"
                + (f", Price = {price}" if price is not None else "")
                + (
                    f", As-of (UTC epoch) = {market_time}"
                    if market_time is not None
                    else ""
                )
                + (f", Exchange TZ = {tz}" if tz else "")
            )

    # ---- Finish with Final Answer ----
    finish_parts = transcript[:]
    if observations:
        finish_parts.append("\n".join(f"Observation: {o}" for o in observations))

    # Conditional synthesis instruction: only force Item 1A/1C if the intent is risks
    if item_intent == "risks":
        finish_parts.append(
            "Finish now by synthesizing the Observations into a concise answer. "
            "Summarize only risks from Item 1A (and 1C if relevant) of the latest 10-K. "
            "Cite concrete figures from the Observations only (no guesses)."
        )
    else:
        finish_parts.append(
            "Finish now by synthesizing the Observations into a concise answer. "
            "Cite concrete figures from the Observations only (no guesses)."
        )

    if must_include_line:
        finish_parts.append(must_include_line)
    finish_parts.append("YOUR LAST LINE MUST START WITH EXACTLY:\nFinal Answer:")
    final_out = await _llm_complete("\n".join(finish_parts))

    m = re.search(
        r"(?:^|\n)\s*Final Answer\s*:\s*(.*)$", final_out, re.IGNORECASE | re.DOTALL
    )
    if not m:
        # Enforce format on a second pass (one retry, minimal prompt)
        enforce = [
            "You forgot to output 'Final Answer:'. Output ONLY one line:",
            "Final Answer: <concise synthesis using only Observations>",
        ]
        if must_include_line:
            enforce.append(must_include_line)
        enforce.append("Do not include Thought/Action/Observation or any preface.")
        final_out = await _llm_complete("\n".join(enforce))
        m = re.search(
            r"(?:^|\n)\s*Final Answer\s*:\s*(.*)$", final_out, re.IGNORECASE | re.DOTALL
        )

    text = m.group(1).strip() if m else _sanitize_final_text(final_out)

    ticker = _extract_ticker(user_query)
    # === On-topic validator + repair pass ===
    if not _is_on_topic(text, ticker):
        repair = []
        repair.append("You produced an off-topic answer previously.")
        repair.append(
            "Using ONLY the Observations below, write ONE short paragraph answering the user:"
        )
        if item_intent == "risks":
            repair.append(
                f"- Summarize {ticker}'s key risks from the latest Form 10-K (Item 1A / 1C only)."
            )
        else:
            repair.append(
                "- Summarize the key points relevant to the user's question from the latest 10-K."
            )
        repair.append(
            "- Include the trailing P/E from Observations verbatim if present."
        )
        repair.append(
            "- Do NOT mention healthcare, patients, surgery, or any unrelated domain."
        )
        repair.append("- Output must start with exactly: Final Answer:")
        repair.append("\n".join(f"Observation: {o}" for o in observations))
        final_out = await _llm_complete("\n".join(repair))
        m = re.search(
            r"(?:^|\n)\s*Final Answer\s*:\s*(.*)$", final_out, re.IGNORECASE | re.DOTALL
        )
        text = m.group(1).strip() if m else _sanitize_final_text(final_out)

    # === Enforce numeric correctness & de-hallucinate metrics ===
    if ratios_payload:
        metrics_line, required_pe = _format_metrics_line(ratios_payload)

        # If the model didn't include the exact trailing P/E we fetched, strip its P/E sentence.
        if required_pe is not None and f"{float(required_pe):.2f}" not in text:
            text = re.sub(
                r"(?i)\b(?:p/?e|price[-\s]*to[-\s]*earnings)[^.]*\.", "", text
            )

        # If the model mentioned dividend yield at all, remove that sentence (avoid 69% hallucinations)
        if re.search(r"(?i)\bdividend\b", text):
            text = re.sub(r"(?i)\bdividend[^.]*\.", "", text)

        # Append the canonical, tool-derived metrics line (truth source)
        text = text.strip()
        if not text.endswith("."):
            text += "."
        if metrics_line:
            text += " " + metrics_line

    # Deduplicate provenance tool list (preserve order)
    used_tools = list(dict.fromkeys(used_tools))

    return RunResult(text=text, pipeline="react", tools=used_tools or ["(none)"])


# # ================================= Main =================================
# async def main():
#     """
#     Entry point for AlphaAgent using manual ReAct pipeline.
#
#     - Sets up logging and runtime (LLM, RAG tool, quantitative tool).
#     - Runs a test financial query about Microsoft's latest 10-K risks and P/E ratio.
#     - Logs the query, final response, and provenance (pipeline and tools used).
#     - Handles and logs any exceptions during execution.
#     """
#     try:
#         log = setup_logging()
#         _, rag_tool, qtool = setup_runtime()
#         log.info(
#             "--- AlphaAgent Initialised (MVP manual ReAct). Ask a financial question. ---"
#         )
#
#         test_query = "What are the main risks for Microsoft according to its latest 10-K filing, and what is its current P/E ratio?"
#         log.info(f"Running test query: '{test_query}'")
#
#         result = await run_manual_react(test_query, rag_tool, qtool)
#
#         log.info("\n--- Final Response ---")
#         log.info(result.text)
#         log.info(
#             f"\n[provenance: {result.pipeline}; tools: {', '.join(result.tools) or 'n/a'}]"
#         )
#
#     except Exception as e:
#         logger.error(f"An error occurred during execution: {e}", exc_info=True)
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
