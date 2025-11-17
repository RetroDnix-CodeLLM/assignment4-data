import hashlib
from collections import Counter
from pathlib import Path
import pandas as pd

def deduplicate_files(input_file_paths, output_file_path):
    """
    Perform exact line deduplication across multiple files.
    
    Args:
        input_file_paths (list[str]): List of paths to input files.

    This function:
    1. Computes a hash for each line across all files and counts frequency.
    2. Rewrites each file keeping only lines that are unique globally.
    """

    def line_hash(line: str) -> str:
        """Return a short, stable hash for the line to save memory."""
        return hashlib.sha1(line.encode("utf-8", errors="ignore")).hexdigest()

    # --- Step 1: Count line hashes across all files ---
    freq = Counter()
    for path in input_file_paths:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                h = line_hash(line.rstrip("\n"))
                freq[h] += 1

    # --- Step 2: Rewrite each file with unique lines only ---
    for path in input_file_paths:
        with open(path, "r", encoding="utf-8", errors="ignore") as fin, \
            open(output_file_path / path.name, "w", encoding="utf-8") as fout:
            for line in fin:
                h = line_hash(line.rstrip("\n"))
                if freq[h] == 1:
                    fout.write(line)

def deduplicate_parquets(input_parquet_paths, output_parquet_path):
    deduped_line_cnt = 0
    all_line_cnt = 0

    def line_hash(line: str) -> str:
        """Return a short, stable hash for the line to save memory."""
        return hashlib.sha1(line.encode("utf-8", errors="ignore")).hexdigest()

    # --- Step 1: Count line hashes across all files ---
    freq = Counter()
    paths = []
    for path in input_parquet_paths:
        paths.append(path)
        print(f"Reading {path} for line frequency counting...")
        df = pd.read_parquet(path)
        for text in df['text']:
            for line in text.splitlines():
                h = line_hash(line.rstrip("\n"))
                freq[h] += 1
                all_line_cnt += 1

    # --- Step 2: Rewrite each file with unique lines only ---
    output_data = []
    for path in paths:
        df = pd.read_parquet(path)
        for row in df.itertuples():
            text = row.text
            lang = row.language
            url = row.url
            new_texts = []
            for line in text.splitlines():
                h = line_hash(line.rstrip("\n"))
                if freq[h] == 1:
                    new_texts.append(line)
                else:
                    deduped_line_cnt += 1
            new_text = "\n".join(new_texts)
            output_data.append((url, lang, new_text))
    output_df = pd.DataFrame(output_data, columns=['url', 'language', 'text'])
    output_path = Path(output_parquet_path) / "deduplicated_data.parquet"
    output_df.to_parquet(output_path, index=False)
    print(f"Deduped Size: {len(output_data)} rows")
    return output_path, deduped_line_cnt, all_line_cnt
            