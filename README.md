# multimodal-ai-trend-engine
An agentic multimodal pipeline for AI/ML trend analysis and project opportunity scoring, optimized for Inclusive UX.

# Multimodal AI Trend Engine

An intelligent pipeline designed to extract high-signal technical trends from social media noise. 

## 🧠 The Philosophy
Most trend-spotting tools focus on engagement metrics. This engine focuses on **Semantic Signal**. By combining web automation with local LLM inference (Ollama), we distill technical expert content into actionable insights.

## 🛠️ Technical Stack
- **Scraping:** Playwright (Stealth mode) for robust DOM navigation.
- **Intelligence:** Ollama (Llama 3) for local, privacy-first inference.
- **Logic:** Python-based asynchronous pipeline with heuristic-based data extraction.

## 📈 Featured Insight: The Memory Wall
The engine successfully identified a critical bottleneck in LLM inference: the shift from **Compute-bound** to **Memory-bound** constraints, specifically analyzing the H100 TFLOPS-to-Bandwidth ratio.

## 🚀 Setup
1. `pip install -r requirements.txt`
2. `playwright install chromium`
3. `ollama serve` and `ollama pull llama3`
4. Run `src/metadata_extractor.py` followed by `src/ai_analyzer.py`