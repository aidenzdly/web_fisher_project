# 初始化app等一些代码
from flask import Flask
from flask_login import LoginManager
from app.models.book import db
from flask_mail import Mail

login_manager = LoginManager()
mail = Mail()

def register_web_blueprint(app):
    # 将蓝图注册到视图函数中
    from app.web.book import web
    app.register_blueprint(web)

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.secure')
    app.config.from_object('app.setting')
    # 调用蓝图注册的方法
    register_web_blueprint(app)
    # 初始化db，关联app核心对象
    db.init_app(app)
    # 初始化login_manager
    login_manager.init_app(app)
    # 将某些 未登录 则不能访问的视图函数，正确的引导到web的登录界面
    login_manager.login_view = 'web.login'
    # 自定义未登录的错误提示信息
    login_manager.login_message = '请先登录或注册'
    mail.init_app(app) # 注册mail到核心对象app上
    db.create_all(app=app)
    return app





