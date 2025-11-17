import fasttext
import requests
import random
from tqdm import tqdm
from warcio.archiveiterator import ArchiveIterator
from pickle import dump, load

from extract_from_html import extract_text_from_html_bytes
from identify_language import identify_language
from remove_personal_info import mask_emails, mask_phone_numbers, mask_ip_addresses
from detect_harmful_info import detect_nsfw, detect_toxic_speech
from detect_low_quality_crawl import gopher_quality_filter

positive_exp_path = "/data/home/hyzheng/Projects/CS336/assignment4-data/cs336-data/data/url_contents.warc.gz"
positive_data = []
negetive_exp_paths = [
    "/data/home/hyzheng/Projects/CS336/assignment4-data/cs336-data/data/CC-MAIN-20251005114239-20251005144239-00000.warc.gz",
    "/data/home/hyzheng/Projects/CS336/assignment4-data/cs336-data/data/CC-MAIN-20251005114239-20251005144239-00001.warc.gz",
    "/data/home/hyzheng/Projects/CS336/assignment4-data/cs336-data/data/CC-MAIN-20251005114239-20251005144239-00002.warc.gz",
    "/data/home/hyzheng/Projects/CS336/assignment4-data/cs336-data/data/CC-MAIN-20251005114239-20251005144239-00003.warc.gz",
]
negetive_data = []

train_data_path = "./data/low_quality_train.txt"
valid_data_path = "./data/low_quality_valid.txt"
model_path = "./models/low_quality_classifier.bin"

random.seed(42)

# print("Reading Positive Data")
# with open(positive_exp_path, 'rb') as stream:
#     print("Processing WARC file:", positive_exp_path)
#     for record in tqdm(ArchiveIterator(stream)):
#         if record.rec_type == 'response':
#             url = record.rec_headers.get_header('WARC-Target-URI')
#             payload = record.content_stream().read()

#             data = extract_text_from_html_bytes(payload)
#             data = data.replace("\n", " ").replace("\r", " ").strip()
#             quality, _ = gopher_quality_filter(data)
#             lang, _ = identify_language(data)
#             nsfw, _ = detect_nsfw(data)
#             toxic, _ = detect_toxic_speech(data)
#             if lang != "en" or nsfw == "nsfw" or toxic == "toxic" or quality == False:
#                 continue
#             masked_data, _ = mask_emails(data)
#             masked_data, _ = mask_phone_numbers(masked_data)
#             masked_data, _ = mask_ip_addresses(masked_data)
#             positive_data.append(masked_data)
# print(f"Write {len(positive_data)} positive samples.")
# dump(positive_data, open("./data/low_quality_positive_data.pkl", "wb"))

positive_data = load(open("./data/low_quality_positive_data.pkl", "rb"))

# print("Reading Negetive Data")
# for negetive_exp_path in negetive_exp_paths:
#     with open(negetive_exp_path, 'rb') as stream:
#         print(f"Processing {negetive_exp_path}...")
#         for record in tqdm(ArchiveIterator(stream)):
#             if record.rec_type == 'response':
#                 url = record.rec_headers.get_header('WARC-Target-URI')
#                 payload = record.content_stream().read()

#                 data = extract_text_from_html_bytes(payload)
#                 data = data.replace("\n", " ").replace("\r", " ").strip()
#                 quality, _ = gopher_quality_filter(data)
#                 lang, _ = identify_language(data)
#                 nsfw, _ = detect_nsfw(data)
#                 toxic, _ = detect_toxic_speech(data)
#                 if lang != "en" or nsfw == "nsfw" or toxic == "toxic" or quality == False:
#                     negetive_data.append(data)

# random.sample(negetive_data, len(positive_data))
# dump(negetive_data, open("./data/low_quality_negetive_data.pkl", "wb"))
negetive_data = load(open("./data/low_quality_negetive_data.pkl", "rb"))

positive_data = [f"__label__positive {d}\n" for d in positive_data]
negetive_data = [f"__label__negetive {d}\n" for d in negetive_data]

all_data = positive_data + negetive_data
del positive_data
del negetive_data
random.shuffle(all_data)

split = int(0.8 * len(all_data))
print(f"Write {split} samples to train.txt.")
with open(train_data_path, "w", encoding="utf-8") as f:
    f.writelines(all_data[:split])

print(f"Write {len(all_data) - split} samples to valid.txt.")
with open(valid_data_path, "w", encoding="utf-8") as f:
    f.writelines(all_data[split:])

# 训练模型
model = fasttext.train_supervised(
    input=train_data_path,      # 训练文件路径
    lr=0.5,                 # 学习率
    epoch=25,               # 训练轮数
    wordNgrams=2,           # 使用多少个词 n-gram
    dim=100,                # 向量维度
    loss="softmax"          # 或者 "hs"、"ova"
)

# 保存模型
print("Validation accuracy:", model.test(valid_data_path))
model.save_model(model_path)

# model = fasttext.load_model(model_path)
model.quantize(input=train_data_path, qnorm=True, retrain=True, cutoff=200000)
model.save_model("low_quality_classifier_q.bin")

# 测试集准确率
print("Validation accuracy:", model.test(valid_data_path))
# 预测
print(model.predict("I hate this movie."))
