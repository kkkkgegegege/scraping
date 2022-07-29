from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
import re
import pandas as pd
import time
from tqdm import tqdm
import sys
import os

filename = 'time_required.xlsx'
URL = 'https://transit.yahoo.co.jp/'
START_INPUT_TAG = '/html/body/div/div/div[2]/div[2]/div[1]/div[1]/div[2]/div[2]/form/dl[1]/dd/input'
END_INPUT_TAG = '/html/body/div/div/div[2]/div[2]/div[1]/div[1]/div[2]/div[2]/form/dl[2]/dd/input'
CITY_DF = pd.read_excel('適当\city.xlsx')
START_CITIES = list(CITY_DF['検索用'])
END_CITIES = ['東京都庁', '大阪市役所', '名古屋市役所', '京都市役所', '横浜市役所', '神戸市役所', '北九州市役所', '札幌市役所'
              , '川崎市役所', '福岡市役所', '広島市役所', '仙台市役所', '千葉市役所', 'さいたま市役所', '静岡市役所', '堺市役所'
              , '新潟市役所', '浜松市役所', '岡山市役所', '相模原市役所', '熊本市役所']

def is_file_exists(filename):
    return os.path.isfile(filename)

def get_last_data(filename):
    df = pd.read_excel(filename)
    last_data = df.tail(1)['start'].values[0]
    return last_data

def get_exsit_df(filename):
    df = pd.read_excel(filename)
    return df

def save_data(new_data, filename):
    if is_file_exists(filename):
        exsited_data = get_exsit_df(filename)
        df = pd.concat([new_data, exsited_data])
        df.drop_duplicates(inplace = True)
        df.to_excel(filename, index = False)
    else:
        new_data.to_excel(filename, index = False)

def input_location(driver, start_or_end, location_name):
    if start_or_end == 'start':
        driver.find_element_by_xpath(START_INPUT_TAG).send_keys(location_name)
    else:
        driver.find_element_by_xpath(END_INPUT_TAG).send_keys(location_name)

def check_no_time_specified(driver):
    driver.find_element_by_xpath('//*[@id="tsAvr"]').click()

def click_search_button(driver):
    driver.find_element_by_xpath('//*[@id="searchModuleSubmit"]').click()

def modify_time_format(time_required):
    if time_required.find('時間') > 0 and time_required.find('分') > 0:
        hour = time_required[:time_required.find('時間')]
        minute = time_required[time_required.find('時間')+2:time_required.find('分')]
        total_time = int(hour) * 60 + int(minute)
    elif time_required.find('時間') > 0:
        hour = time_required[:time_required.find('時間')]
        total_time = int(hour) * 60
    else:
        minute = time_required[:time_required.find('分')]
        total_time = int(minute)
    return total_time

def remove_unnecessary_str_from_data(data_type, data):
    if data_type == 'time':
        data = data.strip('[!]')
        data = data[:data.find('（')]
    elif data_type == 'num_of_transfers':
        data = re.sub(r'\D','', data)
        data = int(data)
    elif data_type == 'fee':
        data = data[data.find('：')+1:data.find('（')]
        data = data.strip(',円')
        data = data.replace(',','')
        data = int(data)
    return data

def get_required_data(driver):
    time_required = driver.find_element_by_xpath('//*[@id="route01"]/dl/dd[1]/ul/li[1]').text
    time_required = remove_unnecessary_str_from_data('time', time_required)
    time_required = modify_time_format(time_required)
    num_of_transfers = driver.find_element_by_xpath('//*[@id="route01"]/dl/dd[1]/ul/li[2]').text
    num_of_transfers = remove_unnecessary_str_from_data('num_of_transfers', num_of_transfers)
    fee = driver.find_element_by_xpath('//*[@id="route01"]/dl/dd[1]/ul/li[3]').text
    fee = remove_unnecessary_str_from_data('fee', fee)
    return time_required, num_of_transfers, fee

def main():
    global START_CITIES
    if is_file_exists(filename):
        last_data = get_last_data(filename)
        START_CITIES = START_CITIES[START_CITIES.index(last_data):]
    try:
        result = []
        for start_city in tqdm(START_CITIES):
            for end_city in END_CITIES:
                print(start_city, end_city)
                options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                options.add_argument("--no-sandbox")
                Chorome = webdriver.Chrome(ChromeDriverManager().install(), options=options)
                Chorome.get(URL)
                input_location(Chorome, 'start', start_city)
                input_location(Chorome, 'end', end_city)
                check_no_time_specified(Chorome)
                click_search_button(Chorome)
                try:
                    time_required, num_of_transfers, fee = get_required_data(Chorome)
                    result_dict = {
                        'start' : start_city
                        ,'end' : end_city
                        ,'time_required' : time_required
                        ,'num_of_transfers' : num_of_transfers
                        ,'fee' : fee
                    }
                except NoSuchElementException:
                    result_dict = {
                        'start' : start_city
                        ,'end' : end_city
                        ,'time_required' : 0
                        ,'num_of_transfers' : 0
                        ,'fee' : 0
                    }
                    print(f'{start_city}:search failed')
                result.append(result_dict)
                Chorome.quit()
                time.sleep(5)
        new_data = pd.DataFrame(result)
        save_data(new_data, filename)
    except WebDriverException:
        new_data = pd.DataFrame(result)
        save_data(new_data, filename)
        print('something went wrong')
    except KeyboardInterrupt:
        new_data = pd.DataFrame(result)
        save_data(new_data, filename)
        sys.exit('中断')
if __name__ == '__main__':
    main()