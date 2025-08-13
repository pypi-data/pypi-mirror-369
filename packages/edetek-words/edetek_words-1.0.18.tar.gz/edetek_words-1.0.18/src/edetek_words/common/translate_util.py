import base64
import time

import requests
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

from edetek_words.common.calc_time import calc_func_time

# server_base_url = "http://127.0.0.1:8088/api/external"
server_base_url = "http://eclinical-tools.chengdudev.edetekapps.cn:9090/api/external"


@calc_func_time
def extraction_semantic(source_text: list, target_text: str, source_language: str, target_language: str,
                        strict_model: bool = True):
    """
    语义提取
    参数：
        source_text: 提取的源文本列表
        target_text: 匹配的目标文本
        source_language: 源语言
        target_language: 目标语言
        strict_model: true：匹配结果的文本必须包含在target_text中， false：匹配结果的文本可能不包含在target_text中，但是语义上是包含的
    返回：
        extracted_texts: 语义提取后的结构列表
    """
    data = {
        'sourceLanguage': source_language,
        'targetLanguage': target_language,
        'sourceSentences': source_text,
        'targetParagraph': target_text,
        'strict': strict_model
    }
    response = postJson(f'{server_base_url}/semantic/extraction', data)
    if response["procCode"] != 200:
        raise Exception(response["message"])
    return response["payload"]


@calc_func_time
def translate_multi_text(texts: list, source_language: str, target_language: str):
    """
    批量翻译多条文本
    参数：
        texts: 待翻译的文本列表
        source_language: 源语言
        target_language: 目标语言
    返回：
        translated_texts: 翻译后的文本列表
    """
    data = {
        'sourceLanguage': source_language,
        'targetLanguage': target_language,
        'texts': texts
    }
    response = postJson(f'{server_base_url}/translation', data)
    if response["procCode"] != 200:
        raise Exception(response["message"])
    return response["payload"]


def postJson(url: str, json: dict) -> dict:
    """
    post json data to eclinical assistant
    """
    key = "testing"
    secret = b"BlrYGpX6PjSNpjCW"
    iv = generate_iv16()
    iv_base64 = base64.b64encode(iv).decode('utf-8')
    encrypted_data = encrypt_data(str(int(time.time() * 1000)).encode('utf-8'), secret, iv)
    headers = {
        'Authorization': f"{key}_{iv_base64}_{encrypted_data}",
    }
    start_time = time.time()
    response = requests.post(url, json=json, headers=headers)
    if response.status_code != 200:
        print("=" * 30)
        print(f"📡 Status Code: {response.status_code} {response.reason}")
        print(f"🔗 URL: {response.url}")
        end_time = time.time()
        duration = end_time - start_time
        print(f"⏱ Request took {duration:.3f} seconds")
        print("=" * 30)
        print("📤 Request Headers:")
        for k, v in response.request.headers.items():
            print(f"  {k}: {v}")
        print("\n📦 Request Body:")
        print(response.request.body)
        print("\n📥 Response Headers:")
        for k, v in response.headers.items():
            print(f"  {k}: {v}")
        print("\n📝 Response Text:")
        print(response.text)
        print("\n🧾 Try parsing as JSON (if possible):")
        try:
            print(response.json())
        except Exception as e:
            print(f"  ❌ Failed to parse JSON: {e}")
        raise Exception(
            f"POST request to {url} failed with status code {response.status_code}. "
            f"Response body: {response.text}"
        )
    return response.json()


def generate_iv16():
    """
    generate aes iv
    """
    return get_random_bytes(16)


def encrypt_data(data: bytes, key: bytes, iv: bytes) -> str:
    """
    generate aes encrypted data
    """
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct_bytes = cipher.encrypt(pad(data, AES.block_size))
    return base64.b64encode(ct_bytes).decode('utf-8')


def mapping_semantic(source_texts: list, target_texts: list, source_language: str, target_language: str):
    """
    语义匹配
    参数：
        source_texts: 源文本列表
        target_texts: 目标文本列表
        source_language: 源语言
        target_language: 目标语言
    返回：
        extracted_texts: 语义匹配字典
    """
    data = {
        'sourceLanguage': source_language,
        'targetLanguage': target_language,
        'sourceTexts': source_texts,
        'targetTexts': target_texts
    }
    response = postJson(f'{server_base_url}/semantic/mapping', data)
    if response["procCode"] != 200:
        raise Exception(response["message"])
    return response["payload"]
