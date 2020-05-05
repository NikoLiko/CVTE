# -*- coding: utf-8 -*-
import os
import json
import urllib.request
import zlib
import random
import sys
import time
import requests

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException, TimeoutException, NoSuchElementException, ElementNotInteractableException, JavascriptException

project_path = os.getcwd()
split = '\\'
already = []
already_file = ""
folder = sys.argv[1]
one_in_three = sys.argv[2]
# 这里使用25-30分钟的ip
order_id = "928855456333631"
api_key = "3uauz6ng1yet7jx46q6flwxc17p33a3m"


# 请求代理ip，直接返回代理字符串
def get_ip():
    ran = [1, 2]
    seed = random.choice(ran)
    if seed == 0:
        # 这里不使用代理
        return None
    else:
        # 尝试请求代理
        api_url = "http://dps.kdlapi.com/api/getdps/?orderid={}&num=1&pt=1&sep=1".format(order_id)
        headers = {"Accept-Encoding": "Gzip"}  #使用gzip压缩传输数据让访问更快
        req = urllib.request.Request(url=api_url, headers=headers)
        # 请求api链接
        res = urllib.request.urlopen(req)
        content_encoding = res.headers.get('Content-Encoding')
        if content_encoding and "gzip" in content_encoding:
            proxy = zlib.decompress(res.read(), 16 + zlib.MAX_WBITS).decode('utf-8')  #获取页面内容
            # 在这里检测ip
            test_url = "https://dps.kdlapi.com/api/checkdpsvalid?orderid={}&signature={}&proxy={}".format(order_id, api_key, proxy)
            response = requests.get(test_url)
            if "true" in response.text:
                print("ip经检测后可用")
                return proxy
            else:
                return None
        else:
            print(res.read().decode('utf-8'))
            return None


def isNotSelected(info):
    status = info.get_attribute('aria-expanded')
    if status == 'false':
        return True
    else:
        return False


# python main.py p2 pro_line
def check_env():

    global already
    # 两个文件夹路径确定，content多一级菜单，因为要存储三份
    url_folder = project_path + split + "url_list" + split + folder
    content_folder = project_path + split + "content_list" + split + one_in_three + split + folder
    global already_file
    already_file = project_path + split + "already_list" + split + one_in_three + ".txt"
    # 这里新建文件夹
    if not os.path.exists(content_folder):
        os.makedirs(content_folder)

    if os.path.exists(already_file):
        with open(already_file, 'r') as f:
            already_temp = f.read().split()
            already = [int(x) for x in already_temp]
    return url_folder, content_folder


def get_school_id(file):
    with open(file, "r") as f:
        return eval(f.read())


def run_webdriver_pro_line(id, browser):
    content_list = []
    school_id = id
    flag = 1
    try:
        browser.get("https://gkcx.eol.cn/school/{}/provinceline".format(id))
        wait = WebDriverWait(browser, 10)
        schoolname = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'line1-schoolName'))).text
        print("爬取{}".format(id))
        btn_pro = browser.find_elements_by_class_name("ant-select-selection--single")[0]
        btn_subject = browser.find_elements_by_class_name("ant-select-selection--single")[1]
        btn_pro.click()
        pro_list = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "ant-select-dropdown-menu-item")))
        js = "document.getElementsByClassName('ant-select-dropdown-menu')[0].setAttribute('id', 'pro_list');"
        browser.execute_script(js)
        btn_subject.click()
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ant-select-dropdown-menu-item")))
        js = "document.getElementsByClassName('ant-select-dropdown-menu')[1].setAttribute('id', 'subject_list');"
        browser.execute_script(js)
        btn_pro.click()
        wait.until(EC.visibility_of_all_elements_located((By.ID, "pro_list")))
    except (StaleElementReferenceException, ElementClickInterceptedException, TimeoutException, IndexError, ElementNotInteractableException, JavascriptException):
        print("页面加载出错，放弃{}".format(id))
        flag = 0
        browser.close()
        return None, flag
    # 这一部分分开的原因是因为，学校名没有爬取到，可以通过id来对应
    for pro in pro_list:
        try:
            if isNotSelected(btn_pro):
                btn_pro.click()
            time.sleep(0.5)
            wait.until(EC.visibility_of_all_elements_located((By.ID, "pro_list")))
            pro.click()
            btn_subject.click()
            wait.until(EC.visibility_of_all_elements_located((By.ID, "subject_list")))
            subject_list = browser.find_element_by_id("subject_list").find_elements_by_tag_name("li")
            for sub in subject_list:
                if isNotSelected(btn_subject):
                    btn_subject.click()
                wait.until(EC.visibility_of_all_elements_located((By.ID, "subject_list")))
                sub.click()
                box = browser.find_elements_by_class_name("schoolLine")[0]
                li_list = box.find_elements_by_tag_name("li")
                tbody = browser.find_elements_by_tag_name("tbody")[0]
                tr_list = tbody.find_elements_by_tag_name("tr")
                if len(tr_list) == 1:
                    continue
                for tr in range(1, len(tr_list)):
                    province = browser.find_elements_by_class_name("ant-select-selection-selected-value")[0].get_attribute("innerText")
                    subject = browser.find_elements_by_class_name("ant-select-selection-selected-value")[1].get_attribute("innerText")
                    if province == "" or subject == "":
                        continue
                    s = []
                    s.append(school_id)
                    s.append(schoolname)
                    s.append(province)
                    s.append(subject)
                    s.extend(tr_list[tr].text.split())
                    print(s)
                    content_list.append(s)
                if len(li_list) > 3:
                    li_list = li_list[2:-1]
                    for li in li_list:
                        li.click()
                        time.sleep(1)
                        try:
                            tbody = browser.find_elements_by_tag_name("tbody")[2]
                            tr_list = tbody.find_elements_by_tag_name("tr")
                            if len(tr_list) == 1:
                                continue
                            for tr in range(1, len(tr_list)):
                                s = []
                                s.append(school_id)
                                s.append(schoolname)
                                s.append(province)
                                s.append(subject)
                                s.extend(tr_list[tr].text.split())
                                print(s)
                                content_list.append(s)
                        except (StaleElementReferenceException, ElementClickInterceptedException, TimeoutException, IndexError, ElementNotInteractableException):
                            print("翻页错误，跳过这一页")
                            flag = 0
                            pass
        except (StaleElementReferenceException, ElementClickInterceptedException, TimeoutException, IndexError, ElementNotInteractableException) as e:
            print("出现异常，这条Pass")
            print("错误是：", e)
            flag = 0
    if content_list:
        browser.close()
        return content_list, flag
    else:
        browser.close()
        return None, flag


def run_webdriver_enrollment_plan(id, browser):
    content_list = []
    school_id = id
    flag = 1
    try:
        browser.get("https://gkcx.eol.cn/school/{}/provinceline".format(id))
        wait = WebDriverWait(browser, 10)
        schoolname = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'line1-schoolName'))).text
        print("爬取{}".format(id))
        btn_pro = browser.find_elements_by_class_name("ant-select-selection--single")[2]
        btn_year = browser.find_elements_by_class_name("ant-select-selection--single")[4]
        btn_subject = browser.find_elements_by_class_name("ant-select-selection--single")[3]
        btn_batch = browser.find_elements_by_class_name("ant-select-selection--single")[5]
        btn_pro.click()
        pro_list = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "ant-select-dropdown-menu-item")))
        js = "document.getElementsByClassName('ant-select-dropdown-menu')[0].setAttribute('id', 'pro_list');"
        browser.execute_script(js)
        btn_year.click()
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ant-select-dropdown-menu-item")))
        js = "document.getElementsByClassName('ant-select-dropdown-menu')[1].setAttribute('id', 'year_list');"
        browser.execute_script(js)
        btn_subject.click()
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ant-select-dropdown-menu-item")))
        js = "document.getElementsByClassName('ant-select-dropdown-menu')[2].setAttribute('id', 'subject_list');"
        browser.execute_script(js)
        btn_batch.click()
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ant-select-dropdown-menu-item")))
        js = "document.getElementsByClassName('ant-select-dropdown-menu')[3].setAttribute('id', 'batch_list');"
        browser.execute_script(js)
        btn_pro.click()
        wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//ul[@id='pro_list']/li")))
    except (StaleElementReferenceException, ElementClickInterceptedException, TimeoutException, IndexError, ElementNotInteractableException, JavascriptException):
        print("页面加载出错，放弃{}".format(id))
        flag = 0
        browser.close()
        return None, flag
    for pro in pro_list:
        try:
            if isNotSelected(btn_pro):
                btn_pro.click()
            wait.until(EC.visibility_of_all_elements_located((By.ID, "pro_list")))
            pro.click()
            btn_year.click()
            year_list = wait.until(EC.presence_of_all_elements_located((By.ID, "year_list")))
            year_list = browser.find_element_by_id("year_list").find_elements_by_tag_name("li")
            for year in year_list:
                if isNotSelected(btn_year):
                    btn_year.click()
                wait.until(EC.visibility_of_all_elements_located((By.ID, "year_list")))
                year.click()
                btn_subject.click()
                subject_list = wait.until(EC.presence_of_all_elements_located((By.ID, "subject_list")))
                subject_list = browser.find_element_by_id("subject_list").find_elements_by_tag_name("li")
                for sub in subject_list:
                    if isNotSelected(btn_subject):
                        btn_subject.click()
                    wait.until(EC.visibility_of_all_elements_located((By.ID, "subject_list")))
                    sub.click()
                    btn_batch.click()
                    batch_list = wait.until(EC.presence_of_all_elements_located((By.ID, "batch_list")))
                    batch_list = browser.find_element_by_id("batch_list").find_elements_by_tag_name("li")
                    for batch in batch_list:
                        if isNotSelected(btn_batch):
                            btn_batch.click()
                        wait.until(EC.visibility_of_all_elements_located((By.ID, "batch_list")))
                        batch.click()
                        time.sleep(1)
                        box = browser.find_elements_by_class_name("schoolLine")[1]
                        li_list = box.find_elements_by_tag_name("li")
                        tbody = browser.find_elements_by_tag_name("tbody")[1]
                        tr_list = tbody.find_elements_by_tag_name("tr")
                        if len(tr_list) == 1:
                            continue
                        for tr in range(1, len(tr_list)):
                            province = browser.find_elements_by_class_name("ant-select-selection-selected-value")[2].get_attribute("innerText")
                            which_year = browser.find_elements_by_class_name("ant-select-selection-selected-value")[4].get_attribute("innerText")
                            subject = browser.find_elements_by_class_name("ant-select-selection-selected-value")[3].get_attribute("innerText")
                            ba = browser.find_elements_by_class_name("ant-select-selection-selected-value")[5].get_attribute("innerText")
                            if province == "" or which_year == "" or subject == "" or ba == "":
                                continue
                            s = []
                            s.append(school_id)
                            s.append(schoolname)
                            s.append(province)
                            s.append(which_year)
                            s.append(subject)
                            s.append(ba)
                            s.extend(tr_list[tr].text.split())
                            print(s)
                            content_list.append(s)
                        if len(li_list) > 3:
                            li_list = li_list[2:-1]
                            for li in li_list:
                                li.click()
                                time.sleep(1)
                                try:
                                    tbody = browser.find_elements_by_tag_name("tbody")[1]
                                    tr_list = tbody.find_elements_by_tag_name("tr")
                                    if len(tr_list) == 1:
                                        continue
                                    for tr in range(1, len(tr_list)):
                                        s = []
                                        s.append(school_id)
                                        s.append(schoolname)
                                        s.append(province)
                                        s.append(which_year)
                                        s.append(subject)
                                        s.append(ba)
                                        s.extend(tr_list[tr].text.split())
                                        print(s)
                                        content_list.append(s)
                                except (StaleElementReferenceException, ElementClickInterceptedException, TimeoutException, IndexError, ElementNotInteractableException):
                                    print("翻页错误，跳过这一页")
                                    flag = 0
                                    pass
        except (StaleElementReferenceException, ElementClickInterceptedException, TimeoutException, IndexError, ElementNotInteractableException) as e:
            print("出现异常，这条Pass")
            print("错误是：", e)
            flag = 0
    if content_list:
        browser.close()
        return content_list, flag
    else:
        browser.close()
        return None, flag


def run_webdriver_professional_score(id, browser):
    content_list = []
    school_id = id
    flag = 1
    try:
        browser.get("https://gkcx.eol.cn/school/{}/provinceline".format(id))
        wait = WebDriverWait(browser, 10)
        schoolname = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'line1-schoolName'))).text
        print("爬取{}".format(id))
        btn_pro = browser.find_elements_by_class_name("ant-select-selection--single")[6]
        btn_year = browser.find_elements_by_class_name("ant-select-selection--single")[8]
        btn_subject = browser.find_elements_by_class_name("ant-select-selection--single")[7]
        btn_pro.click()
        pro_list = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "ant-select-dropdown-menu-item")))
        js = "document.getElementsByClassName('ant-select-dropdown-menu')[0].setAttribute('id', 'pro_list');"
        browser.execute_script(js)
        btn_year.click()
        time.sleep(0.5)
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ant-select-dropdown-menu-item")))
        js = "document.getElementsByClassName('ant-select-dropdown-menu')[1].setAttribute('id', 'year_list');"
        browser.execute_script(js)
        btn_subject.click()
        time.sleep(0.5)
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ant-select-dropdown-menu-item")))
        js = "document.getElementsByClassName('ant-select-dropdown-menu')[2].setAttribute('id', 'subject_list');"
        browser.execute_script(js)
    except (StaleElementReferenceException, ElementClickInterceptedException, TimeoutException, IndexError, ElementNotInteractableException, JavascriptException):
        print("页面加载出错，放弃{}".format(id))
        flag = 0
        browser.close()
        return None, flag
    # 在这个位置btn_pro是点开的
    for pro in pro_list:
        try:
            if isNotSelected(btn_pro):
                btn_pro.click()
            wait.until(EC.visibility_of_all_elements_located((By.ID, "pro_list")))
            pro.click()
            btn_year.click()
            year_list = wait.until(EC.presence_of_all_elements_located((By.ID, "year_list")))
            year_list = browser.find_element_by_id("year_list").find_elements_by_tag_name("li")
            # province = browser.find_elements_by_class_name("ant-select-selection-selected-value")[6].get_attribute("innerText")
            for year in year_list:
                if isNotSelected(btn_year):
                    btn_year.click()
                wait.until(EC.visibility_of_all_elements_located((By.ID, "year_list")))
                year.click()
                btn_subject.click()
                subject_list = wait.until(EC.presence_of_all_elements_located((By.ID, "subject_list")))
                subject_list = browser.find_element_by_id("subject_list").find_elements_by_tag_name("li")
                # which_year = browser.find_elements_by_class_name("ant-select-selection-selected-value")[8].get_attribute("innerText")
                for sub in subject_list:
                    if isNotSelected(btn_subject):
                        btn_subject.click()
                    wait.until(EC.visibility_of_all_elements_located((By.ID, "subject_list")))
                    sub.click()
                    time.sleep(1)
                    # subject = browser.find_elements_by_class_name("ant-select-selection-selected-value")[7].get_attribute("innerText")
                    box = browser.find_elements_by_class_name("schoolLine")[2]
                    li_list = box.find_elements_by_tag_name("li")
                    tbody = browser.find_elements_by_tag_name("tbody")[2]
                    tr_list = tbody.find_elements_by_tag_name("tr")
                    if len(tr_list) == 1:
                        continue
                    for tr in range(1, len(tr_list)):
                        province = browser.find_elements_by_class_name("ant-select-selection-selected-value")[6].get_attribute("innerText")
                        which_year = browser.find_elements_by_class_name("ant-select-selection-selected-value")[8].get_attribute("innerText")
                        subject = browser.find_elements_by_class_name("ant-select-selection-selected-value")[7].get_attribute("innerText")
                        if province == "" or which_year == "" or subject == "":
                            continue
                        s = []
                        s.append(school_id)
                        s.append(schoolname)
                        s.append(province)
                        s.append(which_year)
                        s.append(subject)
                        s.extend(tr_list[tr].text.split())
                        print(s)
                        content_list.append(s)
                    if len(li_list) > 3:
                        li_list = li_list[2:-1]
                        for li in li_list:
                            li.click()
                            time.sleep(1)
                            try:
                                tbody = browser.find_elements_by_tag_name("tbody")[2]
                                tr_list = tbody.find_elements_by_tag_name("tr")
                                if len(tr_list) == 1:
                                    continue
                                for tr in range(1, len(tr_list)):
                                    s = []
                                    s.append(school_id)
                                    s.append(schoolname)
                                    s.append(province)
                                    s.append(which_year)
                                    s.append(subject)
                                    s.extend(tr_list[tr].text.split())
                                    print(s)
                                    content_list.append(s)
                            except (StaleElementReferenceException, ElementClickInterceptedException, TimeoutException, IndexError, ElementNotInteractableException):
                                print("翻页错误，跳过这一页")
                                flag = 0
                                pass
            #         btn_subject.click()
            #     btn_year.click()
            #     wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ant-select-dropdown")))
            # btn_pro.click()
            # wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ant-select-dropdown")))
        except (StaleElementReferenceException, ElementClickInterceptedException, TimeoutException, IndexError, ElementNotInteractableException) as e:
            print("出现异常，这条Pass")
            print("错误是：", e)
            flag = 0
            if isNotSelected(btn_pro):
                btn_pro.click()
            time.sleep(1)
    if content_list:
        browser.close()
        return content_list, flag
    else:
        browser.close()
        return None, flag


def handle_pro_line(l, flag, id, content_path):
    if l is not None:
        with open(already_file, "a") as f:
            f.write(" " + str(id) + " ")
        print("{}爬取完毕，写入".format(id))
        with open(content_path, 'a') as f:
            f.write(str(l))
    if flag == 0:
        # 在网页没有全部爬取的情况下
        with open("uncrawl" + split + "pro_line", 'a') as f:
            f.write(str(id) + " ")


def handle_professional_score(l, flag, id, content_path):
    if l is not None:
        with open(already_file, "a") as f:
            f.write(" " + str(id) + " ")
        print("{}爬取完毕，写入".format(id))
        with open(content_path, 'a') as f:
            f.write(str(l))
    if flag == 0:
        # 在网页没有全部爬取的情况下
        with open("uncrawl" + split + "professional_score", 'a') as f:
            f.write(str(id) + " ")


def handle_enrollment_plan(l, flag, id, content_path):
    if l is not None:
        with open(already_file, "a") as f:
            f.write(" " + str(id) + " ")
        print("{}爬取完毕，写入".format(id))
        with open(content_path, 'a', encoding='utf-8') as f:
            f.write(str(l))
    if flag == 0:
        # 在网页没有全部爬取的情况下
        with open("uncrawl" + split + "enrollment_plan", 'a') as f:
            f.write(str(id) + " ")


def main(url_folder, content_folder):
    url_file_list = os.listdir(url_folder)
    for file in url_file_list:
        id_list = get_school_id(url_folder + split + file)
        one_root_file_content = []
        # 用来记录哪些id确实被爬取了
        a_list = []
        for id in id_list:
            if id in already:
                print("{}已经爬取".format(id))
                continue
            print("更改代理")
            ip = get_ip()
            if ip is None:
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--no-sandbox')
                # browser = webdriver.Chrome(chrome_options=chrome_options, executable_path="/home/qizhang/downloads/chromedriver")
                browser = webdriver.Chrome(chrome_options=chrome_options)
                print("浏览器重启成功，不使用代理")
            else:
                chrome_options = webdriver.ChromeOptions()
                # chrome_options.add_argument('--headless')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument("--proxy-server={}".format(ip))
                # browser = webdriver.Chrome(chrome_options=chrome_options, executable_path="/home/qizhang/downloads/chromedriver")
                browser = webdriver.Chrome(chrome_options=chrome_options)
                print("浏览器重启成功，使用的代理是{}".format(ip))
            if one_in_three == 'pro_line':
                l, flag = run_webdriver_pro_line(id, browser)
                content_path = content_folder + split + str(id_list[0]) + "_" + str(id_list[-1])
                handle_pro_line(l, flag, id, content_path)
            elif one_in_three == 'professional_score':
                l, flag = run_webdriver_professional_score(id, browser)
                content_path = content_folder + split + str(id_list[0]) + "_" + str(id_list[-1])
                handle_professional_score(l, flag, id, content_path)
            elif one_in_three == 'enrollment_plan':
                l, flag = run_webdriver_enrollment_plan(id, browser)
                content_path = content_folder + split + str(id_list[0]) + "_" + str(id_list[-1])
                handle_enrollment_plan(l, flag, id, content_path)
            else:
                print("输入有误！")
                exit()
        print("一个文件爬取成功")






