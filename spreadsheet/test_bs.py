import requests
from pathlib import Path
import pickle
from bs4 import BeautifulSoup
import numpy as np

from test_ftp import ftp_connector, FtpHandler, spreadsheet_connector

class admvs_handler:

    def __init__(self):
        self.domain_list = []
        self.csv_exist_list = []
        self.csv_imported_list = []
        self.csv_synced_list = []
        self.index_list = []

        # self.session = self.create_session()
        self.create_session()

        self.domain_list_html = self.get_html("https://advms.sizebook.jp/sftpgit/site/")
        self.client_list_html = self.get_html("https://advms.sizebook.jp/client/")
        self.get_admvs_list()

    def create_session(self):
        self.payload = {
            "csrfmiddlewaretoken": "",
            "username": "",
            "password": ""
        }

        with open("password.txt", "r") as f:
            self.payload["username"] = f.readline().strip()
            self.payload["password"] = f.readline().strip()

        self.session = requests.Session()
        res = self.session.get("https://advms.sizebook.jp/accounts/login/?next=/sftpgit/site/")
        soup = BeautifulSoup(res.text, "lxml")
        self.payload["csrfmiddlewaretoken"] = soup.find(attrs={"name": "csrfmiddlewaretoken"}).get("value")
        print("payload : {}".format(self.payload["csrfmiddlewaretoken"]))
        res = self.session.post("https://advms.sizebook.jp/accounts/login/", data=self.payload)
        res.raise_for_status()

    def get_html(self, url):
        res = self.session.get(url)
        res.raise_for_status()
        return res.text
    
    def get_table_head_and_body(self, html):
        soup = BeautifulSoup(html, "lxml")
        table = soup.find(attrs={"id": "data_table"})
        thead = table.find("thead")
        tbody = table.find("tbody")

        return thead, tbody

    def get_table_list(self, tbody, index_list):
        list_num = len(index_list)
        table_list = [[] for _ in range(list_num)]
        
        for tr in tbody.findAll("tr"):
            td_list = [td.get_text() for td in tr.findAll("td")]
            for i in range(list_num):
                table_list[i] += [td_list[index_list[i]]]

        return table_list
    
    def get_admvs_list(self):
        thead, tbody = self.get_table_head_and_body(self.domain_list_html)
    
        header_list = [th.get_text()  for th in thead.findAll("th")]
        idx_idx = header_list.index("#")
        name_idx = header_list.index("名前")
        csv_exist_idx = header_list.index("検索管理機能有効")
        csv_imported_idx = header_list.index("商品データ登録済み")
        csv_synced_idx = header_list.index("data.csv同期済み")
        index_list = [idx_idx, name_idx, csv_exist_idx, csv_imported_idx, csv_synced_idx]

        self.index_list, self.domain_list, self.csv_exist_list, self.csv_imported_list, self.csv_synced_list =\
            self.get_table_list(tbody, index_list)
        
        return self.domain_list, self.csv_exist_list, self.csv_imported_list

    def get_client_list(self):
        thead, tbody = self.get_table_head_and_body(self.client_list_html)
        header_list = [th.get_text() for th in thead.findAll("th")]

        pk_idx = header_list.index("#")
        name_idx = header_list.index("名前")

        pk_list, name_list = self.get_table_list(tbody, [pk_idx, name_idx])

        return pk_list, name_list

    def get_multi_report_list(self, pk):
        html = self.get_html("https://advms.sizebook.jp/client/{}/multireport".format(pk))
        thead, tbody = self.get_table_head_and_body(html)
        header_list = [th.get_text() for th in thead.findAll(["th", "td"])]
        # print("header_list : {}".format(header_list))
        table_rows = tbody.findAll("tr")
        # print(len(table_rows))
        if len(table_rows) == 0:
            return [], []

        name_idx = header_list.index("名前")
        activate_idx = header_list.index("有効／無効")
        # print("{}, {}".format(name_idx, activate_idx))
        name_list, activate_list = self.get_table_list(tbody, [name_idx, activate_idx])

        return name_list, activate_list

    def get_pakurepo_list(self, pk):
        html = self.get_html("https://advms.sizebook.jp/client/{}/pakurepo".format(pk))
        thead, tbody = self.get_table_head_and_body(html)
        header_list = [th.get_text() for th in thead.findAll("th")]

        table_rows = tbody.findAll("tr")

        if len(table_rows) == 0:
            return []

        name_idx = header_list.index("名前")
        name_list = self.get_table_list(tbody, [name_idx])
        return name_list


def get_not_imported_list(ftp, sh, admvs, min_idx=0):
    all_list = []
    admvs_list = sh.get_admvs_list()
    domain_list = sh.get_domain_list()

    subdir_list = []
    
    for connector in ftp.connector_list:
        for f in connector.data_csv_site_list:
            domain = f.split("/")[0]
            if domain in domain_list:
                if not admvs_list[list(domain_list).index(domain)] == "x":
                   subdir_list += [f]
                   
    subdir_list.sort()
    # print(subdir_list)

    not_in_admvs_list = []
    
    midx = admvs.index_list[admvs.domain_list.index(subdir_list[0])]
    is_imported = False
    site_list = [subdir_list[0]]
    flag = False
    for i in range(1, len(subdir_list)):
        if subdir_list[i - 1].split(".")[0] == subdir_list[i].split(".")[0]:
            site_list += [subdir_list[i]]
            if subdir_list[i] in admvs.domain_list:
                admvs_idx = admvs.domain_list.index(subdir_list[i])
                tmp_idx = admvs.index_list[admvs_idx]
                is_imported = is_imported or admvs.csv_imported_list[admvs_idx]
                # if is_imported:
                #     print("imported: {}".format(subdir_list[i]))
                midx = midx if midx < tmp_idx else tmp_idx
            else:
                not_in_admvs_list += [subdir_list[i]]
        else:
            if min_idx < midx and not is_imported:
            # if True:
                if len(site_list) > 0:
                    print("")
                    print("* {}".format(site_list[0]))
                    for i in range(1, len(site_list)):
                        print("** {}".format(site_list[i]))

                        
            is_imported = False
            site_list = [subdir_list[i]]
            midx = 1000
            if subdir_list[i] in admvs.domain_list:
                admvs_idx = admvs.domain_list.index(subdir_list[i])
                midx = admvs.index_list[admvs_idx]
                is_imported = admvs.csv_imported_list[admvs_idx]
            else:
                not_in_admvs_list += [subdir_list[i]]

    # for i in not_in_admvs_list:
    #     print("not {}".format(i))

def get_domain_list(admvs):
    all_list, csv_exist_list, csv_imported_list = admvs.get_admvs_list()

    all_list.sort()
    # for l in all_list:
    #     print(l)
    
    domain_list = [all_list[0]]
    sub_site_list = [all_list[0]]

    for i in range(1, len(all_list)):
        if all_list[i - 1].split(".")[0] == all_list[i].split(".")[0]:
            sub_site_list += [all_list[i]]
        else:
            # print("")
            # print("* {}".format(sub_site_list[0]))
            # for i in range(1, len(sub_site_list)):
            #     print("** {}".format(sub_site_list[i]))
            # print("domain : {}".format(all_list[i]))
            domain_list += [all_list[i]]
            sub_site_list = [all_list[i]]

    # for d in domain_list:
    #     print("* {}".format(d))

    print("domain num : {}, all admvs num : {}".format(len(domain_list), len(all_list)))

    return domain_list


def get_flaged_site_num_impl(all_list, flag_list):
    merged_list = list(np.array((all_list, flag_list)).transpose())
    merged_list.sort(key=lambda x : x[0])

    count = 0
    all_count = 0
    is_counted = False
    site_list = []
    
    if merged_list[0][1] == "True":
        count = 1
        all_count = 1
        is_counted = True
        site_list = [merged_list[0][0]]

    # print(len(merged_list))
    for i in range(1, len(merged_list)):
        all_count += 1 if merged_list[i][1] == "True" else 0
        if merged_list[i - 1][0].split(".")[0] == merged_list[i][0].split(".")[0]:
            if not is_counted and merged_list[i][1] == "True":
                count += 1
                is_counted = True
        else:
            # print("domain : {}".format(merged_list[i][0]))
            is_counted = False
            if merged_list[i][1] == "True":
                count += 1
                is_counted = True
                
    print("count : {}, all_count : {}".format(count, all_count))


def get_flaged_site_num(admvs):
    admvs.get_admvs_list()

    print("csv exist list num")
    get_flaged_site_num_impl(admvs.domain_list, admvs.csv_exist_list)
    print("csv imported num")
    get_flaged_site_num_impl(admvs.domain_list, admvs.csv_imported_list)
    print("csv synced num")
    get_flaged_site_num_impl(admvs.domain_list, admvs.csv_synced_list)
    
    
if __name__ == "__main__":
    admvs = admvs_handler()
    # ftp_filename = "data/ftphandler.pickle"
    # if Path(ftp_filename).exists():
    #     print("load {}".format(ftp_filename))
    #     with open(ftp_filename, 'rb') as f:
    #         handler = pickle.load(f)
    # else:
    #     handler = FtpHandler()

    # with open(ftp_filename, 'wb') as f:
    #     pickle.dump(handler, f)
    
    # sh = spreadsheet_connector()

    # get_domain_list(admvs)
    get_flaged_site_num(admvs)
    
    # import re

    # regex = re.compile("wakigashu-ranking*")
    # for f in admvs.domain_list:
    #     if regex.match(f):
    #         idx = admvs.domain_list.index(f)
    #         if admvs.csv_imported_list[idx]:
    #             print("csv imported")
    #         print(f)

    # count = 0
    # for f in admvs.csv_imported_list:
    #     if f:
    #         print("csv imported")
    #         count += 1

    # print("imported : {}".format(count))
    # get_not_imported_list(handler, sh, admvs, 345)
