import pandas as pd
import numpy as np
from tqdm import tqdm
from transformers import GPT2TokenizerFast

data_path = "/data/home/hyzheng/Projects/CS336/assignment4-data/cs336-data/flitered_data/CC-MAIN-20251005114239-20251005144239-00000.warc.parquet"
tokenized_data_path = "/data/home/hyzheng/Projects/CS336/assignment4-data/cs336-basics/tokenized_data/tokenized_data.bin"
tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

df = pd.read_parquet(data_path)
ids_array = []
for text in tqdm(df["text"]):
    ids = tokenizer.encode(text + tokenizer.eos_token)
    ids_array.extend(ids)

ids_array = np.array(ids_array, dtype=np.uint16)
ids_array.tofile(tokenized_data_path)