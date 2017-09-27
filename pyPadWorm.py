# for monster data of puzzle and dragon 下载战友网图片和资料
# bug 多线程，最后更新列表的时候会有问题
import os
import sys
from queue import Queue
import re
import time
import threading
import urllib.request
import urllib.error
import bs4
import json
import lxml
sys.path.append(".")
import singlepage as single

#replace url to start your own download
url = "http://pad.skyozora.com/pets/"

MaxThread = 40
# list control
pagecount = 3950
start = pagecount
# group size
countstep = 50
DST_DIR = "dst"

print_lock = threading.Lock()
data_q = Queue()
textlist = []
teststack = []
allerrid = []
# latest one
topstack = 0

def inerrorlist(id):
    for istr in allerrid:
        if(istr == id):
            return True
    return False

def saveImg(imgUrl):
    time.sleep(0.1)
    with print_lock:
        monid = int(imgUrl.split('/')[-1])
        global pagecount
        global countstep
        global topstack
        global start
        ilist = int((monid-start) / countstep)
        print(ilist)
        print(monid)
        teststack[ilist] -= 1
        print(teststack[ilist])
        rtlist = single.getPage(imgUrl,DST_DIR)

        if(type(rtlist) == str):
            print(str(monid) + rtlist)
            if(not inerrorlist(monid)):
                filename = DST_DIR+"\\log.txt"
                single.check(filename)
                with open(filename,"a",encoding='utf-8') as logfile:
                    logfile.write("Error: "+ str(monid)+"\n")
        else:
            textlist[ilist].append(rtlist)
            if(monid > topstack):
                topstack = monid
                filename = DST_DIR + "\\log.txt"
                single.check(filename)
                with open(filename, "r", encoding='utf-8') as logfile:
                    lines = logfile.readlines()
                with open(filename, "w", encoding='utf-8') as logfile:
                    lines[0] = "Latest: " + str(topstack) + "\n"
                    logfile.writelines(lines)
            if (monid > pagecount):
                # print(pagecount, " less than", monid)
                pagecount += countstep
                simglist = []
                for i in range(pagecount, pagecount + countstep):
                    tmpurl = url + str(i)
                    data_q.put(tmpurl)
                for iimg in simglist:
                    data_q.put(iimg)
                simglist.clear()
                teststack.append(countstep)
                list = []
                textlist.append(list)
                print("update list. Top" + str(pagecount))
        if (teststack[ilist] == 0):
            print("save")
            textlist[ilist].sort(key=lambda monster: int(monster[0]))
            if(textlist[ilist] == []):
                print("List empty " + str(start+ilist*countstep))
                return
            name = textlist[ilist][0][0]
            filename = DST_DIR + "\\" + str(name).zfill(4) + ".txt"
            single.check(filename)
            with open(filename, "w", encoding='utf-8') as htmlfile:
                # id jp cn attr[] hp atk rcv type[] awake[] skill"" lskill""
                for ihtml in textlist[ilist]:
                    istr = str(ihtml[0]) + "\t" + ihtml[1] + "\t" + ihtml[2] + "\n"
                    for i in ihtml[3]:
                        istr = istr + i + "\t"
                    istr = istr + "\n" + str(ihtml[4]) + "\t" + str(ihtml[5]) + "\t" + str(ihtml[6]) + "\n"
                    for i in ihtml[7]:
                        istr = istr + i + "\t"
                    istr = istr + "\n"
                    for i in ihtml[8]:
                        istr = istr + i + "\t"
                    istr += "\n" + str(ihtml[9]) + "\n" + str(ihtml[10]) + "\n\n"
                    htmlfile.write(istr)
            textlist[ilist].clear()

def worker():
    while True:
        tmpUrl = data_q.get()
        saveImg(tmpUrl)
        data_q.task_done()

def main():
    for x in range(MaxThread):
        t = threading.Thread(target = worker)
        t.daemon = True
        t.start()
    start = time.time()
    filename = DST_DIR +"\\log.txt"
    single.check(filename)
    with open(filename,"w",encoding='utf-8') as logfile:
        logfile.write("Latest: "+str(topstack)+"\n")
#----------------------------------
    teststack.append(countstep)
    teststack.append(countstep)
    list1 = []
    list2 = []
    textlist.append(list1)
    textlist.append(list2)
    for i in range(pagecount,pagecount+countstep):
        tmpurl = url+str(i)
        data_q.put(tmpurl)

    data_q.join()
    print("entire job took:", time.time()-start)
    #print("errorid:\t",allerrid)

if __name__ == '__main__':
  main()
