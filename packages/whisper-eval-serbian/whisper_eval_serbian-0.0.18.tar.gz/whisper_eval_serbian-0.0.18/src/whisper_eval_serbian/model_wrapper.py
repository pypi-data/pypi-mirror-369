# whisper_evaluator/model_wrapper.py
import torch
from transformers import pipeline

class WhisperModel:
    """
    A wrapper for the Hugging Face ASR pipeline for Whisper models.
    """
    def __init__(self, name_or_path: str, device: str = "cuda"):
        """
        Initializes the Whisper model using the Hugging Face pipeline.
        """
        if device == "cuda" and not torch.cuda.is_available():
            print("Warning: CUDA not available, falling back to CPU.")
            resolved_device = "cpu"
        else:
            resolved_device = device

        print(f"Loading Whisper model from {name_or_path} on {resolved_device}...")
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=name_or_path,
            device=resolved_device,
            chunk_length_s=30,
            stride_length_s=5,
        )

        # --- NEW: Define explicit generation arguments ---
        # We define these once here for clarity and reuse.
        self.generate_kwargs = {
            "task": "transcribe",
            "language": "<|sr|>", # Use the formal language token for Serbian
        }

    def transcribe(self, audio_array, sampling_rate: int) -> str:
        """
        Generates a transcription for a single audio input.
        """
        # --- MODIFIED: Pass the explicit kwargs with every call ---
        # This is more robust and ensures the model is always correctly prompted.
        result = self.pipe(
            {"raw": audio_array, "sampling_rate": sampling_rate},
            generate_kwargs=self.generate_kwargs
        )
        return result["text"]