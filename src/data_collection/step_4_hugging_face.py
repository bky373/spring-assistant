import os

import dotenv
from huggingface_hub.hf_api import HfApi

dotenv.load_dotenv()

api = HfApi(
    token=os.getenv("HF_TOKEN")
)

api.upload_file(
    path_or_fileobj="../../data/qa/ko/qa_total_ko.csv",
    path_in_repo="qa_total_ko.csv",
    repo_id="bky373/spring-docs",
    repo_type="dataset"
)

from datasets import load_dataset

dataset = load_dataset("bky373/spring-docs")
print(dataset)

train_data = dataset['train']
print(len(train_data))
