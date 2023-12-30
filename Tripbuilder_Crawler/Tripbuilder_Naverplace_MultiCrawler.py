import re
import os
import sys
import time
import warnings
import openpyxl
import pandas as pd

from pykospacing import Spacing
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

warnings.filterwarnings(action='ignore')


class NaverPlaceUrlCollecter:

    def UrlCollector(df):
        for i, keyword in enumerate(df['name'].tolist()):
            key = keyword
            naver_map_search_url = f'https://map.naver.com/p/search/{key}'

            driver.get(naver_map_search_url)
            time.sleep(5)

            try:
                driver.switch_to.frame('entryIframe')
                time.sleep(1)
                place = driver.find_element(
                    By.CSS_SELECTOR, "#_pcmap_list_scroll_container > ul > li:nth-child(1) > div.qbGlu > div.ouxiq > a:nth-child(1) > div > div > span.YwYLL")
                time.sleep(1)
                place.click()
                time.sleep(3)

                tmp = driver.current_url
                df['naverURL'][i] = tmp

            except:
                tmp = driver.current_url
                df['naverURL'][i] = tmp

        return df

    def NaverCodeMaker(df):
        for i in range(len(df['naverURL'])):
            url = df['naverURL'][i]

            if pd.isna(url):
                pass
            else:
                pattern = r'/place/(\d+)'
                match = re.search(pattern, url)

                if match:
                    extracted_number = match.group(1)
                    df['naverCode'][i] = extracted_number
                else:
                    df['naverCode'][i] = 0

        return df

    def ReviewUrlMaker(df):
        for i, cd in enumerate(df['naverCode']):
            final_url = f'https://pcmap.place.naver.com/restaurant/{cd}/review/visitor#'
            df['naverURL'][i] = final_url
            final_url_2 = f'https://pcmap.place.naver.com/restaurant/{cd}/review/ugc'
            df['naverBlogURL'][i] = final_url_2

        return df


class NaverPlaceReviewCollector():

    def NaverPlaceReviewCollector(df):
        count = 0
        current = 0
        goal = len(df['name'])

        rev = pd.DataFrame(data='', columns=['name', 'review', '총 리뷰 수', '상태'])
        rev['총 리뷰 수'] = ''
        rev['상태'] = ''

        rev_list = []

        for i in range(goal):

            current += 1
            print('진행상황 : ', current, '/', goal, sep="")

            driver.get(df['naverURL'][i])
            time.sleep(2)
            print('현재 수집중인 식당 : ', df['name'][i])

            while True:
                try:
                    driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    driver.find_element(
                        By.CSS_SELECTOR, '#app-root > div > div > div > div:nth-child(6) > div:nth-child(3) > div.place_section.k5tcc > div.NSTUp > div > a > span').click()
                    time.sleep(2)

                except NoSuchElementException:
                    break

            html = driver.page_source
            bs = BeautifulSoup(html, 'lxml')

            try:
                review_lists = bs.select('li.YeINN')

                rev['총 리뷰 수'][i] = len(review_lists)

                if len(review_lists) > 0:

                    for j, review in enumerate(review_lists):
                        try:
                            try:
                                time.sleep(1)

                                user_review = review.select(
                                    'div.ZZ4OK > a > span')

                                if len(user_review) > 0:
                                    rev['name'][i] = df['name'][i]
                                    rev_list.append([user_review[0].text])
                                    rev['review'][i] = rev_list
                                time.sleep(1)

                            except:
                                user_review = review.select(
                                    ' div.ZZ4OK.IwhtZ > a > span')

                                if len(user_review) > 0:
                                    rev['name'][i] = df['name'][i]
                                    rev_list.append([user_review[0].text])
                                    rev['review'][i] = rev_list

                                time.sleep(1)

                        except NoSuchElementException:
                            rev['상태'][i] = '리뷰 텍스트가 인식되지 않음'
                            continue

                else:
                    rev['상태'][i] = '리뷰 선택자가 인식되지 않음'
                    time.sleep(1)

            except NoSuchElementException:

                rev['name'][i] = df['name'][i]
                rev_list.append([''])
                rev['review'][i] = rev_list

                time.sleep(2)
                rev['상태'][i] = "리뷰가 존재하지 않음"

        return rev

    def BlogReviewUrlCollector(df):

        count = 0
        current = 0
        goal = len(df['name'])

        rev_list = []

        for i in range(goal):

            current += 1
            print('진행상황 : ', current, '/', goal, sep="")

            driver.get(df['naverBlogURL'][i])
            time.sleep(2)
            print('현재 수집중인 식당 : ', df['name'][i])

            while True:
                try:
                    time.sleep(1)
                    driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);")
                    driver.find_element(
                        By.XPATH, '/html/body/div[3]/div/div/div/div[6]/div[3]/div/div[2]/div/a').click()
                    time.sleep(2)

                except NoSuchElementException:
                    print("-모든 리뷰 더보기 완료-")
                    break

            html = driver.page_source
            bs = BeautifulSoup(html, 'lxml')

            try:
                time.sleep(1)
                review_lists = driver.find_elements(
                    By.CSS_SELECTOR, '#app-root > div > div > div > div:nth-child(6) > div:nth-child(3) > div > div.place_section_content > ul > li')

                print('총 리뷰 수 : ', len(review_lists))

                if len(review_lists) > 0:

                    for j, review in enumerate(review_lists):
                        try:
                            try:
                                time.sleep(1)

                                user_review = driver.find_element(
                                    By.CSS_SELECTOR, f'.place_section_content > ul > li:nth-child({j + 1}) > a')
                                blog_link = user_review.get_attribute('href')
                                rev_list.append([df['name'][i], blog_link])
                                time.sleep(1)

                            except:
                                user_review = driver.find_element(
                                    By.CSS_SELECTOR, f'.place_section_content > ul > li:nth-child({j + 1}) > a')
                                blog_link = user_review.get_attribute('href')
                                rev_list.append([df['name'][i], blog_link])
                                time.sleep(1)

                        except NoSuchElementException:
                            print('리뷰 텍스트가 인식되지 않음')
                            continue

                else:
                    print('리뷰 선택자가 인식되지 않음')
                    time.sleep(1)

            except NoSuchElementException:

                rev_list.append([df['name'][i], ''])
                time.sleep(2)
                print("리뷰가 존재하지 않음")

        column = ["name", "blog_link"]
        rev = pd.DataFrame(rev_list, columns=column)

        return rev

    def InfoCrawler():
        count = 0
        current = 0
        goal = len(df['name'])

        info_lst = []

        for i in range(goal):

            current += 1
            print('진행상황: ', current, '/', goal, sep="")

            driver.get(df['naverURL'][i])
            thisurl = df['naverURL'][i]
            time.sleep(2)
            print('현재 수집중인 식당: ', df['name'][i])

            try:
                try:
                    time.sleep(2)
                    more = driver.find_element(
                        By.CSS_SELECTOR, "#app-root > div > div > div > div:nth-child(5) > div > div:nth-child(2) > div.place_section_content > div > div.O8qbU.pSavy > div > a > div > div")
                    time.sleep(1)
                    more_button = more.find_element(
                        By.CSS_SELECTOR, "#app-root > div > div > div > div:nth-child(5) > div > div:nth-child(2) > div.place_section_content > div > div.O8qbU.pSavy > div > a > div > div > span")
                    time.sleep(1)
                    more.click()

                except:
                    pass

                titles = driver.find_element(
                    By.CSS_SELECTOR, "#app-root > div > div > div > div.place_section.no_margin.OP4V8 > div.zD5Nm.undefined")
                title_text = titles.text
                time.sleep(3)
                target_element = driver.find_element(
                    By.CSS_SELECTOR, '#app-root > div > div > div > div:nth-child(5) > div > div:nth-child(2) > div.place_section_content > div')
                text_content = target_element.text
                time.sleep(1)

                info_lst.append([df['name'][i], title_text, text_content])

            except Exception as e:
                print(f"에러 발생: {e}")

        column = ["name", "title_lst", "info_lst"]
        res = pd.DataFrame(info_lst, columns=column)

        # res 전처리 필요

        return res


class DataPreprocessing():

    def Preprocessing(df):
        df['preprocessed_text'] = ''

        for i in range(len(df)):
            origin = df['review'][i]
            text = re.sub(r'[^\w\s.]', '', origin)
            text2 = text.replace(" ", "")
            text2 = text2.replace("\n", "")
            txt = spacing(text2, ignore='pre2')

            df['preprocessed_text'][i] = txt

        return df
