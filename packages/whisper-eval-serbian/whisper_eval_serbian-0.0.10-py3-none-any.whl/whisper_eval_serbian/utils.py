# whisper_evaluator/utils.py
import cyrtranslit

def to_latin_serbian(text: str) -> str:
    """
    Transliterates a given text string from Serbian Cyrillic to Latin script.
    
    Args:
        text (str): The input text, potentially in Cyrillic.

    Returns:
        str: The transliterated text in Latin script.
    """
    # The 'sr' language code is the default, so it's not strictly necessary,
    # but it's good practice to be explicit.
    return cyrtranslit.to_latin(text, "sr")