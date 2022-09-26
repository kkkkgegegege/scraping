import datetime
import time
import re
import numpy as np
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException

address_list = ['東京都新宿区神楽坂1-3','東京都港区赤坂9-7-1']
URL = 'https://www.benricho.org/map_stationsearch/Chiriin/'

def launch_chrome_driver(is_headless = False):
    options = webdriver.ChromeOptions()
    if is_headless:
        options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    return driver

def delete_text_box(driver):
    driver.find_element_by_xpath('/html/body/div[5]/div/div[1]/main/div/div/article/form/div/div[1]/input[1]').clear()    

def search_address_on_website(driver, address):
    delete_text_box(driver)
    driver.find_element_by_xpath('/html/body/div[5]/div/div[1]/main/div/div/article/form/div/div[1]/input[1]').send_keys(address)
    time.sleep(5)
    driver.find_element_by_xpath('/html/body/div[5]/div/div[1]/main/div/div/article/form/div/div[1]/input[2]').click()
    time.sleep(5)
    return driver

def get_df_from_web(driver):
    data = driver.find_element_by_class_name('gyocolor')
    data_list = re.split('[\n " "]', data.text)
    data_array = np.array(data_list).reshape(int(len(data_list)/4),4)
    df = pd.DataFrame(data_array[1:], columns=data_array[0])
    return df

def remove_trash_from_raw_df(df):
    df['距離'] = df['距離'].str.replace('m', '').astype(int)
    return df

def append_adress_to_df(df, search_word):
    df['address'] = search_word
    return df

def main():
    try:
        Chrome = launch_chrome_driver()
        Chrome.get(URL)
        result_df = pd.DataFrame()
        for address in address_list:
            Chrome = search_address_on_website(Chrome, address)
            raw_df = get_df_from_web(Chrome)
            df = remove_trash_from_raw_df(raw_df)
            df = append_adress_to_df(df, address)
            result_df = pd.concat([result_df,df])
        result_df.to_excel('distance.xlsx')
    except:
        result_df.to_excel('distance.xlsx')
if __name__ == '__main__':
    main()