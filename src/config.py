"""
Central configuration for Cora application.
Stores all global constants and settings.
"""

import os
import torch

# --- Global Settings ---
DEFAULT_MODEL = "qwen2.5:7b"
MAX_TURNS = 20  # Conversation history length

# --- System Settings ---
# Auto-detect device
if torch.cuda.is_available():
    _default_device = "cuda"
else:
    _default_device = "cpu"

DEVICE = os.getenv("DEVICE", _default_device)


# --- External Services ---
# Translator API
TRANSLATOR_API_URL = os.getenv("TRANSLATOR_API_URL", "http://localhost:8000")

# --- Classification Settings (Cora) ---
CLASSIFICATION_TEMPERATURE = 0.4
CLASSIFICATION_TOP_P = 0.15
CLASSIFICATION_SEED = 42
CLASSIFICATION_FORMAT = "json"

# --- Q&A Settings (QA) ---
QA_TEMPERATURE = 0.65
QA_TOP_P = 0.8
QA_NUM_PREDICT = 300
