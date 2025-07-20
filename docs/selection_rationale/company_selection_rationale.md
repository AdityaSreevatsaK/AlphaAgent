# Initial Company Selection Rationale

**Date**: 20th July 2025

### Context

For the initial analysis phase of the **AlphaAgent** project, a representative and diverse set of publicly traded companies was required. The primary goal was to select companies that would provide a rich and varied dataset for testing the agent's data ingestion, analysis, and language processing capabilities. A key technical constraint is that the companies must be listed on a US stock exchange to ensure their financial filings are available via the SEC EDGAR database.

### Decision Rationale

The selection strategy was to create a balanced portfolio covering key global sectors. To meet the technical requirements while maintaining global diversity, the list includes market leaders from the United States, alongside influential, US-listed corporations from Japan and India. This global mix is crucial for training the agent to handle diverse financial reporting styles, market conditions, and industry-specific terminology.

The selected companies are:

* **Technology (Mega-Cap US)**:
    * `AAPL` (Apple Inc.): A benchmark for consumer electronics and brand loyalty.
    * `MSFT` (Microsoft Corporation): Represents a complex blend of enterprise software, cloud computing, and consumer products.
    * `NVDA` (NVIDIA Corporation): A key player in the AI and semiconductor space.

* **E-commerce & Cloud**:
    * `AMZN` (Amazon.com, Inc.): A leader in both e-commerce and cloud services (AWS).

* **Finance**:
    * `JPM` (JPMorgan Chase & Co.): One of the largest US banks, providing insight into the financial sector.

* **Automotive & Advanced Manufacturing**:
    * `TSLA` (Tesla, Inc.): A high-growth technology company and auto manufacturer.
    * `TM` (Toyota Motor Corporation): A traditional, established global automotive leader, providing a valuable point of comparison.

* **Conglomerate/Investment**:
    * `BRK-B` (Berkshire Hathaway Inc.): A holding company with a vast and diverse portfolio.

* **International Representation (US-Listed)**:
    * `SONY` (Sony Group Corporation): A major Japanese global leader in electronics and entertainment, ensuring representation from the Asian technology sector.
    * `INFY` (Infosys Limited): A top-tier IT services and consulting firm from India with a strong global presence and a US listing (ADR).

---

### Revision Note (20th July 2025)

The initial list included Samsung (`005930.KS`) and Tata Consultancy Services (`TCS.NS`). These were replaced with Sony (`SONY`) and Infosys (`INFY`) because Samsung and TCS are not directly listed on a US exchange, and therefore their filings are not available in the SEC EDGAR database that our downloader script relies on. The replacements maintain the desired sector and geographic diversity.
