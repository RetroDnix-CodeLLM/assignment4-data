import requests

from resiliparse.extract.html2text import extract_plain_text
from resiliparse.parse.encoding import detect_encoding

def extract_text_from_html_bytes(html_bytes: bytes) -> str:
    """
    Extracts plain text from a raw HTML byte string using Resiliparse.

    Steps:
      1. Try decoding the bytes as UTF-8 first.
      2. If UTF-8 decoding fails, detect the encoding using resiliparse.parse.encoding.detect_encoding().
      3. Decode again using the detected encoding.
      4. Use resiliparse.extract.html2text.extract_plain_text() to get clean text.

    Args:
        html_bytes (bytes): Raw HTML byte string.

    Returns:
        str: Extracted plain text.
    """
    if not html_bytes:
        return ""

    # Step 1: Try UTF-8 decoding
    try:
        html_str = html_bytes.decode('utf-8')
    except UnicodeDecodeError:
        # Step 2: Detect encoding if UTF-8 fails
        enc = detect_encoding(html_bytes)
        # Fallback if detection fails or returns None
        # encoding = enc.encoding if enc and enc.encoding else 'latin-1'
        html_str = html_bytes.decode(enc, errors='replace')

    # Step 3: Extract plain text
    text = extract_plain_text(html_str)

    return text.strip()

if __name__ == "__main__":
    url = "https://hit-scir-la.github.io/"
    response = requests.get(url)
    html_bytes = response.content
    extracted_text = extract_text_from_html_bytes(html_bytes)
    print("Extracted Text:")
    print(extracted_text)

