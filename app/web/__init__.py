# 蓝图的初始化
from flask import Blueprint, render_template

web = Blueprint('web', __name__, template_folder='templates')

# 导入文件，否则执行蓝图的时候不执行蓝图文件
# 注意先后顺序--必须先初始化web蓝图，否则找不到web蓝图对象

# 监听到code为404时，才会抛出异常
# 还可写入日志等，一切逻辑
# AOP思想：集中处理
@web.errorhandler(404)
def not_found(e):
    return render_template('404.html')

from app.web import book
from app.web import auth
from app.web import drift
from app.web import gift
from app.web import main
from app.web import wish
