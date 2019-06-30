import requests
from pathlib import Path
import pickle
from bs4 import BeautifulSoup

from test_ftp import ftp_connector, ftp_handler, spreadsheet_connector

class admvs_handler:

    def __init__(self):
        self.domain_list = []
        self.csv_exist_list = []
        self.csv_imported_list = []
        self.index_list = []

        self.html = self.get_domain_list_html()
        # self.get_admvs_list()
    
    def get_domain_list_html(self):
        payload = {
            "csrfmiddlewaretoken": "",
            "username": "",
            "password": ""
        }

        with open("password.txt", "r") as f:
            payload["username"] = f.readline()
            payload["password"] = f.readline()
        session = requests.Session()

        res = session.get("https://advms.sizebook.jp/accounts/login/?next=/sftpgit/site/")
        soup = BeautifulSoup(res.text, "lxml")
        payload["csrfmiddlewaretoken"] = soup.find(attrs={"name": "csrfmiddlewaretoken"}).get("value")

        res = session.post("https://advms.sizebook.jp/accounts/login/?next=/sftpgit/site/", data=payload)
        res.raise_for_status()
        return res.text

    def get_admvs_list(self):
        soup = BeautifulSoup(self.html, "lxml")

        table = soup.find(attrs={"id": "data_table"})
        thead = table.find("thead")
        tbody = table.find("tbody")

        header_list = [th.get_text()  for th in table.findAll("th")]
        idx_idx = header_list.index("#")
        name_idx = header_list.index("名前")
        csv_exist_idx = header_list.index("検索管理機能有効")
        csv_imported_idx = header_list.index("商品データ登録済み")

        # table_data = [[ for td in tr.findAll("t")] for tr in tbody.findAll("tr")]
        for tr in tbody.findAll("tr"):
            td_list = [td.get_text() for td in tr.findAll("td")]
            self.index_list += [int(td_list[idx_idx])]
            self.domain_list += [td_list[name_idx]]
            if td_list[csv_exist_idx] == "True":
                self.csv_exist_list += [True]
            else:
                self.csv_exist_list += [False]

            if td_list[csv_imported_idx] == "True":
                self.csv_imported_list += [True]
            else:
                self.csv_imported_list += [False]

        return self.domain_list, self.csv_exist_list, self.csv_imported_list


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

if __name__ == "__main__":
    admvs = admvs_handler()
    
    ftp_filename = "data/ftphandler.pickle"
    if Path(ftp_filename).exists():
        print("load {}".format(ftp_filename))
        with open(ftp_filename, 'rb') as f:
            handler = pickle.load(f)
    else:
        handler = ftp_handler()

    with open(ftp_filename, 'wb') as f:
        pickle.dump(handler, f)
    
    sh = spreadsheet_connector()

    import re

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
    get_not_imported_list(handler, sh, admvs, 345)
