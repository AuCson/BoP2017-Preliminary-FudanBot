# coding=utf-8
from __future__ import print_function

def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
        return True
    else:
        return False

class Sematic_tree:
    def __init__(self):
        self.root = self.Node()
        self.s = ""
        self.quote_ref = {}
        self.flatten = []
        self.ner_dict = {}
    class Node:
        def __init__(self):
            self.tag = ''
            self.word = ''
            self.par = 0
            self.child = []
            self.depth = 0

    def preprocess_symb_pair(self):
        i = 0
        ts = []
        self.s = self.s.decode('utf-8')
        while i < len(self.s):
            ts.append(self.s[i])
            if self.s[i] == u'“':
                lcnt = 0
                rcnt = 0
                j = i
                while self.s[j] != u'”' and j < len(self.s):
                    if self.s[j] == u'(':
                        lcnt +=1
                    elif self.s[j] == u')':
                        rcnt += 1
                    j += 1
                if lcnt == rcnt:
                    k = len(ts) - 1
                    while ts[k]!= u'U':
                        del ts[k]
                        k-=1
                    ts[k-1] = u'N'
                    ts[k] = u'P'
                    ts.append(u' ')
                    while i<= j and i < len(self.s):
                        if self.s[i] != u'(' and self.s[i] != u')' and not self.s[i].isspace() and not is_alphabet(self.s[i]):
                            ts.append(self.s[i])
                        i+=1
                    i = j
            i+=1
        ts = [i.encode('utf-8') for i in ts]
        self.s = ''.join(ts)

    def preprocess_quote(self):
        self.preprocess_symb_pair()
        stack = []
        i = 0
        while i < len(self.s):
            if self.s[i] == '(':
                stack.append(i)
            elif self.s[i] == ')':
                l = stack[-1]
                stack.pop()
                self.quote_ref[l] = i
            i += 1

    def build_tree(self, start_pos,depth = 0):
        n = self.Node()
        n.depth = depth
        i = start_pos + 1
        # ignore blanks
        while str.isspace(self.s[i]):
            i += 1
        # get the tag of the node
        c = i
        while not (str.isspace(self.s[i]) or self.s[i] in ('(',')')):
            i += 1
        n.tag = self.s[c:i]
        # recurrently build the tree
        try:
            r = self.quote_ref[start_pos]
        except KeyError:
            print (self.quote_ref)
            print (self.s)
            r = 0
        while i < r:
            while str.isspace(self.s[i]):
                i += 1
            if self.s[i] != '(':
                # it is leaf
                n.word = self.s[i:r]
                break
            new_n = self.build_tree(i,depth+1)
            n.child.append(new_n)
            i = self.quote_ref[i] + 1
        return n

    def build_tree_from_root(self):
        self.preprocess_quote()
        self.root = self.build_tree(min(self.quote_ref.keys()),depth=0)

    def do_flatten(self,node,res):
        res.append(node)
        for child in node.child:
            self.do_flatten(child,res)

    def find_tag(self,tag,root='root'):
        if root == None:
            return []
        if root == 'root':
            root = self.root
        flatten = []
        self.do_flatten(root,flatten)
        res = []
        depth_lock = None
        for node in flatten:
            if depth_lock and node.depth > depth_lock:
                continue
            else:
               depth_lock = None
            if (type(tag) is list and node.tag in tag) or node.tag == tag:
                res.append(node)
                depth_lock = node.depth
        return res

    def find_nearest_tag(self,node,tag,backward = True,punct = True,consecutive = False):
        if not self.flatten:
            self.do_flatten(self.root,self.flatten)
        idx = -1
        for i,n in enumerate(self.flatten):
            if node == n:
                idx = i
                break
        if idx == -1:
            return None
        res = []
        depth_lock = None
        while idx >= 0 and idx < len(self.flatten):
            #if not depth_lock or self.flatten[idx].depth <= depth_lock:
            if (type(tag) is list and self.flatten[idx].tag in tag) or self.flatten[idx].tag == tag:
                if backward:
                    res.insert(0,self.flatten[idx])
                else:
                    res.append(self.flatten[idx])
                if not consecutive:
                    break
                depth_lock = self.flatten[idx].depth
            else:
                if self.flatten[idx].tag == 'PU' and self.flatten[idx].word != '、' and punct:
                    break
                elif consecutive and res and self.flatten[idx].word != '、':
                    break
            if backward:
                idx -= 1
            else:
                idx += 1
        if not consecutive:
            if not res:
                return None
            return res[0]
        else:
            return res

    def find_all_leaf_word(self,node,res):
        if node.word != '':
            res.append(node.word)
        for child in node.child:
            self.find_all_leaf_word(child,res)

    def get_content_recur(self,node):
        if node == None:
            return None
        if type(node) == list:
            s = ''
            for item in node:
                res = []
                self.find_all_leaf_word(item,res)
                s += ''.join(res)
            return s
        else:
            res = []
            self.find_all_leaf_word(node,res)
            return ''.join(res)

    def find_nearest_ner(self,node,ner,backward = True,punct = True,consecutive = False):
        if not self.flatten:
            self.do_flatten(self.root,self.flatten)
        idx = -1
        for i,n in enumerate(self.flatten):
            if node == n:
                idx = i
                break
        if idx == -1:
            return []

        ret = []

        while idx >= 0 and idx < len(self.flatten):
            if self.ner_dict.get(self.flatten[idx].word,None) in [ner,'MISC']:
                if backward:
                    ret.insert(0,self.flatten[idx])
                else:
                    ret.append(self.flatten[idx])
                if consecutive == False:
                    break
            else:
                if self.flatten[idx].tag == 'PU' and self.flatten[idx].word != '、' and punct:
                    break
                # must be consecutive ner
                elif consecutive and ret and self.flatten[idx].word != '、':
                    break
            if backward:
                idx -= 1
            else:
                idx += 1
        if not consecutive:
            if not ret:
                return None
            else:
                return ret[0].word
        else:
            return ''.join(node.word for node in ret)