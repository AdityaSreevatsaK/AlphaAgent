# Roadmap
### **Phase A: Project & Environment Setup Checklist**

This checklist covers the initial scaffolding of your project.

* **Version Control & Repository:**

    * [X] Create a new repository on GitHub named `AlphaAgent`.
    * [X] Clone the repository to your local machine.
    * [X] Create a `.gitignore` file (a standard Python template is a good start).
    * [X] Make your initial commit: `git commit -m "Initial project setup"`.

* **Python Environment:**

    * [X] Create a dedicated Python virtual environment: `conda create --name AlphaAgentEnv python=3.11`.
    * [X] Activate the environment: `conda activate AlphaAgentEnv`.
    * [X] Install foundational libraries:
        * [X] Core ML/AI: `pip install torch transformers accelerate bitsandbytes`
        * [X] Agent Framework: `pip install llama-index`
        * [X] Embeddings: `pip install sentence-transformers`
        * [X] Vector DB: `pip install faiss-cpu` (or `faiss-gpu`)
        * [X] Data Tools: `pip install pandas yfinance`
        * [X] Web App: `pip install streamlit`
        * [X] Utilities: `pip install python-dotenv jupyter notebook beautifulsoup4`
    * [X] Freeze the installed packages into a file for reproducibility: `conda env export > environment.yml`.

* **API Keys & Configuration:**

    * [X] Obtain an API key from a financial news service (e.g., Finnhub or NewsAPI).
    * [ ] Identify your user agent for the SEC EDGAR API (this is typically your "FirstName LastName email@domain.com").
    * [X] Create a `.env` file in your project's root directory to securely store your API keys.
    * [X] Add the `.env` file to your `.gitignore` to prevent committing secrets.
    * [ ] Write a `config.py` script or utility function to load these keys from the environment.

### **Phase B: Data Gathering & Preparation Checklist**

This covers sourcing the raw material for your agent's tools.

* **Target Entities:**

    * [ ] Define an initial list of 5-10 publicly traded companies for your analysis (e.g., a mix of tech, finance, and industrial sectors). Store this list in a configuration file.

* **Unstructured Data (for RAG Tool):**

    * [ ] Write a script (`scripts/fetch_sec_data.py`) to download 10-K (annual) and 8-K (current report) filings for your target companies from EDGAR.
    * [ ] Write a script (`scripts/fetch_news_data.py`) to download recent news articles for your target companies using your chosen news API.
    * [ ] Implement a simple caching strategy for both scripts (e.g., check if a file for a specific company and date already exists before downloading again).
    * [ ] Create a data cleaning function to strip out basic HTML, boilerplate text, and other noise from the raw text files.

* **Structured Data (for Quantitative Tool):**

    * [ ] Write a small script (`notebooks/01_yfinance_test.ipynb`) to test fetching data using the `yfinance` library for your target companies.
    * [ ] Confirm you can retrieve essential data points:
        * [ ] Current stock price.
        * [ ] Historical price data (for moving averages).
        * [ ] Key financial ratios (P/E, P/S).
        * [ ] Company information (Market Cap, EPS).

### **Phase C: Other Essential Prerequisites Checklist**

* **Project Documentation & Structure:**

    * [ ] Establish your project's directory structure:
        ```
            /AlphaAgent
            |-- /data
            |   |-- /raw       # Raw downloaded data
            |   |-- /processed # Cleaned data
            |-- /notebooks     # For exploration and experiments
            |-- /scripts       # Standalone scripts for data gathering etc.
            |-- /src           # Main source code (agent, tools, app)
            |-- /tests         # Unit tests
            |-- .env
            |-- .gitignore
            |-- README.md
            |-- environment.yml
        ```
    * [ ] Update your `README.md` with the full project abstract and high-level goals.
    * [ ] Create a project board (e.g., GitHub Projects, Trello) and populate it with the high-level tasks from the 12-week roadmap.

* **Core Model & Architecture Decisions:**

    * [ ] Finalise the base LLM you will fine-tune (e.g., Llama-3-8B-Instruct).
    * [ ] Finalise the embedding model for the RAG pipeline (e.g., `bge-large-en-v1.5`).
    * [ ] Confirm the choice of agent framework (LlamaIndex).
    * [ ] Confirm the choice of vector database for initial development (FAISS).
