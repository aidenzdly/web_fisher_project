
# 三种定义类的写法：book/drift/gift  最推荐book的写法--一目了然；最不推荐--gift--字典不好拓展
# 中间drift--不好读
class BookViewModel():
    def __init__(self, book):
        self.title = book['title']
        self.publisher = book['publisher']
        self.author = '、'.join(book['author'])
        self.image = book['image']
        self.price = book['price']
        self.summary = book['summary']
        self.isbn = book['isbn']   # 不加isb字段，则缺少isbn，返回not found
        self.pages = book['pages']
        self.binding = book['binding']
        self.pubdate = book['pubdate']

    @property
    def intro(self):
        # 如果lambda函数返回True，则保留；返回False，则去除(三个参数会依次带入到lambda函数中，观察返回结果)
        intros = filter(lambda x:True if x else False,
                        [self.author, self.publisher, self.price])
        return '/'.join(intros)

class BookCollection():
    def __init__(self):
        self.total = 0
        self.books = []
        self.keyword = ''

    def fill(self, yushu_book, keyword):
        self.total = yushu_book.total
        self.keyword = keyword
        self.books = [BookViewModel(book) for book in yushu_book.books]



class _BookViewModel():
    '''
    处理返回数据，满足页面等业务需求
    '''
    @classmethod
    def package_single(cls, data, keyword):
        '''
        单项数据处理
        '''
        returned = {
            'books':[],
            'total':0,
            'keyword':keyword
        }
        if data:
            returned['total'] = 1
            returned['books'] = [cls.__cut_book_data(data)]
        return returned

    @classmethod
    def package_collection(cls, data, keyword):
        '''
        多项数据处理
        '''
        returned = {
            'books': [],
            'total': 0,
            'keyword': keyword
        }
        if data:
            returned['total'] = data['total']
            returned['books'] = [cls.__cut_book_data(book) for book in data['books']]
        return returned

    @classmethod
    def __cut_book_data(cls, data):
        # 需要修剪的任务是由项目经理设计
        # 单本数据处理
        book = {
            'title':data['title'],
            'publisher':data['publisher'],
            'pages':data['pages'] or '',         # 若是空，则返回空字符串在页面上显示，否则null会渲染在页面上
            'author':'、'.join(data['author']),
            'price':data['price'],
            'summary':data['summary'] or '',
            'image':data['image']
        }
        return book

    @classmethod
    def __cut_books_data(cls, data):
        # 多本数据处理
        books = []
        for book in data['books']:
            r = {
                'title':book['title'],
                'publisher':book['publisher'],
                'pages':book['pages'] or '',
                'author':'、'.join(book['author']),
                'price':book['price'],
                'summary':book['summary'] or '',
                'image':book['image']
            }
            books.append(r)
        return books