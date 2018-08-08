from flask import Flask, request
from flask_cors import CORS
from regex_select import tag_by_regex, law_to_sentence

app = Flask(__name__)
CORS(app, supports_credentials=True)


@app.route('/tagging', methods=['GET', 'POST'])
def tagging():
    law_sentence = request.get_json()

    print('items:', law_sentence)

    if law_sentence is None or len(law_sentence) == 0:
        return ""

    data = dict()
    for s_id, sentence in law_sentence.items():
        result, _ = tag_by_regex(sentence)
        data[s_id] = result
    return str(data)


@app.route('/splitting', methods=['GET', 'POST'])
def splitting():
    law_items = request.get_json()

    print('items:', law_items)

    if law_items is None or len(law_items) == 0:
        return ""

    data = dict()
    for item_id, item in law_items.items():
        result = law_to_sentence(item)
        data[item_id] = result
    return str(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8484, debug=True)