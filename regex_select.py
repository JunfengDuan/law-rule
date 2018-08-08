import re
from function_lib.rule_table import *
from model_1.law_extract_one import do_regex_one, law_item_parse_j
from model_2.law_extract_two import do_regex_two, item_info_parse_j

regex1 = '.*(下列|以下|如下).*'

regex2 = '.*(应当|不得|禁止|严禁|可以|方可).*'


def regex_filter(sentence, reg):
    return re.match(reg, sentence)


def tag_by_regex(sentence):
    """
    按句式选择标注算法
    :param sentence: 句子
    :return: 标注结果
    """
    if regex_filter(sentence, regex1):
        print('Use regex-1:', regex1)
        return do_regex_one(sentence), 1
    elif regex_filter(sentence, regex2):
        print('Use regex-2:', regex2)
        return do_regex_two(sentence), 2
    else:
        return None, 0


# 传入参数：需要知道对应的法条line，剩下两个不会用到
def sentences_to_parts(line):
    generate_temp = []
    # 如果有（一）……（十） 以及“以下”，“如下”等，则证明属于第一类，然后需要判断它是否应该属于在行为中，若是（一）……（十），则需要放在行为中
    # 否则需要再划分

    line = line.strip().replace('；', '</p>').replace('。', '</p>').replace(' ', ''). \
        replace('“', '').replace('”', '').replace('\u3000', '').replace('<p>', '').replace('\ufeff', '')

    # law_id, law_name = contents_temp[0], contents_temp[1]
    content = line

    # 判断是否有model_1和model_2的句子

    if has_key_one(content) and has_key_one_plus(content):
        generate_temp = sentences_to_parts_one(content)
    elif has_key_two(content):
        generate_temp = sentences_to_parts_two(content)
    return generate_temp


# 第一类
def sentences_to_parts_one(content):
    content = content.split('</p>')
    # 这两个flag用于检验“以下”和“（一）……（十）”
    beg_flag = 0
    num_flag = 0
    # content_temp 用于暂存（一）……（十）文本
    content_temp = ''
    generated_template = []

    for item in content:
        if item == '':
            continue

        # 如果未能检测到（以下，如下，下列）等关键词
        elif (has_key_one_plus(item) is False) and beg_flag == 0:
            if has_key_two(item):
                tem = (sentences_to_parts_two(item))
                generated_template.append(tem[0])

        # 如果第一次检测到（下列，以下，如下）关键词
        elif has_key_one_plus(item) and beg_flag == 0:
            beg_flag = 1
            content_temp += item + '</p>'
        # 检测到（一）……（十)
        elif has_key_one(item) and beg_flag == 1:
            content_temp += item + '</p>'
            num_flag = 1
        # 未检测到（一）……（十）前要一直用content_temp存储
        elif (has_key_one(item) == False) and beg_flag == 1 and num_flag == 0:
            content_temp += item
            content_temp = re.sub('</p>', '，', content_temp)
            content_temp += '</p>'
        # 处理content_temp
        elif (has_key_one(item) == False) and beg_flag == 1 and num_flag == 1:
            generated_template.append(law_item_parse_j(content_temp))
            content_temp = ''
            beg_flag = 0
            num_flag = 0
    if len(generated_template) == 0:
        generated_template.append(law_item_parse_j(content_temp))

    return generated_template


# 第二类
def sentences_to_parts_two(line):
    line = line.split('</p>')
    generated_final = []
    sub_temp = ''
    for i, s in enumerate(line):
        if s == '':
            continue
        s = s.replace('\u3000', '').replace('<p>', '').replace('</p>', '').replace(' ', '')
        # 主函数
        generated_template = item_info_parse_j(s)
        # 若本句没有主语，则拿上一句的主语过来作为本句主语
        if generated_template:
            if generated_template['subject'] != '':
                sub_temp = generated_template['subject']
            elif generated_template['subject'] == '':
                generated_template['subject'] = sub_temp
            generated_final.append(generated_template)
    return generated_final


def law_to_sentence(sentence):
    """
    法条拆分成句子
    :param sentence: 法条句子
    :return: 拆分后的句子列表
    """
    line = sentence.strip().replace(' ', '').replace('“', '').replace('”', '').replace('\u3000', '')\
        .replace('\ufeff', '').replace('\n', '')

    con = line.split('。')

    # sen是句子对应的list，sen_id是句子对应的id的list
    sen = []
    for c in con:
        if c == '<p>' or c == '</p>' or len(c) <= 1:
            continue
        sen.append(c)
    return sen


if __name__ == '__main__':
    print()