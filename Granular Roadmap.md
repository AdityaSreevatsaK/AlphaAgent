# Granular Roadmap

---

## **Part 1: Foundational Model Development** 🏗️

* **Goal:** Build a functional, end-to-end Minimum Viable Product (MVP). This is the core working model I can
  demonstrate early on.

---

### **Phase A: Project & Environment Setup**

This phase covers the initial scaffolding and configuration of the project environment.

* **Version Control & Repository:**
    * `[X]` Create a new repository on GitHub named `AlphaAgent`.
    * `[X]` Clone the repository to my local machine.
    * `[X]` Create a `.gitignore` file using a standard Python template.
    * `[X]` Make my initial commit: `git commit -m "Initial project setup"`.

* **Python Environment:**
    * `[X]` Create a dedicated Conda environment: `conda create --name AlphaAgentEnv python=3.11 -y`.
    * `[X]` Activate the environment: `conda activate AlphaAgentEnv`.
    * `[X]` Install all foundational libraries (e.g., `llama-index`, `torch`, `transformers`, `yfinance`, `streamlit`,
      `ruff`, etc.).
    * `[X]` Freeze the packages for reproducibility: `conda env export > environment.yml`.

* **API Keys & Configuration:**
    * `[X]` Obtain API keys from a financial news service (e.g., Finnhub) and identify your SEC user agent.
    * `[X]` Create a `.env` file in the project's root directory for these secrets.
    * `[X]` Add the `.env` file to `.gitignore`.
    * `[X]` Write a `src/utils/config.py` script to load environment variables and manage project-wide settings.

---

### **Phase B: MVP Data Ingestion & Processing**

This phase focuses on sourcing and preparing the core data for the MVP.

* **Scaffolding & Target Entities:**
    * `[X]` Establish the full project directory structure (`/data/raw`, `/data/processed`, `/scripts`, `/src`, etc.).
    * `[X]` Define my initial list of 10 company tickers in `src/utils/config.py`.

* **Unstructured Data Ingestion (MVP Scope):**
    * `[X]` Write a script (`scripts/fetch_sec_data.py`) to download **10-K** and **8-K** filings to `/data/raw`.
    * `[X]` Write a script (`scripts/fetch_news_data.py`) to download recent news articles to `/data/raw`.
    * `[X]` Implement a simple file-exists check in both scripts to act as a cache.

* **Data Cleaning:**
    * `[X]` Create a data cleaning module (`src/data_pipeline/data_processing.py`).
    * `[X]` Implement a function inside it to strip boilerplate, HTML, and normalise whitespace from the raw text files.
    * `[X]` Write a runner script (`scripts/run_processing.py`) that applies this cleaning function to all files in
      `/data/raw` and saves the output to `/data/processed`.

---

### **Phase C: Core Component Implementation**

This phase involves building the individual "tools" that the agent will use in its MVP form.

* **Structured Data Exploration:**
    * `[X]` In a notebook (`notebooks/01_yfinance_test.ipynb`), test and validate fetching key data points via the
      `yfinance` library (e.g., current price, P/E ratio, market cap).

* **Quantitative Tool Development (`src/tools/quantitative_tool.py`):**
    * `[X]` Refactor the notebook code into a robust `QuantitativeTool` class.
    * `[X]` Implement specific, well-documented methods such as `get_key_financial_ratios(ticker: str)` and
      `get_daily_stock_performance(ticker: str)`.

* **RAG Pipeline Development (`src/tools/rag_pipeline.py`):**
    * `[X]` Implement an `IngestionPipeline` class that loads documents from `/data/processed`, chunks them using
      `SentenceSplitter`, generates embeddings, and saves a FAISS vector index to disk.
    * `[X]` Create a separate `RAGTool` class that loads the pre-built index from disk and exposes a `query(question)`
      method.

---

### **Phase D: MVP Integration & UI Development**

This phase brings all the MVP components together into a single, functional application.

* **Agent Orchestration (`src/agent/alpha_agent.py`):**
    * `[X]` Instantiate the `RAGTool` and `QuantitativeTool`.
    * `[X]` Convert the tool methods into LlamaIndex `FunctionTool` objects, ensuring their docstrings are clear and
      descriptive for the agent.
    * `[X]` Initialise a `ReActAgent` using a powerful **base pre-trained LLM** (e.g., Llama-3-8B-Instruct) and the list
      of tools.

* **Web Application (`app.py`):**
    * `[X]` Develop a simple Streamlit user interface with an input field and a chat display.
    * `[X]` Implement logic to pass the user's query to the agent and display the response. Use `@st.cache_resource` to
      avoid reloading the agent.

* **End-to-End Testing:**
    * `[X]` Perform comprehensive tests of the entire application flow to ensure the MVP is fully operational and ready
      to be demonstrated.

---

## **Part 2: Enhancement & Specialisation** 🚀

* **Goal:** Evolve the MVP by incorporating richer data, a specialised LLM, and more advanced reasoning capabilities.

---

### **Phase E: Data Augmentation**

This phase's sole purpose is to expand the agent's knowledge base with more diverse and frequent data.

* **Unstructured Data Expansion:**
    * `[ ]` Update `scripts/fetch_sec_data.py` to also download **10-Q** (quarterly) reports.
    * `[ ]` Create a new script, `scripts/fetch_transcripts.py`, to download earnings call transcripts using a service
      like Financial Modeling Prep.

* **Structured Data Expansion:**
    * `[ ]` Enhance the `QuantitativeTool` by adding a `get_analyst_ratings(ticker)` method.
    * `[ ]` Create a new `src/tools/macro_tool.py` file with a `MacroeconomicTool` class to fetch data (e.g., CPI,
      interest rates) from the FRED API.

* **Update RAG Index:**
    * `[ ]` Re-run the full data processing and RAG ingestion pipeline (`IngestionPipeline`) to add all the new
      unstructured data to the vector store.

---

### **Phase F: LLM Fine-Tuning**

This phase is dedicated entirely to specialising the LLM for high-stakes financial analysis.

* **Dataset Curation:**
    * `[ ]` Create a script (`scripts/generate_finetune_dataset.py`) to generate a high-quality, instruction-following
      dataset (min. 500 examples) from my newly augmented data sources.

* **Fine-Tuning Process:**
    * `[ ]` Write a fine-tuning script (`scripts/run_finetuning.py`) using Hugging Face Transformers and PEFT (LoRA).
    * `[ ]` Run the fine-tuning process on the curated dataset (using Colab/Kaggle for GPUs if necessary).
    * `[ ]` Save the trained LoRA adapters to a local directory.

---

### **Phase G: Advanced Agent Integration**

This phase focuses on integrating all the enhancements into the core agent logic for superior performance.

* **Model Integration:**
    * `[ ]` Modify `src/agent/alpha_agent.py` to load the base LLM and apply my trained LoRA adapters, creating the
      specialised `AlphaAgent`.

* **Tool & Memory Integration:**
    * `[ ]` Instantiate the new `MacroeconomicTool` and add it to the agent's list of available tools.
    * `[ ]` Integrate a `ChatMemoryBuffer` from LlamaIndex into the agent to enable conversational context and follow-up
      questions.

* **System Refinement:**
    * `[ ]` Refine the `ReActAgent`'s system prompt and tool descriptions to ensure it can effectively leverage its new
      model and tools for multi-step reasoning.

---

## **Part 3: Finalisation & Delivery** 🏆

* **Goal:** Rigorously test the enhanced model, polish the system, and produce all final project deliverables.

---

### **Phase H: Rigorous Evaluation & Refinement**

This phase is dedicated to quantitatively measuring performance and polishing the application.

* **Quantitative Evaluation:**
    * `[ ]` Create a `tests/golden_benchmark.csv` file with 20-30 complex questions and their verified, ground-truth
      answers.
    * `[ ]` Write an evaluation script (`scripts/evaluate_agent.py`) that runs the agent against the benchmark.
    * `[ ]` Inside the script, use the **Ragas** framework to compute metrics like `faithfulness`, `answer_relevancy`,
      and `context_precision`.

* **Refinement & Explainability:**
    * `[ ]` Analyse the evaluation results to identify and fix common failure modes (e.g., by further refining prompts
      or tool descriptions).
    * `[ ]` In `app.py`, use `st.expander` to add an "Explainability" feature that shows the source text chunks
      retrieved by the RAG tool for each answer.

---

### **Phase I: Final Documentation & Deliverables**

This final phase is focused solely on producing the project outputs for submission.

* **Code Quality & Documentation:**
    * `[ ]` Refactor the entire codebase for clarity and efficiency.
    * `[ ]` Run `ruff check . --fix` and `ruff format .` to standardise the code.
    * `[ ]` Add comprehensive docstrings and type hints to all major functions and classes.

* **Written Deliverables:**
    * `[ ]` Write the final project report in `/docs`, detailing the architecture, methodology, evaluation results, and
      conclusions.
    * `[ ]` Draft a journal-quality paper that summarises the project's novel contributions and empirical findings.

* **Presentation & Demo:**
    * `[ ]` Create a polished slide deck for the final presentation.
    * `[ ]` Record a comprehensive video demo of the final AlphaAgent application in action.
