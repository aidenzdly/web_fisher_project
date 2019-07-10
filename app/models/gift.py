from flask import current_app
from app.models.base import db, Base
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, desc, func
from sqlalchemy.orm import relationship
from collections import namedtuple

# 创建Gift的目的是：相当于数据库中多读多，User和Book之间是多对多的关系，中间需要创建一个模型来关联二者之间的联系

from app.spider.yushu_book import YuShuBook

# EachGiftWishCount = namedtuple('EachGiftWishCount', ['count', 'isbn'])

class Gift(Base):
    id = Column(Integer, primary_key=True)

    user = relationship('User')  # 确定送出去的书是关联哪个模型
    # 小写user是上面定义的user字段，uid具体表示哪个User表中哪个用户送出的书
    uid = Column(Integer, ForeignKey('user.id'), nullable=False)

    # 同理，也Gift模型也要和Book模型关联，但只需要用isbn即可关联二者关系
    isbn = Column(String(15), nullable=False)
    launched = Column(Boolean, default=False)  # true表示书已送出去

    def is_yourself_gift(self, uid):
        # 接收用户的id号，如果相等，表示是该用户的礼物
        return True if self.uid == uid else False


    @classmethod
    def get_user_gifts(cls, uid):
        '''
        根据uid号查询用户的所有礼物
        :param uid:
        :return:
        '''
        gifts = Gift.query.filter_by(uid=uid, launched=False).order_by(
            desc(Gift.create_time)).all()
        return gifts

    @classmethod
    def get_wish_counts(cls, isbn_list):
        from app.models.wish import Wish
        '''
        根据传入一组的isbn，到Wish表中计算出某个礼物的Wish心愿数量
        # 需要一组数量，分组求数量
        当涉及到跨模型或者跨表查询的时候，db.session。query方法较好
        '''
        count_list = db.session.query(func.count(), Wish.isbn).filter(Wish.launched == False,
                                                                      Wish.isbn.in_(isbn_list),
                                                                      Wish.status == 1).group_by(Wish.isbn).all()
        count_list = [{'count':w[0], 'isbn':w[1]} for w in count_list]
        return count_list

    @property
    def book(self):
        '''
        定义一个通过isbn取指定书本数据的方法
        '''
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(self.isbn)
        return yushu_book.first

    @classmethod
    def recent(cls):
        '''
        首页：显示最近书籍--最近礼物---显示要求：1.只显示一定数量（30本）
                                                 2.去重，同一本书籍的礼物不重复出现
                                                 3.按照时间倒序排列，最新的排在最前面
        '''
        # 链式调用
        recent_gift = Gift.query.filter_by(launched=False).group_by(
            Gift.isbn).order_by(
            desc(Gift.create_time)).limit(
            current_app.config['RECENT_BOOK_COUNT']).distinct().all()
        return recent_gift
