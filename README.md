# AlphaAgent

A **local financial-research prototype** combining document retrieval and market-data tools behind a Streamlit interface.

The current implementation uses **Ollama with a Mistral model**, **LlamaIndex/Hugging Face embeddings** for local news and filing retrieval, and **yfinance** for market information. A manually orchestrated ReAct-style loop selects tools and produces a response.

## Implemented components

| Component | Location |
| --- | --- |
| Streamlit user interface | [`app.py`](app.py) |
| Tool-routing and response logic | [`src/agent/alpha_agent.py`](src/agent/alpha_agent.py) |
| Local news/filings retrieval | [`src/tools/rag_pipeline.py`](src/tools/rag_pipeline.py) |
| Market data and financial ratios | [`src/tools/quantitative_tool.py`](src/tools/quantitative_tool.py) |
| Data ingestion | [`scripts/run_rag_ingestion.py`](scripts/run_rag_ingestion.py) |

## Running locally

**Prerequisites:** Windows with Conda, Ollama, adequate memory and a local corpus of permitted financial documents. The checked-in `environment.yml` contains Windows-specific dependency builds and has not been validated on other systems.

```powershell
conda env create -f environment.yml
conda activate AlphaAgentEnv
ollama pull mistral:7b-instruct-q4_0
streamlit run app.py
```

The Streamlit application expects Ollama to be running and a compatible retrieval index to have been populated. Place authorised source documents in the project's processed-data location and review the [ingestion script](scripts/run_rag_ingestion.py) before running it. The repository does **not** include a ready-to-use financial-document index.

## Limitations

- **Research prototype, not an investment-advice service or production platform.** Generated answers and market figures can be incomplete, stale or incorrect. Verify against primary financial disclosures before relying on them.
- [Offline CI](.github/workflows/ci.yml) covers 10 mocked unit scenarios for market-data formatting, API failures, caching and ingestion exit codes on Windows/Linux with Python 3.11/3.12. These checks do **not** exercise Ollama, external market APIs or full financial-research accuracy.
- Live news availability, data completeness, factual accuracy and financial outcomes have **not** been independently evaluated.
- The runtime uses a local Ollama Mistral model; fine-tuning, guaranteed real-time data and independent security approval should **not** be inferred.
- The provided environment is sizeable and OS-specific. First-time model and embedding downloads require internet access.

This source is made available as an engineering experiment under the [MIT License](LICENSE).
