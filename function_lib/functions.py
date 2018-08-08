import re
import requests
import json


def ltp_tool(text, target):
    """
    使用 LTP 作语义分析
    :param text: 输入句子
    :param target: 选择解析器(seg, ner, parse, srl)
    :return:
    """
    url_prefix = 'http://192.168.2.32:8082/ltp'
    # url_prefix = 'http://localhost:5000/ltp'

    json_str = {'text': text}
    url = url_prefix + '/' + target
    res = requests.post(url, json=json_str)
    if res.status_code == 200:
        ltp_result_json = res.text.replace("'", '"')
        # print('ltp_result_json:', ltp_result_json)
        ltp_result_dict = json.loads(ltp_result_json, encoding='UTF-8')
        return ltp_result_dict
    else:
        return None


def read_from_file(path):
    with open(path, 'r', encoding='UTF-8') as infile:
        return infile.readlines()


