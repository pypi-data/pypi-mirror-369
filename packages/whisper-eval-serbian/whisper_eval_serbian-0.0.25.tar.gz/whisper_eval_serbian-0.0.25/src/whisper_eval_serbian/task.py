# whisper_evaluator/task.py
from datasets import load_dataset, Audio
import soundfile as sf
from .utils import to_latin_serbian

class ASRTask:
    """
    Handles loading and preparing a dataset for Automatic Speech Recognition evaluation.
    """
    def __init__(
        self,
        dataset_name: str,
        dataset_subset: str,
        dataset_split: str,
        audio_column: str,
        text_column: str,
        hf_token: str | None = None
    ):
        print(f"--- [DEBUG] ASRTask received dataset_split: '{dataset_split}' ---")

        # Load dataset
        self.dataset = load_dataset(
            dataset_name,
            dataset_subset,
            split=dataset_split,
            trust_remote_code=True,
            token=hf_token
        )

        # Resample audio column to 16 kHz
        self.dataset = self.dataset.cast_column(audio_column, Audio(sampling_rate=16000))

        # Standardize column names
        self.dataset = self.dataset.rename_columns({
            audio_column: "audio",
            text_column: "reference_text"
        })

        # Apply transliteration
        def transliterate_example(example):
            example["reference_text"] = to_latin_serbian(example["reference_text"])
            return example

        self.dataset = self.dataset.map(transliterate_example)



    def __iter__(self):
        return iter(self.dataset)
    
    def __len__(self):
        return len(self.dataset)
