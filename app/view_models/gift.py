from  .book import BookViewModel
from collections import namedtuple

# MyGift = namedtuple('MyGift', ['id', 'book', 'wishes_count'])

class MyGifts():
    def __init__(self, gifts_of_mine, wish_count_list):
        self.gifts = []
        self.__gifts_of_mine = gifts_of_mine
        self.__wish_count_list = wish_count_list
        self.gifts = self.__parse()

    def __parse(self):
        # 定义一个临时的列表，保证不要对某一个函数里面的列表直接进行操作(修改)
        temp_gifts = []
        for gift in self.__gifts_of_mine:
            my_gift = self.__matching(gift)
            temp_gifts.append(my_gift)
        return temp_gifts

    def __matching(self, gift):
        count = 0
        for wish_count in self.__wish_count_list:
            if gift.isbn == wish_count['isbn']:
                count = wish_count['count']
        # 单体--直接定义为字典 好处：简化代码；缺点：不能很好拓展
        r = {
            'wishes_count':count,
            'book':BookViewModel(gift.book),
            'id':gift.id
        }
        return r
        # my_gift = MyGift(gift.id, gift.book, count)
        # return my_gift