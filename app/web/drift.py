from flask import flash, redirect, url_for, render_template, request
from sqlalchemy import desc, or_
from app.libs.email import send_mail
from app.libs.enums import PendingStatus
from app.models.base import db
from app.models.drift import Drift
from app.models.gift import Gift
from app.models.user import User
from app.models.wish import Wish
from app.view_models.book import BookViewModel
from app.view_models.drift import DriftCollection
from . import web
from flask_login import login_required, current_user
from app.forms.book import DriftForm


@web.route('/drift/<int:gid>', methods=['GET', 'POST'])
@login_required
def send_drift(gid):
    current_gift = Gift.query.get_or_404(gid)
    if current_gift.is_yourself_gift(current_user.id):
        flash('这本书是你自己的^_^, 不能向自己索要书籍噢')
        return redirect(url_for('web.book_detail', isbn=current_gift.isbn))
    # 判断用户是否有足够的鱼漂
    can = current_user.can_send_drift()
    if not can:
        return render_template('not_enough_beans.html', beans=current_user.beans)
    form = DriftForm(request.form)
    if request.method == 'POST' and form.validate():
        save_drift(form, current_gift)
        send_mail(current_gift.user.email, '有人想要一本书', 'email/get_gift.html',
                  wisher=current_user, gift=current_gift)
        return redirect(url_for('web.pending'))
    gifter = current_gift.user.summary  # 联表，获取赠送者的模型信息
    return render_template('drift.html', gifter=gifter, user_beans=current_user.beans, form=form)


@web.route('/pending')
@login_required
def pending():
    # 点击鱼漂时跳转
    # 交易记录--查询drift表---1.我作为索要者的交易 或者  2.我作为赠送者的交易
    drifts = Drift.query.filter(
        or_(Drift.requester_id == current_user.id,
            Drift.gifter_id == current_user.id)).order_by(desc(Drift.create_time)).all()
    # 没有在DriftCollection这个模型中直接写入cuurent_user，保证了模型的完整性，不会被current_user所束缚
    views = DriftCollection(drifts, current_user.id)
    return render_template('pending.html', drifts=views.data)


@web.route('/drift/<int:did>/reject')
@login_required
def reject_drift(did):
    '''
    拒绝
    '''
    # 书籍的赠送者才会出现拒绝按钮，索要者只会出现撤销按钮
    with db.auto_commit():
        # 超权防范：Gift.uid == current_user.id
        drift = Drift.query.filter(Gift.uid == current_user.id,
                                   Drift.id == did).first_or_404()
        drift.pending = PendingStatus.Reject
        # 查询书籍的索要者，然后拒绝之后，将鱼豆归还给索要者
        requester = User.query.get_or_404(drift.requester_id)
        requester.beans += 1
    return redirect(url_for('web.pending'))



@web.route('/drift/<int:did>/redraw')
@login_required
def redraw_drift(did):  # did:drift id
    # 撤销索要书籍
    # 存在超权现象--用户1登录之后，获得redraw_drift的权限，修改用户2的did
    with db.auto_commit():
        drift = Drift.query.filter_by(
            # 加上requester_id=current_user.id，表示如果用户传过来的did不属于本人的did，是查询不到结果
            requester_id=current_user.id, id=did).first_or_404()
        drift.pending = PendingStatus.Redraw
        # 自己撤销之后，你的鱼豆将归还
        current_user.beans += 1
    return redirect(url_for('web.pending'))   # 最好ajax


@web.route('/drift/<int:did>/mailed')
def mailed_drift(did):
    '''
    邮寄成功
    防止超权：gifter_id=current_user.id
    都有数据库事务支持(with db.auto_commit())，以免发生当状态发生改变，鱼豆没有发生变化
    '''
    with db.auto_commit():
        drift = Drift.query.filter_by(
            gifter_id=current_user.id, id=did).first_or_404()
        # 修改状态
        drift.pending = PendingStatus.Success
        current_user.beans += 1
        gift = Gift.query.filter_by(id=drift.gift_id).first_or_404()
        gift.launched = True  # 查询gift，gift中的launched默认为False，当成功赠送的时候，更改为True

        # 同理Wish模型中也有launched，当心愿完成时，重新更新一下数据库中的launched的状态为True
        # 写法与上可以类似
        Wish.query.filter_by(isbn=drift.isbn, uid=drift.requester_id,
                             launched=False).update({Wish.launched: True})
    return redirect(url_for('web.pending'))


def save_drift(drift_form, current_gift):
    # 保存鱼漂到数据库中
    with db.auto_commit():
        drift = Drift()
        # 使用populate_obj（）是将目标对象drift对应的模型字段全部导入
        # 前提是要写入到数据库的字段必须和原模型字段相同
        drift_form.populate_obj(drift)

        drift.gift_id = current_gift.id
        drift.requester_id = current_user.id
        drift.requester_nickname = current_user.nickname
        drift.gifter_nickname = current_gift.user.nickname
        drift.gifter_id = current_gift.user.id

        book = BookViewModel(current_gift.book)

        drift.book_title = book.title
        drift.book_author = book.author
        drift.book_img = book.image
        drift.isbn = book.isbn

        current_user.beans -= 1
        db.session.add(drift)
