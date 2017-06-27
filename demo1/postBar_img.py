from html.parser import HTMLParser
from bs4 import BeautifulSoup, Comment
import requests
import re

HTMLSRC=[]

class GetImg(HTMLParser):
    # 处理头像src
    def __init__(self):
        super().__init__()
        self.in_a = False
        self.src = None

    def handle_starttag(self, tag, attrs):
        if tag == 'a' and _attr(attrs, 'href') == "javascript:;" and _attr(attrs, 'class') == "userinfo_head" :
            self.in_a = True

        if self.in_a and tag == 'img':
            self.src = _attr(attrs, 'src')

class CommentHTMLParser(HTMLParser):
    '''获取隐藏内容...'''
    def __init__(self):
        super().__init__()
        self.imagesName = []
        
    def handle_comment(self,data):
        self.cparser = PostBar()
        self.cparser.feed(data) 


class PostBar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_name =False
        self.in_img =False
        self.imagesName = []

    def handle_starttag(self, tag, attrs):
        rule = re.compile(r'frs-author-name.*j_user_card.*')
        className = _attr(attrs, 'class')
        m = rule.match(str(className))

        if tag == 'a' and m:
            for name, value in attrs:
                if name  == 'href':
                    url = 'http://tieba.baidu.com' + value
                    get_img = GetImg()
                    r = requests.get(url=url, headers=getHeader())
                    get_img.feed(r.content.decode('utf-8', 'ignore'))
                    self.src = get_img.src
            self.in_name = True

    def handle_endtag(self, tag):
        self.in_name =False
        self.in_img =False

    def handle_data(self, data):
        global HTMLSRC
        if self.in_name :
            name = {}
            name['name'] = data
            name['src'] = self.src
            self.imagesName.append(name)
            HTMLSRC = self.imagesName

def _attr(attrlist, attrname):
    for attr in attrlist:
        if attr[0] == attrname:
            return attr[1]
    return None

def _download_img(name,src):
    rule = re.compile(r'http:/.*')
    m= rule.match(str(src))
    if src is None or not m:
        return
    r = requests.get(src)
    with open(name+'.jpg', 'wb') as f:
        f.write(r.content)

def getHeader():
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.2141.400 QQBrowser/9.5.10219.400'
    headers = {'User-Agent': user_agent}
    return headers

def getURL(url):
    r = requests.get(url=url, headers=getHeader())
    parser = CommentHTMLParser()
    parser.feed(r.content.decode('utf-8', 'ignore'))
    

if __name__ == '__main__':
    url='http://tieba.baidu.com/f?kw=python&fr=ala0&tpl=5'
    getURL(url)
    print(HTMLSRC)
        
    for i in range(len(HTMLSRC)):
        _download_img(HTMLSRC[i]['name'], HTMLSRC[i]['src'])
            