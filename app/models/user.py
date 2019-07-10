from math import floor

from flask import current_app
from sqlalchemy import Column, Integer, String, Boolean, Float
from werkzeug.security import generate_password_hash, check_password_hash
# UserMixin类中有许多关于用户身份，属性等方法，用User直接继承，即可使用
# 但是如果在模型中用于表示用户身份的不是id，是其他的名称，则需要重写如get_id等方法
from flask_login import UserMixin

from app import login_manager
from app.libs.enums import PendingStatus
from app.libs.helper import is_isbn_or_key
from app.models.base import db, Base
from app.models.drift import Drift
from app.models.gift import Gift
from app.spider.yushu_book import YuShuBook
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class User(UserMixin, Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    nickname = Column(String(24), nullable=False)
    _password = Column('password', String(128), nullable=False)  # 字符串为表字段的名字
    phone_number = Column(String(18), unique=True)
    email = Column(String(50), unique=True, nullable=False)
    confirmed = Column(Boolean, default=False)
    beans = Column(Float, default=0)
    send_counter = Column(Integer, default=0)
    receive_counter = Column(Integer, default=0)
    wx_open_id = Column(String(50))
    wx_name = Column(String(32))

    # 不能直接在user表里增添password字段，因为用户输入的密码不能直接明文保存在数据库中

    @property  # 读取属性
    def password(self):
        return self._password

    def can_send_drift(self):
        # 鱼豆数必须足够(大于等于1)
        if self.beans < 1:
            return False
        # 自己不能够向自己请求书籍
        success_gifts_count = Gift.query.filter_by(
            # 找到当前用户的id，launched=True表示礼物已经赠送出去
            uid=self.id, launched=True).count()
        success_receive_count = Drift.query.filter_by(
            requester_id=self.id, _pending=PendingStatus.Success).count()
        # 每索取两本书，自己必须送出一本书
        return True if floor(success_receive_count / 2) <= floor(success_gifts_count) else False

    @password.setter  # 写入属性
    def password(self, raw):
        self._password = generate_password_hash(raw)

    def check_password(self, raw):
        # 不用判定是否为空，表中已经定义不能为空
        return check_password_hash(self._password, raw)

    # def get_id(self):  # 已经继承
    #     # 插件固定要求名为get_id,表明用户身份id
    #     return self.id

    def can_save_to_list(self, isbn):
        '''
        验证赠送者的isbn编号是否正确及存在这本书
        '''
        if is_isbn_or_key(isbn) != 'isbn':
            return False
        # 判断isbn是否存在
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(isbn)
        if not yushu_book.first:
            return False
        # 不允许一个用户同时赠送多本相同的图书，launched=False表示书还没有赠送出去，手中可以有多本相同的书，但不能同时赠送
        # 一个用户不可能同时成为赠送者和索要者

        #
        gifting = Gift.query.filter_by(uid=self.id, isbn=isbn,
                                       launched=False).first()  # 确认当前的图书是否已经存在于用户的赠送清单中
        wishing = Gift.query.filter_by(uid=self.id, isbn=isbn,
                                       launched=False).first()  # 判断这本书是否存在用户的心愿清单中
        # 既不在赠送清单，也不再心愿清单才能添加
        if not gifting and not wishing:
            return True
        else:
            return False

    def generate_token(self, expiration=600):
        # token:1.加入想要的信息，比如用户的id号，能够识别出是哪个用户想要修改密码
        #       2.token必须加密和编码，不能明文保存
        # 序列化器
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    # 修改完密码之后，更新用户密码
    # 别人拿到你的token值没有用，我们在密码写入的时候，将SECRET_KEY一起写入
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        uid = data.get('id')
        with db.auto_commit():
            user = User.query.get(uid)  # 当查询条件为模型的主键时，可以直接用get进行查询，拿到对应的User模型
            user.password = new_password
        return True

    # 注：此方法是将我们存储在cookie中的uid转化为对应的模型对象 --->current_user变为模型对象

    @property
    def summary(self):
        # 用户的简介信息，对应页面信息（适配页面）
        return dict(
            nickname=self.nickname,
            beans=self.beans,
            email=self.email,
            send_receive=str(self.send_counter) + '/' + str(self.receive_counter)
        )


@login_manager.user_loader
def get_user(uid):
    return User.query.get(int(uid))
