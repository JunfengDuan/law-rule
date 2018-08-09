import re


# 去除句子开始的（一）、（十）
def number_zh_filter(s):
    return re.sub('^\（[一二三四五六七八九十]\）', '', s)


# 去除句子首位的标点符号
def remove_special_character(s):
    return re.sub('^(、|，|；|。|：)+|(、|，|；|。|：)+$', '', s)


# 去除句子最后一个“的”字
def remove_last_de(s):
    return re.sub('的$', '', s)


def item_title_filter(s):
    item = re.sub('第.*?条', '',  s)
    return item


# 去除条件中的描述性文字“四、增加一款，作为第二款：”
# “第三款修改为：”
def remove_useless_desc(s):
    return re.sub('.*：', '', s)


def remove_dun(s):
    return re.sub('^（[一二三四五六七八九十]+）', '', s)


# 判断的方法应该是看法条里有没有“（一）（二）”
def has_key_one(s):
    has_key_flag = False
    pattern = re.compile('（[一二三四五六七八九十]+）')
    sub_matcher = pattern.findall(s)
    if len(sub_matcher) >= 1:
        has_key_flag = True
    return has_key_flag


def has_key_one_plus(s):
    key1 = ['下列', '以下', '如下']
    has_key_flag = False
    for k in key1:
        if k in s:
            has_key_flag = True
            break
    return has_key_flag


def has_key_two(s):
    keys = ['当', '应当', '方可', '不得', '禁止', '严禁', '可以']
    has_key_flag = False
    for k in keys:
        if k in s:
            has_key_flag = True
            break
    return has_key_flag

