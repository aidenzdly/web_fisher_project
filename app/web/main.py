from flask import render_template
from app.models.gift import Gift
from app.view_models.book import BookViewModel
from . import web


@web.route('/')
def index():
    rencent_gifts = Gift.recent()
    books = [BookViewModel(gift.book) for gift in rencent_gifts]
    return render_template('index.html', recent=books)
