from pathlib import Path
import tempfile
import pandas as pd

from exact_line_deduplication import deduplicate_parquets
from fuzzy_deduplication import fuzzy_deduplicate_min_hash_lsh_parquet

flitered_data_path = Path("/data/home/hyzheng/Projects/CS336/assignment4-data/cs336-data/flitered_data")
flitered_datas = flitered_data_path.glob("*.parquet")

dudeped_data_path = Path("/data/home/hyzheng/Projects/CS336/assignment4-data/cs336-data/deduped_data")

# with tempfile.TemporaryDirectory() as tmpdir:
#     output_path, dedup_line_cnt, all_line_cnt = deduplicate_parquets(flitered_datas, tmpdir)
#     print(f"Dedup rate: {dedup_line_cnt}/{all_line_cnt} = {dedup_line_cnt/all_line_cnt:.2%}")
    
#     fuzzy_deduplicate_min_hash_lsh_parquet(
#         parquet_path=output_path,
#         num_hashes=128,
#         num_bands=32,
#         ngram=3,
#         output_dir=dudeped_data_path,
#     )

data = pd.read_parquet("/data/home/hyzheng/Projects/CS336/assignment4-data/cs336-data/deduped_data/deduplicated_data.parquet")
print(f"Final deduped data size: {len(data)} rows")