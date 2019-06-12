# ftp 接続
# https://qiita.com/nononote/items/97905699bea0d9092b0f
# docker で local に FTP server 構築してテスト
from ftplib import FTP
from pathlib import Path
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pickle
import numpy as np


class ftp_connector():

    data_csv = "data.csv"
    
    def __init__(self, ftp_server, account, password):
        self.ftp_server = ftp_server;
        self.account = account;
        self.password = password;
        self.file_list = []
        self.domain_list = []
        self.data_csv_site_list = None

    def get_data_csv_list(self):
        rankingsite_list = []
        with FTP(self.ftp_server, self.account, self.password) as ftp:
            self.file_list = ftp.nlst()

            for dname in self.file_list:
                if dname == ".." or dname == "." or dname == ".htaccess" or dname == ".ftpaccess":
                    continue

                self.domain_list += [dname]
                print(dname)
                file_list = ftp.nlst(dname)

                if "{}/{}".format(dname, self.data_csv) in file_list:
                    rankingsite_list += ["{}".format(dname)]

                for fname in file_list:
                    # print(fname)
                    if "{}/{}".format(fname, self.data_csv) in ftp.nlst("{}".format(fname)):
                        rankingsite_list += ["{}".format(fname)]

        self.data_csv_site_list = rankingsite_list
        print(rankingsite_list)
        return rankingsite_list

    def get_domain_rankingsite_list(self, domain):
        rankingsite_list = []
        with FTP(self.ftp_server, self.account, self.password) as ftp:
            for fname in ftp.nlst(domain):
                if "{}/{}".format(fname, self.data_csv) in ftp.nlst(fname):
                    rankingsite_list += [fname.split("/")[1]]

        return rankingsite_list
        

    def get_subdir(self, domain):
        # regex = re.compile("^" + domain + "*")
        # self.data_csv_site_list
        subdir = []
        if domain in self.domain_list:
            subdir = self.get_domain_rankingsite_list(domain)

        return subdir
            
            
    
class ftp_handler():
    def __init__(self):
        self.connector_list = [
            ftp_connector("ftp.seitai-hikaku.lolipop.jp", "lolipop.jp-seitai-hikaku", "h36yyu"),
            ftp_connector("ftp.site-ranking.lolipop.jp", "lolipop.jp-site-ranking", "V7k9c591"),
            ftp_connector("ftp.satellite-rank.main.jp", "main.jp-satellite-rank", "hMGCz3e54k4E"),
            ftp_connector("ftp.satellite-site.main.jp", "main.jp-satellite-site", "EmUqTei5"),
            ftp_connector("ftp.aqua-sb.main.jp", "main.jp-aqua-sb", "EChiEVXw"),
            ftp_connector("ftp.g-sb.main.jp", "main.jp-g-sb", "3jkkL6Zv"),
            ftp_connector("ftp.kn-sb.main.jp", "main.jp-kn-sb", "h4FrK4cJ"),
            ftp_connector("ftp.sf-sb.main.jp", "main.jp-sf-sb", "aJx3qzD8"),
            ftp_connector("ftp.comix-sb.main.jp", "main.jp-comix-sb", "Af5e7j46"),
            ftp_connector("ftp.cosmetics-sb.main.jp", "main.jp-cosmetics-sb", "e5Y7d2An"),
            ftp_connector("ftp.trusty-sb.main.jp", "main.jp-trusty-sb", "9aNy3wde"),
            ftp_connector("ftp.fs-sb.main.jp", "main.jp-fs-sb", "Fy2mb6aj"),]
        
        for connector in self.connector_list:
            print(connector.ftp_server)
            connector.get_data_csv_list()


    def has_data_csv(self, domain):
        regex = re.compile("^" + domain + "*")
        site_list = []
        for connector in self.connector_list:
            for dom in connector.data_csv_site_list:
                if (regex.match(dom)):
                    print(dom)
                    site_list += [dom]

        return site_list

    def get_domain_list(self):
        domain_list = []
        for connector in self.connector_list:
            domain_list += connector.domain_list
        return domain_list

    def get_subdir(self, domain):
        subdir = []
        for connector in self.connector_list:
            subdir += connector.get_subdir(domain)
        return subdir
            

class spreadsheet_connector():

    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    def __init__(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name('spreadsheet-api-e754b793bcea.json', self.scope)
        gc = gspread.authorize(credentials)

        # ドメイン一覧のスプレッドシートにアクセス
        wks = gc.open('ドメイン一覧').sheet1
        all_list = wks.get_all_values()
        
        self.header_list = all_list[0]
        self.all_value = np.array(all_list[1:])

        self.domain_idx = self.header_list.index("ドメイン名")
        self.admvs_idx = self.header_list.index("アドマネ移行\n（FTP禁止）")
        self.subdir_idx = self.header_list.index("パスの有無\n（ある場合パス名記載）")

        # print(self.domain_idx, self.admvs_idx)

    def get_domain_list(self):
        # for val in self.all_value[:, self.domain_idx]:
        #     print(val)
        return self.all_value[:, self.domain_idx]
    
    def get_admvs_list(self):
        return self.all_value[:, self.admvs_idx]

    def get_subdir_list(self):
        return self.all_value[:, self.subdir_idx]

    def get_subdir(self, domain="", index=-1):
        subdir_list = []
        if not domain == "":
            index = list(self.get_domain_list()).index(domain)
            subdir_str = self.all_value[index, self.subdir_idx]
            # subdir_list = subdir_str.split(",")
            subdir_list = list(set(re.split("[,|(\r\n)]", subdir_str)))
            if "" in subdir_list:
                subdir_list.remove("")
            if "×" in subdir_list:
                subdir_list.remove("×")
                
            # if subdir_list:
            #     print("domain : {}, subdir : {}".format(domain, subdir_list))
        return subdir_list


def check_domain_list(ftp_handler, sh_connector):
    ftp_list = ftp_handler.get_domain_list()
    sh_list = sh_connector.get_domain_list()

    diff_list = list(set(ftp_list) - set(sh_list))

    print(diff_list)
    


def check_subdir_list(ftp_handler, sh_connector):
    admvs_list = sh.get_admvs_list()
    domain_list = sh_connector.get_domain_list()
    for i in range(len(domain_list)):
        if (admvs_list[i] == "×"):
            continue
        
        domain = domain_list[i]
        sh_subdir = sh_connector.get_subdir(domain)
        ftp_subdir = ftp_handler.get_subdir(domain)

        diff_list = list(set(ftp_subdir) - set(sh_subdir))

        if len(diff_list) > 0:
            print("domain : {}, not in sh : {}".format(domain, diff_list))
        # else:
        #     print("domain : {}".format(domain))


if __name__ == "__main__":
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

    # check_domain_list(handler, sh)

    check_subdir_list(handler, sh)
    
    # print(sh.all_value[0])

    # sh.get_domain_list()
    
    # while True:
    #     domain = input("input domain : ")

        # handler.has_data_csv(domain)
