import requests
import re
import time
from lxml import etree

limit = 200  # 限制查询的条数
savePath = 'D:/Github/hotine/dybb/index.html'


# 处理正则表达式匹配的结果，取出第一条，并清除第二个参数中的字符串
def parseReMatch(re, replaceStrArr):
    if re:
        str = re.group()
        for s in replaceStrArr:
            str = str.replace(s, '')
        return str
    else:
        return ''


def getMovieDownloadList():
    # 获取电影下载清单
    url = 'https://dytt8.net/index2.htm'
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}
    try:
        data = requests.get(url, headers=header)
    except Exception as e:
        print('解析电影网址失败:', url, '错误信息：')
        print(e)
        return
    data.encoding = 'gb2312'
    s = etree.HTML(data.text)
    urlArr = s.xpath('//*[@id="header"]/div/div[3]/div[2]/div[1]/div/div[2]/ul/a/@href')

    # 打开网页模板文件
    try:
        file = open(file='index_t.html', mode='r', encoding='utf-8')
    except Exception as e:
        print('加载html模板文件失败:', 'index_t.html', '错误信息：')
        print(e)
        return
    htmlTextMain = file.read()
    file.close()
    htmlMovieTemp = parseReMatch(re.search('<!---模板片段开始-->[\d\D]*<!---模板片段结束-->', htmlTextMain), ['<!---模板片段开始-->', '<!---模板片段结束-->'])
    htmlMovieContent = ''
    # print(fileContentMovieDiv)

    # 获取电影详细信息
    i = 0
    while i < limit:
        if i >= len(urlArr):
            break
        data = requests.get('https://dytt8.net/'+urlArr[i], header)
        data.encoding = 'gb2312'
        s = etree.HTML(data.text)
        # 电影名
        i_title = ''.join(s.xpath('//*[@id="header"]/div/div[3]/div[3]/div[1]/div[2]/div[1]/h1/font/text()'))
        i_title = parseReMatch(re.search('《(.*?)》', i_title), ['《', '》'])
        if len(i_title) == 0:
            i += 1
            continue
        # 年份
        i_year = parseReMatch(re.search('◎年　　代　[0-9]*', data.text), ['◎年　　代　'])
        # 国家
        i_country = parseReMatch(re.search('◎产　　地　.+(<br />◎类)', data.text), ['◎产　　地　', '<br />◎类', ' '])
        # 评分
        i_score = parseReMatch(re.search('◎豆瓣评分　.+?\(|◎豆瓣评分　.+?(from)|◎豆瓣评分　.+?(from)', data.text), ['◎', 'from', ' ', '　', '('])
        if len(i_score) < 2:
            i_score = parseReMatch(re.search('◎IMDb评分　.+?(from)', data.text), ['◎', 'from', ' ', '　'])
        i_score = parseReMatch(re.search('[0-9]+.[0-9]+/[0-9]*', i_score), [])
        if len(i_score) < 2:
            i_score = '暂无评分'
        # 类型
        i_type = parseReMatch(re.search('◎类　　别　.+(<br />◎语)', data.text), ['◎类　　别　', '<br />◎语', ' '])
        # 简介
        i_plot = parseReMatch(re.search('◎简　　介<br /><br />　　.+?(<br /><br /><)', data.text), ['◎简　　介<br /><br />　　', '<br /><br /><', '\n\n'])
        # 海报地址 <img border="0" src=".+?"
        i_posturl = parseReMatch(re.search('<img border="0" src=".+?"', data.text), ['<img border="0" src=', '"'])
        # 下载地址
        i_downloadurl = ''
        i_downloadurl_r = re.search('magnet(.*?)[^"]+', data.text)
        if i_downloadurl_r:
            i_downloadurl = i_downloadurl_r.group()
        i += 1
        print(i, ':', i_title, i_year, i_country, i_score, i_plot[0:100])
        print('---------------------------------------------------------------')
        divItem = htmlMovieTemp
        divItem = divItem.replace('#电影名#', i_title)
        divItem = divItem.replace('#年份#', i_year)
        divItem = divItem.replace('#国家#', i_country)
        divItem = divItem.replace('#评分#', i_score)
        divItem = divItem.replace('#类型#', i_type)
        divItem = divItem.replace('#简介#', i_plot[0:250]+'...')
        divItem = divItem.replace('#下载地址#', i_downloadurl)
        divItem = divItem.replace('#海报链接#', i_posturl)
        htmlMovieContent += divItem

    htmlTextMain = htmlTextMain.replace(htmlMovieTemp, htmlMovieContent)
    htmlTextMain = htmlTextMain.replace('#更新日期#', time.strftime('%Y年%m月%d日', time.localtime(time.time())))
    file = open(file=savePath, mode='w+', encoding='utf-8')
    file.write(htmlTextMain)
    file.close()
    print('电影瓣瓣爬虫执行完毕！')


getMovieDownloadList()
