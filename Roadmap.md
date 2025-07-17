# Roadmap
### **Phase A: Project & Environment Setup Checklist**

This checklist covers the initial scaffolding of your project.

  * **Version Control & Repository:**

      * [ ] Create a new repository on GitHub named `AlphaAgent`.
      * [ ] Clone the repository to your local machine.
      * [ ] Create a `.gitignore` file (a standard Python template is a good start).
      * [ ] Make initial commit: `git commit -m "Initial project setup"`.

  * **Python Environment:**

      * [ ] Create a dedicated Python virtual environment: `python3 -m venv AlphaAgentEnv`.
      * [ ] Activate the environment: `source AlphaAgentEnv/bin/activate`.
      * [ ] Install foundational libraries:
          * [ ] Core ML/AI: `pip install torch transformers accelerate bitsandbytes`
          * [ ] Agent Framework: `pip install llama-index`
          * [ ] Embeddings: `pip install sentence-transformers`
          * [ ] Vector DB: `pip install faiss-cpu` (or `faiss-gpu` if you have a compatible environment)
          * [ ] Data Tools: `pip install pandas yfinance`
          * [ ] Web App: `pip install streamlit`
          * [ ] Utilities: `pip install python-dotenv jupyter notebook beautifulsoup4`
      * [ ] Freeze the installed packages into a file for reproducibility: `pip freeze > requirements.txt`.

  * **API Keys & Configuration:**

      * [ ] Obtain an API key from a financial news service (e.g., [Finnhub](https://finnhub.io/) or [NewsAPI](https://newsapi.org/)).
      * [ ] Identify your user agent for the SEC EDGAR API (this is typically your "FirstName LastName email@domain.com").
      * [ ] Create a `.env` file in your project's root directory to securely store your API keys.
      * [ ] Add the `.env` file to your `.gitignore` to prevent committing secrets.
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

This covers documentation, planning, and architectural decisions.

  * **Project Documentation & Structure:**

      * [ ] Establish your project's directory structure:
        ```
        /AlphaAgent
        |-- /data
        |   |-- /raw       # Raw downloaded files
        |   |-- /processed # Cleaned text
        |-- /notebooks     # For exploration and experiments
        |-- /scripts       # Standalone scripts for data gathering etc.
        |-- /src           # Main source code (agent, tools, app)
        |-- /tests         # Unit tests
        |-- .env
        |-- .gitignore
        |-- README.md
        |-- requirements.txt
        ```
      * [ ] Update your `README.md` with the full project abstract and high-level goals.
      * [ ] Create a project board (e.g., GitHub Projects, Trello) and populate it with the high-level tasks from the 12-week roadmap.

  * **Core Model & Architecture Decisions:**

      * [ ] Finalise the base LLM you will fine-tune (e.g., Llama-3-8B-Instruct).
      * [ ] Finalise the embedding model for the RAG pipeline (e.g., `bge-large-en-v1.5`).
      * [ ] Confirm the choice of agent framework (LlamaIndex).
      * [ ] Confirm the choice of vector database for initial development (FAISS).

Completing this comprehensive checklist will put you in an excellent position to begin building the core components of AlphaAgent with confidence and clarity.