from pathlib import Path

import scrapy
import os

class Level0Spider(scrapy.Spider):
    name = "level_0"

    def start_requests(self):
        url = "https://www.vietjack.com"
    
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        output_path = "./vietjack/outputs/"
        url_root = response.url
        for cls in response.css("ul.nav li.level-1"):
            text = cls.css("a::text").get()
            link = cls.css("a::attr(href)").get()
            if text != None and link != None:
                
                link = url_root + link[2:]

                name = link.split('/')[-1].split('.')[0]
                folder_path = output_path + name
                if not os.path.exists(folder_path):
                    os.mkdir(folder_path)
                
                with open(folder_path + "/root.txt", 'w') as f:
                    f.write(link)
                with open(folder_path + "/name.txt", 'w', encoding='utf-8') as f:
                    f.write(text)
