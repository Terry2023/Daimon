# Daimon

**Daimon** is a psychometric narrative engine designed to bridge the gap between abstract personality traits and high-fidelity prose generation. By utilizing a neuro-symbolic feedback loop—mapping Big Five personality traits, Zodiac archetypes, and trauma weights to physiological hormone tensors—Daimon forces large language models (like `gemma3:27b`) to adhere to a consistent "Authorial Manifold."

## The Core Concept
Standard prompting produces generic AI output. Daimon produces **calibrated prose**. By grounding the model in a fixed neurochemical set point, we bypass "prompt drift" and ensure the narrative voice is a deterministic byproduct of the author's internal state.

## System Architecture
Daimon operates as a closed-loop system:

1.  **State Calibration (`sliders_app_2.py`):** Define the author's personality via psychometric sliders (Big Five + Trauma).
2.  **Hormone Mapping (`hormone_lab_v4.2.py`):** Translates psychometric inputs into a physiological tensor profile (Cortisol, Dopamine, Oxytocin, Adrenaline).
3.  **Governance Layer:** Injects these tensors as immutable `system_instruction` constraints, effectively creating a "mathematical cage" for the model.
4.  **Hedge-Trimming Loop:** An iterative process of auditing generated prose to refine Negative Prompt registries, ensuring the "Author" does not hallucinate or revert to base model tropes.

## Quick Start

1.  **Dependencies:** Ensure `ollama` is running and the `gemma3:27b-it-qat` model is pulled locally.
2.  **Database Initialization:** Run the core engine to setup your `hormone_lab.db`:
```bash
    python hormone_lab_v4.2.py
```
3.  **Interface Calibration:** Launch the Streamlit control panel:
```bash
    streamlit run sliders_app_2.py
```

## Repository Structure
*   `/stories`: Archival storage for generated artifacts.
*   `hormone_lab.db`: SQLite ledger containing all authored presets and limbic state transitions.
*   `hormone_lab_v4.2.py`: The core generation and SQLite-integration engine.
*   `sliders_app_2.py`: The psychometric interface and control panel for live inference.

## The Hedge-Trimming Philosophy
Daimon is not a static tool; it is a collaborative instrument. Use the output audit to identify structural failure modes (clichés, overused adjectives, procedural drift). As you trim these stylistic hedges, your authorial profiles become increasingly indistinguishable from the target manifold.

---

> *“A Daimon is not a ghost, but a guiding spirit—the internal spark that determines one's character and fate.”*
