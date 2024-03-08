from pathlib import Path

import scrapy
import os
import uuid
import unicodedata
import re

from vietjack.common import appconstant

def create_level_path():
    level0_path = f"./vietjack/outputs/{appconstant.lop}/"
    level1_path = [level0_path + n for n in os.listdir(level0_path) if '.txt' not in n]
    level2_path, level3_path, level4_path = [], [], []
    for l in level1_path:
        level2_path += [l + '/' + n for n in os.listdir(l) if '.txt' not in n]
    for l in level2_path:
        level3_path += [l + '/' + n for n in os.listdir(l) if '.txt' not in n]
    for l in level3_path:
        level4_path += [l + '/' + n for n in os.listdir(l) if '.txt' not in n]

    # Create dictionary to mapping url-path
    level_dicts = {}
    for l in level4_path:
        with open(l + '/root.txt') as f: 
            url_level = f.read()

        level_dicts[l] = url_level
    
    return level4_path, level_dicts

class Level4Spider(scrapy.Spider):
    name = "level_4"

    levels, level_dicts = create_level_path()

    def start_requests(self):
        urls = []

        for path in self.levels:
            with open(path + '/root.txt', 'r') as f:
                urls.append(f.read())

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        url = response.url
        url_root =  "https://www.vietjack.com"

        if len(response.css('div.vj__list div.col-md-6 h3.sub-title')) > 0:
            col_response = response.css('div.vj__list div.col-md-6 h3.sub-title')
        elif len(response.css('h3.sub-title')) > 0:
            col_response = response.css('h3.sub-title')
        else:
            col_response = []

        pattern = ["Phần \d+:"]
        combine_pattern = '|'.join(pattern)

        level_dict_path = []
        for k, v in self.level_dicts.items():
            if v == url:
                level_dict_path.append(k)
        
        level_dict_path = [p for p in level_dict_path if len(os.listdir(p)) == 2]

        count = 0
        for col in col_response:
            link = col.css('a::attr(href)').get()
            text = col.css('a b::text').get()
            color = col.css('a b::attr(style)').get()

            if link != None and text != None and color == 'color:blue;':
                text = unicodedata.normalize("NFKC", text)
                out_find = re.findall(combine_pattern, text)

                if len(out_find) > 0:
                    continue

                name = link.split('/')[-1].split('.')[0]
                name = '-'.join(name.split('-')[:2] + name.split('-')[-1:]) + '_' + str(uuid.uuid4())[:5]
                link = url_root + link[2:]
                    
                if len(level_dict_path) > 0: 
                    for path_dict in level_dict_path:        
                        name_folder = path_dict + '/' + name
                        if not os.path.exists(name_folder):
                            os.mkdir(name_folder)
                        with open(name_folder + '/root.txt', 'w') as f:
                            f.write(link)
                        with open(name_folder + '/name.txt', 'w', encoding='utf-8') as f:
                            f.write(text)
                        
                        count += 1
                else:
                    print("Error not found path of url")
                    continue

            
        if count == 0:
            if len(level_dict_path) > 0: 
                name_text = response.css('h2.sub-title::text').get()
                name_none = url.split('/')[-1].split('.')[0]
                for path_dict in level_dict_path:
                    name_none = '-'.join(name_none.split('-')[:2] + name_none.split('-')[-1:]) + '_' + str(uuid.uuid4())[:5]
                    name_folder = path_dict + '/none_' + name_none
                    if not os.path.exists(name_folder):
                        os.mkdir(name_folder)
                    with open(name_folder + '/root.txt', 'w') as f:
                        f.write(url)

                    # Process name
                    if name_text != None:
                        with open(name_folder + '/name.txt', 'w', encoding='utf-8') as f:
                            f.write(name_text)
                    else:
                        with open(path_dict + '/name.txt', 'r', encoding='utf-8') as f:
                            name_text = f.read()
                        with open(name_folder + '/name.txt', 'w', encoding='utf-8') as f:
                            f.write(name_text)
            else:
                print("Error not found path of url")
        