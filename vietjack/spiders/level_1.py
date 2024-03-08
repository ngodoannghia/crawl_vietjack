from pathlib import Path

import scrapy
import os
from vietjack.common import appconstant


class Level1Spider(scrapy.Spider):
    name = "level_1"
    def start_requests(self):
        level1_path = f"./vietjack/outputs/{appconstant.lop}/"
        with open(level1_path + "root.txt", 'r') as f:
            url = f.read() 

        yield scrapy.Request(url=url, callback=self.parse)
        
    def parse(self, response):
        url = response.url
        url_root =  "https://www.vietjack.com"
        output_root = f"./vietjack/outputs/{appconstant.lop}/"
        count = 0
        for title in response.xpath('//h3[@class="sub-title" and not(ancestor::div[@class="toggle-content"])]'):
            link = title.css("a::attr(href)").get()
            text = title.css("a b::text").get()
            if text != None and link != None:
                name = link.split('/')[-1].split('.')[0]
                link = url_root + link[2:]
                save_path = output_root + name
                if not os.path.exists(save_path):
                    os.mkdir(save_path)
                with open(save_path + '/root.txt', 'w') as f:
                    f.write(link)
                with open(save_path + '/name.txt', 'w', encoding='utf-8') as f:
                    f.write(text)
                
                count += 1
        
        if count == 0:
            name = url.split('/')[-1].split('.')[0]
            save_path = output_root + name
            if not os.path.exists(save_path):
                os.mkdir(save_path)
            
            text = response.css('div.col-md-7 h1::text').get()
            if text == None:
                with open(output_root + 'name.txt', 'r', encoding='utf-8') as f:
                    text = f.read()

            with open(save_path + '/root.txt', 'w') as f:
                f.write(url)
            with open(save_path + '/name.txt', 'w', encoding='utf-8') as f:
                f.write(text)

