# ftp 接続
# https://qiita.com/nononote/items/97905699bea0d9092b0f
# docker で local に FTP server 構築してテスト
from ftplib import FTP

rankingsite_list = []
data_csv = "index.html"

with FTP("localhost", "kitamura", passwd="ymyk6422") as ftp:
    dir_list = ftp.nlst()

    for dname in dir_list:
        file_list = ftp.nlst(dname)

        if data_csv in file_list:
            rankingsite_list += ["{}".format(dname)]

        for fname in file_list:
            if data_csv in ftp.nlst("{}/{}".format(dname, fname)):
                rankingsite_list += ["{}/{}".format(dname, fname)]

for f in rankingsite_list:
    print(f)
