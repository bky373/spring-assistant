import csv
import os
import sys

from src.constant.spring_docs_urls import PROJECT_REFERENCES
from src.data_collection.step_1_get_docs_urls import get_docs_urls
from src.data_collection.step_2_docs_crawling import crawl_docs_and_save_as_csv
from src.data_collection.step_3_generate_qa import load_data_from_csv, generate_questions_and_answers, save_as_qa_csv

csv.field_size_limit(sys.maxsize)

def step_1_and_2():
    add_num = 0
    references = PROJECT_REFERENCES[add_num:]

    for i in range(len(references)):
        url = references[i]

        urls = get_docs_urls(url)

        print(f"## {i + add_num}번째 {url} 시작")

        crawl_docs_and_save_as_csv(urls)

        print(f"## {i + add_num}번째 {url} 완료\n")


def step_3():
    directory = '../../data/docs'
    file_list = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    file_list.sort()

    add_num = 4
    file_list = file_list[add_num:]
    print(file_list[add_num:add_num+1])

    for i in range(len(file_list)):
        file = file_list[i]
        urls_and_contents = load_data_from_csv(file)

        print(f"## {i + add_num}번째 {file} 시작")

        for info in urls_and_contents:
            try:
                qa_pairs = generate_questions_and_answers(info)
                save_as_qa_csv(info['file'], qa_pairs)
            except Exception as e:
                print("[Exception] error: {}, info: {}".format(e, info))

        print(f"## {i + add_num}번째 {file} 완료")

# step_1_and_2()
# step_3()
