# <u><p align="center">Alpha Agent</p></u>
## <p align="center"><i>Financial Clarity, Powered by AI</i></p>
An AI financial analyst that combines qualitative news analysis (RAG) with quantitative market data to deliver
comprehensive, data-grounded insights.

### Project Vision & Goal
AlphaAgent is an autonomous AI framework designed to emulate the comprehensive workflow of a human financial analyst.
The project's core objective is to overcome the limitations of standard Large Language Models (LLMs), such as factual
hallucination and a lack of access to real-time, domain-specific data. By creating an agent that can intelligently use
multiple specialised tools, AlphaAgent aims to produce financial analysis that is accurate, transparent, auditable, and
actionable, providing a reliable foundation for investment decisions.

### Core Architecture
The framework is built on a modular, multi-component architecture, separating reasoning from execution.
#### The Orchestrator (The Brain):
This is the central reasoning engine of the agent, powered by a domain-specifically fine-tuned LLM (e.g., Llama-3-8B or
Mistral-7B). It interprets complex user prompts, formulates a multi-step plan, and intelligently dispatches tasks to
the appropriate tool. Its primary role is planning and synthesis.
#### Tool 1: The News & Filings Analyst (RAG System):
This is your core Retrieval-Augmented Generation (RAG) system. It functions as a specialised tool that allows the agent
to query and understand unstructured, qualitative data. Its knowledge base includes:
- SEC filings (10-K, 8-K)
- Earnings call transcripts
- Real-time market news
#### Tool 2: The Quantitative Data Analyst:
This is a new, dedicated tool for handling structured, numerical data. Implemented in Python (likely with Pandas and
yfinance), it gives the agent the ability to perform precise calculations and fetch verifiable metrics. Its
capabilities include:
- Fetching current and historical stock prices.
- Calculating technical indicators (e.g., moving averages).
- Retrieving fundamental financial ratios (P/E, EPS, etc.).

### Operational Workflow
AlphaAgent's innovation lies in its autonomous, multi-step execution process. Consider the user prompt:
"Analyse the market reaction to NVIDIA's latest earnings report and compare its current P/E ratio to that of AMD."
- Deconstruction & Planning: The Orchestrator receives the prompt and breaks it down into a logical plan:
  - Step 1: Find qualitative information on market sentiment regarding NVIDIA's earnings.
  - Step 2: Fetch the quantitative P/E ratio for NVIDIA.
  - Step 3: Fetch the quantitative P/E ratio for AMD.
  - Step 4: Synthesise all findings into a final answer.
- Intelligent Tool Execution: The Orchestrator calls the correct tool for each step:
  - Call Tool 1 (RAG): "Summarise news and analyst sentiment following NVIDIA's recent earnings release."
  - Call Tool 2 (Quantitative): "Fetch the current P/E ratio for ticker NVDA."
  - Call Tool 2 (Quantitative): "Fetch the current P/E ratio for ticker AMD."
- Synthesis: After receiving the outputs from all tool calls, the Orchestrator combines the qualitative sentiment
analysis with the direct P/E ratio comparison to generate a single, comprehensive, and evidence-backed response for
the user.
