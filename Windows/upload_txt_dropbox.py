import os
from dotenv import load_dotenv
import sys
import dropbox
import dropbox.exceptions
import requests

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

#保存先フォルダ
FOLDER_PATH = '/report'  #作成済みの基盤フォルダ

def upload_to_dropbox(file_path):
    try:
        #アップロードファイル名・パス
        file_name = os.path.basename(file_path)
        dropbox_path = f"{FOLDER_PATH}/{file_name}"

        #既存ファイル確認
        try:
            #メタデータを取得
            dbx.files_get_metadata(dropbox_path)
            #ファイルが存在する場合削除
            dbx.files_delete_v2(dropbox_path)
        except dropbox.exceptions.ApiError as e:
            if isinstance(e.error, dropbox.files.GetMetadataError) and e.error.is_path() and e.error.get_path().is_not_found():
                pass
            else:
                pass

        #ファイルアップロード
        with open(file_path, 'rb') as f:
            dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)

        #共有リンク作成
        shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)

        #共有リンクURLを返す
        return shared_link_metadata.url

    except dropbox.exceptions.ApiError as e:
        print(f"Dropbox API エラー: {e}")
        return None

if __name__ == "__main__":
    #引数からファイルパスを取得
    file_path = sys.argv[1]

    #Dropboxアップロード
    url = upload_to_dropbox(file_path)
    print(url)