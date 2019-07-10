from app.libs.enums import PendingStatus
from sqlalchemy import Column, String, Integer, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship
from app.models.base import Base

class Drift(Base):
    """
        一次具体的交易信息
    """
    __tablename__ = 'drift'

    def __init__(self):
        self.pending = PendingStatus.Waiting
        super(Drift, self).__init__()

    id = Column(Integer, primary_key=True)
    # 邮寄信息
    recipient_name = Column(String(20), nullable=False)
    address = Column(String(100), nullable=False)
    message = Column(String(200))
    mobile = Column(String(20), nullable=False)
    # 书籍信息
    isbn = Column(String(13))
    book_title = Column(String(50))
    book_author = Column(String(30))
    book_img = Column(String(50))
    # 请求者信息
    requester_id = Column(Integer)
    requester_nickname = Column(String(20))
    # 赠送者信息
    gifter_id = Column(Integer)
    gift_id = Column(Integer)
    gifter_nickname = Column(String(20))
    # 鱼漂的状态
    _pending = Column('pending', SmallInteger, default=1)

    # 未做外键关联 -->  缺点：数据有冗余 ||| 优点：减少查询次数
    # 模型与模型之间的关联是实时的，如果某个时候用户的名称改了，那么原始的请求者的名字也就变了
    # 如果不用模型关联，即便修改了用户的名称，页面也会保存原始的名称，直接记录

    # 模型关联的缺点：1.没有忠实记录交易时的状态 2.关联需要查询多张表，查询速度比较慢
    # requester_id = Column(Integer, ForeignKey('user.id'))
    # requester = relationship('User')
    # gift_id = Column(Integer, ForeignKey('gift.id'))
    # gift = relationship('Gift')

    @property
    def pending(self):
        # 返回的不是数字类型，而是枚举类型
        return PendingStatus(self._pending)

    @pending.setter
    def pending(self, status):
    # 将枚举类型转为数字类型
        self._pending = status.value