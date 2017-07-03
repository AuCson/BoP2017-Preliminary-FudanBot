# -*- coding: utf-8 -*-

Created on Sun Jul  2 16:07:35 2017
@author: lenovo

import pandas as pd  
import numpy as np

import pickle, time

from urllib import request 
from bs4 import BeautifulSoup as bs
import re       
import sys 
import string 


cookie="_ga=GA1.3.687925272.1488514763; amlbcookie=02; iPlanetDirectoryPro=LOGOUT"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36"

def OpenUrl( req ):
    t = 0
    soup = None
    while True:
        try:
            if t > 5:
                break 
            resq = request.urlopen( req, timeout = 0.5 )
            soup = bs( resq,"html.parser")
            break
        except:
            time.sleep(2)
            t += 1
            continue
    return soup

def LetterPages( url ):
    urlList = [ url, ]
    while True:
        req = request.Request( url )
        req.add_header( UA, cookie )
        soup = OpenUrl( req )
        if soup is None:
            break
        nextPageList = soup.select("body > div.wrapper > div > section > div > \
                                   div.small-12.large-10.columns.contents > div.row > div.small-12.large-8.columns > ul > li > span > a")
        page = nextPageList[-1]
        url =  "http://www.fudan.edu.cn" + page.get( "href" )
        if url in urlList:
            break
        urlList.append( url )

    return urlList
    
def EntityPage( url ):
    entityUrlList = []
    req = request.Request( url )
    req.add_header( UA, cookie )
    soup = OpenUrl( req )
    if soup is None:
        return 
    
    entityPageList = soup.select("#mainText > dl > div.entryTitle.row > div > h3 > a")
    #print( entityPageList )
    for page in entityPageList:
        url = page.get( "href" )
        entityUrlList.append( "http://www.fudan.edu.cn" + url )
        
    return entityUrlList

def EntityAttributes( entityUrl ):
 
    req = request.Request( entityUrl )
    req.add_header( UA, cookie )
    soup = OpenUrl( req )
    if soup is None:
        return 

    titleList = soup.select("#mainText > div.entryTitle > h3")
    sortList = soup.select("#mainText > div.entrySort > a")
    infoList = soup.select("#mainText > div.entryInfo")   
    summaryList = soup.select("#mainText > div.entrySummarys.row > div")     
    contentList = soup.select("#mainText > div.entryContent")
    dataDict = dict()
    for title, sort, info, summary, content in zip( titleList, sortList, infoList, summaryList, contentList):
        data = {
            'title':title.get_text(),
            'sort':sort.get_text(),
            'info':info.get_text().replace('\r','').replace('\n','').replace('\t',''),
            'summary':summary.get_text().replace("摘要:",'').replace("\xa0",''),
            "content:":content.get_text().replace('\u3000',' ').replace("\xa0",''),
        }
        dataDict[data['title']] = data
        
    return dataDict
  
def BasicWebData( url ):
    #time.sleep(3)
    urlList = LetterPages( url )
    if urlList is None or len( urlList ) == 0:
        return 
    if len( urlList ) > 0:
        print("对应检索词下的页面数目:",len(urlList))
        print(urlList)   
        for url in urlList:
            entityUrlList = EntityPage( url )
            #time.sleep(1)
            try:
                print("对应页面下的实体数目:",len(entityUrlList))
                print(entityUrlList)
            except:
                pass
            if entityUrlList is not None:
                for entityUrl in entityUrlList:
                    print("entityUrl",entityUrl)
                    EntityDict = EntityAttributes( entityUrl )
                    if EntityDict is not None:
                        with open("FudanWiki.pkl","ab") as f:
                            pickle.dump( EntityDict, f)
                        f.close()
       
def main():
    basicUrl = "http://www.fudan.edu.cn/entries/index/page:1/letter:"
    suffix = "/listType:alphabet"  
    for word in string.ascii_lowercase:
        print(word)
        url = basicUrl + word + suffix
        BasicWebData( url )

def mainv1():
    with open("FudanWiki.pkl","rb") as f:
        #content = f.read()
        #print(type(content))
        #print(content)
        #print("="*50)
        DataDict = dict()
        while True:
            try:
                Data = pickle.load( f )
                for k, v in Data.items():
                    DataDict[k] = v
            except:
                break
        print(len(DataDict))
        try:
            print(DataDict.get("姚一隽"))
        except:
            pass
    f.close()   
        
if __name__=="__main__":
    mainv1()
    
