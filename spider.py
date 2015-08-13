#__author__ = 'v-waxun'
#__modify__ = 'v-guayin'
#coding=utf-8
import urllib2
import codecs
import re
import time
import os
import sys
import Queue
import thread
import threading
import signal
from tld import get_tld

def getFromHtml(html):
      #print html
     # f_0 = open('file1.html','w')
      #f_0.write(html)
      title = ""
      titleList = re.findall(titleC,html)
      if len(titleList) > 0:
          title = titleList[0]     
      for t in titleList:
          print(t)
          #u = t.decode('utf-8')
          #print u
      urlList = re.findall(urlC,html)
      x = 0
      urls = []
      for url in urlList:
          if isImageUrl(url) or isCssUrl(url):
              print("filter:" + url)
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
    def __init__(self,startUrl,maxPage):
        self.m_startUrl = startUrl
        self.m_maxPage = maxPage
        self.outFileCount = 0
        self.m_urlId= 0
        self.m_url2idMap = {}
        self.m_id2urlMap = {}  
        self.lock = threading.Lock()
        self.myqueue = Queue.Queue()
        self.is_sigint_up = False
        
    def scrawler2(self):
        
        while(not self.is_sigint_up):        
            url = self.myqueue.get()
            titleName = DSTDIR + str(self.m_url2idMap[url]) + '.title'
            htmlName = DSTDIR + str(self.m_url2idMap[url]) + '.html'
            html = ""
			
            try:
                html = getHtml(url)
                #print "###",html,"@@@"
            except:
                continue
            
            fileHtml = open(htmlName,'w')
            fileHtml.write(html)
            fileHtml.close()
            
            urls,title = getFromHtml(html)
            
            urlFile = open(titleName,'w')
            urlFile.write(title)
            urlFile.close()
            
            self.lock.acquire()
            
            for u in urls:
                if u not in self.m_url2idMap:
                    try:
                        if get_tld(u) == get_tld(self.m_startUrl):
                            self.m_urlId += 1
                            self.m_id2urlMap[self.m_urlId] = u
                            self.m_url2idMap[u] = self.m_urlId
                            self.myqueue.put(u)
                    except:
                        pass
            self.lock.release()
        
    def sigint_handler(self, signum, frame):
        self.is_sigint_up = True
        self.doSerialize()
        
    def start(self, thread_num):
        signal.signal(signal.SIGINT, self.sigint_handler)
        #self.scrawler(self.m_startUrl,1)
        self.myqueue.put(self.m_startUrl)
        self.m_urlId = 1
        self.m_id2urlMap[1] = self.m_startUrl
        self.m_url2idMap[self.m_startUrl] = 1
        threads = []
        for i in range(thread_num):
            t = threading.Thread(target = self.scrawler2,args=())
            t.setDaemon(True)
            threads.append(t)
            t.start()
        
        while True:
            alive = False
            for thread in threads:
                alive = alive or thread.isAlive()
            if not alive:
                break

        
    def doSerialize(self):
        serialFilePath = DSTDIR + "id2url.map"
        mapFile = open(serialFilePath,'w')
        for k in self.m_id2urlMap.keys():
            line = "%d\t%s\n"%(k,self.m_id2urlMap[k])
            mapFile.write(line)
        mapFile.close()
        print('serilization done in id2url.map')
             
def printUsage():
    print('''
    usage:  python spider.py startUrl maxPage
    example:python spider.py http://www.sina.com 3
    ''')
if __name__ == "__main__":
    dstPath = os.getcwd() + "\\" + SPIDER_OUT
    if not os.path.exists(dstPath):
        os.mkdir(dstPath)
    if len(sys.argv) != 3 :
        printUsage()
        sys.exit()
    startUrl = sys.argv[1]
    maxPage = int(sys.argv[2])
    print(startUrl,maxPage)
    #startUrl = "http://www.eastmoney.com/"
    #startUrl = "http://www.baidu.com/"
    #startUrl = "http://www.sina.com/"
    #maxDepth = 2
    spider = Spider(startUrl,maxPage)
    spider.start(maxPage)
    #to do serilize maps ...
