# whisper_evaluator/evaluator.py
from logging import config
import evaluate
import re
from tqdm.notebook import tqdm
from datetime import datetime
from typing import List, Dict, Tuple

from .model_wrapper import WhisperModel
from .task import ASRTask
from .utils import to_latin_serbian  # <-- 1. Import the transliteration function

def normalize_text_serbian(text: str) -> str:
    """
    Applies orthographic normalization for Serbian text.
    - Lowercases
    - Removes punctuation (keeps Serbian letters)
    - Standardizes whitespace
    """
    text = text.lower()
    # This regex keeps letters (including Serbian alphabet) and numbers
    text = re.sub(r"[^\w\sабвгдђежзијклљмнњопрстћуфхцчџш]", "", text)
    # Remove all characters that are not letters, numbers, or whitespace
    text = re.sub(r"[^\w\s]", "", text)
    # Collapse multiple whitespace characters into a single space
    text = re.sub(r"\s+", " ", text).strip()

    return text


class Evaluator:
    """
    A class to run a comprehensive ASR evaluation for a Whisper model.
    """
    def __init__(self, config: dict):
        """Initializes the evaluator with model and task settings."""
        # Cleaned up the debug print for model arguments
        print("--- Model Arguments ---")
        for k, v in config.get("model_args", {}).items():
            print(f"  {k}: {v}")
        print("-------------------------------")

        self.model = WhisperModel(**config["model_args"])
        self.task = ASRTask(**config["task_args"])
        
        self.wer_metric = evaluate.load("wer")
        self.cer_metric = evaluate.load("cer")
        self.bleu_metric = evaluate.load("bleu")
        self.rouge_metric = evaluate.load("rouge")

    def run(self, log_to_file: bool = True) -> Tuple[List[Dict[str, str]], Dict[str, float]]:
        """
        Runs the full evaluation loop.

        Args:
            log_to_file (bool): If True, saves all predictions to 'evaluation_log.txt'.

        Returns:
            Tuple[List[Dict[str, str]], Dict[str, float]]:
                - A list of dictionaries with detailed 'reference' and 'prediction' keys.
                - A dictionary containing all calculated metrics.
        """
        detailed_results = []
        predictions = []
        references = []

        print(f"Running evaluation on {len(self.task)} samples...")
        for item in tqdm(self.task, desc="Transcribing"):
            raw_prediction = self.model.transcribe(item["audio"]["array"], item["audio"]["sampling_rate"])
            reference = item["reference_text"] # This is already in Latin script from ASRTask

            # <-- 2. Transliterate the model's prediction to Serbian Latin
            prediction = to_latin_serbian(raw_prediction)

            predictions.append(prediction)
            references.append(reference)
            detailed_results.append({"reference": reference, "prediction": prediction})

        print("Calculating metrics...")
        # Normalize text for orthographic metrics
        norm_predictions = [normalize_text_serbian(p) for p in predictions]
        norm_references = [normalize_text_serbian(r) for r in references]

        # --- Calculate all metrics ---
        wer = self.wer_metric.compute(predictions=predictions, references=references)
        cer = self.cer_metric.compute(predictions=predictions, references=references)
        rouge = self.rouge_metric.compute(predictions=predictions, references=references)
        bleu = self.bleu_metric.compute(predictions=predictions, references=[[r] for r in references])
        
        wer_ortho = self.wer_metric.compute(predictions=norm_predictions, references=norm_references)
        cer_ortho = self.cer_metric.compute(predictions=norm_predictions, references=norm_references)

        metrics = {
            "wer": wer * 100,
            "cer": cer * 100,
            "wer_ortho": wer_ortho * 100,
            "cer_ortho": cer_ortho * 100,
            "bleu": bleu["bleu"] * 100,
            "rougeL": rouge["rougeL"] * 100,
        }

        # --- Log results to a file ---
        if log_to_file:
            with open("evaluation_log.txt", "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n{'='*50}\nEVALUATION @ {timestamp}\n{'='*50}\n")
                f.write(f"MODEL: {self.model.pipe.model.name_or_path}\n")
                f.write(f"METRICS: {metrics}\n\n")
                for result in detailed_results:
                    f.write(f"REF:  {result['reference']}\n")
                    f.write(f"PRED: {result['prediction']}\n\n")
            print("Evaluation details saved to evaluation_log.txt")

        # --- Print a summary to the console ---
        print("\n--- ✅ Evaluation Complete ---")
        print(f"  Word Error Rate (WER): {metrics['wer']:.2f}%")
        print(f"  Character Error Rate (CER): {metrics['cer']:.2f}%")
        print(f"  WER Orthographic: {metrics['wer_ortho']:.2f}%")
        print(f"  CER Orthographic: {metrics['cer_ortho']:.2f}%")
        print(f"  BLEU: {metrics['bleu']:.2f}%")
        print(f"  ROUGE-L: {metrics['rougeL']:.2f}%")
        print("-----------------------------")

        return detailed_results, metrics