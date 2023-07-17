import bs4
import urllib
import json
import pandas as pd

from src.utils import (
    save_img,
    get_today
)

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
id2midCategory = {'50000087': '학습기기',
                '50000088': '게임기/타이틀',
                '50000089': 'PC',
                '50000090': 'PC액세서리',
                '50000091': '노트북액세서리',
                '50000092': '태블릿PC액세서리',
                '50000093': '모니터주변기기',
                '50000094': '주변기기',
                '50000095': '멀티미디어장비',
                '50000096': '저장장치',
                '50000097': 'PC부품',
                '50000098': '네트워크장비',
                '50000099': '소프트웨어',
                '50000151': '노트북',
                '50000152': '태블릿PC',
                '50000153': '모니터',
                '50000204': '휴대폰',
                '50000205': '휴대폰액세서리',
                '50000206': '카메라/캠코더용품',
                '50000208': '영상가전',
                '50000209': '음향가전',
                '50000210': '생활가전',
                '50000211': '이미용가전',
                '50000212': '계절가전',
                '50000213': '주방가전',
                '50000214': '자동차기기'}
id2childCategory = {'50001419': '냉풍기',
                '50001420': '선풍기',
                '50001421': '에어컨',
                '50001422': '온풍기',
                '50001423': '온수기',
                '50001424': '보일러',
                '50001425': '가습기',
                '50001426': '공기정화기',
                '50001427': '제습기',
                '50001428': '전기매트/장판',
                '50001429': '전기요/담요/방석',
                '50001851': '냉온풍기',
                '50006834': '에어컨주변기기',
                '50006971': '업소용냉온풍기',
                '50009120': '온수매트',
                '50009180': '히터'}
id2type = {"click": "많이 본 상품", "purchase": "많이 구매한 상품", "brand": "인기 브랜드", "keyword": "트렌드 키워드"}


child_id = "50001420"
mid_id = "50000212"
root_id = "50000003"
type_id = "purchase"

class ShoppingDataLoader():
    def __init__(self, child_id, mid_id, root_id, type_id):
        request_url = f"https://search.shopping.naver.com/best/category/{type_id}?categoryCategoryId={child_id}&categoryChildCategoryId={child_id}&categoryDemo=A00&categoryMidCategoryId={mid_id}&categoryRootCategoryId={root_id}&period=P1D"
        self.data = self._load_data(request_url)
        self.child_id = child_id
        self.type_id = type_id
        self.child_name = id2childCategory[child_id]
        self.trend_type = id2type[type_id]
        self.date = get_today()


    def _load_data(self, url):
        source = urllib.request.urlopen(url).read()
        soup = bs4.BeautifulSoup(source, "lxml")
        trend_json = json.loads(soup.select("script#__NEXT_DATA__")[0].text)
        trend_queries = trend_json['props']['pageProps']['dehydratedState']['queries']
        for item in trend_queries:
            if item['queryKey'][0] == 'CATEGORY_PRODUCTS':
                trend_df = pd.DataFrame(item['state']['data']['products'][:10], columns=["rank", "imageUrl", "mobileLowPrice", "productTitle"])
                break
        return trend_df

    def save_image(self, save_dir, drop=True):
        for i, row in self.data.iterrows():
            save_img(row['imageUrl'], [self.date, self.child_id, row["rank"]], save_dir)
        if drop:
            self.data = self.data.drop(columns=["imageUrl"])
    
    def to_markdown(self):
        if "imageUrl" in self.data.columns:
            return self.data.drop(columns=["imageUrl"]).to_markdown()
        else:
            return self.data.to_markdown()
    
    def get_prompt(self, **kwargs):
        system_content = "제목 : {} {} {} 베스트 10 \n{}".format(self.date, self.child_name, self.trend_type, self.to_markdown())
        user_content = "오늘 {}의 {}을 요약해서 소개해줘".format(self.child_name, self.trend_type)
        return system_content, user_content
