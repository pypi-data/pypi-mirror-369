# whisper_evaluator/evaluator.py
from logging import config
import evaluate
import re
from tqdm.notebook import tqdm
from datetime import datetime
from typing import List, Dict, Tuple
from .model_wrapper import WhisperModel
from .task import ASRTask

def normalize_text_serbian(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\sабвгдђежзијклљмнњопрстћуфхцчџш]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

class Evaluator:
    def __init__(self, config: dict):
        self.model = WhisperModel(**config["model_args"])
        self.task = ASRTask(**config["task_args"])
        self.wer_metric = evaluate.load("wer")
        self.cer_metric = evaluate.load("cer")
        self.rouge_metric = evaluate.load("rouge")
        self.bleu_metric = evaluate.load("bleu")

    def run(self, log_to_file: bool = True) -> Tuple[List[Dict[str, str]], Dict[str, float]]:
        """
        Runs the full evaluation loop using efficient batching.
        """
        print(f"Running evaluation on {len(self.task)} samples...")

        # Create a generator to feed the raw audio data to the pipeline.
        # The pipeline will handle the batching internally.
        def audio_iterator():
            for item in self.task.dataset:
                # Yield the audio data in the format the pipeline expects
                yield item["audio"]

        # Call the pipeline with the iterator. It returns an iterator of results.
        results_iterator = self.model.pipe(
            audio_iterator(), 
            batch_size=16, 
            generate_kwargs=self.model.generate_kwargs
        )
        
        # Extract the text from the results, using tqdm for a progress bar.
        print("Transcribing dataset with batch size 16...")
        predictions = [out["text"] for out in tqdm(results_iterator, total=len(self.task.dataset))]
        
        # The references can be extracted directly from the dataset column.
        references = self.task.dataset["reference_text"]

        print("Combining results and calculating metrics...")
        detailed_results = [{"reference": ref, "prediction": pred} for ref, pred in zip(references, predictions)]

        # Normalize text for orthographic metrics
        norm_predictions = [normalize_text_serbian(p) for p in predictions]
        norm_references = [normalize_text_serbian(r) for r in references]
        
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
            
        print("\n--- ✅ Evaluation Complete ---")
        print(f"  Word Error Rate (WER): {metrics['wer']:.2f}%")
        print(f"  Character Error Rate (CER): {metrics['cer']:.2f}%")
        print(f"  WER Orthographic: {metrics['wer_ortho']:.2f}%")
        print(f"  CER Orthographic: {metrics['cer_ortho']:.2f}%")
        print(f"  BLEU: {metrics['bleu']:.2f}%")
        print(f"  ROUGE-L: {metrics['rougeL']:.2f}%")
        print("-----------------------------")
        
        return detailed_results, metrics
