from urllib import request
from bs4 import BeautifulSoup
import json
import tkinter as tk

window = tk.Tk()
window.title('BookCrawler')
window.geometry('500x260')
d=tk.Text(bg='lightgray',font=('Song', 10),width=70,height=7)

def download(inputUrl):
    head = {}
    head['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12H143'
    # 先获取目录页
    try:
        catalogUrl = inputUrl  # 'https://book.qidian.com/info/2083259#Catalog'
    except inputUrl=='':
        return
    try:
        catalogRes = request.urlopen(request.Request(url=catalogUrl, headers=head))
    except:
        return
    catalogHtml = catalogRes.read().decode('utf-8', 'ignore')
    catalogText = BeautifulSoup(catalogHtml, 'lxml')
    # 在目录页中查找章节连接
    texts = catalogText.find_all(class_='volume-wrap')
    # print(texts)
    if str(texts) == '[]':
        # 没有获取到目录，按老版本html处理
        # 先获取目录页
        # bookid
        bookid = catalogUrl[29:-8]
        # print(bookid)
        catalogUrl = 'https://book.qidian.com/ajax/book/category?_csrfToken=&bookId=' + bookid
        catalogRes = request.urlopen(request.Request(url=catalogUrl, headers=head))
        catalogHtml1 = catalogRes.read().decode('utf-8', 'ignore')
        catalogText1 = BeautifulSoup(catalogHtml1, 'lxml')
        jsonData = json.loads(catalogHtml1)
        jsonData = jsonData['data']['vs']
        jsonDump = json.dumps(jsonData)
        blockNum = len(jsonData)
        # print(len(jsonData),'blocks')

        # 创建文件，获取书名
        filenameHtml = catalogText.find_all('div', class_='book-information cf')
        tempText = BeautifulSoup(str(filenameHtml), 'lxml')
        print(tempText.em.text)
        temps = '书籍名：' + tempText.em.text + '\n'
        d.insert('1.0', temps)
        d.update()
        filename = tempText.em.text + '.txt'
        file = open(filename, 'w', encoding='utf-8')
        numChapter = 0
        progress = 0
        # 获取章节总数
        for tempNum in range(blockNum):
            numChapter += len(jsonData[tempNum]['cs'])
        # 章节数量
        print('章节数量：', numChapter)
        temps = '章节数量：' + str(numChapter) + '\n'
        d.insert('1.0', temps)
        d.update()
        # 在目录页中查找章节连接
        # 遍历，一项一项获取
        for tempNum in range(blockNum):
            # numChapter += len(jsonData[tempNum]['cs'])
            for tempNum1 in range(jsonData[tempNum]['cCnt']):
                textChapter = jsonData[tempNum]['cs'][tempNum1]['cN']
                downloadUrl = 'https://read.qidian.com/chapter/' + jsonData[tempNum]['cs'][tempNum1]['cU']
                # print(textChapter, ':', textUrl)
                downloadReq = request.Request(url=downloadUrl, headers=head)
                downloadRes = request.urlopen(downloadReq)
                downloadHtml = downloadRes.read().replace(b'<p>', b'\r\n').decode('utf-8', 'ignore')
                chapterText = BeautifulSoup(downloadHtml, 'lxml')
                texts = chapterText.find_all(class_='read-content j_readContent')
                chapterText = BeautifulSoup(str(texts), 'lxml')
                # 写入文件
                file.write('[' + textChapter + ']' + '\r\n')
                file.write(chapterText.div.text + '\r\n')
                progress += 1
                print('已下载：', progress, '/', int(numChapter))
                temps = '已下载：'+str(progress) + '/' + str(numChapter) + '\n'
                d.insert('1.0', temps)
                d.update()
        file.close()

    else:
        catalogTextNew = BeautifulSoup(str(texts), 'lxml')
        texts1 = catalogTextNew.find_all('li')
        # 计算章节数量
        numChapter = len(texts1)
        print('章节数量：', int(numChapter))
        temps = '章节数量：' + str(numChapter) + '\n'
        d.insert('1.0', temps)
        d.update()
        progress = 0;
        # 创建文件，获取书名
        filenameHtml = catalogText.find_all('div', class_='book-info ')
        if str(filenameHtml) == '[]':
            filenameHtml = catalogText.find_all('div', class_='book-information cf')
        tempText = BeautifulSoup(str(filenameHtml), 'lxml')
        print(tempText.em.text)
        temps = '书籍名：' + tempText.em.text + '\n'
        d.insert('1.0', temps)
        d.update()
        filename = tempText.em.text + '.txt'
        file = open(filename, 'w', encoding='utf-8')
        for unit in texts1:
            if unit.string == None:  # 过滤掉空项
                # 下面为爬取单个文章页的代码
                downloadUrl = 'https:' + unit.a.get('href')
                downloadReq = request.Request(url=downloadUrl, headers=head)
                downloadRes = request.urlopen(downloadReq)
                downloadHtml = downloadRes.read().replace(b'<p>', b'\r\n').decode('utf-8', 'ignore')
                chapterText = BeautifulSoup(downloadHtml, 'lxml')
                texts = chapterText.find_all(class_='read-content j_readContent')
                chapterText = BeautifulSoup(str(texts), 'lxml')
                # 写入文件
                file.write('[' + unit.a.string + ']' + '\r\n')
                file.write(chapterText.div.text + '\r\n')
                progress += 1
                print('已下载：', progress, '/', int(numChapter))
                temps = '已下载：' + str(progress) + '/' + str(numChapter) + '\n'
                d.insert('1.0', temps)
                d.update()
        file.close()
    return
def buttonHandler():
    #d.insert('1.0','hello\n')
    download(e.get())
    return

# 显示提示文字
l = tk.Label(window,
    text='粘贴书籍目录的网址',    # 标签的文字
    # bg='green',     # 背景颜色
    font=('Song', 12),     # 字体和字体大小
    width=20, height=2)  # 标签长宽
l.pack(pady='0.5cm')    # 固定窗口位置
# 显示文本框
e = tk.Entry(window,show=None,width=40,font=('Song', 14))
e.pack()
b=tk.Button(text='下载',font=('Song', 12),command=buttonHandler)
b.pack(pady='0.5cm')
d.pack(side='bottom',pady='0.2cm')
window.mainloop()

