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

#replace url to start your own download
url = "http://pad.skyozora.com/pets/"
typestr = ["龍","神","惡魔","機械",
           "平衡","攻擊","體力","回復",
           "進化用","能力覚醒用","強化合成用","売却用"]
MaxThread = 40
pagecount = 0
countstep = 40

dirname = os.getcwd()
print_lock = threading.Lock()
data_q = Queue()
textlist = []
teststack = []
allerrid = []
topstack = 0

class Monster:
    id = 0
    jpname = ""
    cnname = ""
    type = []
    skill = ""
    lskill = ""
    def __init__(self,id,jpname,cnname,type,skill,lskill):
        self.id = id
        self.jpname = jpname
        self.cnname = cnname
        self.type = type
        self.skill = skill
        self.lskill = lskill

def mkdir(path):
    tmppath = os.getcwd()+"\\"+path
    try:
        os.makedirs(tmppath)
    except:
        print("DIR exist!")

    return tmppath

def inerrorlist(id):
    for istr in allerrid:
        if(istr == id):
            return True
    return False

def saveImg(imgUrl):
    time.sleep(0.1)
    with print_lock:
        # =========data set
        monid = int(imgUrl.split('/')[-1])
        monimg = ""
        monjp = ""
        moncn = ""
        montype = []
        monskill = ""
        monlskill = ""
        global pagecount
        global countstep
        ilist = int(monid / countstep)
        teststack[ilist]-=1
        # =================
        try:
            print("get page\t",monid)
            raw = urllib.request.urlopen(imgUrl,timeout=30)
            rawurl = raw.read()
            raw.close()
            # get info
            print("start soup")
            soup = bs4.BeautifulSoup(rawurl, "lxml")
            tmpimgaddr = soup.find("body").find_all("table")
            for iaddr in tmpimgaddr:
                tmptable = iaddr.find_all("table")
                if (tmptable != []):
                    for itable in tmptable:
                        tmptag = itable.find("h3")
                        if (tmptag != None):
                            monimg = itable.find("img")['src']
                            monjp = itable.find("h3").string
                            moncn = itable.find("h2").string
                        skill = itable.find("td", colspan="5")
                        if (skill != None):
                            monskill = skill
                        lskill = itable.find("td", colspan="2")
                        if (lskill != None):
                            tlskil = lskill.find("span")
                            if (tlskil == None):
                                monlskill = lskill
            for istr in range(0, len(typestr)):
                type1 = soup.find_all("a", title=typestr[istr])
                if (type1 != []):
                    montype.append(istr)
            print("data scan done")
            if( monimg == ""):
                return False
            print(str(monid) + "\tdone")
            textlist[ilist].append(Monster(monid, monjp, moncn, montype, monskill, monlskill))
            if(teststack[ilist] ==0):
                textlist[ilist].sort(key=lambda monster: monster.id)
                name = textlist[ilist][0].id
                with open(str(name).zfill(4) + ".txt", "w", encoding='utf-8') as htmlfile:
                    for ihtml in textlist[ilist]:
                        istr = str(ihtml.id) + "\t" + ihtml.jpname + "\t" + ihtml.cnname + "\n"
                        for i in ihtml.type:
                            istr = istr + typestr[i] + "\t"
                        istr += "\n" + str(ihtml.skill) + "\n" + str(ihtml.lskill) + "\n\n"
                        htmlfile.write(istr)
                textlist[ilist].clear()
            # print(monimg)
            # print(monjp)
            # print(moncn)
            # print(monskill)
            # print(monlskill)
            # print("------------------")
            # save img
            print("svaing\t" + monimg)
            with urllib.request.urlopen(monimg) as imghtml:
                rawimg = imghtml.read()
            with open(str(monid).zfill(4)+".png",'wb') as file:
                file.write(rawimg)
            # update list
            if(pagecount<300):
                if (monid > pagecount):
                    #print(pagecount, " less than", monid)
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
                    print("update list")

        except OSError as err:
            print("OS error: {0}".format(err))
            # print(str(err.args)+"\n"+str(err.errno))
            #print("error:", monid, " not exist")
            if(inerrorlist(monid)==False):
                if(err.errno == 10054):
                    tmpurl = url + str(monid)
                    data_q.put(tmpurl)
                    ilist = int(monid / countstep)
                    print(ilist,"\t",len(teststack))
                    teststack[ilist] += 1
                elif(err.args=="time out"):
                    tmpurl = url + str(monid)
                    data_q.put(tmpurl)
                    ilist = int(monid / countstep)
                    teststack[ilist] += 1
            allerrid.append(monid)
            pass

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

    os.chdir(mkdir("monster"))
#----------------------------------
    for i in range(pagecount,pagecount+countstep):
        tmpurl = url+str(i)
        data_q.put(tmpurl)
    teststack.append(countstep)
    list = []
    textlist.append(list)

    data_q.join()
    print("entire job took:", time.time()-start)
    print("errorid:\t",allerrid)

if __name__ == '__main__':
  main()

