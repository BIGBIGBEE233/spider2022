import re

import scrapy
from scrapy import Selector
from scrapy.http import HtmlResponse

from spider2022.items import MovieItem


class DoubanSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['movie.douban.com']
    # spider定义一个初始请求URL，后续链接通过解析响应获取
    start_urls = ['https://movie.douban.com/top250']

    # 提前构造好全部请求链接，交给scheduler 调度
    # def start_requests(self):
    #     for page in range(10):
    #         yield scrapy.Request(url=f'https://movie.douban.com/top250?start={page*25}&filter=')

    def parse(self, response: HtmlResponse, **kwargs):
        # 使用选择器解析
        # sel = Selector(response)
        # list_items = sel.css('#content > div > div.article > ol > li')

        # 使用响应直接解析
        list_items = response.css('#content > div > div.article > ol > li')
        for item in list_items:
            # 影片详情链接
            movie_detail_url = item.css('div.info > div.hd > a::attr(href)').extract_first()
            print(movie_detail_url)
            movie_item = MovieItem()
            movie_item['title'] = item.css('span.title::text').extract_first()
            movie_item['score'] = item.css('span.rating_num::text').extract_first()
            movie_item['subject'] = item.css('span.inq::text').extract_first()
            yield scrapy.Request(url=movie_detail_url, callback=self.parse_detail, cb_kwargs={'item': movie_item})

        # 如何抓取多页数据

        # 方法1：获取所有页的链接，scrapy.Response 构造请求链接列表
        # 但是这种方式会在首次翻页后，获取到首页链接（运行开始时首页数据其实已经爬取完毕）
        # 导致重复一次请求首页链接，数据爬取重复（如果保存在本地文件，重复数据会在文件最后）

        # hrefs_list=sel.css('div.paginator > a::attr(href)')
        # for href in hrefs_list:
        #     url=response.urljoin(href.extract())
        #     print(url)
        #     yield Request(url=url)

        # 方法2：通过获取下一页按钮href属性值，每次只获取一个下页数据链接,scrapy.Response构造请求，爬取下页数据，直至所有页数据抓取完毕

        next_link = response.css('div.article > div.paginator > span.next > a::attr(href)').extract_first()
        url = response.urljoin(url=next_link)
        print(url)
        yield scrapy.Request(url=url, callback=self.parse)

    #
    def parse_detail(self, response, **kwargs):
        movie_item = kwargs['item']
        sel = Selector(response)
        movie_item['duration'] = sel.css('span[property="v:runtime"]::text').extract_first()
        # intro_text = sel.css('span[property="v:summary"]::text').extract_first()
        # intro = re.sub('[\/:*?"<>|\n\t\r]', intro_text)
        # movie_item['intro'] = intro
        yield movie_item
