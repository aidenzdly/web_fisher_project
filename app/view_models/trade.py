# 原始数据到视图数据的转化
from app.view_models.book import BookViewModel


class TradeInfo():
    def __init__(self, trades):
        self.total = 0
        self.trades = []  # 视图的实际数据
        self.__parse(trades)

    def __parse(self, trades):
        # 实现具体的转换
        self.total = len(trades)
        self.trades = [self.__map_to_trade(single) for single in trades]

    def __map_to_trade(self, single):
        # 处理单独的数据，三个字段表示将原始数据转化为页面所要展示的信息
        if single.create_datetime:
            time = single.create_datetime.strftime('%Y-%m-%d')
        else:
            time = '未知'
        return dict(
            user_name=single.user.nickname,  # 取user模型下的用户名
            time=time,
            id=single.id
        )


class MyTrades():
    '''
    MyTrades是基类
    将相同的类封装为一个大类（MyWishes和MyGifts，如果两个类的逻辑有差异，可以继承MyTrades类，每个子类执行自己差异的业务逻辑）
    '''

    def __init__(self, trades_of_mine, trade_count_list):
        self.trades = []
        self.__trades_of_mine = trades_of_mine
        self.__trade_count_list = trade_count_list
        self.trades = self.__parse()

    def __parse(self):
        # 定义一个临时的列表，保证不要对某一个函数里面的列表直接进行操作(修改)
        # 将子循环重新写成一个新的函数，然后在被调用
        temp_trades = []
        for trade in self.__trades_of_mine:
            my_trade = self.__matching(trade)
            temp_trades.append(my_trade)
        return temp_trades

    def __matching(self, trade):
        count = 0
        for trade_count in self.__trade_count_list:
            if trade.isbn == trade_count['isbn']:
                count = trade_count['count']
        r = {
            # 模板里是wishes
            'wishes_count': count,
            'book': BookViewModel(trade.book),
            'id': trade.id
        }
        return r
