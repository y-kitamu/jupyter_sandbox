import pandas as pd
import csv
import math


def convert_csv(filename="/home/kitamura/Downloads/2019-06-07_dropbox_member.csv"):
    """
    グループ別の csv に変換
    """
    df = pd.read_csv(filename)

    group_user_list = {}

    for _, user in df.iterrows():
        groups_str = user['企業管理グループ']
        if not type(groups_str) == type(str()):
            continue

        groups = groups_str.split(',')
        groups = [g.strip() for g in groups]
        # print(groups)

        for group in groups:
            group.strip()
            if group in group_user_list:
                group_user_list[group] += [user['姓'] + " " + user['名']]
            else:
                group_user_list[group] = [user['姓'] + " " + user['名']]

    # for key, item in group_user_list.items():
        # print(key)
        # print(item)

    save_fname = filename.replace(".csv", "_reorder.csv")
    with open(save_fname, "w", newline='') as f:
        csv_writer = csv.writer(f, delimiter=',', quotechar='"')
        csv_writer.writerow(["グループ名", "所属ユーザー"])
        for key, item in group_user_list.items():
            csv_writer.writerow([key, ','.join(item)])

    return group_user_list
