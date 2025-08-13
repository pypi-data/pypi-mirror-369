# whisper_evaluator/task.py
from datasets import load_dataset
from .utils import to_latin_serbian 

class ASRTask:
    """
    Handles loading and preparing a dataset for Automatic Speech Recognition evaluation.
    """
    def __init__(self, dataset_name: str, dataset_subset: str, dataset_split: str, audio_column: str, text_column: str):
        """
        Initializes and loads the dataset from the Hugging Face Hub.
        """
        print(f"--- [DEBUG] ASRTask received dataset_split: '{dataset_split}' ---")

        self.dataset = load_dataset(dataset_name, dataset_subset, split=dataset_split, trust_remote_code=True)

        # Standardize column names
        self.dataset = self.dataset.rename_columns({
            audio_column: "audio",
            text_column: "reference_text"
        })
        
        # 👇 2. Apply the transliteration function to the entire dataset
        # The .map() method is highly efficient for this kind of operation.
        def transliterate_example(example):
            example["reference_text"] = to_latin_serbian(example["reference_text"])
            return example

        self.dataset = self.dataset.map(transliterate_example)

    def __iter__(self):
        """Allows iterating directly over the processed dataset."""
        return iter(self.dataset)
    
    def __len__(self): 
        """Returns the number of examples in the dataset."""
        return len(self.dataset)