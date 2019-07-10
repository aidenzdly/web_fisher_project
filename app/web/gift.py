from flask import current_app, flash, redirect, url_for, render_template

from app.libs.enums import PendingStatus
from app.models.base import db
from app.models.drift import Drift
from app.models.gift import Gift
from app.view_models.gift import MyGifts
from app.view_models.trade import MyTrades
from . import web
from flask_login import login_required, current_user



@web.route('/my/gifts')
@login_required   # 装饰器的意义表示必须登录才可以访问视图函数
def my_gifts():
    uid = current_user.id
    gifts_of_mine = Gift.get_user_gifts(uid)
    isbn_list = [gift.isbn for gift in gifts_of_mine]
    wish_count_list = Gift.get_wish_counts(isbn_list)
    view_model = MyTrades(gifts_of_mine, wish_count_list)
    return render_template('my_gifts.html', gifts=view_model.trades)


@web.route('/gifts/book/<isbn>')
@login_required  # 赠送时需要登录
def save_to_gifts(isbn):
    '''
    上传一本书
    加上0.5个鱼豆
    '''
    if current_user.can_save_to_list(isbn):
        with db.auto_commit():  # 增添了auto_commit事务的回滚方法(建议每次关于提交到数据库的操作都加上回滚操作)
            gift = Gift()
            gift.isbn = isbn
            # current_user 指定为赠送者对象 ---> 由get_id方法 通过cookie中uid转为模型对象-->赠送者
            gift.uid = current_user.id
            current_user.beans += current_app.config['BEANS_UPLOAD_ONE_BOOK']
            db.session.add(gift)
    else:
        flash('这本书已添加至你的赠送清单或已存在于你的心愿清单，请不要重复添加')
    return redirect(url_for('web.book_detail', isbn=isbn)) # 跳转到本页面，可选择ajax


@web.route('/gifts/<gid>/redraw')
@login_required
def redraw_from_gifts(gid):
    '''
    撤销按钮
    '''
    gift = Gift.query.filter_by(id=gid, launched=False).first_or_404()
    # 解决一个额外思考问题：
    # 当一本书在赠送清单内，而且此书也在交易中，就要保证此书先交易完成之后，在从赠送清单中删除掉
    drift = Drift.query.filter_by(
        gift_id=gid, pending=PendingStatus.Waiting).first()
    if drift:
        flash('这个礼物正处于交易状态，请先前往鱼漂完成该交易')
    else:
        with db.auto_commit():
            # 撤销，归还0.5个鱼豆
            current_user.beans -= current_app.config['BEANS_UPLOAD_ONE_BOOK']
            gift.delete() # 逻辑删除，只是修改状态。在Gift模型的父类定义一个delete逻辑删除的方法
                          # 保证Gift和Base模型内都有此逻辑删除的方法
    return redirect(url_for('web.my_gifts'))



