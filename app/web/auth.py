from flask import render_template, request, redirect, url_for, flash
from app.forms.auth import RegisterForm, LoginForm, EmailForm, ResetPasswordForm
from flask_login import login_user, logout_user
from app.models.user import User
from app.models.base import db
from app.libs.email import send_mail
from . import web


@web.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)  # 参数校验  # 错误信息及用户输入信息都保留在form中
    if request.method == 'POST' and form.validate():
        with db.auto_commit():
            user = User()
            user.set_attrs(form.data)
            db.session.add(user)
        return redirect(url_for('web.login'))
    return render_template('auth/register.html', form=form)


@web.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        # 查询用email为依据，是用户注册时用了email来注册，可作为判断依据
        user = User.query.filter_by(email=form.email.data).first()
        # 1.首先判断用户是存在的 2.判断用户输入的密码与数据库中的密码是否相等
        # 由于数据库中的密码是通过加密之后得到的，所以也需要获取用户输入的密码，加密之后再与数据库中的密码进行比较
        if user and user.check_password(form.password.data):
            # login_user的本质是将用户信息写入到cookie中，需要id号表明用户身份
            # 将用户的id号写入到cookie中--->对某些视图函数做一些访问权限的控制，就是说需要登录才可以操作其他的
            login_user(user, remember=True)  # 参数是表示一定时间免密登录，cookie的默认时间为365天
            # http://127.0.0.1:5000/login?next=%2Fmy%2Fgifts 此url是引导返回的登录页面，同样也是登录页面
            next = request.args.get('next')  # 获取next↑的url地址，next表示地址
            if not next or not next.startswith('/'):  # 防止重定向攻击
                next = url_for('web.index')
            return redirect(next)
        else:
            flash('账号不存在或密码错误')
    return render_template('auth/login.html', form=form)


@web.route('/reset/password', methods=['GET', 'POST'])
def forget_password_request():
    form = EmailForm(request.form)
    if request.method == 'POST':
        if form.validate():
            account_email = form.email.data  # 826577863@qq.com
            # first_or_404表示当查询失败或者没有次数据时，会抛出一个异常，后续代码不在执行(简单，不会再次处理判空)
            user = User.query.filter_by(email=account_email).first_or_404()
            send_mail(form.email.data, '重置你的密码',
                      'email/reset_password.html', user=user,
                      token=user.generate_token())
            flash('一封邮件已发送到邮箱' + account_email + ', 请及时查收')
    return render_template('auth/forget_password_request.html', form=form)


@web.route('/reset/password/<token>', methods=['GET', 'POST'])
def forget_password(token):
    '''
    忘记密码功能
    '''
    form = ResetPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        success = User.reset_password(token, form.password1.data)
        if success:
            flash('你的密码已更新，请使用新密码登录')
            return redirect(url_for('web.index'))
        else:
            flash('密码重置失败')
    return render_template('auth/forget_password.html', form=form)


@web.route('/logout')
def logout():
    '''
    清空浏览器的cookie
    '''
    logout_user()
    return redirect(url_for('web.index'))
