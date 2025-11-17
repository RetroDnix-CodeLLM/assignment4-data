import re
import fasttext

def gopher_quality_filter(text: str, 
                          min_words=50, 
                          max_words=100_000, 
                          min_mean_word_len=3, 
                          max_mean_word_len=10, 
                          max_ellipsis_ratio=0.3, 
                          min_alpha_word_ratio=0.8):
    """
    Apply a subset of Gopher-style quality filters to a text sample.
    
    Returns:
        (bool, dict): (passes_quality_check, diagnostics)
    """
    diagnostics = {}
    
    # Tokenize words (rough heuristic)
    words = re.findall(r"\b\w+\b", text)
    num_words = len(words)
    diagnostics["num_words"] = num_words
    
    # 1. Word count filter
    if num_words < min_words or num_words > max_words:
        diagnostics["fail_reason"] = f"Word count out of range [{min_words}, {max_words}]"
        return False, diagnostics
    
    # 2. Mean word length filter
    mean_word_len = sum(len(w) for w in words) / num_words if num_words > 0 else 0
    diagnostics["mean_word_len"] = mean_word_len
    if mean_word_len < min_mean_word_len or mean_word_len > max_mean_word_len:
        diagnostics["fail_reason"] = f"Mean word length out of range [{min_mean_word_len}, {max_mean_word_len}]"
        return False, diagnostics
    
    # 3. Ellipsis ratio filter
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if lines:
        ellipsis_lines = sum(1 for l in lines if l.endswith("..."))
        ellipsis_ratio = ellipsis_lines / len(lines)
    else:
        ellipsis_ratio = 0.0
    diagnostics["ellipsis_ratio"] = ellipsis_ratio
    if ellipsis_ratio > max_ellipsis_ratio:
        diagnostics["fail_reason"] = f"Too many lines ending with ellipsis ({ellipsis_ratio:.2%})"
        return False, diagnostics
    
    # 4. Alphabetic word ratio filter
    alpha_words = sum(1 for w in words if re.search(r"[A-Za-z]", w))
    alpha_ratio = alpha_words / num_words if num_words > 0 else 0
    diagnostics["alpha_word_ratio"] = alpha_ratio
    if alpha_ratio < min_alpha_word_ratio:
        diagnostics["fail_reason"] = f"Too few alphabetic words ({alpha_ratio:.2%})"
        return False, diagnostics
    
    # Passed all filters
    diagnostics["fail_reason"] = None
    return True, diagnostics

model_path = "/data/home/hyzheng/Projects/CS336/assignment4-data/cs336-data/models/low_quality_classifier_q.bin"
model = fasttext.load_model(model_path)
def fasttext_quality_classify(text: str) -> tuple[str, float]:
    """
    Classify text quality using a FastText model.
    
    Args:
        text (str): The input text to classify.
        model: The loaded FastText model.
        
    Returns:
        (str, float): (predicted_label, confidence_score)
    """
    text = text.replace("\n", " ").replace("\r", " ").strip()
    labels, probabilities = model.predict(text)
    predicted_label = labels[0].replace("__label__", "")
    confidence_score = probabilities[0]
    return predicted_label, confidence_score