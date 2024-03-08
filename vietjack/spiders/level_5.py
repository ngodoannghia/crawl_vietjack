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
    level2_path, level3_path, level4_path, level5_path = [], [], [], []
    for l in level1_path:
        level2_path += [l + '/' + n for n in os.listdir(l) if '.txt' not in n]
    for l in level2_path:
        level3_path += [l + '/' + n for n in os.listdir(l) if '.txt' not in n]
    for l in level3_path:
        level4_path += [l + '/' + n for n in os.listdir(l) if '.txt' not in n]
    for l in level4_path:
        level5_path += [l + '/' + n for n in os.listdir(l) if '.txt' not in n]
    # Create dictionary to mapping url-path
    level_dicts = {}
    for l in level5_path:
        with open(l + '/root.txt') as f: 
            url_level = f.read()

        level_dicts[l] = url_level
    
    return level5_path, level_dicts

class Level5Spider(scrapy.Spider):
    name = "level_5"
    
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

        pattern = ["Chuyên đề [\w\s]+ \d+ Chuyên đề \d+\.*\d*:", "Top \d+ Đề thi [\w\s]+ \w* \d+", "SBT [\w\s]+ \d+ Chương \d+\.*\d*:",
                   "Lý thuyết [\w\s]+ \d+ Chương \d+\.*\d*:", "Trắc nghiệm [\w\s]+ \d+ Chương \d+\.*\d*:", "Chương \d+\.*\d*:", "Chuyên đề \d+\.*\d*:",
                   "Lý thuyết [\w\s]+ \d+ Chương \d+", "Hoạt động thực hành trải nghiệm", "Bài tập ôn tập cuối năm",
                   "Lý thuyết Chủ đề \d+\.*\d*:", "Trắc nghiệm [\w\s]+ \d+ Chủ đề \d+\.*\d*", "Top \d+", "Chủ đề \d+\.*\d*:", "\d+ bài tập", "\d+ câu trắc nghiệm",
                   "Các dạng bài tập", "PDF Bộ sách lớp \d+", "\d+ bài văn hay lớp \d+", "Văn mẫu lớp \d+", "\d+ câu trắc nghiệm Ngữ văn \d+", "\d+ câu hỏi ôn tập Ngữ văn \d+",
                   "Tổng hợp Sơ đồ tư duy môn Văn \d+", "Lý thuyết, Bài tập Tiếng việt", "Kiến thức trọng tâm tác giả tác phẩm Ngữ văn \d+", "Tổng hợp ý nghĩa nhan đề Văn \d+",
                   "Chủ đề:", "Xem online bộ sách lớp \d+", "Xem online bộ sách lớp \d+", "Xem online bộ sách lớp \d+"]
        combine_pattern = '|'.join(pattern)

        level_dict_path = []
        for k, v in self.level_dicts.items():
            if v == url:
                level_dict_path.append(k)
        
        level_dict_path = [p for p in level_dict_path if len(os.listdir(p)) == 2]
        
        count = 0
        for line in response.xpath('//ul[@class="list" and not(ancestor::div[contains(@class, "vj__list")]) and not(ancestor::div[@class="toggle-content"])]/li'):
            link = line.css('a::attr(href)').get()
            text = line.css('a b::text').get()
            color = line.css('a b::attr(style)').get()
            target = line.css('a::attr(target)').get()

            if target == "_blank":
                continue

            if link in self.level_dicts:
                continue

            if link != None and text != None and color == 'color:green;':
                text = unicodedata.normalize("NFKC", text)
                out_find = re.findall(combine_pattern, text)

                if len(out_find) > 0:
                    continue

                if len(level_dict_path) > 0:    
                    for path_dict in level_dict_path: 
                        name = link.split('/')[-1].split('.')[0]
                        name = '-'.join(name.split('-')[:2] + name.split('-')[-1:]) + '_' + str(uuid.uuid4())[:5]

                        link = url_root + link[2:]    
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
            for line in response.css("div.col-md-7 p"):
                p_style = line.css('p::attr(style)').get()
                if p_style != "text-align: center;":
                    continue
                
                link = line.css('a::attr(href)').get()
                text = line.css('a b::text').get()

                if link != None and text != None:
                    if len(level_dict_path) > 0:
                        for path_dict in level_dict_path: 

                            name = link.split('/')[-1].split('.')[0]
                            name = '-'.join(name.split('-')[:2] + name.split('-')[-1:]) + '_' + str(uuid.uuid4())[:5]

                            link = url_root + link[2:]    
                            name_folder = path_dict + '/' + name
                            if not os.path.exists(name_folder):
                                os.mkdir(name_folder)
                            with open(name_folder + '/root.txt', 'w') as f:
                                f.write(link)
                            with open(name_folder + '/name.txt', 'w', encoding='utf-8') as f:
                                f.write(text)
                