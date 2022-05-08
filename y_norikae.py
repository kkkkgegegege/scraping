from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
import re
import pandas as pd
import time
from tqdm import tqdm
import sys

URL = 'https://transit.yahoo.co.jp/'
START_INPUT_TAG = '/html/body/div/body/div/div[1]/div[2]/div[1]/div[1]/div[2]/div[2]/form/dl[1]/dd/input'
END_INPUT_TAG = '/html/body/div/body/div/div[1]/div[2]/div[1]/div[1]/div[2]/div[2]/form/dl[2]/dd/input'
CITY_DF = pd.read_excel('city.xlsx')
START_CITIES = list(CITY_DF['検索用'])
END_CITIES = ['東京駅', '大阪駅']

def firefox_driver():
    options = Options()
    options.headless = True
    #user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
    #profile = webdriver.FirefoxProfile()
    #profile.set_preference("general.useragent.override", user_agent)
    driver = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver',options=options
                                #,firefox_profile=profile
                                )
    return driver

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
    try:
        result = []
        for start_city in tqdm(START_CITIES):
            for end_city in END_CITIES:
                firefox = firefox_driver()
                firefox.get(URL)
                input_location(firefox, 'start', start_city)
                input_location(firefox, 'end', end_city)
                check_no_time_specified(firefox)
                click_search_button(firefox)
                try:
                    time_required, num_of_transfers, fee = get_required_data(firefox)
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
                firefox.quit()
                time.sleep(5)
        pd.DataFrame(result).to_excel('time_required.xlsx')
    except KeyboardInterrupt:
        pd.DataFrame(result).to_excel('time_required.xlsx')
        sys.exit('中断')
if __name__ == '__main__':
    main()