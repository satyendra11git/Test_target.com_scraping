import scrapy
import json
from scrapy.http import Request, FormRequest
import re

# scrapy crawl target -a url=

class TargetSpider(scrapy.Spider):
    name = 'target'
    def __init__(self, **kwargs):
        self.start_urls = kwargs.get('url')
        self.headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        }

    def start_requests(self):
        # start_url = "https://www.target.com/p/-/A-79344798"
        start_url = self.start_urls


        yield Request(url=start_url, headers=self.headers, callback=self.parse_1)

    def parse_1(self, response):
        html_text= response.text

        regex_script_data = re.findall(r"deepFreeze\(JSON\.parse(.*?)\,\s*writable\:", str(html_text))
        # print(regex_script_data)

        cleaned_regex_script_data = (
            regex_script_data[0]
            .encode("ascii", "ignore")
            .decode()
            .replace('\\"', "")
            .replace("\\", "")
        )
        # print(cleaned_regex_script_data)

        target_regex_script_data=re.findall(r'domain-product\/get-pdp-v1\,(.*?)\}\,\_\_NOT\_PC',cleaned_regex_script_data)[0]
        # print(target_regex_script_data)

        tcin = re.findall(r'tcin\:(\d+)\,', target_regex_script_data)[0]
        product_url = re.findall(r'buy_url:(.*?)\,', target_regex_script_data)[0]
        barcode = re.findall(r'primary_barcode:(\d+)\,', target_regex_script_data)[0]
        price = re.findall(r'current_retail:(.*?)\,', target_regex_script_data)[0]
        description = re.findall(r'downstream_description\:(.*?)\,soft_bullet_description', target_regex_script_data)[0]

        questions_regex_script_data = re.findall(r'most_recent\:\[(.*?)\],', target_regex_script_data)[0]
        all_questions = re.findall(r'\{id\:(.*?)\}\}\,', questions_regex_script_data)


        for question in all_questions:
            question_id=re.findall(r'(\w+-\w+-\w+-.*?)\,', question)[0]
            question_text = re.findall(r'text:(.*?),author\:', question)[0]
            answer_id = re.findall(r'external_id\:(.*?)\}', question)[0]
            user_nickname=re.findall(r'author:(.*?)external_id', question)[0]
            user_nickname=user_nickname.replace("{nickname:","").replace(",","").replace("{",'')
            answer_text=re.findall(r'title\:(.*?)\,rating\:', question)[0]
            submission_date=re.findall(r'submitted_at\:(\d{4}-\d{1,2}-\d{1,2})', question)[0]

            result_data = {
                "tcin": tcin,
                "product_url": product_url,
                "upc": barcode,
                "price_amount": price,
                "product_description": description,
                "question_id": question_id,
                "question_summary": question_text,
                "answer_id": answer_id,
                "answer_summary": answer_text,
                "user_nickname": user_nickname,
                "submission_date": submission_date

            }

            yield result_data


















