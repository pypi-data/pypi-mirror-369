# check_data.py
from datasets import load_dataset
import soundfile as sf
import os

# --- Parameters from your config ---
DATASET_NAME = "mozilla-foundation/common_voice_11_0"
SUBSET = "sr"
SPLIT = "test"
TEXT_COLUMN = "sentence"
AUDIO_COLUMN = "audio"

print("Loading dataset...")
# Load the dataset, using a streaming True to avoid downloading everything if not needed
dataset = load_dataset(DATASET_NAME, SUBSET, split=SPLIT, trust_remote_code=True)
print("Dataset loaded.")

# --- Pick an example to check (e.g., the 3rd one) ---
index_to_check = 2 
example = dataset[index_to_check]

# --- Extract audio and text ---
reference_text = example[TEXT_COLUMN]
audio_data = example[AUDIO_COLUMN]

# --- Print the reference text ---
print("\n" + "="*60)
print(f"CHECKING THE INTEGRITY OF DATASET EXAMPLE #{index_to_check}")
print(f"\nREFERENCE TEXT: '{reference_text}'")

# --- Save the corresponding audio to a file ---
output_filename = "debug_audio.wav"
sampling_rate = audio_data["sampling_rate"]
sf.write(output_filename, audio_data["array"], sampling_rate)

print(f"\nAUDIO SAVED: The audio for this example has been saved to:")
print(f"'{os.path.abspath(output_filename)}'")
print("\nACTION REQUIRED:")
print("Please listen to 'debug_audio.wav' and see if the person is")
print("saying the reference text printed above.")
print("="*60)