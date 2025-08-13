import pytest
from unittest import mock

# Import the class we want to test
from whisper_eval_serbian.evaluator import Evaluator

@mock.patch("whisper_evaluator.evaluator.evaluate.load") # Mock metric loading
@mock.patch("whisper_evaluator.evaluator.ASRTask")      # Mock the ASRTask class
@mock.patch("whisper_evaluator.evaluator.WhisperModel") # Mock the WhisperModel class
def test_evaluator_uses_config_to_initialize_components(
    mock_whisper_model, mock_asr_task, mock_evaluate_load
):
    """
    ✅ GIVEN: A configuration dictionary.
    ✅ WHEN:  The Evaluator is initialized with that config.
    ✅ THEN:  It should initialize WhisperModel and ASRTask with the correct parts of the config.
    """
    # 1. Define the exact config dictionary we want to test
    sample_config = {
        "model_args": {
            "name_or_path": "datatab/aida_parla_whisper_large_v3_1_1_4",
            "device": "cuda"
        },
        "task_args": {
            "dataset_name": "mozilla-foundation/common_voice_17_0",
            "dataset_subset": "sr",
            "dataset_split": "test[:5]",
            "audio_column": "audio",
            "text_column": "sentence"
        }
    }

    # 2. Initialize the Evaluator with our sample config
    evaluator = Evaluator(config=sample_config)
  

    # 3. Assert that the underlying classes were called with the correct arguments
    
    # Check that WhisperModel was called once with the contents of "model_args"
    mock_whisper_model.assert_called_once_with(
        name_or_path="datatab/aida_parla_whisper_large_v3_1_1_4",
        device="cuda"
    )
    # An alternative way to check this:
    mock_whisper_model.assert_called_once_with(**sample_config["model_args"])

    # Check that ASRTask was called once with the contents of "task_args"
    mock_asr_task.assert_called_once_with(
        dataset_name="mozilla-foundation/common_voice_17_0",
        dataset_subset="sr",
        dataset_split="test[:5]",
        audio_column="audio",
        text_column="sentence"
    )
    # An alternative way to check this:
    mock_asr_task.assert_called_once_with(**sample_config["task_args"])
    
    # Optional: Verify that the metric loaders were called
    assert mock_evaluate_load.call_count == 4