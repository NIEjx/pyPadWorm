# for monster data of puzzle and dragon 下载战友网图片和资料
import os
from queue import Queue
import re
import time
import threading
import urllib.request
import urllib.error
import bs4
import lxml

#replace url to start your own download
url = "http://pad.skyozora.com/pets/"
typestr = ["龍","神","惡魔","機械",
           "平衡","攻擊","體力","回復",
           "進化用","能力覚醒用","強化合成用","売却用"]
MaxThread = 40
pagecount = 0
countstep = 100

dirname = os.getcwd()
print_lock = threading.Lock()
data_q = Queue()
textlist = []


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

# def saveImg(imgUrl):
#     time.sleep(0.05)
#     with print_lock:
#         # =========data set
#         monid = imgUrl.split('/')[-1]
#         monimg = ""
#         monjp = ""
#         moncn = ""
#         montype = []
#         monskill = ""
#         monlskill = ""
#         global pagecount
#         # =================
#         try:
#             raw = urllib.request.urlopen(imgUrl)
#             rawurl = raw.read()
#             raw.close()
#             # get info
#             soup = bs4.BeautifulSoup(rawurl, "lxml")
#             tmpimgaddr = soup.find("body").find_all("table")
#             for iaddr in tmpimgaddr:
#                 tmptable = iaddr.find_all("table")
#                 if (tmptable != []):
#                     for itable in tmptable:
#                         tmptag = itable.find("h3")
#                         if (tmptag != None):
#                             monimg = itable.find("img")['src']
#                             monjp = itable.find("h3").string
#                             moncn = itable.find("h2").string
#                         skill = itable.find("td", colspan="5")
#                         if (skill != None):
#                             monskill = skill
#                         lskill = itable.find("td", colspan="2")
#                         if (lskill != None):
#                             tlskil = lskill.find("span")
#                             if (tlskil == None):
#                                 monlskill = lskill
#             for istr in range(0, len(typestr)):
#                 type1 = soup.find_all("a", title=typestr[istr])
#                 if (type1 != []):
#                     montype.append(istr)
#
#             print(str(monid)+"done")
#             # print(monimg)
#             # print(monjp)
#             # print(moncn)
#             # print(monskill)
#             # print(monlskill)
#             # print("------------------")
#             # save img
#             with urllib.request.urlopen(monimg) as imghtml:
#                 rawimg = imghtml.read()
#             with open(str(monid).zfill(4)+".png",'wb') as file:
#                 file.write(rawimg)
#             # update list
#             print(pagecount, " less than", monid)
#             if (monid > pagecount ):
#                 print(pagecount," less than",monid)
#                 pagecount += countstep
#                 simglist = []
#                 for i in range(pagecount, pagecount + countstep):
#                     tmpurl = url + str(i)
#                     data_q.put(tmpurl)
#                 for iimg in simglist:
#                     data_q.put(iimg)
#                 simglist.clear()
#                 print("update list")
#
#         except:
#             print("error:", monid, " not exist")
#             pass
#
# def worker():
#     while True:
#         tmpUrl = data_q.get()
#         saveImg(tmpUrl)
#         data_q.task_done()

def main():

    # for x in range(MaxThread):
    #     t = threading.Thread(target = worker)
    #     t.daemon = True
    #     t.start()
    start = time.time()

    os.chdir(mkdir("monster"))
    pagecount = 0
    countstep = 100
#----------------------------------
    while(True):
        weldonecount = 0
        list = []
        for i in range(pagecount,pagecount+countstep):
            # =========data set
            monid = i
            monimg = ""
            monjp = ""
            moncn = ""
            montype = []
            monskill = ""
            monlskill = ""
            # =================
            imgUrl = url+str(i)
            try:
                raw = urllib.request.urlopen(imgUrl)
                rawurl = raw.read()

                raw.close()
                # get info
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

                if(monimg!=""):
                    print(str(monid)+"\tdone")
                else:
                    continue
                list.append(Monster(monid,monjp,moncn,montype,monskill,monlskill))
                # print(monimg)
                # print(monjp)
                # print(moncn)
                # print(monskill)
                # print(monlskill)
                # print("------------------")
                # save img
                with urllib.request.urlopen(monimg) as imghtml:
                    rawimg = imghtml.read()
                with open(str(monid).zfill(4)+".png",'wb') as file:
                    file.write(rawimg)
                # update list
                weldonecount +=1
            except:
                pass
        if(weldonecount > 0):
            pagecount+=countstep
            with open(str(pagecount)+".txt", "w", encoding='utf-8') as htmlfile:
                for ihtml in list:
                    istr = str(ihtml.id) + "\t" + ihtml.jpname +"\t"+ihtml.cnname+"\n"
                    for i in ihtml.type:
                        istr = istr + typestr[i]+"\t"
                    istr+="\n"+str(ihtml.skill)+"\n"+str(ihtml.lskill)+"\n"
                    htmlfile.write(istr)
            list.clear()
        else:
            break
    print("entire job took:", time.time()-start)

if __name__ == '__main__':
  main()

