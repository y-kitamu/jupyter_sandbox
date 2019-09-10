import io
import csv

def convertCSV(input_byte_string):
    """
    """
    url_dict = {
        "派遣": "https://700700.jp/haken/search/index.php?c=offer_view&pk=",
        "派遣/紹介予定派遣": "https://700700.jp/haken/search/index.php?c=offer_view&pk=",
        "契約社員・アルバイト・パート": "https://700700.jp/haken/search/index.php?c=offer_view&pk=",
        "職業紹介（転職支援）/契約社員・アルバイト・パート": "https://700700.jp/tensyoku/search/index.php?c=offer_view&pk=",
        "職業紹介（転職支援）": "https://700700.jp/tensyoku/search/index.php?c=offer_view&pk=",
        "紹介予定派遣": "https://700700.jp/haken/search/index.php?c=offer_view&pk=",
        "派遣/紹介予定派遣/職業紹介（転職支援）": "https://700700.jp/tensyoku/search/index.php?c=offer_view&pk=",
    }

    workplace_dict = {
        "0": "",
        "4": "宮城県",
	"6": "山形県",
	"7": "福島県",
	"8": "茨城県",
	"9": "栃木県",
        "10": "群馬県",
	"11": "埼玉県",
	"12": "千葉県",
	"13": "東京都",
	"14": "神奈川県",
	"15": "新潟県",
	"17": "石川県",
	"21": "岐阜県",
	"22": "静岡県",
	"23": "愛知県",
	"24": "三重県",
	"25": "滋賀県",
	"26": "京都府",
	"27": "大阪府",
	"28": "兵庫県",
	"29": "奈良県",
	"30": "和歌山県",
	"31": "鳥取県",
	"32": "島根県",
	"33": "岡山県",
	"34": "広島県",
	"35": "山口県",
	"36": "徳島県",
	"37": "香川県",
	"38": "愛媛県",
	"39": "高知県",
	"40": "福岡県",
	"41": "佐賀県",
	"42": "長崎県",
	"43": "熊本県",
	"44": "大分県",
	"48": "福井県",
	"49": "宮崎県",
	"50": "岩手県",
	"51": "山梨県",
	"52": "青森県",
    }
    
    csv_str = io.StringIO(input_byte_string.decode("ms932"))
    reader = csv.reader(csv_str, delimiter=',')
    csv_header = next(reader)
    #print(csv_header)
    
    id_idx = csv_header.index("主キー")
    name_idx = csv_header.index("セールスポイント")
    name_sub_idx = csv_header.index("職種表示用")
    product_idx = csv_header.index("雇用形態")
    category1_idx = csv_header.index("勤務地1_1")
    category2_idx = csv_header.index("職種中分類")
    category3_idx = csv_header.index("給与(1時間)")
    description_idx = csv_header.index("仕事の内容")
    extra_atp_idx = csv_header.index("給与(表示用)")

    output_csv = io.StringIO()
    writer = csv.writer(output_csv)
    writer.writerow(["id",
                     "name",
                     "producturl",
                     "bigimage",
                     "categoryid1",
                     "categoryid2",
                     "categoryid3",
                     "description",
                     "price",
                     "extra_atp"])

    for row in reader:
        # print(row)
        pk = row[id_idx]
        salespoint = row[name_idx].strip().replace("_x000D_", "")
        if not salespoint:
            salespoint = row[name_sub_idx].strip().replace("_x000D_", "")
        url = url_dict[row[product_idx]] + pk
        workplace = workplace_dict[row[category1_idx]]
        payment_str = ""
        if row[category3_idx]:
            payment = int(row[category3_idx]) // 100 * 100
            payment_str = "{}~{}".format(payment, payment + 99)
        
        writer.writerow([pk,
                         salespoint,
                         url,
                         None,
                         workplace,
                         row[category2_idx],
                         payment_str,
                         row[description_idx].replace("_x000D_", "").strip(),
                         None,
                         row[extra_atp_idx].replace("_x000D_", "").strip()])

    # print(output_csv.getvalue())
    return output_csv.getvalue().encode("ms932")

if __name__ == "__main__":
    with open('元データ.csv', 'rb') as f:
        output = convertCSV(f.read())

        with open('output.csv', 'wb') as f_out:
            f_out.write(output)
