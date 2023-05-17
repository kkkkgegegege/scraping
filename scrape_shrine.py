import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
#寺：0705001
#神社:0705002
URL = 'https://www.navitime.co.jp/category/0705002/{prefecture_id}/'

def format_prefecture_id(prefecture_id: int) -> str:
    return str(prefecture_id).zfill(2)

def find_number_of_shrine(parsed_html) -> list:
    return parsed_html.find("ul", class_ = "shortcut-link-area").find_all("li")

def transform_string_to_dict(input_string):
    input_string = input_string.strip()
    pattern = r'^(.*?)\((\d+)\)$'
    match = re.match(pattern, input_string)
    if match:
        transformed_dict = {
            '市区町村' : match.group(1)
            ,'神社数' : int(match.group(2))}
    else:
        transformed_dict = {}
    return transformed_dict

def main():
    df = pd.DataFrame(columns=['市区町村', '神社数'])
    for prefecture_id in range(1, 48):
        prefecture_id = format_prefecture_id(prefecture_id)
        html = requests.get(URL.format(prefecture_id = prefecture_id))
        parsed_html = BeautifulSoup(html.text, 'html.parser')
        municiparity_links = find_number_of_shrine(parsed_html)
        results = [transform_string_to_dict(municiparity_link.text) for municiparity_link in municiparity_links]
        df = pd.concat([df, pd.DataFrame(results)])
    df.to_csv('./shrine.csv', index = False)
if __name__ == '__main__':
    main()