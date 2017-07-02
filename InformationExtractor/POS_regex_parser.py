# coding=utf-8
from __future__ import print_function
import xml.etree.cElementTree as ET
from sematic_tree import Sematic_tree
import csv

class POS_regex_parser:
    class Relation:
        def __init__(self):
            self.origin_sentence = ''
            self.subject = ''
            self.object = ''
            self.predicate = ''
            self.ners = None

    def __init__(self):
        self.xml_file = None
        self.relation_all = []
        self.file_name = ''

    def load_parsed_xml(self,file_name):
        self.file_name = file_name
        self.xml_file = ET.parse('res/xml/'+file_name).getroot()
        self.root = self.xml_file[0][0]

    def get_ner_dict(self,st):
        ner_dict = {}
        for token in st[0]:
            ner_dict[token.findtext('word').encode('utf-8')] = token.findtext('NER').encode('utf-8')
        return ner_dict

    def get_ner_relation(self,vp_node,tree):
        # time ner. Only seach backwardly.
        time_ner = tree.find_nearest_ner(vp_node,'DATE',backward=True,punct=False,consecutive=True)
        if not time_ner:
            time_ner = tree.find_nearest_ner(vp_node, 'DATE', backward=False, punct=True, consecutive=True)
        if not time_ner:
            time_ner = tree.get_content_recur(tree.find_nearest_tag(vp_node,'NT',backward=True,punct=False))
        org_ner = tree.find_nearest_ner(vp_node,'ORGANIZATION',backward=True,punct=True,consecutive=True)
        person_ner = tree.find_nearest_ner(vp_node,'PERSON',backward=True,punct=True,consecutive=True)
        number_ner = tree.find_nearest_ner(vp_node,'NUMBER',backward=False,punct=True,consecutive=True)
        if not number_ner:
            number_ner = tree.find_nearest_ner(vp_node,'PERCENT',backward=False,punct=True,consecutive=True)
        if not number_ner:
            number_ner = tree.find_nearest_ner(vp_node,'NUMBER', backward=True, punct=True, consecutive=True)
        if not number_ner:
            number_ner = tree.find_nearest_ner(vp_node, 'PERCENT', backward=True, punct=True, consecutive=True)
        return {'time':time_ner,'org':org_ner,'person':person_ner,'number':number_ner}

    def process_sentence(self,st):

        tree = Sematic_tree()
        tree.s = st.findtext('parse').encode('utf-8')
        tree.ner_dict = self.get_ner_dict(st)
        try:
            tree.build_tree_from_root()
        except Exception:
            print ('tree error')

        relation_list = []
        subj_list = []
        pred_list = []
        obj_list = []
        ner_list = []

        # step 1, find all the VP from the sentence
        VP_list = tree.find_tag('VP')

        # step 2, find out the subjects and the objects, search backwardly and forwardly
        first_np = None
        for vp in VP_list:
            # if subject is None, previous subject is used
            nearest_np_b = tree.find_nearest_tag(vp,'NP',backward=True,punct = True,consecutive=True)
            if not nearest_np_b and first_np:
                nearest_np_b = first_np
            if not first_np:
                first_np = nearest_np_b
            #if tree.find_tag('NN',root = nearest_np_b):
            subj = nearest_np_b
            #else:
            #    subj = None
            # find detailed predicates
            vv_list = tree.find_tag(['VRD','VV','VE'],root=vp)
            if not vv_list:
                qp_list = tree.find_tag('QP',root=vp)
                vp_phrase = tree.get_content_recur(vp)
                if qp_list:
                    qp_phrase = tree.get_content_recur(qp_list[0])
                    if qp_phrase == '19个':
                        a = 1
                    sidx = vp_phrase.find(qp_phrase)
                    if sidx != -1:
                        t_vp_phrase = vp_phrase[0:sidx] + vp_phrase[sidx+len(qp_phrase):]
                        if len(t_vp_phrase) != 0:
                            vp_phrase = t_vp_phrase
                subj_list.append(tree.get_content_recur(subj))
                pred_list.append(vp_phrase)
                obj_list.append(None)
                ner_list.append(self.get_ner_relation(vp,tree))
            else:
                for vv in vv_list:
                    if tree.get_content_recur(vv):
                        a = 1
                    nearest_np_f = tree.find_nearest_tag(vv, ['NP', 'IP', 'PP'], backward=False, punct=False,
                                                         consecutive=True)
                    subj_list.append(tree.get_content_recur(subj))
                    pred_list.append(tree.get_content_recur(vv))
                    obj_list.append(tree.get_content_recur(nearest_np_f))
                    ner_list.append(self.get_ner_relation(vv, tree))

        # generate relation tuples
        for idx,pred in enumerate(pred_list):
            r = self.Relation()
            r.subject = subj_list[idx]
            r.object = obj_list[idx]
            r.predicate = pred
            r.ners = ner_list[idx]
            relation_list.append(r)
        return relation_list

    def process(self):

        for st in self.root:
            relation_list = self.process_sentence(st)
            self.relation_all.append(relation_list)
        print ('complete')
        self.output()

    def output(self):
        f = open('res/ie/' + self.file_name.split('.')[0] + '.csv','wb')
        writer = csv.writer(f, quotechar='"')
        for relation_list in self.relation_all:
            for relation in relation_list:
                writer.writerow([relation.subject,relation.predicate,relation.object,
                                 relation.ners['time'],relation.ners['org'],relation.ners['person'],relation.ners['number']])
        f.close()



p = POS_regex_parser()
p.load_parsed_xml('test2.txt.xml')
p.process()





