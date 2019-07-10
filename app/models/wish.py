from app.models.base import db, Base
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, desc, func
from sqlalchemy.orm import relationship

# 注：赠送此书的gift模型和心愿清单里面的wish模型类似  一给一收

from app.spider.yushu_book import YuShuBook


class Wish(Base):
    id = Column(Integer, primary_key=True)
    user = relationship('User')
    uid = Column(Integer, ForeignKey('user.id'), nullable=False)
    isbn = Column(String(15), nullable=False)
    launched = Column(Boolean, default=False)

    @classmethod
    def get_user_wishes(cls, uid):
        '''
        根据uid号查询用户的所有礼物
        :param uid:
        :return:
        '''
        wishes = Wish.query.filter_by(uid=uid, launched=False).order_by(
            desc(Wish.create_time)).all()
        return wishes

    @classmethod
    def get_gifts_counts(cls, isbn_list):
        from app.models.gift import Gift  # 防止循环引入
        '''
        根据传入一组的isbn，到Wish表中计算出某个礼物的Wish心愿数量
        # 需要一组数量，分组求数量
        当涉及到跨模型或者跨表查询的时候，db.session。query方法较好
        '''
        count_list = db.session.query(func.count(), Gift.isbn).filter(Gift.launched == False,
                                                                      Gift.isbn.in_(isbn_list),
                                                                      Gift.status == 1).group_by(Gift.isbn).all()
        count_list = [{'count': w[0], 'isbn': w[1]} for w in count_list]
        return count_list

    @property
    def book(self):
        '''
        定义一个通过isbn取指定书本数据的方法
        '''
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(self.isbn)
        return yushu_book.first
