from test_bs import admvs_handler
import re
import gspread
import time
from oauth2client.service_account import ServiceAccountCredentials

if __name__ == "__main__":
    # spreadsheet
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('spreadsheet-api-e754b793bcea.json', scope)
    gc = gspread.authorize(credentials)
    # wks = gc.open('pakurepo').sheet1
    wks = gc.open_by_url('https://docs.google.com/spreadsheets/d/1S4Q_wQXuZdtGl4LRhtLlqNbt9nopg-Zk_1R8IG1sZTw').sheet1

    # admvs
    handler = admvs_handler()
    pk_list, name_list = handler.get_client_list()

    duration = time.time()
    
    index = 2
    for pk, name in zip(pk_list, name_list):
        print("* {}".format(name))
        # print(pk)
        pk_str = re.sub("\\D", "", pk.split(',')[-1])
        spreadsheet_list, activate_list = handler.get_multi_report_list(pk_str)
        pakurepo_list = handler.get_pakurepo_list(pk_str)

        spreadsheet_num = len(spreadsheet_list)
        pakurepo_num = len(pakurepo_list[0]) if pakurepo_list else 0
        max_num = max([spreadsheet_num, pakurepo_num, 1])
        
        cell_list = wks.range('A{}:E{}'.format(index, index + max_num))

        cell_list[0].value = pk_str
        cell_list[1].value = name

        for i in range(max_num):
            if i < spreadsheet_num:
                cell_list[i * 4 + 2].value = spreadsheet_list[i].strip()
            if i < pakurepo_num:
                cell_list[i * 4 + 4].value = pakurepo_list[0][i].strip()
            
        wks.update_cells(cell_list)

        index += max_num

        while time.time() - duration < 2:
            pass

        duration = time.time()
        
        # for sheet, is_active in zip(spreadsheet_list, activate_list):
        #     print("** {}".format(sheet.strip()))
        # print("")
        
        # if pakurepo_list:
        #     for pakurepo in pakurepo_list[0]:
        #         print("** {}".format(pakurepo.strip()))
            
        # print("\n\n")

    # for pk, name in zip(pk_list, name_list):
    #     print("{}, {}".format(pk, name))
