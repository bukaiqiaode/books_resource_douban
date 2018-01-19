# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
import codecs
import json
import os
import random
import re
import sys
import time
import urllib

# https://www.cnblogs.com/eejron/p/4708980.html
# http://blog.csdn.net/yelbosh/article/details/21022263
def get_html_text(url):
    '''
    Given url, query the page-content using this url
    '''
    try:
        resp = urllib.urlopen(url)
        html_data = resp.read().decode('utf-8')
        return html_data
    except:
        #just return empty-string if any failure.
        return ""

def collect_books_detai_urls():
    '''
    Given the seed url, iterate detail-url of the top-250 books
    '''
    encode_type = sys.getfilesystemencoding()
    
    seedurl = "https://book.douban.com/top250?start="
    indexer = 0

    detail_urls = []
    while indexer <= 225:
        url = seedurl + str(indexer)
        print "Reading ", url

        #request the content, and get the outter-tables
        html_data = get_html_text(url)
        soup = BeautifulSoup(html_data,'html.parser')
        
        level_a = soup.find('div',attrs={'class':'indent'})
        table_list = level_a.find_all('table')

        #process each table, abstract the detail-url
        for table in table_list:
            a_div = table.find('div',attrs={'class':'pl2'})
            a_tag = a_div.find('a')
            book_detail_url = a_tag.attrs['href'].encode(encode_type)

            if is_url_correct(book_detail_url):
                detail_urls.append(book_detail_url)
            else:
                print "Wrong for ", book_detail_url
            
        #25-books per page, so we need to increase 25 each-time
        indexer += 25

    #save to a file
    f = codecs.open("detail_urls.txt", "a", "utf-8")
    for item in detail_urls:
        f.write(item + '\n')
    f.close()

    print len(detail_urls)
    pass

def is_url_correct(url):
    pattern = r'^https://book.douban.com/subject/[1-9][0-9]+/$'
    result = re.match(pattern, url, re.I)
    if not result:
        return False
    else:
        return True

def read_detail_urls_file():
    url_list = []
    f = codecs.open("detail_urls.txt", "r", "utf-8")
    for line in f:
        url_list.append( line.strip())
    f.close()
    return url_list

class book_item(object):
    def __init__(self, name, auther, pub_date, pub_by, pages, isbn, poster_url):
        self.name = name
        self.auther = auther
        self.pub_date = pub_date
        self.pub_by = pub_by
        self.pages = pages
        self.isbn = isbn
        self.poster_url = poster_url

    def to_dict(self):
        encode_type = sys.getfilesystemencoding()
        info = {}
        info['book_name'] = self.name.decode(encode_type)
        info['auther_name'] = self.auther.decode(encode_type)
        info['pub_date'] = self.pub_date.decode(encode_type)
        info['pub_by'] = self.pub_by.decode(encode_type)
        info['pages'] = self.pages.decode(encode_type)
        info['isbn'] = self.isbn.decode(encode_type)
        info['poster_url'] = self.poster_url.decode(encode_type)
        return info
        
        

def read_book_info_from_detail_url(url):
    encode_type = sys.getfilesystemencoding()
    
    #request the url
    html_data = get_html_text(url)
    soup = BeautifulSoup(html_data,'html.parser')
    
    #position to the poster-address
    #and read
    image_div = soup.find('div',attrs={'id':'mainpic'})
    img_tag = image_div.find('img')
    image_url = img_tag.attrs['src'].encode(encode_type)
    book_name = img_tag.attrs['alt'].encode(encode_type)
    
    #position to the information-part
    #and read
    info_div = soup.find('div',attrs={'id':'info'})
    temp_arr = info_div.text.split('\n')

    auther_a_tag = info_div.find_all('a')[0]
    auther_name = auther_a_tag.text.replace('\n', '').strip().replace('  ','').encode(encode_type)


    publisher = ""
    published_year = ""
    pages = ""
    ISBN = ""
    for line in temp_arr:
        line = line.strip().encode(encode_type)

        if u"出版社".encode(encode_type) in line:
            publisher = line.split(':')[1].strip()

        if u"出版年".encode(encode_type) in line:
            published_year = line.split(':')[1].strip()

        if u"页数".encode(encode_type) in line:
            pages = line.split(':')[1].strip()

        if "ISBN" in line:
            ISBN = line.split(':')[1].strip()
            
    #build the book-instance
    the_book = book_item(book_name, auther_name, published_year, publisher, pages, ISBN, image_url)
    return the_book
    
def load_book_detail_save_to_json():
    book_urls = read_detail_urls_file()

    list_for_json = []
    for url in book_urls:
        print "loading ", url
        try:
            temp_book = read_book_info_from_detail_url(url)
            list_for_json.append(temp_book.to_dict())
            time.sleep(random.random() * 2 + 1)
        except Exception as err:
            print err
            print "failed to loading ", url
        
    with open('data.json', 'w') as json_file:
        json_file.write(json.dumps(list_for_json))

def read_book_detail_from_json():
    data = ""
    with open('data.json', 'r') as json_file:
        data = json.load(json_file)
    return data


def save_book_poster(book_item):
    url = book_item["poster_url"]
    local_file = "posters\\{0}.jpg".format(book_item["isbn"])

    #print local_file
    urllib.urlretrieve(url, local_file)
    return

def check_book_posters():
    books = read_book_detail_from_json()

    number = 0
    for book in books:
        target_file = "posters\\{0}.jpg".format(book["isbn"])
        if os.path.exists(target_file):
            pass
        else:
            print "expected ", target_file, " but not found!"
        if len(book["isbn"]) < len("9787020002207"):
            print target_file
    
if __name__ == "__main__":
    #check_book_posters()
            
    exit()
    
    print 'done'
























