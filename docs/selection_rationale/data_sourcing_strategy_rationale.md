# Data Sourcing Strategy Rationale

**Date**: 22nd July 2025

### Context

The quality and reliability of AlphaAgent's analysis are directly dependent on the quality of its input data. For this
reason, I've established a clear strategy for sourcing both the qualitative (textual) and quantitative (numerical) data
required for the project. My primary criteria were authoritativeness, accessibility, and relevance to financial
analysis.

### Decision Rationale

* **Qualitative Data: Official Filings**:
    * **Source**: **SEC EDGAR Database**.
    * **Rationale**: For official company reports, the SEC EDGAR database is the ground truth. I chose this as my
      primary source for 10-K (annual) and 8-K (current event) filings because the data is authoritative, comprehensive
      for US-listed companies, and publicly accessible. Using the official source ensures the agent's analysis is based
      on verified, unfiltered company disclosures. This choice directly influenced my company selection, as I needed to
      ensure all target companies were listed on a US exchange.

* **Qualitative Data: Market News & Sentiment**:
    * **Source**: **Finnhub API**.
    * **Rationale**: While official filings are crucial, they do not capture real-time market sentiment. To fill this
      gap, I chose the Finnhub API for news data. I selected it because it offers a generous free tier that is
      sufficient for the project's MVP, provides access to a wide range of financial news sources, and has a
      straightforward Python client library, which makes integration simple and efficient.

* **Quantitative Data: Market Metrics**:
    * **Source**: **Yahoo Finance (via `yfinance` library)**.
    * **Rationale**: For the agent's quantitative tool, I needed a source for real-time and historical stock prices, key
      financial ratios (like P/E), and market capitalisation data. I selected Yahoo Finance as the source because of its
      comprehensive coverage and ease of access. The `yfinance` library provides a stable and easy-to-use interface,
      allowing the agent to fetch this critical data on-demand without the need for managing API keys in the initial
      stages of the project.
