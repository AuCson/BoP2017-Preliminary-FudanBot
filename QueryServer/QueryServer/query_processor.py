# coding=utf-8
import MySQLdb
import urllib,urllib2
import json
import jieba
from POS_regex_parser import Relation
from POS_regex_parser import parse_request
from POS_regex_parser import POS_regex_parser

def connect_db():
    db = MySQLdb.connect(host='127.0.0.1',user='root',passwd='kim419819',db='bop')
    return db

def synset(word):
    d = {
        '含有':'有'
    }
    return d.get(word,word)

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

fudan_property = [
'校徽','校庆日','校名','校训','校风','校歌','创办日期','校区','创建','校庆','创办','创办于','建校','建校于','校友',
    '本科专业','研究生专业','博士后流动站','邯郸校区','枫林校区','张江校区','江湾校区' ]
school_property = [
'体育教学部','艺术教育中心','武装部','社会科学基础部','实验动物科学部','数学科学学院','国际关系与公共事务学院','药学院',
    '生命科学学院','公共卫生学院','管理学院','护理学院','经济学院','社会发展与公共政策学院','国际文化交流学院',
    '软件学院','计算机科学与技术学院','信息科学与工程学院','哲学学院','继续教育学院','新闻学院','法学院','大数据学院',
    '历史学系','文物和博物馆学系','外国语言文学系','环境科学与工程系','高分子科学系','材料科学系','中国语言文学系','化学系'
    ,'物理学系','数学系','计算机系','哲学系','金融研究所','生物医学研究院','现代物理研究所','放射医学研究所',
    '专用材料与装备技术研究院', '大数据研究院'
]
department_property = ['党委办公室','共青团复旦大学委员会', '保卫处', '武装部', '文科科研处', '对外联络与发展处', '人事处', '财务处', '张江校区管理委员会', '资产经营公司（原产业化与校产管理办公室）', '总务处', '研究生院', '学生工作部', '老干部工作处', '审计处', '医院管理处', '枫林校区管理委员会', '统战部', '基建处', '纪委', '监察处', '研究生工作部', '工会', '发展规划处', '机关党委', '教务处', '复旦大学校务委员会', '复旦大学学位评定委员会', '上海医学院办公室', '医学发展规划办公室', '医学学位与研究生教育管理办公室', '退管会', '医学教育管理办公室', '外国留学生工作处', '党委党校办公室', '后勤党委', '资产管理处']
job_property = ['校长', '副校长', '党委书记','常务书记','党委副书记', '院长', '副院长', '院党委书记', '系主任', '校长助理', '院士', '长江学者', '全国高校名师', '中国科学院院士', '中国工程院院士', '文科杰出教授', '科学院院士', '工程院院士', '本科生', '研究生', '预科生', '青年学者', '青年研究员', '副教授', '讲师', '学生', '老师', '教授', '专科生', '留学生', '千人计划', '千人计划学者', '国家杰出青年', '国家杰青', '文科资深教授', '文科特聘资深教授']

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
    for intent in intent_list:
        func_dict[intent](st,intent,entities)


def query_prop(st,intent,entities):
    pass

def query_time(st,intent,entities):
    pass

def query_number(st,intent,entities):
    # method 1. Fetch from '统计概览'
    db = connect_db()
    cursor = db.cursor()
    entities.sort(key=lambda x:-x[u'startIndex'])
    type_entities= [i[u'type'] for i in entities]
    words = [i[u'entity'] for i in entities]
    # multiple entity / property

    multiple = False
    if st.find('和')+st.find('与')+st.find('分别') != 0:
        multiple = True
    res = []
    for item in entities:
        query_word = to_query(item[u'entity'])
        if u'院系所和公共教学单位' not in type_entities:
            cursor.execute("select object from relation where page='统计概览' and subject like '%s'" % query_word)
            res += cursor.fetchall()
            if not multiple:
                break
        if u'院系所和公共教学单位' not in type_entities or not res:
            departments = [to_query(i[u'entity']) for i in entities if i['type']==u'学校相关实体']
            l = jieba._lcut_for_search(st)
            for department in departments:
                for word in l:
                    word = to_query(word)
                    cursor.execute("select num,origin from relation where page='%s' and subject like '%s'" % (department,word))
                    ret = cursor.fetchall()
                    if not ret:
                        for word in l:
                            word = to_query(word)
                            cursor.execute("select num,origin from relation where (page='%s' or subject='%s') "
                                           "and (object like '%s' or predicate like '%s')" % department,department,word,word)
                            ret = cursor.fetchall()
                    res += ret
            if not multiple:
                break

    return res

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
    st = '计算机系有多少教授？'
    js = get_query(st)
    handler(st,js['intents'],js['entities'])