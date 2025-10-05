# Base LLM Selection Rationale

**Date**: 5th October 2025

### Context

The selection of a foundational Large Language Model (LLM) is a cornerstone of the AlphaAgent's architecture. This model
serves as the agent's central reasoning engine, responsible for interpreting user queries, planning tasks, and
synthesising information from its specialised tools. For the Minimum Viable Product (MVP), the primary constraint is
ensuring the model can run efficiently on standard, CPU-only hardware with limited memory, making computational
efficiency and a small resource footprint the most critical selection criteria.

### Decision Rationale

The strategy was to identify a small, powerful, and highly efficient open-source model that could deliver a satisfactory
baseline performance without requiring GPU acceleration. After evaluating several leading small language models (SLMs),
the chosen base model for the AlphaAgent MVP is **`Microsoft Phi-3-mini`**.

The decision was based on a comparative analysis of the following models, with a focus on their quantised versions which
are optimised for CPU inference:

| Model Name                | Parameters      | Quantized Size (4-bit) | Recommended RAM | Key Characteristics                                                                                                                                                                     |
|:--------------------------|:----------------|:-----------------------|:----------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **`Phi-3-mini` (Chosen)** | **3.8 Billion** | **~2.2 GB**            | **8 GB**        | **State-of-the-art performance for its size, offering strong reasoning and language understanding capabilities with a very low memory footprint.**                                      |
| `Mistral-7B`              | 7 Billion       | ~4.1 GB                | 16 GB           | A highly capable model known for its strong performance, but it requires significantly more RAM, making it less suitable for resource-constrained MVP development.                      |
| `Gemma 2B`                | 2 Billion       | ~1.4 GB                | 8 GB            | An extremely lightweight model from Google, excellent for memory-limited environments, but `Phi-3-mini` generally offers superior reasoning capabilities for a slight increase in size. |

The selection of **`Phi-3-mini`** is a pragmatic choice that directly addresses the MVP's primary constraints. Its
ability to run effectively on systems with as little as 8 GB of RAM makes it highly accessible and ensures a smooth
development and demonstration experience on standard hardware. It represents the optimal balance between computational
efficiency and the advanced reasoning capabilities required for a financial analysis agent.

### Future Considerations

While `Phi-3-mini` is the ideal starting point, the roadmap for AlphaAgent includes a fine-tuning phase where a more
powerful model will be specialised on financial data. Post-MVP, and with access to GPU resources, an upgrade to a larger
and more capable model, such as a fine-tuned version of `Mistral-7B` or a future, more advanced SLM, will be explored to
enhance the depth and accuracy of the agent's analytical capabilities.
