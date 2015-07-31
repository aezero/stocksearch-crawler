#__author__ = 'v-waxun'
#coding=utf-8
import urllib2
import codecs
import re
import time
import os
import sys
def getFromHtml(html):
      #print html
     # f_0 = open('file1.html','w')
      #f_0.write(html)
      title = ""
      titleList = re.findall(titleC,html)
      if len(titleList) > 0:
          title = titleList[0]     
      for t in titleList:
          print t
          #u = t.decode('utf-8')
          #print u
      urlList = re.findall(urlC,html)
      x = 0
      urls = []
      for url in urlList:
          if isImageUrl(url) or isCssUrl(url):
              print "filter:" + url
          else:
              urls.append(url)
             #urllib.urlretrieve(imgurl,'%s.jpg' % x)
          x+=1
      #print urls
      return urls,title

def getHtml(url):
       page = urllib2.urlopen(url,timeout=5)
       html = page.read()
       return html
def isImageUrl(url):
       imgReg =  ".*(svg|bmp|gif|jpeg|png|jpg|css|js)$"
       regC = re.compile(imgReg)
       isMatch = regC.match(url)
       if isMatch != None:
           return True
       else:
           return False

def isCssUrl(url):
    return url.find('css') != -1
#url = "http://g1.dfcfw.com/g1/special/Apple.ico"
#print isImageUrl(url)


urlR = r'href="(http.*?)"'
urlC = re.compile(urlR)
titleReg ="<title>(.*)</title>"
titleC = re.compile(titleReg)
SPIDER_OUT = 'SpiderOut' 
DSTDIR = os.getcwd() + "\\" + SPIDER_OUT + "\\" 

class Spider():
    def __init__(self,startUrl,maxDepth):
        self.m_startUrl = startUrl
        self.m_maxDepth = maxDepth
        self.outFileCount = 0
        self.m_urlId= 0
        self.m_url2idMap = {}
        self.m_id2urlMap = {}  
    
    def scrawler(self,url,depth):
        if depth > self.m_maxDepth:
            return 

        if url in self.m_url2idMap.keys():
            return
        else:
            self.m_urlId += 1
            self.m_url2idMap[url] = self.m_urlId
            self.m_id2urlMap[self.m_urlId] = url
        print "visting url:" + url
        startTime = time.clock()
        
        titleName = DSTDIR + str(self.m_urlId)+'.title'
        htmlName = DSTDIR + str(self.m_urlId) + ".html"
        try:  #remote server close the connection
            html = getHtml(url)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            return
        fileHtml = open(htmlName,'w')
        fileHtml.write(html)
        
        urls,title = getFromHtml(html)
        print "visited %s time:%d"%(url,time.clock()-startTime)
    
        urlFile = open(titleName,'w')
        urlFile.write(title)

        for u in urls:
            self.scrawler(u,depth + 1)
    def start(self):
        self.scrawler(self.m_startUrl,1)
    def doSerialize(self):
        serialFilePath = DSTDIR + "id2url.map"
        mapFile = open(serialFilePath,'w')
        for k in self.m_id2urlMap.keys():
            line = "%d\t%s\n"%(k,self.m_id2urlMap[k])
            mapFile.write(line)
        mapFile.close()
        print 'serilization done in id2url.map'
             
def printUsage():
    print '''
    usage:  python spider.py startUrl maxDepth
    example:python spider.py http://www.sina.com 3
    '''
if __name__ == "__main__":
    dstPath = os.getcwd() + "\\" + SPIDER_OUT
    if os.path.exists(dstPath):
        os.remove(dstPath)
    os.mkdir(dstPath)
    if len(sys.argv) != 3 :
        printUsage()
        sys.exit()
    startUrl = sys.argv[1]
    maxDepth = int(sys.argv[2])
    print startUrl,maxDepth
    #startUrl = "http://www.eastmoney.com/"
    #startUrl = "http://www.baidu.com/"
    #startUrl = "http://www.sina.com/"
    #maxDepth = 2
    spider = Spider(startUrl,maxDepth)
    spider.start()
    spider.doSerialize()
    #to do serilize maps ...
