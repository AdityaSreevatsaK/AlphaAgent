# Roadmap
## **Phase A: Project & Environment Setup Checklist**

This phase covers the initial scaffolding and configuration of your project environment.

* **Version Control & Repository:**
    * [X] Create a new repository on GitHub named `AlphaAgent`.
    * [X] Clone the repository to your local machine.
    * [X] Create a `.gitignore` file (a standard Python template is a good start).
    * [X] Make your initial commit: `git commit -m "Initial project setup"`.

* **Python Environment:**
    * [X] Create a dedicated Python virtual environment: `conda create --name AlphaAgentEnv python=3.11`.
    * [X] Activate the environment: `conda activate AlphaAgentEnv`.
    * [X] Install foundational libraries:
        * [X] Core ML/AI: `pip install torch transformers accelerate bitsandbytes peft`
        * [X] Agent Framework: `pip install llama-index`
        * [X] Embeddings: `pip install sentence-transformers`
        * [X] Vector DB: `pip install faiss-cpu` (or `faiss-gpu`)
        * [X] Data Tools: `pip install pandas yfinance`
        * [X] Web App: `pip install streamlit`
        * [X] Utilities: `pip install python-dotenv jupyter notebook beautifulsoup4 sec-edgar-downloader`
    * [X] Freeze the installed packages for reproducibility: `conda env export > environment.yml`.

* **API Keys & Configuration:**
    * [X] Obtain an API key from a financial news service (e.g., Finnhub or NewsAPI).
    * [X] Identify your user agent for the SEC EDGAR API.
    * [X] Create a `.env` file in the project's root directory.
    * [X] Add the `.env` file to `.gitignore` to prevent committing secrets.
    * [ ] Write a `config.py` script in `src/utils` to load environment variables and manage project-wide settings.

---

## **Phase B: Data Ingestion & Pre-processing Checklist**

This phase focuses on sourcing and preparing the raw data needed for the agent's tools.

* **Target Entities:**
    * [ ] Define an initial list of 5-10 publicly traded companies for analysis (e.g., a mix of tech, finance, and industrial sectors). Store this list in your `config.py` or a separate `JSON` file.

* **Unstructured Data (for RAG Tool):**
    * [ ] Write a script (`scripts/fetch_sec_data.py`) to download 10-K (annual) and 8-K (current report) filings for your target companies from EDGAR.
    * [ ] Write a script (`scripts/fetch_news_data.py`) to download recent news articles for your target companies using your chosen news API.
    * [ ] Implement a simple file-based caching strategy in both scripts to avoid re-downloading data.
    * [ ] Create data cleaning functions (`src/data_processing.py`) to strip boilerplate text, HTML, and other noise from the raw text files, saving the output to `/data/processed`.

* **Structured Data (for Quantitative Tool):**
    * [ ] Use a notebook (`notebooks/01_yfinance_test.ipynb`) to test fetching data via the `yfinance` library for target companies.
    * [ ] Confirm retrieval of key data points: current price, historical data, financial ratios (P/E, P/S, etc.), and company information (Market Cap, EPS).

---

## **Phase C: Core Architecture & Project Structure Checklist**

This phase involves finalising the technical design and organising the project structure.

* **Project Structure:**
    * [ ] Establish the full project directory structure as planned.
    * [ ] Update `README.md` with the project abstract, goals, and setup instructions.
    * [ ] Create a project board (e.g., GitHub Projects) and populate it with tasks from this roadmap.

* **Core Model & Architecture Decisions:**
    * [ ] Finalise the base LLM for fine-tuning (e.g., Llama-3-8B-Instruct, Mistral-7B-Instruct).
    * [ ] Finalise the embedding model for the RAG pipeline (e.g., `bge-large-en-v1.5`).
    * [ ] Confirm the choice of agent framework (LlamaIndex).
    * [ ] Confirm the choice of vector database for initial development (FAISS).

---

## **Phase D: Core Component Implementation Checklist**

This phase involves building the individual tools that the agent will use.

* **RAG Pipeline Development (in `/src/tools`):**
    * [ ] Implement the ingestion pipeline:
        * [ ] Document loader for cleaned text files from `/data/processed`.
        * [ ] Text chunking/splitting strategy.
        * [ ] Embedding generation using the chosen sentence-transformer.
        * [ ] Store embeddings and document chunks in a FAISS vector index.
    * [ ] Create a `RAGTool` class that can take a query, retrieve relevant context from the vector index, and return it.

* **Quantitative Tool Development (in `/src/tools`):**
    * [ ] Refactor the `yfinance` exploration code from the notebook into a robust `QuantitativeTool` class.
    * [ ] Implement specific functions within the class, such as:
        * `get_current_stock_price(ticker)`
        * `get_key_financial_ratios(ticker)`
        * `get_latest_company_news(ticker)` (using the news API)

---

## **Phase E: LLM Fine-Tuning Checklist**

This phase focuses on specialising the chosen LLM for financial analysis.

* **Dataset Curation:**
    * [ ] Generate a high-quality instruction-following dataset for finance. This could involve creating question-answer pairs based on the financial data you have gathered (e.g., Q: "What was the revenue for AAPL in their last 10-K?" A: "Based on the 10-K filing from [date], the revenue was...").
    * [ ] Format the dataset correctly for the chosen fine-tuning script.

* **Fine-Tuning Process:**
    * [ ] Write a fine-tuning script using Hugging Face Transformers and PEFT (LoRA) for efficiency.
    * [ ] Run the fine-tuning process on the curated dataset. Use a platform like Google Colab or Kaggle if you require GPU resources.
    * [ ] Save the trained LoRA adapters and merge them with the base model if necessary.

* **Evaluation:**
    * [ ] Create a small, held-out evaluation set of financial questions.
    * [ ] Evaluate the performance of the fine-tuned model against the base model on this set, checking for accuracy and relevance.

---

## **Phase F: System Integration & Application Development Checklist**

This phase brings all the components together into a single, functional system.

* **Agent Orchestration (in `/src/agent`):**
    * [ ] Integrate the fine-tuned LLM into the LlamaIndex framework.
    * [ ] Define the `RAGTool` and `QuantitativeTool` with clear descriptions so the agent understands their capabilities.
    * [ ] Create the master `AlphaAgent` that orchestrates calls to the appropriate tool based on the user's query.

* **Web Application (in `/src/app.py`):**
    * [ ] Develop the Streamlit user interface.
    * [ ] Create an input field for the user to ask financial questions.
    * [ ] Implement logic to pass the query to the `AlphaAgent`.
    * [ ] Design the output display to show the agent's final answer, along with the evidence (e.g., text snippets from the RAG tool, data from the quantitative tool).

* **End-to-End Testing:**
    * [ ] Perform comprehensive tests of the entire application flow, from entering a query in Streamlit to receiving a fully analysed, evidence-backed response.

---

## **Phase G: Evaluation, Refinement & Finalisation Checklist**

The final phase for polishing the project, conducting a final evaluation, and preparing for submission.

* **Holistic Evaluation & Refinement:**
    * [ ] Define a set of complex, multi-step analysis tasks to benchmark the agent's performance.
    * [ ] Conduct a thorough error analysis to identify common failure modes (e.g., incorrect tool selection, hallucinated details).
    * [ ] Refine the tool descriptions, agent prompts, or model based on the evaluation results.

* **Documentation & Code Quality:**
    * [ ] Refactor code for clarity, modularity, and efficiency. Remove redundant notebooks.
    * [ ] Add docstrings and comments to all major functions and classes.
    * [ ] Write the final project report, detailing the architecture, methodology, challenges, and results.
    * [ ] Prepare a final presentation or demo of the working AlphaAgent.