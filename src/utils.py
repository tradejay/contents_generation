import os
import datetime
import requests

def save_img(img_url, fn_attrs, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    img_response = requests.get(img_url, stream=True)
    fn_name = "_".join(map(str, fn_attrs))
    with open(f"{save_dir}/{fn_name}.jpg", "wb") as f:
        f.write(img_response.content)

def get_today():
    return datetime.date.today().strftime("%Y%m%d")

def save_text(text, fn_attrs, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    fn_name = "_".join(map(str, fn_attrs))
    with open(f"{save_dir}/{fn_name}.txt", "w") as f:
        f.write(text)