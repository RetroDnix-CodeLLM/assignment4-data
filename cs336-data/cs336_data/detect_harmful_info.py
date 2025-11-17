import fasttext

NSFW_MODEL_PATH = "./models/jigsaw_fasttext_bigrams_nsfw_final.bin"
TOXIC_MODEL_PATH = "./models/jigsaw_fasttext_bigrams_hatespeech_final.bin"

# Load model once
nsfw_model = fasttext.load_model(NSFW_MODEL_PATH)
toxic_model = fasttext.load_model(TOXIC_MODEL_PATH)

def detect_nsfw(text: str):
    """
    Use the jigsaw FastText NSFW classifier to predict whether text is NSFW.
    Returns:
        (label: str, confidence: float)
    """
    labels, probs = nsfw_model.predict(text)
    label = labels[0].replace("__label__", "")
    confidence = float(probs[0])
    return label, confidence

def detect_toxic_speech(text: str):
    """
    Use the jigsaw FastText Toxic Speech classifier to predict whether text is toxic.
    Returns:
        (label: str, confidence: float)
    """
    labels, probs = toxic_model.predict(text)
    label = labels[0].replace("__label__", "")
    confidence = float(probs[0])
    return label, confidence