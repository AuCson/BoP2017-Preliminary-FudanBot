# coding=utf-8
from POS_regex_parser import Relation
from wiki_loader import output
def contact_loader(contact_file):
    f = open(contact_file,'r')
    entity = None
    relations = []
    for line in f.readlines():
        line = line.strip()
        if not line:
            continue
        if '：' in line:
            l = line.split('：')
            if len(l) == 2:
                r = Relation(page=entity,subject=l[0],predicate='是',object=l[1])
                relations.append(r)
        elif len(line.split(' ')) == 2:
            l = line.split(' ')
            r = Relation(page=entity, subject=l[0], predicate='是', object=l[1])
            relations.append(r)
        else:
            entity = line
    f.close()
    return relations

if __name__ == '__main__':
    r = contact_loader(u'res/raw/电话黄页.txt')
    output(r,dest=u'res/ie/电话黄页.csv')
