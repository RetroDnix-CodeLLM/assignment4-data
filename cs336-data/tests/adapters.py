#!/usr/bin/env python3
from __future__ import annotations

import os
from typing import Any

from cs336_data.extract_from_html import extract_text_from_html_bytes
from cs336_data.identify_language import identify_language
from cs336_data.remove_personal_info import mask_emails, mask_phone_numbers, mask_ip_addresses
from cs336_data.detect_harmful_info import detect_nsfw, detect_toxic_speech
from cs336_data.detect_low_quality_crawl import gopher_quality_filter, fasttext_quality_classify
from cs336_data.exact_line_deduplication import deduplicate_files
from cs336_data.fuzzy_deduplication import fuzzy_deduplicate_min_hash_lsh

def run_extract_text_from_html_bytes(html_bytes: bytes) -> str | None:
    return extract_text_from_html_bytes(html_bytes)


def run_identify_language(text: str) -> tuple[Any, float]:
    return identify_language(text)


def run_mask_emails(text: str) -> tuple[str, int]:
    return mask_emails(text)


def run_mask_phone_numbers(text: str) -> tuple[str, int]:
    return mask_phone_numbers(text)


def run_mask_ips(text: str) -> tuple[str, int]:
    return mask_ip_addresses(text)


def run_classify_nsfw(text: str) -> tuple[Any, float]:
    return detect_nsfw(text)

def run_classify_toxic_speech(text: str) -> tuple[Any, float]:
    return detect_toxic_speech(text)


def run_classify_quality(text: str) -> tuple[Any, float]:
    return fasttext_quality_classify(text)


def run_gopher_quality_filter(text: str) -> bool:
    return gopher_quality_filter(text)[0]


def run_exact_line_deduplication(
    input_files: list[os.PathLike], output_directory: os.PathLike
):
    return deduplicate_files(input_files, output_directory)


def run_minhash_deduplication(
    input_files: list[os.PathLike],
    num_hashes: int,
    num_bands: int,
    ngrams: int,
    jaccard_threshold: float,
    output_directory: os.PathLike,
):
    return fuzzy_deduplicate_min_hash_lsh(
        paths=input_files,
        num_hashes=num_hashes,
        num_bands=num_bands,
        ngram=ngrams,
        output_dir=output_directory,
        threshold=jaccard_threshold,
    )
