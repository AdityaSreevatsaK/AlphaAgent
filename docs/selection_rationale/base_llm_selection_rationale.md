# Base LLM Selection Rationale

**Date**: 5th October 2025

### Context

The selection of a foundational Large Language Model (LLM) is a cornerstone of the AlphaAgent's architecture. This model
serves as the agent's central reasoning engine, responsible for interpreting user queries, planning tasks, and
synthesising information from its specialised tools. For the Minimum Viable Product (MVP), the goal is to balance
computational efficiency with the need for a sufficiently powerful and reliable reasoning engine to establish a strong
performance baseline.

### Decision Rationale

The strategy was to identify a powerful, well-supported, and efficient open-source model that could deliver high-quality
baseline performance. After evaluating several leading language models, the chosen base model for the AlphaAgent MVP is
**`Mistral-7B`**.

The decision was based on a comparative analysis of the following models, with a focus on their quantised versions:

| Model Name                | Parameters    | Quantized Size (4-bit) | Recommended RAM | Key Characteristics                                                                                                                                                                   |
|:--------------------------|:--------------|:-----------------------|:----------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **`Mistral-7B` (Chosen)** | **7 Billion** | **~4.1 GB**            | **16 GB**       | **A highly capable model known for its strong performance and reasoning capabilities. It represents an excellent balance of power and efficiency, making it ideal for a robust MVP.** |
| `Microsoft Phi-3-mini`    | 3.8 Billion   | ~2.2 GB                | 8 GB            | A state-of-the-art small language model with a very low memory footprint, offering strong performance for its size but with less overall reasoning capacity compared to `Mistral-7B`. |
| `Gemma 2B`                | 2 Billion     | ~1.4 GB                | 8 GB            | An extremely lightweight model from Google, excellent for memory-limited environments, but `Mistral-7B` offers significantly superior reasoning capabilities.                         |

The selection of **`Mistral-7B`** is a strategic choice that prioritises a high-quality, reliable baseline for the
agent's analytical capabilities. While it requires more RAM than smaller alternatives, its superior performance in
reasoning and instruction-following justifies the higher resource requirement, ensuring the MVP is built on a powerful
and scalable foundation.

### Future Considerations

While `Mistral-7B` provides a strong starting point, the roadmap for AlphaAgent includes a fine-tuning phase to
specialise the model on financial data. Post-MVP, and with dedicated GPU resources, a fine-tuned version of `Mistral-7B`
will be evaluated against larger, more advanced models to further enhance the depth and accuracy of the agent's
analytical capabilities.

---

### Revision Note (8th October 2025)

The project initially selected `Microsoft Phi-3-mini` as the base LLM, prioritising computational efficiency and a
minimal resource footprint for the MVP. While the model performed adequately on basic tasks, empirical testing revealed
limitations in its ability to handle the multi-step reasoning and complex financial synthesis required by AlphaAgent's
core objectives. To establish a more powerful and reliable analytical baseline, the decision was made to upgrade to
`Mistral-7B`. This change represents a strategic pivot to prioritise superior reasoning and instruction-following
capabilities from the start, thereby ensuring the MVP is built on a more robust and scalable foundation.
