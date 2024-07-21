import glob
import os
import jieba.analyse
import re
from jieba import posseg as pseg
from collections import defaultdict
from dashscope import Generation
from http import HTTPStatus
import json
import logging
 
# 配置日志记录
logging.basicConfig(filename='error.log',
                    filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')
 
# 创建一个日志记录器
logger = logging.getLogger(__name__)
 
# 设置日志级别
logger.setLevel(logging.WARNING)

from markdown import markdown
from bs4 import BeautifulSoup

def remove_markdown_styles(text):
    """
    移除Markdown文本中的链接和样式，只保留纯文本内容
    """
    # 将Markdown转换为HTML
    html = markdown(text)

    # 使用BeautifulSoup解析HTML并提取纯文本
    soup = BeautifulSoup(html, "html.parser")
    plain_text = soup.get_text()

    return plain_text

def process_files(input_dir, output_dir):
    """
    处理目录中的所有Markdown文件，移除链接和样式，只保留文本内容
    """
    for filename in os.listdir(input_dir):
        if filename.endswith(".md"):
            with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as file:
                text = file.read()
            
            plain_text = remove_markdown_styles(text)

            with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as file:
                file.write(plain_text)
            print(f"Processed {filename}")



def get_response(messages):
    response = Generation.call(model="qwen-turbo",
                               messages=messages,
                               # 将输出设置为"message"格式
                               result_format='message')
    return response

def call_with_messages(user_input, filename=''):
    output_json = ''

    # 将用户问题信息添加到messages列表中
    messages = [{'role': 'system', 'content': 'You are a helpful assistant who excels at extracting keywords, tags and summary of articles to help implement SEO for website content'}]
    messages.append({'role': 'user', 'content': '请提取如下文章的keywords（只取top5，用","分隔）, tags（只取top5，用","分隔） and summary（100字以内，尽量精简，字符串形式），并以JSON的形式返回（返回字段名为：keywords, tags , summary）:' + user_input})
    response_msg = get_response(messages)
    print(response_msg)
    if response_msg.status_code == HTTPStatus.OK:
        return response_msg.output.choices[0]['message']['content']
    else:
        logger.error(f"filename: {filename},Error calling model: {response_msg.message}")

        print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response_msg.request_id, response_msg.status_code,
            response_msg.code, response_msg.message
        ))

def remove_urls(text):
    """
    移除文本中的所有URL链接
    """
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return re.sub(url_pattern, '', text)

def set_remove_rematch(my_set, regex_pattern):
    return {item for item in my_set if not re.match(regex_pattern, item)}

def clean_keywords_set(keywords_set):
    # 清理关键词、标签字符串，移除无关内容，包括超链接、网址等
    keywords_set = set_remove_rematch(keywords_set, r'[\"\',]')
    keywords_set = set_remove_rematch(keywords_set, r'\b(?:http|https|img)\S*\b')
    keywords_set = set_remove_rematch(keywords_set, r'\b(?:com|www)\S*\b')
    return set(filter(lambda text: text.strip(), keywords_set))

def clean_description(description):
    # 移除 markdown/html 等非内容型文本
    description = re.sub(r'[\*\#\<\>\[\]\(\)\!\-\_]', '', description)
    description = description.replace('\n', ' ')
    return description

def extract_keywords_set(text, topN=10):
    keywords = jieba.analyse.extract_tags(text, topK=topN)
    return clean_keywords_set(set(keywords))

def extract_description(text, length=200):
    sentences = text.split('。')
    word_frequencies = defaultdict(int)

    for sentence in sentences:
        words = pseg.cut(sentence)
        for word, flag in words:
            if flag not in ['x', 'uj', 'ul', 'p']:
                word_frequencies[word] += 1

    max_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max_frequency

    sentence_scores = defaultdict(int)
    for sentence in sentences:
        words = pseg.cut(sentence)
        for word, flag in words:
            if word in word_frequencies:
                sentence_scores[sentence] += word_frequencies[word]

    summary_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:5]
    summary = '。'.join(summary_sentences)
    clean_summary = clean_description(summary[:length] + "..." if len(summary) > length else summary)
    return clean_summary

def extract_tags_set(text, topN=10):
    tags = jieba.analyse.extract_tags(text, topK=topN)
    return clean_keywords_set(set(tags))

def get_keyword_set(line):
    return set(re.sub(r'^\s+|\s+$', '', line).split(","))  if line else set()


def merge_keywords(existing, new):
    existing_set = get_keyword_set(existing)
    new_set = get_keyword_set(new)
    clean_merged = ",".join(clean_keywords_set(existing_set.union(new_set)))
    return clean_merged

def merge_description(existing, new):
    return f"{new}" if not existing else existing

def merge_tags(existing, new):
    existing_set = set(existing.strip().split("\n  - ")) if existing else set()
    new_set = set(existing.strip().split("\n  - ")) if existing else set()
    clean_tags = "\n  - " + "\n  - ".join(clean_keywords_set(existing_set.union(new_set)))
    return clean_tags


def generate_metadata(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()

    split_text = text.split('---', maxsplit=2)
    if len(split_text) != 3:
        print(f"Warning: {filename} does not have a valid metadata block, skipping")
        return
    original_metadata, content = split_text[1], split_text[2]
    print(original_metadata)
    # 解析并输出纯文本
    plain_text = remove_urls(remove_markdown_styles(content))
    keywords_set = extract_keywords_set(plain_text)
    tags_set = extract_tags_set(plain_text)
    description = extract_description(plain_text, 5000)
    # print(description)

    trimmed_content = call_with_messages(description, filename).split("```json")[1].split("```")[0]
    print(f'模型输出：{trimmed_content}')
    if trimmed_content:
        content_data = json.loads(trimmed_content)
        
        keywords_str = content_data.get('keywords', '')
        keywords_set = clean_keywords_set(get_keyword_set(keywords_str))

        tags_str = content_data.get('tags', '')
        tags_set = clean_keywords_set(get_keyword_set(tags_str))
        description = content_data.get('summary', '')
        print(f'模型分量：keywords：{keywords_str}， \n tags：{tags_str}， \n description：{description}')

    meta_data = '---\n'
    
    # 更新元数据
    desc_found = kw_found = tags_found = False
    old_tags_set = set()
    for line in original_metadata.split('\n'):
        if line.startswith('description:'):
            line = f'description: {description}'
            desc_found = True
        
        elif line.startswith('keywords:'):
            old_keywords_set = clean_keywords_set(get_keyword_set(line[len("keywords: "):]))
            keywords_set = old_keywords_set.union(keywords_set)
            keywords_str = ",".join(keywords_set)
            line = f'keywords: {keywords_str}'
            kw_found = True
        
        elif line.startswith('tags:'):
            tags_list_str = "\n  - ".join(tags_set)
            line = f"tags: \n  - {tags_list_str}"
            tags_found = True
            
        if not (line.strip().startswith('-') and tags_found and (line_str := re.sub(r'^\s+|\s+$', '', line)[1:]) in tags_set):
            if (line.strip().startswith('-') and tags_found):
                line = f"  - {line_str}"
            meta_data += line + '\n'
    
        

    # 如果元数据不存在则新增
    if not desc_found:
        meta_data += f"description: {description}\n"
    if not kw_found:
        meta_data += f'keywords: {",".join(keywords_set)}\n'
    if not tags_found:
        tags_list_str = "\n  - ".join(tags_set)
        meta_data += f"tags: \n  - {tags_list_str}"

    meta_data += '---\n'

    print(meta_data)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(meta_data + content)

def main():
    print("Generating metadata...")
    # file_dir_path = os.path.join(os.getcwd(), 'source/_posts/**/*.md')
    file_dir_path = os.path.join(os.getcwd(), 'source\_posts\Events\巴以冲突/巴以冲突之未来展望与局势推演.md')
    print(file_dir_path)
    posts = glob.glob(file_dir_path, recursive=True)

    for file in posts:
        print(f"Processing file: {file}")
        generate_metadata(file)

if __name__ == "__main__":
    main()
