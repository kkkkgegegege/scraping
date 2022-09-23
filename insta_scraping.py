from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import re
import pandas as pd
import time
import datetime


INSTAGRAM = 'https://www.instagram.com/'
TEXT_TAG = '_a9zr'
TIME_TAG = '_aaqe'

COMPANY_NAME = 'rohto'
COMPANY_PAGE = 'https://www.instagram.com/rohto_official/'
START_DATE = datetime.datetime(2022,9,10)
END_DATE = datetime.datetime(2022,9,20)

def launch_chrome_driver(is_headless = False):
    options = webdriver.ChromeOptions()
    if is_headless:
        options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    return driver

def login_and_move_to_target_page(driver, id, passward, target_page):
    driver.get(INSTAGRAM)
    time.sleep(5)
    driver.find_element_by_xpath('/html/body/div[1]/section/main/article/div[2]/div[1]/div[2]/form/div/div[1]/div/label/input').send_keys(id)
    driver.find_element_by_xpath('/html/body/div[1]/section/main/article/div[2]/div[1]/div[2]/form/div/div[2]/div/label/input').send_keys(passward)
    driver.find_element_by_xpath('/html/body/div[1]/section/main/article/div[2]/div[1]/div[2]/form/div/div[3]/button').click()
    time.sleep(5)
    driver.get(target_page)
    return driver

def scroll_page(driver):
    driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
    time.sleep(3)

def get_urls_from_visible_range(driver):
    url_elements = driver.find_elements_by_xpath("//a[@href]")
    urls = [url_element.get_attribute('href') for url_element in url_elements]
    return urls

def get_all_urls_from_homepage(driver, scroll_num):
    all_urls = []
    for _ in range(scroll_num):
        scroll_page(driver)
        part_of_urls = get_urls_from_visible_range(driver)
        all_urls.extend(part_of_urls)
    return all_urls

def remove_unnecessary_url(urls):
    return [i for i in urls if re.search('https://www.instagram.com/p/*', i) is not None]

def get_posted_text(driver, tag):
    text = driver.find_element_by_class_name(tag).text
    return text

def get_posted_time(driver):
    time_elms = driver.find_elements_by_tag_name("time")
    posted_date = time_elms[0].get_attribute("datetime")
    return datetime.datetime.strptime(posted_date, '%Y-%m-%dT%H:%M:%S.%f%z')

def get_text_and_time_to_df(driver, urls):
    result_list = []
    for url in urls:
        driver.get(url)
        time.sleep(5)
        posted_text = get_posted_text(driver, TEXT_TAG)
        posted_time = get_posted_time(driver)
        result_dict ={
            'text':posted_text,
            'time':posted_time.date()
        }
        result_list.append(result_dict)
    df = pd.DataFrame(result_list)
    return df

def narrow_down_specific_period(df, start_date, end_date):
    return df[(df['time']>=start_date.date()) & (df['time']<=end_date.date())]

def main():
    Chrome = launch_chrome_driver()
    Chrome = login_and_move_to_target_page(Chrome, 'XXXX', 'XXXX', COMPANY_PAGE)
    urls = get_all_urls_from_homepage(Chrome, scroll_num = 1)
    urls = remove_unnecessary_url(urls)
    df = get_text_and_time_to_df(Chrome, urls)
    target_df = narrow_down_specific_period(df, START_DATE, END_DATE)
    target_df.to_excel(f'{COMPANY_NAME}.xlsx', index = False)
if __name__ == '__main__':
    main()
