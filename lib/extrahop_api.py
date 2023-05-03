# rewrite from ExtraHop code-example
# https://github.com/ExtraHop/code-examples/tree/main/py_rx360_auth
# License: https://github.com/ExtraHop/code-examples/blob/main/LICENSE

import requests
import base64
from dotenv import load_dotenv
import os
from termcolor import colored
from requests.exceptions import MissingSchema
from datetime import datetime, timedelta
import re
import json
from requests.packages import urllib3
from getpass import getpass

class ExtrahopApi:
    def __init__(self):
        urllib3.disable_warnings()
        self.check_env()
        self.get_token()
    
    def check_env(self):
        if not os.path.isdir("data"):
            os.mkdir("data")
        if not os.path.isfile("lib/.env"):
            self.new_customer()
        else:
            self.load_config()
        return None

    def new_customer(self):
        try_times = 3
        if os.path.isfile("data/customers.txt"):
            with open("data/customers.txt", "r") as fr:
                self.customers = fr.read().strip("\n")
        else:
            self.customers = []
        while try_times > 0:
            print(colored("[新增客戶]", "green"))
            self.customer = input("請輸入客戶名稱: ")
            if self.customer in self.customers:
                print(colored("此客戶已存在，請重新輸入", "red"))
                try_times -= 1
                continue
            device = input("請輸入設備種類(1. 雲端 2. 地端): ")
            if device == "1":
                self.HOST = input("請輸入 API Endpoint: ")
                if self.HOST.endswith("/oauth/token"):
                    self.HOST = self.HOST.replace("/oauth/token", "")
                self.ID = input("請輸入 ID: ")
                self.SECRET = input("請輸入 SECRET: ")
                self.device = "cloud"
            elif device == "2":
                self.HOST = input("請輸入 API Endpoint: ")
                if self.HOST.endswith("/oauth/token"):
                    self.HOST = self.HOST.replace("/oauth/token", "")
                self.API_KEY = input("請輸入 API_KEY: ")
                self.device = "local"
            else:
                print(colored("輸入錯誤，請重新輸入", "red"))
                try_times -= 1
                continue
            try:
                # self.get_info("apikeys")
                self.get_token()
            # except AttributeError:
            except (ConnectionError, KeyError, MissingSchema):
                print(colored("輸入錯誤，請重新輸入", "red"))
                try_times -= 1
                continue
            with open("lib/.env", "a") as fa:
                if self.device == "cloud":
                    fa.write(f"{self.customer}_HOST={self.HOST}\n{self.customer}_ID={self.ID}\n{self.customer}_SECRET={self.SECRET}\n")
                else:
                    fa.write(f"{self.customer}_HOST={self.HOST}\n{self.customer}_API_KEY={self.API_KEY}\n")
            with open("data/customers.txt", "a") as fa:
                fa.write(f"\n{self.customer}")
            print(colored("新增客戶成功!", "green"))
            return None 
        print(colored("錯誤次數已達 3 次，程式終止", "yellow"))
        exit(1)   

    def load_config(self):
        load_dotenv("lib/.env")
        with open("data/customers.txt", "r") as fr:
            self.customers = fr.read().strip("\n")
        while True:
            self.customer = input("請輸入客戶名稱: ")
            if self.customer not in self.customers:
                check_wrong_customer = input(f"目前不存在客戶名稱 " + colored(f"{self.customer}", "blue") + "\n1. 新增客戶 2. 重新輸入: ")
                if check_wrong_customer == "1":
                    self.new_customer()
                    break
            elif os.getenv(f"{self.customer}_ID") == None:
                self.HOST = os.getenv(f"{self.customer}_HOST")
                self.API_KEY = os.getenv(f"{self.customer}_API_KEY")
                self.device = "local"
                break
            else: 
                self.HOST = os.getenv(f"{self.customer}_HOST")
                self.ID = os.getenv(f"{self.customer}_ID")
                self.SECRET = os.getenv(f"{self.customer}_SECRET")
                self.device = "cloud"
                break
        return None 
    
    def get_start_time(self):
        start_time = input("請輸入開始時間(yyyymmdd): ")
        pattern = r'^\d{8}$'
        while True:
            if re.match(pattern, start_time):
                try:
                    self.start_time = datetime.strptime(start_time, '%Y%m%d')
                    break
                except ValueError:
                    start_time = input(colored("日期錯誤，請輸入日期格式 yyyymmdd: ", "yellow"))
            else:
                start_time = input(colored("日期錯誤，請輸入日期格式 yyyymmdd: ", "yellow"))

    def get_end_time(self):
        end_time = input("請輸入結束時間(yyyymmdd): ")
        pattern = r'^\d{8}$'
        while True:
            if re.match(pattern, end_time):
                try:
                    self.end_time = datetime.strptime(end_time, '%Y%m%d')
                    break
                except ValueError:
                    end_time = input(colored("日期錯誤，請輸入日期格式 yyyymmdd: ", "yellow"))
            else:
                end_time = input(colored("日期錯誤，請輸入日期格式 yyyymmdd: ", "yellow"))

    def get_token(self):
        # get token to access ExtraHop REST API
        if self.device == "cloud":
            auth = base64.b64encode(bytes(self.ID + ":" + self.SECRET, "utf-8")).decode("utf-8")
            headers = {
                "Authorization": "Basic " + auth,
                "Content-Type": "application/x-www-form-urlencoded",
            }
            url = self.HOST + "/oauth2/token"
            r = requests.post(
                url, headers=headers, data="grant_type=client_credentials", verify=False
            )
            self.token = r.json()["access_token"]
            return None
        else:
            return None
    
    def get_info(self, page, params=None):
        # use GET method to get data
        try:
            headers = {
                "Authorization": "Bearer " + self.token
            }
        except AttributeError:
            headers = {
                "accept": "application/json",
                "Authorization": "ExtraHop apikey=" + self.API_KEY,
            }
        url = self.HOST + "/api/v1" + f"/{page}"
        r = requests.get(url, headers=headers, params=params, verify=False)
        return r
    
    def post_info(self, page, payload):
        # use POST method to get data
        try:
            headers = {
                "Authorization": "Bearer " + self.token
            }
        except AttributeError:
            headers = {
                "accept": "application/json",
                "Authorization": "ExtraHop apikey=" + self.API_KEY,
            }
        url = self.HOST + "/api/v1" + f"/{page}"
        r = requests.post(url, headers=headers, json=payload, verify=False)
        return r
    
    def patch_info(self, page, payload):
        # use PATCH method to get data
        try:
            headers = {
                "Authorization": "Bearer " + self.token
            }
        except AttributeError:
            headers = {
                "accept": "application/json",
                "Authorization": "ExtraHop apikey=" + self.API_KEY,
            }
        url = self.HOST + "/api/v1" + f"/{page}"
        r = requests.patch(url, headers=headers, json=payload, verify=False)
        return r
