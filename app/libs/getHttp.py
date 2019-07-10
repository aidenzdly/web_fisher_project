# 封装http请求
import requests

class HTTP():
    # 请求url的方法
    @staticmethod
    def get(url, return_json=True):
        r = requests.get(url)
        if r.status_code != 200:
            # 三元表达式简化代码，可以先全，在改写
            return {} if return_json else ''
        return r.json() if return_json else r.text
