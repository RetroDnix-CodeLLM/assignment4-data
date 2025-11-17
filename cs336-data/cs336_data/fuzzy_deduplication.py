import os
import re
import random
import unicodedata
import string
import pandas as pd
from pathlib import Path
from collections import defaultdict
from typing import List, Set
from datasketch import MinHash, MinHashLSH

def normalize_text(text: str) -> str:
    """
    Normalize text as per Penedo et al. (2023):
      - NFD Unicode normalization
      - remove accents
      - lowercase
      - remove punctuation
      - collapse whitespace
    """
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")  # remove accents
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def word_ngrams(text: str, n: int) -> Set[str]:
    """Return a set of word n-grams from normalized text."""
    words = text.split()
    if len(words) < n:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i:i+n]) for i in range(len(words) - n + 1)}


def jaccard_similarity(a: Set[str], b: Set[str]) -> float:
    """Compute Jaccard similarity between two sets."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


class DSU:
    """Disjoint-set union for clustering duplicates."""
    def __init__(self, n: int):
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def fuzzy_deduplicate_min_hash_lsh(
    paths: List[str],
    num_hashes: int,
    num_bands: int,
    ngram: int,
    output_dir: str,
    threshold: float = 0.8,
    random_seed: int = 42,
) -> List[str]:
    """
    Perform fuzzy document deduplication using MinHash + LSH (datasketch).

    Args:
      paths: list of input file paths
      num_hashes: number of minhash permutations
      num_bands: number of LSH bands
      ngram: n-gram length (in words)
      output_dir: output directory for deduplicated documents
      threshold: Jaccard similarity threshold for duplicate detection
      random_seed: random seed for reproducibility
    Returns:
      List of written output file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    random.seed(random_seed)

    # Read, normalize, and shingle documents
    print("Reading and normalizing documents...")
    docs_text, docs_shingles = [], []
    for path in paths:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
        norm = normalize_text(raw)
        shingles = word_ngrams(norm, ngram)
        docs_text.append(raw)
        docs_shingles.append(shingles)

    # Initialize LSH
    print("Building LSH index...")
    lsh = MinHashLSH(
        threshold=threshold,  # approximate filtering threshold
        num_perm=num_hashes,
        params=(num_bands, num_hashes // num_bands),
    )

    # Create MinHashes and insert into LSH
    minhashes = []
    for i, shingles in enumerate(docs_shingles):
        m = MinHash(num_perm=num_hashes)
        for s in shingles:
            m.update(s.encode("utf-8"))
        lsh.insert(f"doc_{i}", m)
        minhashes.append(m)

    # Find candidate pairs
    print("Collecting candidate pairs...")
    candidates = set()
    for i in range(len(paths)):
        results = lsh.query(minhashes[i])
        for r in results:
            j = int(r.split("_")[1])
            if i < j:
                candidates.add((i, j))

    print(f"Found {len(candidates)} candidate pairs.")

    # Verify with true Jaccard similarity
    dsu = DSU(len(paths))
    for i, j in candidates:
        sim = jaccard_similarity(docs_shingles[i], docs_shingles[j])
        if sim >= threshold:
            dsu.union(i, j)

    # Cluster and decide which documents to keep
    clusters = defaultdict(list)
    for i in range(len(paths)):
        root = dsu.find(i)
        clusters[root].append(i)

    keep_flags = [False] * len(paths)
    for root, members in clusters.items():
        chosen = random.choice(members)
        keep_flags[chosen] = True

    # Write kept documents
    print("Writing deduplicated files...")
    written_paths = []
    for i, path in enumerate(paths):
        if keep_flags[i]:
            dest = os.path.join(output_dir, os.path.basename(path))
            with open(dest, "w", encoding="utf-8") as f:
                f.write(docs_text[i])
            written_paths.append(dest)

    print(f"Wrote {len(written_paths)} unique documents to {output_dir}")
    return written_paths

def fuzzy_deduplicate_min_hash_lsh_parquet(
    parquet_path: str,
    num_hashes: int,
    num_bands: int,
    ngram: int,
    output_dir: str,
    threshold: float = 0.8,
    random_seed: int = 42,
) -> List[str]:
    """
    Perform fuzzy document deduplication using MinHash + LSH (datasketch).

    Args:
      paths: list of input file paths
      num_hashes: number of minhash permutations
      num_bands: number of LSH bands
      ngram: n-gram length (in words)
      output_dir: output directory for deduplicated documents
      threshold: Jaccard similarity threshold for duplicate detection
      random_seed: random seed for reproducibility
    Returns:
      List of written output file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    random.seed(random_seed)

    # Read, normalize, and shingle documents
    print("Reading and normalizing documents...")
    docs_text, docs_shingles = [], []
    df = pd.read_parquet(parquet_path)
    for text in df["text"]:
        norm = normalize_text(text)
        shingles = word_ngrams(norm, ngram)
        docs_text.append(text)
        docs_shingles.append(shingles)

    # Initialize LSH
    print("Building LSH index...")
    lsh = MinHashLSH(
        threshold=threshold,  # approximate filtering threshold
        num_perm=num_hashes,
        params=(num_bands, num_hashes // num_bands),
    )

    # Create MinHashes and insert into LSH
    minhashes = []
    for i, shingles in enumerate(docs_shingles):
        m = MinHash(num_perm=num_hashes)
        for s in shingles:
            m.update(s.encode("utf-8"))
        lsh.insert(f"doc_{i}", m)
        minhashes.append(m)

    # Find candidate pairs
    print("Collecting candidate pairs...")
    candidates = set()
    for i in range(len(df["text"])):
        results = lsh.query(minhashes[i])
        for r in results:
            j = int(r.split("_")[1])
            if i < j:
                candidates.add((i, j))

    print(f"Found {len(candidates)} candidate pairs.")

    # Verify with true Jaccard similarity
    dsu = DSU(len(df["text"]))
    for i, j in candidates:
        sim = jaccard_similarity(docs_shingles[i], docs_shingles[j])
        if sim >= threshold:
            dsu.union(i, j)

    # Cluster and decide which documents to keep
    clusters = defaultdict(list)
    for i in range(len(df["text"])):
        root = dsu.find(i)
        clusters[root].append(i)

    keep_flags = [False] * len(df["text"])
    for root, members in clusters.items():
        chosen = random.choice(members)
        keep_flags[chosen] = True

    # Write kept documents
    print("Writing deduplicated files...")
    deduped_data = []
    for index, row in df.iterrows():
        if keep_flags[index]:
           deduped_data.append(row) 
        
    output_df = pd.DataFrame(deduped_data)
    output_df.to_parquet(Path(output_dir) / "deduplicated_data.parquet")


# Example usage:
if __name__ == "__main__":
    kept = fuzzy_deduplicate_min_hash_lsh(
        paths=["a/1.txt", "a/2.txt", "a/3.txt"],
        num_hashes=128,
        num_bands=32,
        ngram=3,
        output_dir="b/",
        threshold=0.8,
    )
    print("Kept:", kept)
