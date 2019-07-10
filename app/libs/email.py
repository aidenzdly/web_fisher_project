from threading import Thread

from flask import current_app, render_template, app

from app import mail
from flask_mail import Message

# 异步发送信息到邮箱中
def send_async_email(app, msg):
    # 手动的将app推入栈中
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            pass


def send_mail(to, subject, template, **kwargs):
    # recipients参数表示群发,body一般传入文本
    # msg = Message('测试邮箱', sender='826577863@qq.com', body='Test', recipients=['826577863@qq.com'])
    msg = Message('[鱼书]' + ' ' + subject,
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[to])
    msg.html = render_template(template, **kwargs)
    # 创建一个线程,异步传递参数
    # 传入的这个current_app一定是有值得。send_mail函数是在视图函数中调用，
    # 在视图函数中调用说明有Request请求，requestcontext需要入栈，在入栈之前，
    # 会确认AppContext有没有入栈，没有入栈Flask底层会自动的将AppContext压入栈中
    # 所以当current_app访问AppContext这个栈中，一定是有值得；
    # 当如果使用线程的时候，会造成线程隔离，如果不手动将AppContext压入栈中，且
    # flask底层又不会自动的将AppContext压入栈中(线程隔离的作用)，所以此时current_app
    # 取不到值。
    # 解决方法：不传代理current_app，传入真是app核心对象（真是核心对象在每个线程中都有）
    app = current_app._get_current_object()  # -->真是的app核心对象
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr

