import csv
import json
import os
import re

import dotenv
from openai import OpenAI

from src.constant.prompt import QA_SYSTEM_PROMPT, USER_PROMPT

dotenv.load_dotenv()

client = OpenAI(
    api_key=os.getenv("UPSTAGE_API_KEY"),
    base_url="https://api.upstage.ai/v1/solar"
)


def load_data_from_csv(file_name):
    data = []
    with open(f"../../data/docs/{file_name}", mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)

        for row in reader:
            content = header.index('content')
            if content:
                data.append({
                    'file': file_name,
                    'url': row[header.index('url')],
                    'content': row[content]
                })
    return data


def generate_questions_and_answers(info):
    print(f"#### {info} 시작")
    qa_pairs = []
    response = client.chat.completions.create(
        model="solar-1-mini-chat",
        messages=[
            {
                "role": "system",
                "content": QA_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": USER_PROMPT.format(info['content'])
                .replace('url', info['url'].replace("<", "").replace(">", ""))
            }
        ],
        stream=False,
    )

    content = response.choices[0].message.content
    try:
        content_json = parse_json_safely(content)
        if not content_json:
            return qa_pairs

        for pair in content_json.get("qa_pairs", []):
            qa_pairs.append(pair)
        print(f"#### {info} 완료")
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 오류: {e}")
        print(f"문제의 내용: {content}")
    return qa_pairs


def save_as_qa_csv(file_name, qa_pairs):
    if not qa_pairs:
        return

    field_names = ['question', 'answer']
    total_file_name = f"../../data/qa/ko/qa_total_ko.csv"

    file_name = file_name.replace("_docs", "").replace(".csv", "")
    file_name = f"../../data/qa/ko/{file_name}_qa.csv"

    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    with open(file_name, 'a', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names, quoting=csv.QUOTE_ALL)

        for pair in qa_pairs:
            try:
                writer.writerow({
                    'question': pair['question'],
                    'answer': pair['answer']
                })
            except Exception as e:
                print("[Exception] qa: {}, error: {}".format(pair, e))

    print(f"###### {file_name} 완료")

    with open(total_file_name, 'a', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names, quoting=csv.QUOTE_ALL)

        for pair in qa_pairs:
            try:
                writer.writerow({
                    'question': pair['question'],
                    'answer': pair['answer']
                })
            except Exception as e:
                print("[Exception] qa: {}, error: {}".format(pair, e))

    print(f"######{total_file_name} 완료")


def parse_json_safely(json_str):
    def clean_json_string(json_string):
        json_string = json_string.replace('\\"', '\\\\"')
        return re.sub(r'[\x00-\x1F\x7F-\x9F]', '', json_string)

    def fix_json(json_str):
        # 1. 불필요한 쉼표 제거
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)

        # 2. 누락된 쉼표 추가
        json_str = re.sub(r'}\s*{', '},{', json_str)
        json_str = re.sub(r']\s*\[', '],[', json_str)

        # 3. 문자열 내 이스케이프 처리
        json_str = re.sub(r'(?<!\\)"', '\\"', json_str)

        # 4. 중괄호와 대괄호 균형 맞추기
        open_brackets = sum(1 for c in json_str if c in '{[')
        close_brackets = sum(1 for c in json_str if c in ']}')
        json_str += '}' * (open_brackets - close_brackets)
        return json_str

    try:
        return json.loads(clean_json_string(json_str))
    except json.JSONDecodeError as e:
        print(f"Original JSON parsing failed: {e}")

        fixed_json_str = fix_json(json_str)
        try:
            return json.loads(fixed_json_str)
        except json.JSONDecodeError as e:
            print(f"Fixed JSON parsing also failed: {e}")
            return None
