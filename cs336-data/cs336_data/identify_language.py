import fasttext

# Load the FastText language identification model once
# You can download it from: https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
_MODEL_PATH = "./models/lid.176.bin"
_lang_model = fasttext.load_model(_MODEL_PATH)

def identify_language(text: str) -> tuple[str, float]:
    """
    Detect the main language of a Unicode string using fastText's lid.176.bin model.

    Args:
        text (str): Input Unicode text.

    Returns:
        tuple[str, float]: A pair (language_code, confidence_score).
                          language_code is a two-letter ISO code like 'en', 'zh', etc.
                          confidence_score is between 0.0 and 1.0.
    """
    if not text.strip():
        return ("unknown", 0.0)

    labels, scores = _lang_model.predict(text.replace("\n", " "), k=1)
    lang_code = labels[0].replace("__label__", "")
    confidence = float(scores[0])
    return lang_code, confidence

if __name__ == "__main__":
    # Example usage
    sample_text = "我们团队昨天 had a long discussion about model optimization，最后决定先做一个 small-scale prototype 来测试想法。"
    lang, conf = identify_language(sample_text)
    print(sample_text)
    print(f"Detected language: {lang} with confidence {conf:.2f}")