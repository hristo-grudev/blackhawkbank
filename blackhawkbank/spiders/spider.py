import re

import scrapy

from scrapy.loader import ItemLoader

from ..items import BlackhawkbankItem
from itemloaders.processors import TakeFirst


class BlackhawkbankSpider(scrapy.Spider):
	name = 'blackhawkbank'
	start_urls = ['https://www.blackhawkbank.com/get-to-know-us/news-releases']

	def parse(self, response):
		post_links = response.xpath('//div[@data-content-block="bodyCopy"]//h3/a')
		for post in post_links:
			url = post.xpath('./@href').get()
			date = post.xpath('./text()').get()
			try:
				date = re.findall(r'[A-Za-z]+\s\d{1,2},\s\d{4}', date)
			except:
				date = ''
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

	def parse_post(self, response, date):
		title = response.xpath('//h1[@class="breadcrumb"]/text()').get()
		description = response.xpath('//div[@class="col-sm-12"]//text()[normalize-space() and not(ancestor::a[@data-link-type-id="page"] | ancestor::style)]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=BlackhawkbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
