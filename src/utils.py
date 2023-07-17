import datetime
import requests

def save_img(img_url, fn_attrs, save_dir):
    img_response = requests.get(img_url, stream=True)
    fn_name = "_".join(map(str, fn_attrs))
    with open(f"{save_dir}/{fn_name}.jpg", "wb") as f:
        f.write(img_response.content)

def get_today():
    return datetime.date.today().strftime("%Y%m%d")