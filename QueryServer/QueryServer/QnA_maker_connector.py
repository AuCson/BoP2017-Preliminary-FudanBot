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
        'Ocp-Apim-Subscription-Key':'85aeaaa2c905481e92718a6a7986284d',
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
    st = st.replace('哪位','谁')
    st = st.replace('请问','')
    return st
def get_question_type(st):
    url = 'https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/ca5785a1-c574-4757-bf64-8dc5119fc441?subscription-' \
          'key=4a4752c623e94bb09c471e856a7dbe17&timezoneOffset=0&verbose=true&q='
    url = url + st
    urllib2.Request(url)
    response = urllib.urlopen(url)
    js = json.loads(response.read())
    return js

def has_in_set(list_a,list_b):
    for item in list_a:
        if item in list_b:
            return True
    return False

def distinctive_type(trusted_list,parsed_list):
    if has_in_set(parsed_list,['校长','书记','主任','系主任','院长','副主任','副院长','委员','党委书记'])\
        or (has_in_set(parsed_list,['院士','学者','教授']) and not has_in_set(parsed_list,['计算机','信息','数学'])):
        trusted_list.append(u'职务查询')
    if has_in_set(parsed_list,['计算机','数学','信息']):
        trusted_list.append(u'学院概况')
    if has_in_set(parsed_list,['电话','总机','联系方式','联系']):
        trusted_list.append(u'电话查询')
    if has_in_set(parsed_list,['网址','网站','官网']):
        trusted_list.append(u'网站查询')
    if has_in_set(parsed_list,['传真']):
        trusted_list.append(u'传真号码查询')
    if not trusted_list:
        trusted_list.append(u'复旦大学概况查询')

def get_single_answer(q):
    luis_ret = get_question_type(q)
    intent = luis_ret['topScoringIntent']['intent']
    kb_dict = {
        u'职务查询': 'd1ed6abf-2e70-4fd1-bd7b-6ccd3135ec74',
        u'复旦大学概况查询': '00716ffa-7171-49d9-83ca-ac5987b1af09',
        u'电话查询': '6f632b07-e80f-4db6-ac5a-eddd53f0df75',
        u'传真号码查询': '507cad69-c46b-4417-877d-901e754d8da8',
        u'网站查询': '28fb93b0-8af0-4846-8c74-eef524c6fd01',
        u'学院概况':'41546723-30a2-4507-85e0-c737428df79f'
    }
    trusted_list = []
    words = jieba._lcut(q)
    words = [i.encode('utf-8') for i in words]
    distinctive_type(trusted_list, words)
    if not trusted_list:
        trusted_list = kb_dict.keys()
    res = []
    for kb in trusted_list:
        a, score = qna_maker_fetch(q, kb_dict[kb])
        if kb_dict.get(intent, '') == kb:
            score += 10
        res.append((a, score))
        if score > 80:
            break
    res.sort(key=lambda x: -x[1])
    return res[0][0]

def process_question(st,request):
    if type(st) == unicode:
        st = st.encode('utf-8')
    if request:
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
        parsed_l = jieba._lcut(q)
        parsed_l = [i.encode('utf-8') for i in parsed_l]
        tf, ans = TF_question(q, parsed_l)
        if tf:
            ans = TF_handler(q,parsed_l)
            answers.append(ans)
        else:
            ans = get_single_answer(q)
            answers.append(ans)
    return ','.join(answers)

def TF_question(st,parse_l):
    if (('吗' in parse_l or '么' in parse_l) and ('是' in parse_l or '有' in parse_l))\
            or ('是不是' in parse_l):
        return True,'不是'
    return False,''
    #[A]是[B]吗？
    #[B]是[A]吗？

def TF_question_iter(parsed_l,reverse=False):
    target = []
    try:
        idx = parsed_l.index('是')
    except ValueError:
        try:
            idx = parsed_l.index('有')
        except ValueError:
            idx = parsed_l.index('是不是')
    if not reverse:
        new_l = copy.deepcopy(parsed_l)
        while len(new_l) > idx + 1:
            if new_l[idx+1] not in ['吗','么','?','？']:
                target.append(new_l[idx+1])
            del new_l[idx+1]
    else:
        new_l = []
        if '吗' in parsed_l:
            idx_m = parsed_l.index('吗')
        elif '么' in parsed_l:
            idx_m = parsed_l.index('么')
        elif '？' in parsed_l:
            idx_m = parsed_l.index('？')
        else:
            parsed_l.append('？')
            idx_m = parsed_l.index('？')
        i = idx + 1
        while i < idx_m:
            new_l.append(parsed_l[i])
            i += 1
        new_l.append('是')
        i = 0
        while i < idx:
            target.append(parsed_l[i])
            i += 1
    if has_in_set(parsed_l,['校长','书记','主任','系主任','院长','副主任','副院长','委员','党委书记','院士','学者','教授']):
        new_l.append('谁？')
    else:
        new_l.append('什么？')
    return new_l,target

def TF_handler(q,parsed_l):
    # in normal order
    new_l,target_l = TF_question_iter(parsed_l,reverse=False)
    new_q = ''.join(new_l)
    ans = get_single_answer(new_q)
    target = ''.join(target_l)
    if target.find(ans)!=-1 or ans.find(target)!=-1:
        if q.find('有')!= -1:
            return '有'
        else:
            return '是'
    new_l,target_l = TF_question_iter(parsed_l,reverse=True)
    new_q = ''.join(new_l)
    ans = get_single_answer(new_q)
    target = ''.join(target_l)
    if target.find(ans)!=-1 or ans.find(target)!=-1:
        if q.find('有')!= -1:
            return '有'
        else:
            return '是'
    if q.find('有') != -1:
        return '没有'
    else:
        return '不是'


if __name__ == '__main__':
    while True:
        s = raw_input()
        r = process_question(s,None)
        print r