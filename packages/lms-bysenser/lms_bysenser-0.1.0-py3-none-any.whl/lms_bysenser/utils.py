from django.core.cache import cache
import requests
import json
from urllib.parse import urljoin
import hashlib

# 常量定义
TOKEN_CACHE_KEY = "api_token_cache"
TOKEN_TIMEOUT = 3600  # 1小时
API_TIMEOUT = 5  # 请求超时时间


class APIClient:
    def __init__(self, host: str, secret_key: str, timestamp: str, salt: str):
        """
        初始化对象
        :param host: 通信地址
        :param account: 账号
        :param password: 密码
        """
        self.secret_key = secret_key
        self.timestamp = timestamp
        self.salt = salt
        self.base_url = f"http://{host}/index.php?r=app"

        self.signature = self.generate_signature()

    def generate_signature(self):
        """
        拼接字符串
        :param secret_key: 32位字符串密钥，默认值: 7cdc5ef8ata3bd8754a572de958b7e06
        :param timestamp: 时间戳（秒）
        :param salt: 4位随机字符
        :return: 签名
        """
        data = f"{self.secret_key}{self.timestamp}{self.salt}"
        sha1_hash = hashlib.sha1()
        sha1_hash.update(data.encode('utf-8'))
        signature = sha1_hash.hexdigest()
        return signature

    def get_tag(self) -> dict:
        '''
        获取标签列表
        :return:
        '''
        response = requests.get(
            url=f"{self.base_url}/taglist",
            headers={
                "timestamp": self.timestamp,
                "signature": self.signature,
                "salt": self.salt
            }
        )
        return response.json()

    def get_map(self) -> dict:
        '''
        获取标签列表
        :return:
        '''
        response = requests.get(
            url=f"{self.base_url}/getallmaps",
            headers={
                "timestamp": self.timestamp,
                "signature": self.signature,
                "salt": self.salt
            }
        )
        return response.json()

    def get_anchor(self) -> dict:
        '''
        获取标签列表
        :return:
        '''
        response = requests.get(
            url=f"{self.base_url}/basestationlist&pageSize=9999",
            headers={
                "timestamp": self.timestamp,
                "signature": self.signature,
                "salt": self.salt
            }
        )
        return response.json()


if __name__ == '__main__':
    apiclient = APIClient("129.211.174.214:8880", "7cdc5ef8ata3bd8754a572de958b7e06", "1735660800", "SCRI")
    a = apiclient.get_anchor()
    print(a)
