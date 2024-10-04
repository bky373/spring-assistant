import os

import dotenv

dotenv.load_dotenv()

hf_token = os.getenv("HF_TOKEN")
repo_id = "bky373/spring-assistant"

# 모델 업로드
model.push_to_hub(repo_id, use_auth_token=hf_token)

# 토크나이저 업로드
tokenizer.push_to_hub(repo_id, use_auth_token=hf_token)
