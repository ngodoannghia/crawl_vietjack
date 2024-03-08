from pathlib import Path

import scrapy
import os
import uuid

from vietjack.common import appconstant

class Level2Spider(scrapy.Spider):
    name = "level_2"

    def start_requests(self):
        urls = []
        level1_path = f"./vietjack/outputs/{appconstant.lop}/"
        folder_name = [a for a in os.listdir(level1_path) if '.txt' not in a]
        
        for f in folder_name:
            with open(level1_path + f + '/root.txt', 'r') as f:
                link = f.read()
            urls.append(link)

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        url = response.url
        name_folder = url.split('/')[-1].split('.')[0]
        output_path = f"./vietjack/outputs/{appconstant.lop}/" + name_folder
        url_root =  "https://www.vietjack.com"

        for block in response.css("div.col-md-7"):

            for row in block.css("div.vj__list div.col-md-6"):
                text_row =  row.css("h3.sub-title b::text").get()             
                if text_row != None:
                    subject_path = output_path + '/' + text_row
                    if not os.path.exists(subject_path):
                        os.mkdir(subject_path)
                
                    for li in row.css("ul.list li"):
                        link = li.css("a::attr(href)").get()
                        text_li = li.css("a b::text").get()

                        if link != None and text_li != None:
                            name_li = link.split('/')[-2] + '-' + link.split('/')[-1].split('.')[0]
                            name_li = '-'.join(name_li.split('-')[:2] + name_li.split('-')[-1:]) + '_' + str(uuid.uuid4())[:5]
                            li_path = subject_path + '/' + name_li
                            link = url_root + link[2:]
                            if not os.path.exists(li_path):
                                os.mkdir(li_path)
                            with open(li_path + '/root.txt', 'w') as f:
                                f.write(link)
                            with open(li_path + '/name.txt', 'w', encoding='utf-8') as f:
                                f.write(text_li)
