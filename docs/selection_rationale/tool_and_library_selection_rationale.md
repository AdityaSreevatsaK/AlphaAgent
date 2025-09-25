# Tool and Library Selection Rationale

**Date**: 22nd July 2025

### Context

For the **AlphaAgent** project, selecting the right technology stack is critical for both the initial MVP and for future
scalability. My goal was to choose libraries and frameworks that are robust, widely supported, and specifically suited
to the complex demands of financial data analysis and agentic AI. The choices below reflect a strategy focused on
proven, specialised tools for each component of the architecture.

### Decision Rationale

* **Core AI Framework**:
    * `LlamaIndex`: I chose LlamaIndex as the primary framework for building the agent. Its architecture is explicitly
      optimised for Retrieval-Augmented Generation (RAG), which is the absolute core of my qualitative analysis tool.
      While other frameworks exist, LlamaIndex's focus on data ingestion, indexing, and query pipelines made it the
      ideal choice for a RAG-heavy project like this one.

* **Machine Learning & Deep Learning**:
    * `Transformers` & `PyTorch`: For all deep learning tasks, particularly the future fine-tuning of the LLM, I
      selected the Hugging Face `Transformers` library with a `PyTorch` backend. This combination is the industry
      standard for NLP and gives me access to a vast ecosystem of pre-trained models, tokenizers, and state-of-the-art
      training techniques like PEFT LoRA.
    * `sentence-transformers`: This library was chosen for its simplicity and power in generating high-quality
      embeddings. For the RAG pipeline to be effective, the quality of the text embeddings is paramount, and this
      library provides easy access to top-performing models.

* **Quantitative Data Retrieval**:
    * `yfinance`: For fetching structured financial data, I selected `yfinance`. It provides a reliable,
      straightforward, and Pythonic interface to Yahoo Finance's extensive database without requiring an API key for the
      initial MVP scope. This allows me to quickly build and validate the quantitative tool.

* **Environment and Dependency Management**:
    * `Conda`: I decided to use Conda for environment management. Given the complex dependencies in the data science and
      AI ecosystem, particularly with libraries like PyTorch, Conda's ability to manage Python and non-Python packages
      alike is crucial for ensuring the project is reproducible and stable.

* **Web Application Framework**:
    * `Streamlit`: For the user interface, I chose Streamlit because it allows me to build and deploy interactive web
      applications directly from Python scripts with minimal effort. Its simplicity is ideal for creating a functional
      and clean UI for the MVP, allowing me to focus on the core agent logic.
