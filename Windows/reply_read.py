import os
from dotenv import load_dotenv
import dropbox
import dropbox.exceptions
import requests
import shutil
import subprocess
import time

#envファイル読み込み
load_dotenv("config.env")

#認証
APP_KEY = os.environ['APP_KEY']
APP_SECRET = os.environ['APP_SECRET']
REFRESH_TOKEN = os.environ['REFRESH_TOKEN']

#アクセストークン取得
def refresh_access_token():
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": APP_KEY,
        "client_secret": APP_SECRET,
    }

    response = requests.post(url, data=data)
    response_data = response.json()

    if "access_token" in response_data:
        return response_data["access_token"]
    else:
        print("アクセストークンの取得に失敗しました:", response_data)
        return None

access_token = refresh_access_token()

#dropbox接続
if access_token:
    dbx = dropbox.Dropbox(access_token)
else:
    print("dropbox API接続失敗")
    exit(1)

#規定ファイルパス
file_path = '/line_message.txt'

#最新行取得
def get_last_line():
    try:
        #ダウンロードして内容を取得
        _, res = dbx.files_download(file_path)
        content = res.content.decode('utf-8')
        
        #最新行取得
        lines = content.strip().split('\n')
        if lines:
            return lines[-1]
        else:
            return None
    except dropbox.exceptions.ApiError as e:
        print(f"アクセスエラー")
        return None

def process_by_line(last_line):
    if last_line == "1":
        local_folder_path = "isolation"
        if os.path.exists(local_folder_path):
            shutil.rmtree(local_folder_path)
            print(f"フォルダ削除完了")
            subprocess.run(["python", "line_send_reply.py", "フォルダの削除が完了しました"],check=True)
            del_txt_file(file_path)
        
    elif last_line == "2":
        subprocess.run(["python", "line_send_reply.py", "処理を受け付けました\n後ほど確認することをお勧めします"],check=True)
        del_txt_file(file_path)

    else:
        return False
        
    return True

def del_txt_file(file_path):
    try:
        dbx.files_delete(file_path)
        print(f"ファイル削除完了")
    except dropbox.exceptions.ApiError as e:
        print(f"ファイル削除エラー: {e}")

def main():

    print("返信取得開始")
    message_sent = False

    while not message_sent:
        print("取得中...")
        last_line = get_last_line()

        if last_line is not None:
            if process_by_line(last_line):
                break
            else:
                print("返信取得失敗")
        else:
            print("返信取得失敗")
        
        #5秒間待機
        time.sleep(5)

if __name__ == "__main__":
    main()