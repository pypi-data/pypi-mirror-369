# whisper_evaluator/model_wrapper.py
import torch
from transformers import pipeline

class WhisperModel:
    """
    A wrapper for the Hugging Face ASR pipeline for Whisper models.
    This version is optimized for batch processing.
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

        self.generate_kwargs = {
            "task": "transcribe",
            "language": "<|sr|>",
        }

    def transcribe_dataset(self, dataset, batch_size: int = 16):
        """
        Generates transcriptions for an entire dataset using efficient batching.

        Args:
            dataset: An iterable (like a Hugging Face Dataset) that yields dictionaries
                     containing "audio" data.
            batch_size (int): The number of audio samples to process in one batch.
                              Adjust based on your GPU memory.

        Returns:
            A list of transcribed text strings.
        """
        print(f"Transcribing dataset with batch size {batch_size}...")
        # The pipeline can directly iterate over a dataset.
        # It expects the dataset to yield the same dict format: {"raw":..., "sampling_rate":...}
        # We extract the 'audio' column to feed it in the correct format.
        predictions = []
        # The 'for out in pipe(...)' loop is the core of batched inference.
        for out in self.pipe(dataset, batch_size=batch_size, generate_kwargs=self.generate_kwargs):
            predictions.append(out["text"])
        
        return predictions
