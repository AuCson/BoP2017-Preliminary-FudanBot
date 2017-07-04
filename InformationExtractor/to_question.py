# coding=utf-8
def to_question_beta():
    f = open('res/ie2.csv')
    cnt = 0
    qa_pair = []
    for line in f.readlines():
        line = line.split(',')
        #print line
        wl = ''
        try:
            page,subject,predicate,object,time,org,person,num,origin = line[0],line[1],line[2],line[3],line[4],line[5],line[6],line[7],line[8]
        except Exception:
            continue
        if page != subject:
            wl += page+subject + predicate
        else:
            wl += page + predicate
        if time:
            qa = wl + subject + '是什么时候？' + '\t' + time + '\n'
            qa_pair.append(qa)
            cnt += 1
        if num:
            qa = wl + subject + '是多少？' + '\t' + num + '\n'
            qa_pair.append(qa)
            cnt += 1
        if object:
            qa = wl + '什么？' + '\t' + object + '\n'
            qa_pair.append(qa)
            cnt += 1
        if cnt > 5000:
            break


    wf = open('res/qa_test.txt','w')
    wf.writelines(qa_pair)
    wf.close()

if __name__ == '__main__':
    to_question_beta()
