#!/usr/bin/env python3
"""
Model alias normalization for Swiss AI CLI
Centralizes canonical IDs and common user-friendly aliases.
"""

from __future__ import annotations

from typing import Dict


# Canonical model IDs we support out-of-the-box
# Note: OpenRouter typically uses ":free" on the API even if UI shows "(free)".
CANONICAL_MODELS = {
    # DeepSeek
    "deepseek/deepseek-r1:free",
    "deepseek/deepseek-chat-v3-0324:free",

    # Google Gemini
    "google/gemini-2.0-flash-exp:free",
    "google/gemini-2.5-pro-exp-03-25:free",

    # Meta Llama
    "meta-llama/llama-3.3-70b-instruct:free",

    # Qwen / QwQ
    "qwen/qwq-32b:free",
    # Common coder alias (mapped) – may not always be free
    "qwen/qwen2.5-coder",

    # Kimi K2 (MoonshotAI) – free tier varies by region/time
    "moonshot/kimi-k2:free",
}


# Lowercased alias -> canonical id
MODEL_ALIASES: Dict[str, str] = {
    # DeepSeek
    "deepseek-r1": "deepseek/deepseek-r1",
    "deepseek-r1:free": "deepseek/deepseek-r1:free",
    "deepseek-v3": "deepseek/deepseek-chat-v3-0324",
    "deepseek-v3:free": "deepseek/deepseek-chat-v3-0324:free",

    # Gemini
    "gemini-2.0-flash": "google/gemini-2.0-flash-exp",
    "gemini-2.0-flash:free": "google/gemini-2.0-flash-exp:free",
    "gemini-2.5-pro": "google/gemini-2.5-pro",
    "gemini-2.5-pro:free": "google/gemini-2.5-pro:free",
    "gemini-2.5-flash": "google/gemini-2.5-flash",
    "gemini-2.5-flash-lite": "google/gemini-2.5-flash-lite",

    # Llama
    "llama-3.3-70b-instruct": "meta-llama/llama-3.3-70b-instruct",
    "llama-3.3-70b-instruct:free": "meta-llama/llama-3.3-70b-instruct:free",

    # Qwen
    "qwq-32b": "qwen/qwq-32b",
    "qwq-32b:free": "qwen/qwq-32b:free",
    "qwen3-coder": "qwen/qwen3-coder",
    "qwen3-coder:free": "qwen/qwen3-coder:free",

    # Kimi K2 (MoonshotAI)
    "kimi-k2": "moonshot/kimi-k2",
    "kimi-k2:free": "moonshot/kimi-k2:free",
    "moonshot/kimi-k2 (free)": "moonshot/kimi-k2:free",

    # xAI Grok (only current gens)
    "grok-4": "xai/grok-4",
    "grok-3": "xai/grok-3",

    # OpenAI GPT-5
    "gpt-5": "openai/gpt-5",
    "gpt-5-mini": "openai/gpt-5-mini",

    # Anthropic Claude (map 4/4.1 names to anthro routing via OpenRouter when available)
    "claude-4": "anthropic/claude-4",
    "claude-4.1": "anthropic/claude-4.1",
    "claude-4-sonnet": "anthropic/claude-4-sonnet",
    "claude-4.1-opus": "anthropic/claude-4.1-opus",
    "claude-3.7-sonnet": "anthropic/claude-3.7-sonnet",
}


def _standardize_suffix(model_id: str) -> str:
    # Convert "(free)" -> ":free" and remove spaces around colon
    m = model_id.strip()
    if m.endswith("(free)"):
        m = m[:-6].rstrip() + ":free"
    # Collapse accidental spaces, e.g., "kimi-k2 : free"
    return m.replace(" :", ":").replace(": ", ":")


def normalize_model_id(user_input: str) -> str:
    """Normalize a user-specified model to a canonical provider/model id.

    - Resolves common aliases (case-insensitive)
    - Converts (free) to :free
    - Leaves intact unknown IDs (best-effort)
    """
    if not user_input:
        return user_input

    # Standardize free suffix first
    candidate = _standardize_suffix(user_input)

    # Try alias mapping (lowercased)
    mapped = MODEL_ALIASES.get(candidate.lower())
    if mapped:
        return _standardize_suffix(mapped)

    # If user gave bare names without org, add common org prefixes
    # e.g., "deepseek-r1" -> "deepseek/deepseek-r1"
    if "/" not in candidate:
        if candidate.lower().startswith("deepseek-"):
            return _standardize_suffix(f"deepseek/{candidate}")
        if candidate.lower().startswith("qwq-") or candidate.lower().startswith("qwen"):
            return _standardize_suffix(f"qwen/{candidate}")
        if candidate.lower().startswith("llama-"):
            return _standardize_suffix(f"meta-llama/{candidate}")
        if candidate.lower().startswith("gemini-"):
            return _standardize_suffix(f"google/{candidate}")
        if candidate.lower().startswith("kimi-k2"):
            return _standardize_suffix("moonshot/kimi-k2:free" if candidate.endswith(":free") else "moonshot/kimi-k2")

    return candidate


