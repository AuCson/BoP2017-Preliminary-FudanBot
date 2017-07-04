import os
def greg_csv():
    root_dir = 'res/ie/'
    wf = open('res/ie.csv','w')
    for root, dirs, files in os.walk(root_dir):
        for fn in files:
            if fn.endswith('.csv'):
                 f = open(root_dir+fn)
                 wf.write(f.read())
                 f.close()
    wf.close()

if __name__ == '__main__':
    greg_csv()