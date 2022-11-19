import requests
import re
import urllib.parse
import openpyxl
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


# 通过豆瓣ID找电影
def getMovieInfoByID(doubanId):
    info = {}
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}
    url = 'https://movie.douban.com/subject/'+doubanId
    data = requests.get(url, headers=header).text
    s = etree.HTML(data)
    # 给定url并用requests.get()方法来获取页面的text，用etree.HTML()
    info['title'] = ''.join(s.xpath('//*[@id="content"]/h1/span[1]/text()'))
    # info['originaltitle'] = ''  # .join(s.xpath('//*[@id="info"]/text()[4]'))# //*[@id="info"]/text()[4]
    info['year'] = (''.join(s.xpath('//*[@id="content"]/h1/span[2]/text()')))[1:5]
    # info['country'] = etree.tostring(s.xpath('//*[@id="info"]')[0])
    info['rating_value'] = ''.join(s.xpath('//*[@id="interest_sectl"]/div/div[2]/strong/text()'))
    info['rating_votes'] = ''.join(s.xpath('//*[@id="interest_sectl"]/div/div[2]/div/div[2]/a/span/text()'))
    info['poster_url'] = ''.join(s.xpath('//*[@id="mainpic"]/a/img/@src'))
    info['plot'] = ''.join(s.xpath('//*[@id="link-report-intra"]/span[1]/text()')).replace('                                　　', '    ')  # 简介
    # print('豆瓣信息:', info['title'], '评分:', info['rating_value'])
    return info


def run():
    savepath = '电影瓣瓣.xlsx'  # 数据存储位置
    options = Options()
    # options.add_argument("--headless")
    browser = webdriver.Chrome(executable_path="/chromedriver.exe", options=options)  # 浏览器驱动
    sleeptime = 1  # 浏览器打开等待加载的时间

    # 创建xls表格，并初始化表头+保存
    wb = openpyxl.Workbook()
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
    print('读取dytt.net最新电影列表共'+str(len(urlArr))+'条')
    # 进入电影天堂电影下载页面
    for link in urlArr:
        link = 'https://dytt8.net'+link
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
            print('电影天堂标题：' + mname)
        else:
            mname = ''
            print('在电影天堂未获取到电影标题,跳过执行下一条...')
            continue

        # 获取电影的磁力链接
        rsl = re.search('magnet(.*?)[^"]+', data2.text)
        if rsl:
            murl = rsl.group()
            print('电影天堂链接：' + murl[0:45]+'...')
        else:
            murl = ''
            print('在电影天堂未获取到电影链接。')

        # 根据取得的名字，查询豆瓣ID
        kw = urllib.parse.quote(mname)   # 需要格式化一下转换成网页能用的字符
        url = 'https://search.douban.com/movie/subject_search?search_text='+kw+'&cat=1002'
        # print(url)
        doubanID = "0"
        try:
            # 启动浏览器驱动模拟
            browser.get(url)
            browser.implicitly_wait(sleeptime)
            # 获取包含豆瓣ID的url
            idurl = browser.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div[1]/div[1]/div[1]/div/div/div[1]/a').get_attribute('href')
            doubanID = idurl.split("/")[4]
            print('豆瓣ID:'+doubanID)
            movieInfo = getMovieInfoByID(doubanID)
            # 如果抓取不到信息，尝试搜索结果中的第二个结果
            if movieInfo['title'] == '':
                idurl = browser.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div[1]/div[1]/div[3]/div/a').get_attribute('href')
                doubanID = idurl.split("/")[4]
                print('豆瓣ID(第二次尝试):'+doubanID)
                movieInfo = getMovieInfoByID(doubanID)
            # 如果2次都抓取不到豆瓣信息，则不再抓取
            if movieInfo['title'] == '':
                movieInfo['title'] = mname
            movieInfo['downloadurl'] = murl
            print('豆瓣信息:', movieInfo['title'], '评分:', movieInfo['rating_value'])
            ws.append([movieInfo['title'], movieInfo['year'], movieInfo['rating_value'], movieInfo['rating_votes'], movieInfo['plot'], movieInfo['poster_url'], movieInfo['downloadurl']])
            wb.save(savepath)
            print('保存本条电影信息成功。')
        except Exception as e:
            print('解析电影id时错误:', mname, '错误信息：')
            print(e)
        print('------------------------------------------------------------------------')

    browser.close()


run()
