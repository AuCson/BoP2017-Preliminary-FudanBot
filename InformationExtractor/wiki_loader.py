# coding=utf-8
import pickle
import re
import urllib,urllib2
import copy,csv
from POS_regex_parser import POS_regex_parser,Relation,parse_request

def to_files():
    f = open('res/FudanWiki_py2.pkl','rb')
    wiki = pickle.load(f)
    print 1
    wf = open('res/wiki_long_content.txt','w')
    for key,item in wiki.items():
        wf.write(re.sub(r'&nbsp([0-9]*);','\g<1>',item.get(u'content',u'').encode('utf-8')).strip('\n')+'\n')
        wf.write(re.sub(r'&nbsp([0-9]*);','\g<1>',item.get(u'summary',u'').encode('utf-8')).strip('\n')+'\n')
    wf.close()
    f.close()

def WiKi_infromation_extract():
    wiki = pickle.load(open('res/FudanWiki_py2.pkl','rb'))
    print 1
    relation_all = []
    for key,item in wiki.items():
        res = extract_single(key,item)
        relation_all += res
    output(relation_all)

def output(relation_all):
    f = open('res/ie/wiki.csv','wb')
    writer = csv.writer(f, quotechar='"')
    for relation in relation_all:
        writer.writerow([relation.page,relation.subject,relation.predicate,relation.object,
                         relation.ners.get('time',''),relation.ners.get('org',''),relation.ners.get('person','')
                            ,relation.ners.get('number',''),relation.origin_sentence])

    f.close()

def is_predefined_property(s):
    pre_defined_property = ['类型', '名称', '时间','院系', '简介', '研究方向', '所授课程', '联系方式','网址','门类']
    for prop in pre_defined_property:
        if s.find(prop)!=-1:
            return True
    return False

def parse_property(lines,default_relation):
    relations = []
    predicate = '属性'
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if '：' in line:
            p = line.split('：')
            if len(p) == 2:
                r = copy.deepcopy(default_relation)
                r.predicate = p[0]
                r.object = p[1]
                relations.append(r)
                predicate = r.predicate
        elif '。' in line:
            parser = POS_regex_parser()
            parser.file_name = default_relation.page
            xml = parse_request(line)
            parser.load_xml_from_text(xml)
            res = parser.process()
            for item in res:
                if item:
                    relations += item
            predicate = '属性'
        elif is_predefined_property(line):
            predicate = line
        else:
            r = copy.deepcopy(default_relation)
            r.predicate = predicate
            r.object = line
            relations.append(r)

    return relations

def extract_single(entity,prop):
    relations = []
    sort = prop.get(u'sort:',u'').encode('utf-8')
    r = Relation(page=entity.encode('utf-8'),subject=entity.encode('utf-8'),predicate='类型',object=sort)
    relations.append(r)
    content = prop.get(u'content:',u'').encode('utf-8')
    lines = content.split('\r\n')
    default_relation = Relation(page=entity.encode('utf-8'),subject=entity.encode('utf-8'))
    res = parse_property(lines,default_relation)
    relations += res
    summary = prop.get(u'summary',u'').encode('utf-8')
    r = Relation(page=entity.encode('utf-8'), subject=entity.encode('utf-8'), predicate='简介', object=summary)
    relations.append(r)
    return relations

