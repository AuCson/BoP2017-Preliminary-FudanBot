# coding=utf-8
import MySQLdb
import urllib,urllib2
import json
import jieba
import re
from POS_regex_parser import Relation
from POS_regex_parser import parse_request
from POS_regex_parser import POS_regex_parser

def connect_db():
    db = MySQLdb.connect(host='127.0.0.1',user='root',passwd='kim419819',db='bop',charset='utf8')
    return db


def synset(word):
    d = {
        '含有':'有'
    }
    return d.get(word,word)

def repl(word):
    word = word.replace(u' ','')
    word = word.replace(u'学系',u'')
    word = word.replace(u'系',u'')
    word = word.replace(u'学院',u'')
    word = word.replace(u'专业',u'')
    word = word.replace(u'院',u'')
    return word

def get_query_relation(st):
    p = POS_regex_parser()
    xml = parse_request(st)
    p.load_xml_from_text(xml)
    relation_all = p.process()
    relation = []
    for l in relation_all:
        for r in l:
            relation.append(r)
    return relation

def to_query(word):
    s = '%'+word+'%'
    s = s.replace(' ','')
    return s.encode('utf-8')
basic_entity = [u'复旦大学',u'贵校',u'复旦',u'你校',u'我们学校',u'你们学校']
fudan_property = [
u'校徽',u'校庆日',u'校名',u'校训',u'校风',u'校歌',u'创办日期',u'校区',u'创建',u'校庆',u'创办',u'创办于',u'建校',u'建校于',u'校友',
    u'本科专业',u'研究生专业',u'博士后流动站',u'邯郸校区',u'枫林校区',u'张江校区',u'江湾校区' ]
school_property = [
    u'体育教学部',u'艺术教育中心',u'武装部',u'社会科学基础部',u'实验动物科学部',u'数学科学',u'数学',u'国际关系与公共事务',u'药学',
    u'生命科学',u'公共卫生',u'管理',u'护理',u'经济',u'社会发展与公共政策',u'国际文化交流',
    u'软件',u'计算机科学与技术',u'信息科学与工程',u'信息',u'哲学',u'继续教育',u'新闻',u'法学',u'大数据',u'药',
    u'历史',u'文物和博物馆',u'外国语言文',u'外国语言文',u'外语',u'环境科学与工程',u'高分子',u'高分子科学',u'材料科学',u'中文',u'中国语言文学',u'化学',u'化'
    ,u'物理',u'数学',u'计算机',u'哲学',u'金融研究所',u'生物医学研究院',u'现代物理研究所',u'放射医学研究所',
    u'专用材料与装备技术研究院', u'大数据研究院',u'邯郸',u'枫林',u'张江',u'江湾',u'邯郸校区',u'枫林校区',u'张江校区',u'江湾校区'
]
department_property_ = ['党委办公室','共青团复旦大学委员会', '保卫处', '武装部', '文科科研处', '对外联络与发展处', '人事处', '财务处', '张江校区管理委员会', '资产经营公司（原产业化与校产管理办公室）', '总务处', '研究生院', '学生工作部', '老干部工作处', '审计处', '医院管理处', '枫林校区管理委员会', '统战部', '基建处', '纪委', '监察处', '研究生工作部', '工会', '发展规划处', '机关党委', '教务处', '复旦大学校务委员会', '复旦大学学位评定委员会', '上海医学院办公室', '医学发展规划办公室', '医学学位与研究生教育管理办公室', '退管会', '医学教育管理办公室', '外国留学生工作处', '党委党校办公室', '后勤党委', '资产管理处']
department_property = [i.decode('utf-8') for i in department_property_]
job_property_ = ['校长', '副校长', '党委书记','常务书记','党委副书记', '院长', '副院长', '院党委书记', '系主任', '校长助理', '院士', '长江学者', '全国高校名师', '中国科学院院士', '中国工程院院士', '文科杰出教授', '科学院院士', '工程院院士', '本科生', '研究生', '预科生', '青年学者', '青年研究员', '副教授', '讲师', '学生', '老师', '教授', '专科生', '留学生', '千人计划', '千人计划学者', '国家杰出青年', '国家杰青', '文科资深教授', '文科特聘资深教授']
job_property = [i.decode('utf-8') for i in job_property_]

def handler(st,intents,entities):
    func_dict = {
        u'实体属性“谁”查询':query_person,
        u'实体属性“什么”查询':query_prop,
        u'实体属性“多少”查询':query_number,
        u'实体属性“哪里”查询':query_prop,
        u'实体属性“何时”查询':query_prop,
        u'实体属性“是否”查询':query_A_is_subset_of_B,
    }
    # fully independent double questions with differenct intent
    intent_list = []
    for intent in intents:
        if intent[u'score'] > 0.3:
            intent_list.append(intent[u'intent'])
    output = ''
    for intent in intent_list:
        res = func_dict[intent](st,intent,entities)
        if res:
            output += res
    print output
    return output

def query_prop(st,intent,entities):
    pass

def query_time(st,intent,entities):
    pass

def query_number(st,intent,entities):
    db = connect_db()
    cursor = db.cursor()
    entities.sort(key=lambda x:-x[u'startIndex'])
    type_entities= [i[u'type'] for i in entities]
    words = [i[u'entity'] for i in entities]
    # multiple entity / property

    multiple = False
    if st.find(u'和')+st.find(u'与')+st.find(u'分别') != -3:
        multiple = True
    res = []
    constraints = []
    queries = []
    if st.find(u'电话') != -1 or st.find(u'联系方式') != -1:
        queries.append(u'电话')
    if st.find(u'邮编') != -1 or st.find(u'邮政编码')!=-1:
        queries.append(u'邮编')
    relations = get_query_relation(st.encode('utf-8'))

    for item in entities:
        syn_word = repl(item[u'entity'])
        w = jieba._lcut(syn_word)
        for word in w:
            if word in school_property or word in department_property:
                constraints.append(word)
            else:
                if (item[u'type'].find(u'疑问词')==-1) and word not in basic_entity:
                    queries.append(item[u'entity'])

    for r in relations:
        if type(r.predicate) == str:
            r.predicate = r.predicate.decode('utf-8')
            r.subject = r.subject.decode('utf-8')
        #if r.predicate not in basic_entity and r.predicate not in school_property and r.predicate not in \
        #        department_property:
        #    queries.append(r.predicate)
        if r.subject not in basic_entity and r.subject not in school_property and r.subject not in department_property:
            queries.append(r.subject)

    for word in queries:
        query_word = to_query(word)
        if not constraints:
            official_set = "'统计概览','复旦概况','治理架构','辉煌校史','复旦标志','访问复旦','师资队伍','人才培养','学科建设'"
            cursor.execute("select object from relation where page in (%s) and subject like '%s'" % (official_set,query_word))
            res += cursor.fetchall()
        else:
            for constraint in constraints:
                # subject = target, num = num
                constraint_word = to_query(constraint)
                cursor.execute("select num,origin from relation where page like '%s' and subject like '%s'" % (constraint_word, query_word))
                ret = cursor.fetchall()
                if len(ret) <= 5:
                    res += ret
                # subject = constraint, object = target
                sql ="select num,origin from relation where (page like '%s' or subject like '%s') \
                               and (object like '%s' or predicate like '%s')" % (constraint_word,constraint_word,query_word,query_word,)
                cursor.execute(sql)
                ret = cursor.fetchall()
                if(len(ret) <= 5):
                    res += ret
    ans = ''
    for i,item in enumerate(res):
        #origin sentence is null
        if not item[-1]:
            ans += item[0]
        else:
            ans += item[-1]
        if not multiple and ans:
            break
        if i == 1: #max return is 2
            break
    return ans

def query_A_is_subset_of_B(st,intent,entities):
    pass

def query_person(st,intent,entities):
    pass

def multi_search_handler(st,intent,entities):
    pass

def get_query(st):
    url = 'https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/' \
          '42568aab-7cdd-414b-b2e8-74a8d36b6d4d?subscription-key=' \
          '4a4752c623e94bb09c471e856a7dbe17&timezoneOffset=0&verbose=true&q='
    url = url + st
    urllib2.Request(url)
    response = urllib.urlopen(url)
    js = json.loads(response.read())
    return js

if __name__ == '__main__':
    #r = get_query_relation('复旦大学计算机系有多少本科生？')
    while True:
        st = raw_input()
        js = get_query(st)
        if type(st) == str:
			print st
			st = st.decode('utf-8')
        res = handler(st,js['intents'],js['entities'])
