import os
from queue import Queue
import re
import time
import threading
import urllib.request
import urllib.error
import bs4
import lxml

GetImgError = "get img error"
WriteImgError = "write img error"
Done = "done"
GetHtmlError = "get html error"
GetDataError = "get data error"

url = "http://pad.skyozora.com/pets/3929"
typestr = ["龍","神","惡魔","機械",
           "平衡","攻擊","體力","回復",
           "進化用","能力覚醒用","強化合成用","売却用"]
# less 30 [23:30]
modifystr = ["<img src=\"images/drops/Fire.png\" width=\"25\"/>",
             "<img src=\"images/drops/Water.png\" width=\"25\"/>",
             "<img src=\"images/drops/Wood.png\" width=\"25\"/>",
             "<img src=\"images/drops/Light.png\" width=\"25\"/>",
             "<img src=\"images/drops/Dark.png\" width=\"25\"/>",
             "<img src=\"images/drops/Heart.png\" width=\"25\"/>",
             "<img src=\"images/drops/Fire+.png\" width=\"25\"/>",
             "<img src=\"images/drops/Water+.png\" width=\"25\"/>",
             "<img src=\"images/drops/Wood+.png\" width=\"25\"/>",
             "<img src=\"images/drops/Light+.png\" width=\"25\"/>",
             "<img src=\"images/drops/Dark+.png\" width=\"25\"/>",
             "<img src=\"images/drops/Heart+.png\" width=\"25\"/>",
             "<img src=\"images/drops/Dead.png\" width=\"25\"/>",
             "<img src=\"images/drops/Poison.png\" width=\"25\"/>",
             "<img src=\"images/drops/Poison+.png\" width=\"25\"/>",
             "<img src=\"images/change.gif\"/>"]
dststr = ["火珠","水珠","木珠","光珠","暗珠","回复珠",
          "火加珠","水加珠","木加珠","光加珠","暗加珠","回复加珠",
          "废珠","毒珠","猛毒珠","转"]
attrstr = ["火","水","木","光","暗"]
# id jp cn attr[] hp atk rcv type[] awake[] skill"" lskill""


def modify(soupstr):
    for i in range(0,len(modifystr)):
        # print(soupstr[23:30])
        # print(modifystr[i][23:30])
        if(soupstr[23:30] == modifystr[i][23:30]):
            return dststr[i]
    return soupstr

def mkdir(path):
    try:
        os.makedirs(path)
    except:
        pass
    return path

def check(filename):
    tdir, file = os.path.split(filename)
    if (os.path.exists(tdir) == False):
        #print(tdir)
        mkdir(tdir)

def saveImg(imgUrl,id,dir):
    try:
        with urllib.request.urlopen(imgUrl) as imghtml:
            rawimg = imghtml.read()
    except:
        return GetImgError

    imgname = dir + "\\head\\" + str(id).zfill(4) + ".png"
    check(imgname)

    try:
        with open(imgname, 'wb') as file:
            file.write(rawimg)
    except:
        return WriteImgError
    return Done

def getPage(url,dir):
    # for i in modifystr:
    #     print(i[23:30])
    monid = url.split('/')[-1]
    try:
        raw = urllib.request.urlopen(url, timeout=30)
        rawurl = raw.read()
    except:
        return GetHtmlError
    try:
        # get info
        #print("start soup")
        soup = bs4.BeautifulSoup(rawurl, "lxml")
        filename = dir +"\\html\\" +str(monid).zfill(4) +".html"
        check(filename)
        with open(filename,"w",encoding='utf-8') as htmlfile:
            htmlfile.write(str(soup))
        tmptable = soup.find("body").find_all("table")[2].find_all("table")

        # get img
        tagtable = tmptable[1].find_all("table")[0]
        tagimg = tagtable.find("img")
        monimg = tagimg['src']
        rtcode = saveImg(monimg,monid,dir)
        if(rtcode == GetImgError or rtcode == WriteImgError):
            return GetImgError

        # get jp name cn name
        monjp = tagtable.find("h3").string
        moncn = tagtable.find("h2").string
        # get attr
        monattr = []
        tagattr = tmptable[1].find_all("td")[3]
        for istr in attrstr:
            if (re.findall("主屬性:"+istr, str(tagattr)) != []):
                monattr.append(istr)
                break
        for istr in attrstr:
            if (re.findall("副屬性:" + istr, str(tagattr)) != []):
                monattr.append(istr)
                break
        # get type
        montype = []
        tagtype = tmptable[1].find_all("td")[4]
        for istr in range(0, len(typestr)):
            type1 = tagtype.find_all("a", title=typestr[istr])
            if (type1 != []):
                montype.append(typestr[istr])
        # get atk hp rcv
        numtable = len(tmptable)
        count = 0
        for i in range(0,numtable):
            if(re.findall("最大", str(tmptable[i]))!=[]):
                #print(tmptable[i])
                #tmptable[i]
                #print(i,count)
                break
            count += 1
        if(count == numtable):
            return GetDataError
        tagdata = tmptable[count].find_all('table')[1].find_all('td')
        monhp = int(tagdata[1].text[4:])
        monatk = int(tagdata[2].text[5:])
        monrcv = int(tagdata[3].text[5:])
        # get skill
        for i in range(count,numtable):
            if(re.findall("主動技能", str(tmptable[i]))!=[]):
                break
            count += 1
        if(count == numtable):
            return GetDataError
        skill = tmptable[count].find_all("tr")[1].find("td").contents
        monskill = ""
        for i in skill:
            tmpstr = str(i)
            if(len(str(i))>29):
                tmpstr = modify(str(i))
            monskill += tmpstr
        # get awake lskill
        for i in range(count,numtable):
            if(re.findall("隊長技能", str(tmptable[i]))!=[]):
                break
            count += 1
        if(count == numtable):
            return GetDataError
        monlskill = tmptable[count].find_all("tr")[1].find("td").text
        monawake = []
        tmpawake = re.findall("【([\S]+)】", str(tmptable[count-1]))
        for i in tmpawake:
            monawake.append(i)
    except:
        return GetDataError
    rtlist = []
    rtlist.append(monid)
    rtlist.append(monjp)
    rtlist.append(moncn)
    rtlist.append(monattr)
    rtlist.append(monhp)
    rtlist.append(monatk)
    rtlist.append(monrcv)
    rtlist.append(montype)
    rtlist.append(monawake)
    rtlist.append(monskill)
    rtlist.append(monlskill)
    # id jp cn attr[] hp atk rcv type[] awake[] skill"" lskill""
    return rtlist

def main():
    ihtml = getPage(url,"_dst")
    if(type(ihtml)!=str):
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
        print(istr)

if __name__ == '__main__':
  main()