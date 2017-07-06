# coding=utf-8
import urllib,urllib2
import httplib
import json
import jieba
import copy

def qna_maker_fetch(question,kb):
    if type(question) == unicode:
        question = question.encode('utf-8')

    headers = {
        # Request headers
        'type':'application/json',
        'Ocp-Apim-Subscription-Key':'',
    }

    params = urllib.urlencode(
        {'question':'hi','top':1}
    )

    uri = "/qnamaker/v2.0/knowledgebases/%s/generateAnswer?%s" % (kb,params)
    conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
    conn.request("POST", uri
                 , "{'question':'%s','top':1}"%question,
                 headers)
    response = conn.getresponse()
    data = response.read()
    print data
    try:
        js = json.loads(data)
        answer = js[u'answers'][0]
    except Exception:
        return '',0
    conn.close()
    return answer[u'answer'].encode('utf-8'),answer[u'score']

def question_preprocess(st):
    st = st.replace('你们学校','复旦')
    st = st.replace('你校','复旦')
    st = st.replace('我们学校','复旦')
    st = st.replace('我校','复旦')
    st = st.replace('贵校','复旦')
    st = st.replace('复旦大学','复旦')
    return st
def get_question_type(st):
    url = 'https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/{key}?subscription-' \
          'key=&timezoneOffset=0&verbose=true&q='
    url = url + st
    urllib2.Request(url)
    response = urllib.urlopen(url)
    js = json.loads(response.read())
    return js

def process_question(st,request):
    if type(st) == unicode:
        st = st.encode('utf-8')

    request.session.get('prev_ans')

    st = question_preprocess(st)

    l = jieba._lcut(st)
    l = [i.encode('utf-8') for i in l]
    conj_list = ['和','与','还有',',']
    idx = -1
    questions = []
    answers = []

    for i,word in enumerate(l):
        if word in conj_list:
            idx = i
            break
    # delete the latter word
    if idx != -1:
        try:
            bak = copy.deepcopy(l)
            del l[idx+1]
            del l[idx]
            questions.append(''.join(l))
            l = bak
            del l[idx]
            del l[idx-1]
            questions.append(''.join(l))

        except IndexError:
            print 'index error'
    else:
        questions.append(st)

    for q in questions:
        tf, ans = TF_question(q, l)
        if tf:
            answers.append(ans)
            continue
        luis_ret = get_question_type(q)

        intent = luis_ret['topScoringIntent']['intent']
        kb_dict = {
            u'职务查询':'d1ed6abf-2e70-4fd1-bd7b-6ccd3135ec74',
            u'复旦大学概况查询':'00716ffa-7171-49d9-83ca-ac5987b1af09',
            u'电话查询':'6f632b07-e80f-4db6-ac5a-eddd53f0df75',
            u'传真号码查询':'507cad69-c46b-4417-877d-901e754d8da8',
            u'网站查询':'28fb93b0-8af0-4846-8c74-eef524c6fd01',
        }
        res = []
        for kb in kb_dict.values():
            if '谁' in q and kb not in ['d1ed6abf-2e70-4fd1-bd7b-6ccd3135ec74','00716ffa-7171-49d9-83ca-ac5987b1af09']:
                continue
            a,score = qna_maker_fetch(q,kb)
            if kb_dict.get(intent,'') == kb:
                score += 10
            res.append((a,score))
            if score > 80:
                break
        res.sort(key=lambda x:-x[1])
        answers.append(res[0][0])
    if not answers:
        return '不存在的'
    return ','.join(answers)

def TF_question(st,parse_l):
    if ('吗' in parse_l or '么' in parse_l) and '是' in parse_l:
        return True,'不是'
    return False,''
    #xxx是你们的校长吗？
    #你们的校长是xxx吗？
    #[A]是[B]吗？
    #[B]是[A]吗？

if __name__ == '__main__':
    while True:
        s = raw_input()
        r = process_question(s)
        print r