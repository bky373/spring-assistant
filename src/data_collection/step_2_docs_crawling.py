import csv
import os
import re

import requests
from lxml import html


def get_article_content(url):
    tree = html.fromstring(requests.get(url).content)
    content = tree.xpath('/html/body/div[1]/main/div[2]/article/*[not(self::div[1]/nav) and not(self::nav)]')
    if not content:
        content = tree.xpath('/html/body/div[1]/main/div[2]/div/*[not(self::div[1]/nav) and not(self::nav)]')
    def process_element(element):
        if isinstance(element, html.HtmlElement):
            if element.tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                return element.text_content().strip() + ': '
            elif element.tag == 'a':
                href = element.get('href', '')
                return f"{element.text_content().strip()}({href}) "
            else:
                text = element.text.strip() if element.text else ''
                for child in element:
                    child_text = process_element(child)
                    if text and child_text and not text.endswith(' ') and not child_text.startswith(' '):
                        text += ' '
                    text += child_text
                    if child.tail:
                        text += ' ' + child.tail.strip()
                return text.strip() + ' '
        elif isinstance(element, str):
            return element.strip() + ' '
        return ''

    full_text = ""
    for element in content:
        full_text += process_element(element)

    return re.sub(r'\s+', ' ', full_text).strip()


def crawl_docs_and_save_as_csv(urls):
    field_names = ['url', 'content']
    items = []
    for url in urls:
        items.append({
            "url": url,
            "content": (get_article_content(url))
        })
    print(f"#### items size: {len(items)}")

    if urls:
        file_group_name = (urls[0]
        .replace('https://docs.spring.io/', '')
        .replace('.html', '')
        .split('/')[0])
        file_group_name = f"../../data/docs/{file_group_name}_docs.csv"
        os.makedirs(os.path.dirname(file_group_name), exist_ok=True)

        with open(file_group_name, 'a', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names, quoting=csv.QUOTE_ALL)

            if csv_file.tell() == 0:
                writer.writeheader()

            for item in items:
                try:
                    writer.writerow({
                        'url': item['url'],
                        'content': item['content']
                    })
                except Exception as e:
                    print("[Exception] error: {}, res: {}".format(e, item))

        print(f"#### {file_group_name} completed")
