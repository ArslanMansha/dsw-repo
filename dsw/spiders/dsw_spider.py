"""Scrapper for dsw.com."""
import json
import scrapy


class DSWSpider(scrapy.Spider):
    """Spider."""
    name = "dsw"
    start_urls = ['https://www.dsw.com/en/us']
    category_url = "https://www.dsw.com/api/v1/content/pages/{}?No={}&locale=en_US&pagePath=/pages/DSW/category&" \
                   "pushSite=DSW&skipHeaderFooterContent=true&tier=GUEST"
    header = {"X-Requested-With": 'XMLHttpRequest', 'Referer': start_urls[0]}

    def parse(self, response):
        """Yields a call to get category details."""
        yield response.follow("https://www.dsw.com/api/v1/content/zones?contentCollection=%2Fcontent%2FDSW%2"
                              "FContents%2FSharedContents%2FHeaderContent&locale=en_US&pushSite=DSW&tier=GUEST",
                              callback=self.parse_links)

    def parse_links(self,response):
        """Gets category details,and calls product links."""
        json_response = json.loads(response.body_as_unicode())
        top_nav_len = len(json_response['contentContentItem']['contents'][0]['TopNavList'])-1
        for iterator in range(top_nav_len):
            num_shoes = len(json_response['contentContentItem']['contents'][0]['TopNavList'][iterator]['shoes'])
            for iterator1 in range(num_shoes):
                num_records = len(json_response['contentContentItem']['contents'][0]['TopNavList'][iterator]
                                  ['shoes'][iterator1]['HeaderNavigation'])
                for iterator2 in range(num_records):
                    category_code = json_response['contentContentItem']['contents'][0]['TopNavList'][iterator]
                    ['shoes'][iterator1]['HeaderNavigation'][iterator2]['linkText']['queryString'].split('/')[-1]
                    category_url = self.category_url.format(category_code, 0)
                    yield response.follow(category_url, callback=self.parse_products, headers=self.header,
                                          meta={'product_num': 0, 'category_code': category_code,
                                                "cookiejar": response.headers['Set-Cookie']})

    def parse_products(self, response):
        """Gets Product details and handles pagination."""
        json_response = json.loads(response.body_as_unicode())
        products = json_response['pageContentItem']['contents'][0]['mainContent'][6]['contents'][0]['records'] \
            if json_response['pageContentItem']['contents'][0]['mainContent'][6]['contents'][0]['records'] else None
        if products:
            for product in products:
                yield product['attributes']
            category_url = self.category_url.format(response.meta['category_code'], response.meta['product_num']+60)
            yield response.follow(category_url, callback=self.parse_products,
                                  meta={'product_num': response.meta['product_num']+60,
                                        'category_code': response.meta['category_code']})
