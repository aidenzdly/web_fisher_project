from app.libs.getHttp import HTTP
from flask import current_app  # 指代当前的app核心对象


class YuShuBook():
    '''
    封装业务逻辑---鱼书API提供数据
    '''
    isbn_url = 'http://t.yushu.im/v2/book/isbn/{}'
    keyword_url = 'http://t.yushu.im/v2/book/search?q={}&count={}&start={}'

    def __init__(self):
        self.total = 0
        self.books = []  # 原始数据最终保存的地方

    def __fill_single(self, data):
        if data:
            # 单本数据，total=1
            self.total = 1
            self.books.append(data)

    def __fill_collection(self, data):
        # 多本数据
        self.total = data['total']
        self.books = data['books']

    def search_by_isbn(self, isbn):
        # 读取类变量
        url = self.isbn_url.format(isbn)
        # 请求数据
        result = HTTP.get(url)
        # 不将数据返回
        self.__fill_single(result)

    def search_by_keyword(self, keyword, page=1):
        url = self.keyword_url.format(keyword, current_app.config['PER_PAGE'],
                                     self.calculate_start(page))
        result = HTTP.get(url)
        self.__fill_collection(result)

    def calculate_start(self, page):
        return (page - 1) * current_app.config['PER_PAGE']

    @property
    def first(self):
        return self.books[0] if self.total >= 1 else None
