# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import openpyxl
import pymysql


class DbPipeline:
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='lxLR0227',
                                    database='spider_db', charset='utf8mb4')
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        title = item.get('title', '')
        score = item.get('score', '')
        subject = item.get('subject', '')
        self.cursor.execute(
            'insert into douban_movie_top250 (movie_title,movie_score,movie_subject) values (%s,%s,%s)', (title, score, subject)
        )

        return item

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()


class Spider2022Pipeline:

    def __init__(self):
        self.workbook = openpyxl.Workbook()
        self.worksheet = self.workbook.active
        self.worksheet.title = 'Top250'
        self.worksheet.append(('title', 'score', 'subject'))

    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        title = item.get('title', '')
        score = item.get('score', '')
        subject = item.get('subject', '')
        self.worksheet.append((title, score, subject))
        return item

    def close_spider(self, spider):
        self.workbook.save('MovieData.xlsx')
