# helper 帮助判断

def is_isbn_or_key(word):
    '''
    判断输入是否是isbn编号
    # q:普通关键字
    # isbn:1.isbn 13 13个0到9的数字组成  2.10个0到9数字组成，含有一些'-'
    # 默认给key,判断是不是isbn
    '''
    isbn_or_key = 'key'
    if len(word) == 13 and word.isdigit():
        isbn_or_key = 'isbn'
    short_word = word.replace('-', '')
    if '-' in word and len(short_word) == 10 and short_word.isdigit():
        isbn_or_key = 'isbn'
    return isbn_or_key