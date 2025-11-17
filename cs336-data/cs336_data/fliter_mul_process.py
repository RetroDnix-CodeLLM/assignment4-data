import concurrent.futures 
import os
import json
from tqdm import tqdm
from pprint import pprint
from pathlib import Path
from warcio.archiveiterator import ArchiveIterator
import pandas as pd

from extract_from_html import extract_text_from_html_bytes
from identify_language import identify_language
from remove_personal_info import mask_emails, mask_phone_numbers, mask_ip_addresses
from detect_harmful_info import detect_nsfw, detect_toxic_speech
from detect_low_quality_crawl import gopher_quality_filter, fasttext_quality_classify

def process_single_warc_file(input_path: str, output_path: str):  
    # TODO: read input path, process the input, and write the output to output_path 
    outputs = []
    cnt = 0
    with open(input_path, 'rb') as stream:
        for record in ArchiveIterator(stream):
            cnt = cnt + 1
            if record.rec_type == 'response':
                url = record.rec_headers.get_header('WARC-Target-URI')
                payload = record.content_stream().read()

                data = extract_text_from_html_bytes(payload)
                flat_data = data.replace("\n", " ").replace("\r", " ").strip()
                quality, _ = gopher_quality_filter(flat_data)
                # qlabel, _ = fasttext_quality_classify(flat_data)
                lang, _ = identify_language(flat_data)
                nsfw, _ = detect_nsfw(flat_data)
                toxic, _ = detect_toxic_speech(flat_data)
                if lang != "en" or nsfw == "nsfw" or toxic == "toxic" or quality == False:
                    # print(f"Filtered url: {url}, lang: {lang}, nsfw: {nsfw}, toxic: {toxic}, quality: {quality}, qlabel: {qlabel}")
                    continue
                masked_data, _ = mask_emails(data)
                masked_data, _ = mask_phone_numbers(masked_data)
                masked_data, _ = mask_ip_addresses(masked_data)

                outputs.append((url, lang, masked_data))
            if cnt % 1000 == 0:
                print(f"Processed {cnt} records from {input_path}, get {len(outputs)} valid samples.")

    df = pd.DataFrame(outputs, columns=["url", "language", "text"])
    df.to_parquet(output_path, index=False)
    return output_path 
 
# Set up the executor  
num_cpus = 10 # len(os.sched_getaffinity(0)) 
executor = concurrent.futures.ProcessPoolExecutor(max_workers=num_cpus) 

warc_filebase = Path("/data/home/hyzheng/Projects/CS336/assignment4-data/cs336-data/data")
warc_filepaths = list(warc_filebase.glob("CC-MAIN-*.warc.gz"))
output_directory_path = "/data/home/hyzheng/Projects/CS336/assignment4-data/cs336-data/flitered_data"  

futures = [] 

pprint(warc_filepaths)
for warc_filepath in warc_filepaths:  
    # For each WARC filepath, submit a job to the executor and get a future back 
    output_path = os.path.join(output_directory_path, Path(warc_filepath).stem + ".parquet")
    print(output_path)
    future = executor.submit( 
        process_single_warc_file, 
        warc_filepath, 
        output_path,
    ) 
    
    # Store the futures  
    futures.append(future)  
    
# Iterate over the completed futures as they finish, using a progress bar 
# to keep track of progress. 
for future in tqdm( concurrent.futures.as_completed(futures), total=len(warc_filepaths), ): 
    output_file = future.result() 
print(f"Output file written: {output_file}")