# Embedding Model Selection Strategy

**Date**: 2nd October 2025

### Context

For the Retrieval-Augmented Generation (RAG) pipeline in the **AlphaAgent** project, the choice of a text embedding
model is a critical architectural decision. The model must convert financial text into numerical vectors for effective
semantic search. The selection process for the Minimum Viable Product (MVP) was guided by the following criteria:

* **Primary Criterion: Computational Efficiency.** The model must perform efficiently on a local system without a
  dedicated GPU and within the limits of free-tier cloud environments. This prioritises low latency (speed), a low
  memory footprint, and CPU-optimised performance.
* **Secondary Criterion: Retrieval Accuracy.** While speed is the priority, the model must be sufficiently accurate to
  establish a functional and meaningful baseline for the RAG pipeline.

### Decision Rationale

The selection strategy was to evaluate a spectrum of models and choose the one that best balances performance with the
project's strict computational constraints. After review, the chosen model is `sentence-transformers/all-MiniLM-L6-v2`.

The decision was based on a comparison of the following models:

| Model Name                      | Embedding Dimensions | Model Size (Approx.) | Key Characteristics                                                                                                                 |
|:--------------------------------|:---------------------|:---------------------|:------------------------------------------------------------------------------------------------------------------------------------|
| **`all-MiniLM-L6-v2` (Chosen)** | **384**              | **80 MB**            | **A lightweight and fast model, optimised for symmetric semantic search. It offers an excellent balance of speed and performance.** |
| `BAAI/bge-base-en-v1.5`         | 768                  | 440 MB               | A larger, high-performance model that often ranks highly on retrieval benchmarks. It is more resource-intensive.                    |
| `BAAI/bge-large-en-v1.5`        | 1024                 | 1.34 GB              | A state-of-the-art model designed for maximum retrieval accuracy, but with significant computational and memory demands.            |

The selection of **`all-MiniLM-L6-v2`** is a strategic decision directly aligned with the MVP's primary requirement for
computational efficiency. Its small size and optimised performance ensure fast iteration cycles during development on
CPU-only hardware, perfectly suiting the project's current constraints while providing a robust baseline for retrieval.

---

### Future Considerations

While `all-MiniLM-L6-v2` is optimal for the MVP, the plan is to re-evaluate this decision as the project matures. For a
production-level version of AlphaAgent, where retrieval accuracy is paramount and more powerful (GPU-enabled)
infrastructure is available, an upgrade to a larger model like `BAAI/bge-large-en-v1.5` will be considered to enhance
the quality and precision of the financial analysis.
