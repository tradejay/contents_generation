import os
import bs4
import urllib
import json
import pandas as pd

from src.utils import (
    save_img,
    get_today,
    save_text
)

with open("data/shopping_id.json", "r", encoding="utf-8") as f:
    categoryDetail = json.load(f)
id2midCategory = categoryDetail["id2midCategory"]
id2childCategory = categoryDetail["childCategories"]
id2rootCategory = {'50000000': '패션의류',
                    '50000001': '패션잡화',
                    '50000002': '화장품/미용',
                    '50000003': '디지털/가전',
                    '50000004': '가구/인테리어',
                    '50000005': '출산/육아',
                    '50000006': '식품',
                    '50000007': '스포츠/레저',
                    '50000008': '생활/건강',
                    '50000009': '여가/생활편의',
                    'ALL': '전체'}

preset_ids = {"선풍기": {"child_id": "50001420",
                       "mid_id": "50000212",
                       "root_id": "50000003"},
              "냉장고": {"child_id": "50001430",
                       "mid_id": "50000213",
                       "root_id": "50000003"},
              "블랙박스": {"child_id": "50001188",
                        "mid_id": "50000214",
                        "root_id": "50000003"},
              "ALL": {"root_id":"ALL"}}

id2type = {"click": "많이 본 상품", "purchase": "많이 구매한 상품", "brand": "인기 브랜드", "keyword": "트렌드 키워드"}
type2id = {v:k for k, v in id2type.items()}

preset_prompt = {0: "<product_name> <trend_type> 요약해서 소개해줘",
                 1: "<product_name> <trend_type>에서 상위 3개 항목과 상승한 항목만 강조해서 소개해줘"}

class ShoppingPromptTool():
    def __init__(self):
        print("ShoppingDataLoader")

    def setup(self, child_category, trend_type):
        self.save_dir = "output/" + get_today()
        self.child_name = child_category
        self.trend_type = trend_type

    def __call__(self, child_category, trend_type, prompt_type):
        self.setup(child_category, trend_type)
        try:
            param_ids = preset_ids[child_category]
        except:
            param_ids = preset_ids["ALL"]
        param_ids["type_id"] = type2id[trend_type]
        return self.get_data(**param_ids), self.get_prompt(prompt_type)
    
    def get_data(self, type_id="purchase", child_id="", mid_id="", root_id="ALL", output_type="markdown"):

        def _load_json(request_url, query, cols, data_key):
            source = urllib.request.urlopen(request_url).read()
            soup = bs4.BeautifulSoup(source, "lxml")
            trend_json = json.loads(soup.select("script#__NEXT_DATA__")[0].text)
            trend_queries = trend_json['props']['pageProps']['dehydratedState']['queries']
            for item in trend_queries:
                if item['queryKey'][0] == query:
                    df = pd.DataFrame(item['state']['data'][data_key][:10], columns=cols)
                    return df

        if type_id in ["click", "purchase"]:
            request_url = f"https://search.shopping.naver.com/best/category/{type_id}?categoryCategoryId={child_id}&categoryChildCategoryId={child_id}&categoryDemo=A00&categoryMidCategoryId={mid_id}&categoryRootCategoryId={root_id}&period=P1D"
            query = "CATEGORY_PRODUCTS"
            cols = ["rank", "imageUrl", "mobileLowPrice", "productTitle"]
            data_key = 'products'
        elif type_id in ["brand", "keyword"]:
            request_url = f"https://search.shopping.naver.com/best/category/{type_id}?categoryCategoryId={mid_id}&categoryChildCategoryId=&categoryDemo=A00&categoryMidCategoryId={mid_id}&categoryRootCategoryId={root_id}&chartRank=1&period=P1D"
            query = "CHART_LIST"
            data_key = 'charts'
            if type_id == "brand":
                cols = ["rank", "change", "exposeBrandName"]
            elif type_id == "keyword":
                cols = ["rank", "change", "exposeKeyword"]

        self.data = _load_json(request_url, query, cols, data_key)

        if output_type == "markdown":
            return self.to_markdown()
        else:
            return self.data.drop(columns=["imageUrl"])

    def get_fullprompt(self):
        system_content = "제목 : {} {} {} 베스트 10 \n{}".format(get_today(), self.child_name, self.trend_type, self.to_markdown())
        return (system_content, self.user_content)

    def get_prompt(self, prompt_type):
        self.user_content = preset_prompt[prompt_type].replace("<product_name>", self.child_name).replace("<trend_type>", self.trend_type)
        return self.user_content

    def save_image(self, drop=True):
        for _, row in self.data.iterrows():
            save_img(row['imageUrl'], [self.trend_type, self.child_name, row["rank"]], self.save_dir)
        if drop:
            self.data = self.data.drop(columns=["imageUrl"])
    
    def to_markdown(self):
        if "imageUrl" in self.data.columns:
            return self.data.drop(columns=["imageUrl"]).to_markdown()
        else:
            return self.data.to_markdown()

    def save_output(self, output):
        save_text(output, [self.trend_type, self.child_name], self.save_dir)