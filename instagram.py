import glob
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from pathlib import Path
from bs4 import BeautifulSoup
import re
import requests
import os
import sys
import datetime
import csv

#今日の日付を引数に入れる
today = str(datetime.date.today().strftime('%Y%m%d'))

#現在の時間を引数に入れる
dt_now = str(datetime.datetime.now())

#ファイル関数作成
def file(filename):
    files = glob.glob("*/*")
    files = "".join(files)
    already = filename in files
    return already

#URL生後関数作成
def story_url(do_save_url):
    http = "https://"
    correct_wrong = http in do_save_url
    return correct_wrong

#起動済みのChromeに接続
options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
browser = webdriver.Chrome(options=options)

#Instagram_Homeに移動
Instagram = "https://www.instagram.com/"
browser.get(Instagram)
sleep(3)

#ファイルが重複するまでは、ループ保存
while True:
    #ストーリーを閲覧する
    story_button = browser.find_elements(by=By.CLASS_NAME, value="_aa8h")[0]
    to_save_url = []
    to_save_filename = [] 
    to_file_type = []
    if story_button:
        story_button.click()
        sleep(2)
    
    #現在のURLを取得
    cur_url = browser.current_url

    #メンバー名の作成
    member_name = cur_url.split("/")[-3]

    #保存フォルダの作成
    save_folder = Path(member_name)
    save_folder.mkdir(exist_ok=True)

    #現在のURLに再訪問
    browser.get(cur_url)
    sleep(2)

    #現在のURLが、InstagramのHomeでなければストーリーを見るボタンを押す
    cur_url_str = str(cur_url)
    if cur_url_str == "https://www.instagram.com/":
        break

    else:

        #ストーリーが存在する限り、次を実行
        while cur_url != "https://www.instagram.com/":
            story_see_button = browser.find_elements(by=By.TAG_NAME, value="button")[-2]
            story_see_button.click()
            sleep(0.7)
            #HTMLファイルの保存
            cur_source = browser.page_source
            html_file_name = Path("trush").joinpath(member_name + dt_now + ".html")
            with open(html_file_name, "w") as f:
                f.write(cur_source)
            text_file_name = Path("trush").joinpath(member_name + dt_now + ".txt")
            with open(text_file_name, "w") as f:
                f.write(cur_source)
            
            #ローカルHTMLファイルからsoupを作成
            soup = BeautifulSoup(open(html_file_name), "html.parser")

            #動画の場合の動作
            try:
                with open(text_file_name) as f:
                    lines = f.readlines()
                    lines = ''.join(lines)
                    video_url = re.findall("<source(.*)</video>", lines)
                    video_url = save_url = ''.join(video_url).split("\"")[-2].replace("&amp;", "&")
                    file_type = "videos"
                    video_filename = save_filename = video_url.split("?")[0].split("/")[-1]
                    to_save_url.append(video_url)
                    to_save_filename.append(video_filename)
                    to_file_type.append(file_type)
                    print(member_name + "動画")
            
            #画像の場合tryを回避し、こちらを動かす
            except:
                #最上位のimgタグを検索し、リンクを取得する
                element = soup.find("img")
                picture_url = save_url = element.get("src")
                file_type = "picture"
                picture_filename = save_filename = picture_url.split("?")[0].split("/")[-1]
                to_save_url.append(picture_url)
                to_save_filename.append(picture_filename)
                to_file_type.append(file_type)
                print(member_name + "画像")

            #CSVファイルに実行概要を保存
            csv_path = Path("csv").joinpath("nogizaka_stories.csv")
            with open(csv_path, "a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([member_name, file_type, dt_now, save_url, save_filename])

            csv_today_path = Path("csv").joinpath(today + "nogizaka_stories.csv")
            with open(csv_today_path, "a", newline="") as csvfiletoday:
                writer = csv.writer(csvfiletoday)
                writer.writerow([member_name, file_type, dt_now, save_url, save_filename])
            
            #「次へ」ボタンを押す
            sleep(0.3)
            print("取得成功")
            story_next_button = browser.find_element(by=By.CLASS_NAME, value="_ac0d")
            story_next_button.click()
            sleep(1)

            #現在のURLに再訪問
            cur_url = browser.current_url
            browser.get(cur_url)
            sleep(1)


        
        #現在のメンバーのストーリー保存
        for (do_save_url, do_save_filename, do_file_type) in zip(to_save_url, to_save_filename, to_file_type):
            if story_url(do_save_url) == True:
                save_data = requests.get(do_save_url)
                save_path = save_folder.joinpath(do_save_filename)

                if file(do_save_filename) == True:
                    for text_file in glob.glob("trush/*.txt"):
                        os.remove(text_file)
                    for html_file in glob.glob("trush/.html"):
                        os.remove(html_file)
                    print("保存完了(ファイル重複)")
                    try:
                        with open(csv_today_path, "r") as ctp:
                            readers = csv.reader(ctp)
                            for row in readers:
                                member_name = row[0]
                                file_type = row[1]
                                time = row[2]
                                url = row[3]
                                filename = row[4]
                                if file(filename) == True:
                                    print(member_name + " : exist")
                                else:
                                    try:
                                        print(member_name + time + url + filename)
                                        save_folder = Path(member_name)
                                        save_data = requests.get(url)
                                        save_path = save_folder.joinpath(filename)
                                        print(member_name + "  " + file_type)
                                        with open (save_path, mode = "wb") as nf:
                                            nf.write(save_data.content)
                                        print(member_name + " :" + filename + "," + time)
                                        sleep(1)
                                    except:
                                        print("404 Not Found")
                                        sleep(1)
                            print("end")
                            browser.quit()
                            sys.exit()

                    except:
                        print("end")
                        sys.exit()
                
                else:
                    print(member_name + "  " + do_file_type)
                    with open(save_path, mode = "wb") as f:
                        f.write(save_data.content)
                    sleep(1)
                    print(member_name + " :" + do_save_filename)
            
            else:
                print("URL_error")

        print(member_name + "終了")
        sleep(1)