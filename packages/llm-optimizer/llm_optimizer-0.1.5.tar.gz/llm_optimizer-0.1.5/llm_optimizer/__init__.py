# __init__.py - llm_optimizer package
"""
LLM Optimizer Package

Provides functionality for:
- Loading HuggingFace models
- Applying pruning & freezing optimizations
- Tracking CO₂ emissions during inference
- Evaluating performance metrics (Perplexity, BLEU, ROUGE)
"""

from .main import load_and_generate

__all__ = ["load_and_generate"]

__version__ = "0.1.5"
