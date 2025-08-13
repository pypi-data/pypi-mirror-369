# whisper_evaluator/task.py
from datasets import load_dataset
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
        """
        Initializes and loads the dataset from the Hugging Face Hub.
        """
        print(f"--- [DEBUG] ASRTask received dataset_split: '{dataset_split}' ---")

        # Load dataset from HF
        self.dataset = load_dataset(
            dataset_name,
            dataset_subset,
            split=dataset_split,
            trust_remote_code=True,
            token=hf_token
        )

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

        # DEBUG: print and save first 10 samples
        print("\n--- First 10 samples (reference_text + saved audio) ---")
        for i in range(min(10, len(self.dataset))):
            ref_text = self.dataset[i]["reference_text"]
            audio_data = self.dataset[i]["audio"]["array"]
            sr = self.dataset[i]["audio"]["sampling_rate"]

            filename = f"sample_{i+1}.wav"
            sf.write(filename, audio_data, sr)

            print(f"{i+1}: {ref_text}")
            print(f"   Saved: {filename}")
        print("---------------------------------------")

    def __iter__(self):
        """Allows iterating directly over the processed dataset."""
        return iter(self.dataset)
    
    def __len__(self):
        """Returns the number of examples in the dataset."""
        return len(self.dataset)
