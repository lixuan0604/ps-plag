import os
import re
import time

import requests

import hashlib
from datetime import datetime

import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from rouge import Rouge
import docx2txt
import unicodedata
from tqdm import tqdm
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize, pos_tag
from nltk.translate.bleu_score import sentence_bleu
from common.utils.constants import PUBLIC_FOLDER
from sqlalchemy_model import InvertTable, PublicFile, PublicSent, IndiaOrder, c_session
import pandas as pd


bad_file = []
bad_file_size = []
stop_words = ['ⅰ', 'ⅱ', 'iv', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX',',', '', '.', ' ', ":","(",")", "-", "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "you're", "you've", "you'll", "you'd", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "she's", "her", "hers", "herself", "it", "it's", "its", "itself", "they", "them", "their", "theirs", "themselves", "this", "that", "that'll", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "a", "an", "the", "if", "or", "as", "of", "at", "by", "to", "up", "in", "on", "no", "s", "t", "can", "will", "don", "don't", "should", "should've", "now", "d", "ll", "m", "o", "re", "ve", "y", "ain", "aren", "aren't", "couldn", "couldn't", "didn", "didn't", "doesn", "doesn't", "hadn", "hadn't", "hasn", "hasn't", "haven", "haven't", "isn", "isn't", "ma", "mightn", "mightn't", "mustn", "mustn't", "needn", "needn't", "shan", "shan't", "shouldn", "shouldn't", "wasn", "wasn't", "weren", "weren't", "won", "won't", "wouldn", "wouldn't", "and", "for", "with", "which", "from", ]
rouge = Rouge()
wnl = WordNetLemmatizer()


def unicode_to_ascii(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def del_symbol(s):
    s = re.sub(r'[\(\)\+\*\_\·\（\）\/\=\~\：\，\,\£\、\ф]+', ' ', s)
    s = re.sub(r"[' ']+", ' ', s)
    return s


def dump_json(obj, fp, encoding='utf-8', indent=4, ensure_ascii=False):
    with open(fp, 'w', encoding=encoding) as fout:
        json.dump(obj, fout, indent=indent, ensure_ascii=ensure_ascii)


def rouge_l(s1, s2):
    return rouge.get_scores([s1], [s2])[0]['rouge-l']['f']


def process_docx(file, skip_short=True):
    old_file = file
    if file.endswith('doc'):
        file = doc2docx(file)
    paragraphs = unicode_to_ascii(docx2txt.process(file).replace('\u200b', '')).split('\n') #去除​
    doc_sentences = []
    paragraph_index = 0
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(para.split(' ')) < 25 and len(re.split(r'[\.|\!|\?]', para)):
            continue
        for i, sent in enumerate(re.split(r'[\.|!|\?]', para)):
            if len(sent.split(' ')) < 5 and skip_short:
                continue
            doc_sentences.append({'sent_id': str(paragraph_index) + '_' + str(i), 'sent': sent.strip()})
        paragraph_index += 1
    file_content = (str(old_file), doc_sentences)
    return file_content


def doc2docx(file):
    doc2docxF = os.path.join(Path(__file__).resolve().parent, 'doc2docxF')
    root_path = Path(__file__).resolve().parent
    if not os.path.exists(doc2docxF):
        os.makedirs(doc2docxF)
    filename = file.split('/')[-1].replace(' ', '')
    new_file = os.path.join(doc2docxF, filename)
    shutil.copyfile(file, new_file)
    os.system(f"libreoffice --headless --convert-to docx {new_file}")
    shutil.move(os.path.join(root_path, filename + 'x'), new_file + 'x')
    return new_file + 'x'


def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


def lemmatize(text):
    text = del_symbol(text)
    sent = word_tokenize(text.lower())
    sent = pos_tag(sent)
    ret = []
    for word, tag in sent:
        pos = get_wordnet_pos(tag) or wordnet.NOUN
        ret.append(wnl.lemmatize(word, pos=pos).strip())
    return ret


def get_word_dict():
    word_info = session.query(InvertTable).all()
    if len(word_info) == 0:
        word_dict = {}
    else:
        word_dict = {str(info.word): {'id': info.id, 'word_sent_list': eval(info.word_sent_list) if info.word_sent_list else set()} for info in word_info}
    return word_dict


def content2table_(filename, content, WORD_DICT):
    zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
    update_word = set()
    for sent_dict in content:
        sent_id = sent_dict['sent_id']
        sent = sent_dict['sent']
        if zhPattern.search(sent):
            continue
        sen_lem = lemmatize(sent.lower())
        p_sent = PublicSent(sent=sent.strip(), file_path=filename, p_i=sent_id, len_sent=len(sen_lem))
        session.add(p_sent)
        session.flush()
        index_id = p_sent.id
        for word in sen_lem:
            if word in stop_words or re.search('[0-9]+', word) or word.startswith("'") or word.endswith("'") or\
                    word.startswith("-") or word.endswith("-") or len(word) < 3 or word.startswith('"') or word.endswith('"'):
                continue
            if not WORD_DICT.get(word):
                word_invert = InvertTable(word=word)
                session.add(word_invert)
                session.flush()
                WORD_DICT[word] = {}
                WORD_DICT[word]['id'] = word_invert.id
                WORD_DICT[word]['word_sent_list'] = set()
            WORD_DICT[word]['word_sent_list'].add(index_id)
            update_word.add(word)
    session.commit()
    tmp_file = PublicFile(status=1, file_path=str(filename))
    session.add(tmp_file)
    session.commit()
    return WORD_DICT, update_word


def update_invert_table(word_dict):
    for k, v in word_dict.items():
        id = v['id']
        word_sent_list = str(v['word_sent_list'])
        session.query(InvertTable).filter_by(id=id).update({'word_sent_list': word_sent_list})
    session.commit()


def get_all_file(pb_path=PUBLIC_FOLDER):
    file_list = []
    for pwd_path, _, files in os.walk(pb_path):
        for f in files:
            file_list.append(os.path.join(pwd_path, f))
    file_list = list(filter(lambda x: re.search(r'student(s)?(_|\s)?material(s)?', x, re.I) is None and re.search(r'/public/test', x, re.I) is None and re.search(r'student_mateirals', x, re.I) is None and x.endswith('docx'), file_list))
    file_list = list(filter(lambda x: re.search(r'\/\~\$', x) is None and re.search(r'/__MACOSX/', x) is None, file_list))
    print(len(file_list))
    return file_list


def build_invert_table_():
    tmp = session.query(PublicFile).all()
    table_file_set = set(info.file_path for info in tmp)
    public_file = set(get_all_file())
    file_difference = list(public_file.difference(table_file_set))
    WORD_DICT = get_word_dict()
    update_word = set()
    for i, file in enumerate(tqdm(file_difference)):
        try:
            if i % 1000 == 0 and i != 0:
                tmp_dict = {}
                for word in update_word:
                    tmp_dict[word] = WORD_DICT[word]
                update_invert_table(tmp_dict)
                update_word = set()
            filename, content = process_docx(file)
            WORD_DICT, update_word_tmp = content2table_(filename, content, WORD_DICT)
            update_word = update_word.union(update_word_tmp)
        except Exception as e:
            print(str(e))
            tmp_file = PublicFile(status=0, file_path=str(file))
            session.add(tmp_file)
            session.commit()

    s1 = time.time()
    tmp_dict = {}
    for word in update_word:
        tmp_dict[word] = WORD_DICT[word]
    update_invert_table(tmp_dict)
    s2 = time.time()
    print('update_invert_table:', s2 - s1)


def plag_word(file, exclude_order=True, min_word_count=5):
    try:
        pre_order = '/'.join(file.split('/')[:7])
        file, content = process_docx(file)
        print(pre_order)
        ret_list = []
        for sent_dict in tqdm(content):
            sent_id = sent_dict['sent_id']
            sent = sent_dict['sent']
            sen_lem = lemmatize(sent.lower())
            sent_count_list = {}
            ref_sent_list = []
            for word in sen_lem:
                if word in stop_words:
                    continue
                word_info = session.query(InvertTable).filter_by(word=word).first()
                if not word_info:
                    continue
                word_sent_list = eval(word_info.word_sent_list)
                for id_sent in word_sent_list:
                    sent_count_list[str(id_sent)] = sent_count_list.get(str(id_sent), 0) + 1
            sent_count_list = {k for k, v in sent_count_list.items() if v >= min_word_count}
            for id_sent in sent_count_list:
                sent_info = session.query(PublicSent).filter_by(id=id_sent).first()
                ref_sent_list.append([sent_info.id, sent_info.sent, sent_info.p_i, sent_info.file_path])
            if len(ref_sent_list) == 0:
                continue
            if exclude_order:
                rouge_l_score = [[x[0], rouge_l(sent.lower(), x[1].lower()), x[1], x[2], x[3]] for x in ref_sent_list if not x[3].startswith(pre_order)]
                if len(rouge_l_score) == 0:
                    continue
            else:
                rouge_l_score = [[x[0], rouge_l(sent.lower(), x[1].lower()), x[1], x[2], x[3]] for x in ref_sent_list]
            max_data = max(rouge_l_score, key=lambda x: x[1])

            ret_list.append({'sent_id': sent_id, 'sent': sent, 'sim_rouge': {'id': max_data[0], 'rouge_l': max_data[1], 'bleu_1': sentence_bleu([word_tokenize(max_data[2].lower())], word_tokenize(sent.lower()), weights=(1, 0, 0, 0)), 'sent': max_data[2], 'p_i': max_data[3], 'file_path': max_data[4]}})
        print(len(ret_list))
        print(len(content))
        average_bleu1 = sum([x['sim_rouge']['bleu_1'] for x in ret_list]) / len(content)
        average_rouge_l = sum([x['sim_rouge']['rouge_l'] for x in ret_list]) / len(content)
        ret_list.append({'average_rouge_l': average_rouge_l, 'average_bleu1': average_bleu1})
        return ret_list
    except Exception as e:
        print(str(e))
        return False


def plag(id, fid, file, exclude_order=True, update_invert=True, min_word_count=5):
    if update_invert:
        build_invert_table_()
    PLAG_DETALI = os.path.join(Path(__file__).resolve().parent, 'plag_detail')
    list_detail = plag_word(file, exclude_order, min_word_count)
    if list_detail:
        average_rouge_l = list_detail[-1]['average_rouge_l']
        if not os.path.exists(PLAG_DETALI):
            os.makedirs(PLAG_DETALI)
        sentId, sent, refId, rougeL, bleu1, ref_Sent, refPI, filePath  = [], [], [], [], [], [], [], []
        for info in list_detail[:-1]:
            sentId.append(info['sent_id'])
            sent.append(info['sent'])
            refId.append(info['sim_rouge']['id'])
            rougeL.append(info['sim_rouge']['rouge_l'])
            bleu1.append(info['sim_rouge']['bleu_1'])
            ref_Sent.append(info['sim_rouge']['sent'])
            refPI.append(info['sim_rouge']['p_i'])
            filePath.append(info['sim_rouge']['file_path'])
        df = pd.DataFrame({
            'p_i': sentId,
            'sent': sent,
            'ref_sent': ref_Sent,
            'rouge_l': rougeL,
            'bleu1': bleu1,
            'ref_id': refId,
            'ref_p_i': refPI,
            'file_path': filePath
        })
        df.to_excel(os.path.join(PLAG_DETALI, str(fid) + '.xlsx'), encoding='utf-8',index=False)
        dump_json(list_detail, os.path.join(PLAG_DETALI, str(fid) + '.json'))

        session.query(IndiaOrder).filter_by(id=id).update({'score': average_rouge_l, 'status': 1, 'end_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'detail_path': os.path.join(PLAG_DETALI, str(fid) + '.json')})
    else:
        session.query(IndiaOrder).filter_by(id=id).update({'score': -1, 'status': -1, 'end_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
    session.commit()


def hashnow():
    key = hashlib.sha256(str(datetime.now()).encode('utf-8')).hexdigest()
    return key



if __name__ == '__main__':
    # while True:
    #     session = c_session()
    #     un_plag = session.query(IndiaOrder).filter_by(status=0)
    #     for item in un_plag:
    #         id = item.id
    #         fid = hashnow()
    #         file = item.file_path
    #         plag(id, fid, file)
    #     session.close
    while True:
        try:
            session = c_session()
            item = session.query(IndiaOrder).filter_by(status=0).first()
            id = item.id
            fid = hashnow()
            file = item.file_path
            plag(id, fid, file)
            session.close()
        except Exception as e:
            time.sleep(10)

    # session = c_session()
    # arr = []
    # for item in session.query(InvertTable).all():
    #     n = len(eval(item.word_sent_list))
    #     if n > 10000:
    #         print(item.word, n)
    #         arr.append((item.word, n))
    # print(sorted(arr, key=lambda x:x[1], reverse=True))

