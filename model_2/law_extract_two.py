from function_lib.functions import *
from function_lib.rule_table import item_title_filter, remove_special_character, remove_useless_desc
import re
from function_lib.rule_table import remove_last_de
keys = ['当', '应当', '方可', '不得', '禁止', '严禁', '可以']


def info_extract(sentences):
    templates = []
    for sen in sentences:
        tem_dict = dict()
        for i, word in enumerate(sen):
            if word in keys:
                before_key = ''.join(sen[:i])
                tem_dict['condition'], tem_dict['subject'] = subject_condition_filter(before_key)
                tem_dict['key'] = word
                tem_dict['behavior'] = ''.join(sen[i+1:]).replace('<s>','').replace('</s>','')
                break
        else:
            if templates:
                templates[-1]['behavior'] += ''.join(sen).replace('<s>','').replace('</s>','')

        if tem_dict:
            templates.append(tem_dict)

    return templates


def item_info_parse(text):
    sentences = sentence_split(text)
    # print('sentences:', sentences)
    templates = info_extract(sentences)
    return templates


def sentence_split(text):
    item = text.strip().replace('\u3000', '').replace('<p>', '').replace('</p>', '')

    sents = []
    ltp_srl = ltp_tool(item, 'srl')
    # ltp_par = ltp_parse(item, 'parse')

    if not ltp_srl:
        return sents
    seg = ltp_srl['seg']
    role = ltp_srl['role']
    if role:
        sub_flag = 0
        for i, r in enumerate(role):
            beg = r['beg']
            end = r['end']
            role_type = r['type']
            # relate = ltp_par[end]['relate']
            if role_type == 'A0':
                if '<s>' in seg[beg]['word']:
                    continue
                seg[beg]['word'] = '<s>' + seg[beg]['word']
                seg[end]['word'] += '</s>'

                if sub_flag == 0:
                    sub_flag = 1
                    continue
                elif has_key(''.join(s['word'] for s in seg[:beg])):
                    seg[beg]['word'] = '|' + seg[beg]['word']
        # print('seg:', seg)
        sen = []
        for sw in seg:
            w = sw['word']
            if '|' not in w:
                sen.append(w)
            else:
                sents.append(sen)
                sen = [w.replace('|', '')]
        else:
            sents.append(sen)
    return sents


def has_key(s):
    has_key_flag = False
    for k in keys:
        if k in s:
            has_key_flag = True
            break
    return has_key_flag


def do():
    lines = read_from_file('../data_process/four_law.txt')
    for line in lines[:]:
        contents = line.split('\t')
        law_id, item_id, title, content = contents[0], contents[1], contents[2], contents[3]
        generated_template = item_info_parse(content)
        print(item_id, title, content, generated_template)
        yield line + '\n' + str(generated_template)


def do_regex_two(item):
    generated_template = item_info_parse(item)
    print('generated_template_regex_2', generated_template)
    return generated_template


def subject_condition_filter(s):
    pattern = re.compile('<s>(.*?)</s>')
    sub_matcher = pattern.findall(s)

    if sub_matcher:
        sub = sub_matcher[-1]
        con = s.replace(sub, '').replace('<s>','').replace('</s>','')
    else:
        sub = ''
        con = s
    con, sub = item_title_filter(con), item_title_filter(sub)
    con, sub = remove_special_character(con), remove_special_character(sub)
    return con, sub


def item_info_parse_j(text):
    text = remove_useless_desc(text)
    sentences = sentence_split_j(text)
    templates = info_extract_j(sentences)
    return templates


# 分离句子成分

# 未具体分析句子成分的情况下
# 如果是（sub是空或者condition是空）
# 如果（key词前面）的成分没有 的 就返回
# 否则把从后往前的第一个 的 后面的作为主语，前面的作为条件
def sentence_split_j(item):
    item = item_title_filter(item)
    sents = []
    ltp_srl = ltp_tool(item, 'srl')

    if not ltp_srl:
        return sents

    # 按照srl方法拆分
    seg = ltp_srl['seg']
    role = ltp_srl['role']
    sen = []

    if role:
        sub_beg_id = -1  # 记录主体单词开始位置的临时变量
        sub_end_id = -1
        for i, r in enumerate(role):
            beg = r['beg']
            end = r['end']
            role_type = r['type']
            # relate = ltp_par[end]['relate']
            if role_type == 'A0':
                if sub_beg_id == -1 and sub_end_id == -1 or (sub_end_id-sub_beg_id) < (end-beg) or beg >= sub_end_id \
                        and (end-beg) > 0:  # 优先使用句子中靠后的A0和更长的A0作为主体
                    sub_beg_id = beg
                    sub_end_id = end

        # 提取主语
        if sub_beg_id != -1 and sub_end_id != -1:
            seg[sub_beg_id]['word'] = '<s>' + seg[sub_beg_id]['word']
            seg[sub_end_id]['word'] += '</s>'

        # print('seg:', seg)
        # 如果句子中有A0，应该从第一个A0处开始寻找

        for sw in seg:
            w = sw['word']
            sen.append(w)

    return sen


def info_extract_j(sen):
    # 检查句子中有几个key词
    iskey = check_key(sen)
    # 此类分句情况下实际上sen里只有一个list
    tem_dict = dict()
    if iskey:
        for j in range(0, len(iskey)):
            i = iskey[j]  # 关键词的索引
            # 把key词前面的字符串提取出来
            before_key = ''.join(sen[:i])
            tem_dict['condition'], tem_dict['subject'] = subject_condition_filter(before_key)
            tem_dict['condition'] = remove_last_de(tem_dict['condition'])
            # 如果subject未能提取出来，并且还没到最后一个key词，则继续
            if (tem_dict['subject'] == '') and (j < len(iskey) - 1):
                continue
            tem_dict['condition'] = '' if len(tem_dict['condition']) <= 1 else tem_dict['condition']
            tem_dict['subject'] = '' if len(tem_dict['subject']) <= 1 else tem_dict['subject']
            tem_dict['key'] = sen[i]
            tem_dict['behavior'] = ''.join(sen[i + 1:]).replace('<s>', '').replace('</s>', '')
            # templates[-1]['behavior'] += ''.join(sentences).replace('<s>', '').replace('</s>', '')
            if tem_dict:
                break
    return tem_dict


# 检查句子中有没有key词，返回由所有key词组成的list
def check_key(sen):
    tem = []
    for i, word in enumerate(sen):
        if word in keys:
            tem.append(i)
    return tem


# 法条句式
# .*(应当|不得|禁止|严禁|可以|方可).*
if __name__ == '__main__':
    # print(subject_condition_filter('<s>部队</s>执行任务、战备训练需要使用航道的，<s>负责航道管理的部门</s>应当给'))
    with open('result.out2', 'w', encoding='UTF-8') as out:
        for i, r in enumerate(do()):
            print(i, end='\n')
            out.write(r + '\n')