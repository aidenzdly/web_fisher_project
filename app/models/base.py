from contextlib import contextmanager
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy as _SQLALchemy, BaseQuery
from sqlalchemy import SmallInteger, Column, Integer


# base文件表示初始化models里面的一些公共参数

class SQLALchemy(_SQLALchemy):  # SQLALchemy的子类
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


# 重构filter_by,BaseQuery的父类里面有filter_by方法，重新定义filter_by方法(自己的)，
# 然后在继承Query(继承着父类)，实现重写filter_by
# 总结:更改不能直接更改的源代码时，可以用重写基类的方法实现自己的业务逻辑
class Query(BaseQuery):
    def filter_by(self, **kwargs):
        if 'status' not in kwargs.keys():
            kwargs['status'] = 1
        return super(Query, self).filter_by(**kwargs)

# query_calss参数表示可以：使用我们自己定义的Query类
db = SQLALchemy(query_class=Query)


# 定义逻辑删除(状态变化)，本质是修改，防止物理删除造成数据丢失
class Base(db.Model):
    # Base继承db.Model默认表示Model想给Base创建一个表，但实际情况是不想创建表，只是单纯的继承
    # 所以__abstract__=True即可解决这个问题
    __abstract__ = True
    create_time = Column('create_time', Integer)  # 设置default时，数据表中的时间都是相同的
    status = Column(SmallInteger, default=1)  # 1默认表示存在

    # 初始化生成时间，保证当实例化任何一个模型时，都会生成时间
    def __init__(self):
        self.create_time = int(datetime.now().timestamp())

    @property
    def create_datetime(self):
        if self.create_time:
            return datetime.fromtimestamp(self.create_time)
        else:
            return None

    # 动态赋值
    def set_attrs(self, attrs):
        for key, value in attrs.items():
            # hasattr:判断一个对象下是否包含某个属性
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    def delete(self):
        self.status = 0
