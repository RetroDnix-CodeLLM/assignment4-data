#!/usr/bin/env bash
# 批量下载脚本：使用 baseurl + suffix 拼接完整 URL，并用 wget 下载

# ===== 配置区域 =====
# 基础 URL
baseurl="https://data.commoncrawl.org/"

# URL 后缀列表，可以手动写在这里，也可以从文件读取
suffixes=(
    "crawl-data/CC-MAIN-2025-43/segments/1759648357851.76/warc/CC-MAIN-20251005114239-20251005144239-00000.warc.gz"
    "crawl-data/CC-MAIN-2025-43/segments/1759648357851.76/warc/CC-MAIN-20251005114239-20251005144239-00001.warc.gz"
    "crawl-data/CC-MAIN-2025-43/segments/1759648357851.76/warc/CC-MAIN-20251005114239-20251005144239-00002.warc.gz"
    "crawl-data/CC-MAIN-2025-43/segments/1759648357851.76/warc/CC-MAIN-20251005114239-20251005144239-00003.warc.gz"
    "crawl-data/CC-MAIN-2025-43/segments/1759648357851.76/warc/CC-MAIN-20251005114239-20251005144239-00004.warc.gz"
    "crawl-data/CC-MAIN-2025-43/segments/1759648357851.76/warc/CC-MAIN-20251005114239-20251005144239-00005.warc.gz"
    "crawl-data/CC-MAIN-2025-43/segments/1759648357851.76/warc/CC-MAIN-20251005114239-20251005144239-00006.warc.gz"
    "crawl-data/CC-MAIN-2025-43/segments/1759648357851.76/warc/CC-MAIN-20251005114239-20251005144239-00007.warc.gz"
    "crawl-data/CC-MAIN-2025-43/segments/1759648357851.76/warc/CC-MAIN-20251005114239-20251005144239-00008.warc.gz"
    "crawl-data/CC-MAIN-2025-43/segments/1759648357851.76/warc/CC-MAIN-20251005114239-20251005144239-00009.warc.gz"
)

# 下载保存路径（可选）
output_dir="./data"

# ===== 执行逻辑 =====
mkdir -p "$output_dir"

for suffix in "${suffixes[@]}"; do
  full_url="${baseurl%/}/${suffix}"   # 拼接完整URL（去除多余斜杠）
  echo "Downloading: $full_url"
  wget -c -P "$output_dir" "$full_url" || echo "❌ Failed: $full_url"
done

echo "✅ All downloads finished!"
