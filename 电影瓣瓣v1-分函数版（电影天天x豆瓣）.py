# import time  # 这里导入时间模块，以免豆瓣封你IP
import requests
import re
import urllib.parse
import openpyxl
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# from time import sleep

# 请求网页的浏览器头
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}


# 通过豆瓣ID找电影
def getMovieInfoByID(doubanId):
    info = {}
    url = 'https://movie.douban.com/subject/'+doubanId
    data = requests.get(url, headers=header).text
    s = etree.HTML(data)
    # 给定url并用requests.get()方法来获取页面的text，用etree.HTML()
    # 来解析下载的页面数据“data”。
    info['title'] = ''.join(s.xpath('//*[@id="content"]/h1/span[1]/text()'))
    # info['originaltitle'] = ''  # .join(s.xpath('//*[@id="info"]/text()[4]'))# //*[@id="info"]/text()[4]
    info['year'] = (''.join(s.xpath('//*[@id="content"]/h1/span[2]/text()')))[1:5]
    # info['country'] = etree.tostring(s.xpath('//*[@id="info"]')[0])
    info['rating_value'] = ''.join(s.xpath('//*[@id="interest_sectl"]/div/div[2]/strong/text()'))
    info['rating_votes'] = ''.join(s.xpath('//*[@id="interest_sectl"]/div/div[2]/div/div[2]/a/span/text()'))
    info['poster_url'] = ''.join(s.xpath('//*[@id="mainpic"]/a/img/@src'))
    info['plot'] = ''.join(s.xpath('//*[@id="link-report-intra"]/span[1]/text()'))  # 简介
    print('从取豆瓣ID:', doubanId, '获取电影信息:', info['title'])
    if info['title'] != '':
        return info
    else:
        return None


# 通过电影名称找电影
def getMovieId(kw, sleeptime=1):
    kw = urllib.parse.quote(kw)   # 需要格式化一下转换成网页能用的字符
    url = 'https://search.douban.com/movie/subject_search?search_text='+kw+'&cat=1002'
    # print(url)
    options = Options()
    # options.add_argument("--headless")
    browser = webdriver.Chrome(executable_path="/chromedriver.exe", options=options)
    # browser = webdriver.PhantomJS()
    browser.get(url)
    browser.implicitly_wait(sleeptime)
    dbid = "0"
    if browser.page_source:
        #  s = etree.HTML(browser.page_source)
        #  browser.close()
        #  idurl = s.xpath('//*[@id="root"]/div/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/a/@href')[0]
        #  return idurl.split("/")[4]
        try:
            idurl = browser.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/a').get_attribute('href')
            dbid = idurl.split("/")[4]
        except Exception as e:
            print('解析电影id时错误:', e)
        # print("豆瓣ID:"+dbid)
        browser.close()
        print('从'+kw+"获取豆瓣ID:"+dbid)
        return dbid
    else:
        print("豆瓣ID:获取不到页面")
        browser.close()
        return 0


def getMovieByName(name, sleeptime=1):
    id = getMovieId(name, sleeptime)
    if id == 0:
        return None
    else:
        return getMovieInfoByID(id)


def getMovieDownloadList(savepath='moviesinfo.xlsx'):
    mlist = []
    wb = openpyxl.Workbook()  # 打开xls表格
    ws = wb.active
    ws.append(['片名', '年份', '评分', '投票数', '简介', '海报地址', '下载地址'])
    wb.save(savepath)
    # 进入电影天堂首页获得最新电影列表url
    url = 'https://dytt8.net/index2.htm'
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}
    data = requests.get(url, headers=header)
    data.encoding = 'gb2312'
    s = etree.HTML(data.text)
    urlArr = s.xpath('//*[@id="header"]/div/div[3]/div[2]/div[1]/div/div[2]/ul/a/@href')
    print('读取dytt.net最新电影列表'+str(len(urlArr))+'条')

    for link in urlArr:
        link = 'https://dytt8.net'+link
        # print(item)
        # 进入电影下载页，获得电影名称和下载链接
        data2 = requests.get(link, headers=header)
        data2.encoding = 'gb2312'
        s2 = etree.HTML(data2.text)
        # 获取电影标题
        mname = s2.xpath('//*[@id="header"]/div/div[3]/div[3]/div[1]/div[2]/div[1]/h1/font/text()')[0]
        # 获取标题中名称
        rsl = re.search('《(.*?)》', mname)
        if rsl:
            mname = rsl.group()
            mname = mname.replace('《', '').replace('》', '')
        else:
            mname = ''
            print('在电影天堂未获取到电影标题')
            continue

        # 获取电影的磁力链接
        rsl = re.search('magnet(.*?)[^"]+', data2.text)
        if rsl:
            murl = rsl.group()
        else:
            murl = ''

        # 豆瓣匹配电影信息
        db = getMovieByName(mname)
        if db:
            db['downloadurl'] = murl
        else:
            db = {'title': mname, 'downloadurl': murl,'year':'', 'rating_value':'','rating_votes':'','plot':'','poster_url':''}
        mlist.append(db)
        ws.append([db['title'], db['year'], db['rating_value'], db['rating_votes'], db['plot'], db['poster_url'], db['downloadurl']])
        print(db)
        wb.save(savepath)
        


# print(getMovieByName('V字仇杀队', 1))
db = getMovieDownloadList()

