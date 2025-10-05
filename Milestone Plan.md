# Milestone Plan

## Part 1: Foundational Model Development (40% Timeline) 🏗️

**Goal:** To build a functional, end-to-end Minimum Viable Product (MVP) of AlphaAgent. The focus here is on core
infrastructure, basic data ingestion, and proving the agentic workflow.

* **1. Project & Environment Setup**
    * `[X]` **Version Control:** Create and configure the GitHub repository with a Python `.gitignore`.
    * `[X]` **Virtual Environment:** Set up a dedicated Conda environment and export the `environment.yml` file.
    * `[X]` **Install Core Libraries:** Install all necessary packages for the MVP (LlamaIndex, `yfinance`, Streamlit,
      Transformers, etc.).
    * `[X]` **Configuration:** Set up the `.env` file for API keys (News API, SEC User Agent) and a `config.py` script
      to manage settings.

* **2. Core Data Ingestion & Processing (MVP Scope)**
    * `[X]` **Target Entities:** Define my initial list of 10 companies.
    * `[X]` **Ingest Unstructured Data:** Write and test scripts to download **10-K, 8-K filings**, and **news articles
      ** only. Implement simple file caching.
    * `[X]` **Ingest Structured Data:** Use a notebook to validate fetching basic stock data (price, ratios, market cap)
      using the `yfinance` library.
    * `[X]` **Basic Cleaning:** Create initial data cleaning functions to strip boilerplate and HTML from the raw text
      data.

* **3. MVP Component Implementation**
    * `[X]` **Select Base Models:** Finalise the choice of a pre-trained **base LLM** (e.g., Llama-3-8B-Instruct) and an
      **embedding model** (e.g., `bge-large-en-v1.5`). Note: No fine-tuning at this stage.
    * `[X]` **Build RAG Tool:** Implement the core RAG pipeline: load the cleaned 10-K/8-K/news documents, chunk them,
      and create a searchable FAISS vector index.
    * `[X]` **Build Quantitative Tool:** Create a basic `QuantitativeTool` class that wraps the `yfinance` functions to
      get current price, key ratios, etc.

* **4. System Integration & Basic UI**
    * `[ ]` **Agent Orchestration:** Use LlamaIndex to create the main agent. Integrate the base LLM and provide it with
      the RAG and Quantitative tools, including clear descriptions of their capabilities.
    * `[ ]` **Develop UI:** Build a simple Streamlit web application with a text input for user queries and a display
      area for the agent's response.
    * `[ ]` **End-to-End Test:** Ensure a user query flows completely through the Streamlit app to the agent, which then
      correctly uses a tool and returns a sensible answer.

---

## Part 2: Enhancement & Analytical Deepening (30% Timeline) 🚀

**Goal:** To significantly upgrade the agent's intelligence, knowledge base, and reasoning abilities. This phase moves
beyond the MVP to incorporate richer data and a more powerful, specialised LLM.

* **1. Data Augmentation Pipeline**
    * `[ ]` **Ingest Quarterly Reports (10-Q):** Update my SEC script to also download 10-Q filings and add them to
      the RAG index.
    * `[ ]` **Ingest Earnings Call Transcripts:** Write a new script to fetch transcripts using an API (e.g., Financial
      Modeling Prep) and integrate this rich text into the RAG index.
    * `[ ]` **Integrate Analyst Ratings:** Enhance the `QuantitativeTool` with a new function to fetch structured data
      on analyst ratings and price targets.
    * `[ ]` **Integrate Macroeconomic Data:** Create a new `MacroeconomicTool` to fetch key economic indicators (GDP,
      inflation) from a source like the FRED API.

* **2. LLM Fine-Tuning**
    * `[ ]` **Curate Dataset:** Create a high-quality, instruction-following dataset using the newly acquired data
      sources (e.g., questions that require synthesising info from a 10-Q and an earnings call).
    * `[ ]` **Fine-Tune Model:** Write and run a script using Hugging Face PEFT (LoRA) to fine-tune my chosen base LLM
      on the curated financial dataset.
    * `[ ]` **Evaluate & Integrate:** Evaluate the fine-tuned model against the base model and integrate the superior
      version into the agent.

* **3. Advanced Agentic Capabilities**
    * `[ ]` **Implement Multi-Step Reasoning:** Upgrade the agent from a single-tool selector to a planner. Investigate
      and implement a ReAct-style architecture to handle complex, multi-step queries.
    * `[ ]` **Add Conversational Memory:** Integrate a memory module to allow for natural follow-up questions from the
      user.

---

## Part 3: Finalisation, Evaluation & Delivery (30% Timeline) 🏆

**Goal:** To rigorously test the enhanced model, refine the system for robustness, and produce all final deliverables,
including reports, a potential journal paper, and a polished demonstration.

* **1. Rigorous Evaluation & Refinement**
    * `[ ]` **Quantitative Benchmarking:** Develop a "golden dataset" of complex financial questions and use a framework
      like **Ragas** to quantitatively measure the agent's performance on metrics like faithfulness and context
      precision.
    * `[ ]` **Error Analysis & Optimisation:** Analyse the agent's failures to identify root causes. Refine tool
      descriptions, agent prompts, and the RAG retrieval strategy based on these findings.
    * `[ ]` **Implement Advanced Infrastructure:** Improve system robustness by containerising the application (Docker)
      and implementing an advanced caching layer (Redis) to speed up API calls.

* **2. Code Quality & Documentation**
    * `[ ]` **Refactor Code:** Clean the entire codebase, ensuring it is modular, efficient, and well-commented with
      docstrings.
    * `[ ]` **Finalise README:** Update the `README.md` to be a comprehensive guide, including the project's final
      architecture, setup instructions, and usage examples.

* **3. Final Deliverables**
    * `[ ]` **Write Final Project Report:** Draft and complete my M.Tech project report, detailing the methodology,
      architecture, experiments, evaluation results, and conclusions.
    * `[ ]` **Draft Journal Paper:** Structure the project findings into the format of a scientific paper. Write the
      abstract, introduction, methodology, results, and discussion sections.
    * `[ ]` **Prepare Demonstration:** Create a polished slide deck for my final presentation. Record a high-quality
      video demo of AlphaAgent answering a series of complex financial questions, showcasing its advanced capabilities
      and explainability features.
