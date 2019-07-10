from flask import request, flash, render_template
from flask_login import current_user
from app.libs.helper import is_isbn_or_key
from app.models.gift import Gift
from app.models.wish import Wish
from app.spider.yushu_book import YuShuBook
from app.forms.book import SearchForm
from app.view_models.book import BookViewModel
from app.view_models.book import BookCollection
from app.view_models.trade import TradeInfo
from . import web
import json


# book为视图函数

@web.route('/book/search', methods=['POST', 'GET'])
def search():
    # 通过request.args获得请求url中的q和page参数
    # 请求的url:http://127.0.0.1:5000/book/search?q=9787501524044&page=1
    # args本质是dict的子类，但可以以dict的方式操作
    # request使用必须是在http请求或者是视图函数触发的
    # q = request.args['q']
    # page = request.args['page']
    # 参数校验
    form = SearchForm(request.args)
    books = BookCollection()
    if form.validate():
        # q和page从form里面取值，page可以取到默认值1，而通过request.args时取值，若客户端输入为0，则取不到默认值1
        q = form.q.data.strip()
        page = form.page.data
        isbn_or_key = is_isbn_or_key(q)

        yushu_book = YuShuBook()
        if isbn_or_key == 'isbn':
            yushu_book.search_by_isbn(q)
        else:
            yushu_book.search_by_keyword(q, page)
        # 将原始数据返回给BookCollection里面的books
        books.fill(yushu_book, q)
        # 保证对象里面如果还有不能序列化的对象--->继续转化-->直到变成能序列化的字典对象
        # return json.dumps(books, default=lambda o:o.__dict__)
        # return jsonify(books) # TypeError: Object of type 'BookCollection' is not JSON serializable
    else:
        flash('搜索的关键字不符合要求，请重新输入关键字')
        # return jsonify(form.errors)
    return render_template('search_result.html', books=books)


@web.route('/book/<isbn>/detail')
def book_detail(isbn):
    '''
    # url中传入isbn，确定哪本书
    '''
    has_in_gifts = False
    has_in_wishes = False

    # 取书籍详细数据
    yushu_book = YuShuBook()
    yushu_book.search_by_isbn(isbn)
    book = BookViewModel(yushu_book.first)

    # 判断用户是否登陆，如果是True，表示用户处于登录状态
    if current_user.is_authenticated:
        # 判断用户是否是这本书的赠送者,如果能查询到：
        if Gift.query.filter_by(uid=current_user.id, isbn=isbn,
                                launched=False).first():
            has_in_gifts = True  # 表示用户已有此书
        if Wish.query.filter_by(uid=current_user.id, isbn=isbn,
                                launched=False).first():
            has_in_wishes = True  # 表示心愿清单已有
    # 若未登录，则不用做处理，当做就没有赠送清单，也没有心愿清单

    trade_gifts = Gift.query.filter_by(isbn=isbn, launched=False).all()
    trade_wishes = Wish.query.filter_by(isbn=isbn, launched=False).all()

    trade_wishes_model = TradeInfo(trade_wishes)
    trade_gifts_model = TradeInfo(trade_gifts)

    return render_template('book_detail.html',
                           book=book, wishes=trade_wishes_model,
                           gifts=trade_gifts_model, has_in_gifts=has_in_gifts,
                           has_in_wishes=has_in_wishes)
