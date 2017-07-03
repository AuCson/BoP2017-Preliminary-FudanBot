import pickle

with open('FudanWiki.pkl','rb') as f:
    DataDict = {}
    while True:
        try:
            Data = pickle.load( f )
            for k, v in Data.items():
                 DataDict[k] = v
        except Exception:
            break
    print(len(DataDict))
    pickle.dump(DataDict,open('FudanWiki_py2.pkl','wb'),protocol=2)
