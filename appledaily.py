# -*- coding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
import html2text as h2t
import pymysql
import sys
import time
reload(sys)
sys.setdefaultencoding('utf-8')


class Item(object):
    title = None
    time = None
    content = None
    url = None


class get_new(object):
    def __init__(self, url):
        self.url = url
        self.db_url = self.get_dburl()
        self.response = self.get_response(self.url)
        self.href_list = self.get_href_list(self.response, self.db_url)
        self.data_list = self.get_data(self.href_list)
        self.save = self.save2db(self.data_list)

    def get_response(self, url):
        try:
            response = urllib2.urlopen(url.encode('utf-8'), timeout=2)
            return response
        except:
            print('抓取失敗'+url)
        else:
            print('抓取成功')

    def get_dburl(self):
        connection = pymysql.connect(
                host='localhost',
                user='root',
                password='henry!QAZ@WSX',
                db='scrapyDB',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        try:
            with connection.cursor() as cursor:
                sql = """SELECT url FROM news WHERE 1"""
                cursor.execute(sql)
                return cursor.fetchall()
            connection.commit()

        finally:
            connection.close()

    def get_href_list(self, response, db_url):
        soup = BeautifulSoup(response, 'lxml')
        href_list = []
        urls = soup.find_all('a', href=True)
        for url in urls:
            count = 0
            for i in range(0, len(db_url)):

                if url['href'] == db_url[i]['url'].encode('utf-8'):
                     count = count + 1
                else:
                    continue

            if count == 0:
                href_list.append(url['href'])

        print len(href_list)
        return href_list

    def get_data(self, href_list):
        data_list = []

        for url in href_list:
            time.sleep(2)
            response = self.get_response(url)
            try:
                soup = BeautifulSoup(response, 'lxml')
            except:
                continue

            item = Item()

            item.title = soup.find('h1').get_text().encode('utf-8')
            item.time = soup.find('div', class_='ndArticle_creat').get_text().encode('utf-8').split('\x9a')[1]

            soup_content = soup.find('div', class_='ndArticle_margin')
            Bea_content = BeautifulSoup(unicode(soup_content), 'lxml')
            item.content = Bea_content.find('p').get_text().encode('utf-8')

            item.url = url
            print item.title
            data_list.append(item)

        print('資料抓取完成')
        return data_list

    def save2db(self, data_list):
        leng = len(data_list)
        for i in range(0, leng):
            title = data_list[i].title.encode('utf-8')
            time = data_list[i].time.encode('utf-8')
            content = data_list[i].content.encode('utf-8')
            url = data_list[i].url.encode('utf-8')
            who_release = ''
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='henry!QAZ@WSX',
                db='scrapyDB',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            try:
                with connection.cursor() as cursor:
                    sql = """INSERT INTO news(title,time,content,url,who_release)
                            SELECT %s,%s,%s,%s,%s FROM DUAL
                            WHERE NOT EXISTS(SELECT url FROM news WHERE url=%s)"""

                    cursor.execute(sql, (title, time, content, url, who_release, url))

                connection.commit()

            finally:
                connection.close()
        print('存入資料庫成功')


if __name__ == '__main__':
    # url = 'https://tw.appledaily.com/rss/newcreate/kind/rnews/type/106'
    url = 'https://tw.appledaily.com/rss/newcreate/kind/rnews/type/105'
    news = get_new(url)
