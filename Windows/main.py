import os
import time
import json
import requests
import subprocess
from dotenv import load_dotenv
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

#envファイル読み込み
load_dotenv("config.env")

#APIキー設定
API_KEY = os.environ['API_KEY']

def upload_file(file_path):
    url = 'https://www.virustotal.com/api/v3/files'
    headers = {
        'x-apikey': API_KEY
    }
    
    with open(file_path, 'rb') as file:
        response = requests.post(url, headers=headers, files={'file': file})
    
    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(f"ファイルアップロード失敗:{response.status_code} - {response.text}")
        return None

def check_analysis_status(analysis_id):
    url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
    headers = {
        "x-apikey": API_KEY
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"解析状況取得失敗:{response.status_code} - {response.text}")
        return None

def json_name(result_response, base_name, directory):
    #ディレクトリ作成
    os.makedirs(directory, exist_ok=True)

    #現在の日付取得
    current_date = datetime.now().strftime("%Y-%m-%d")

    #初期ファイル名設定
    count = 1
    file_name = f"{base_name}_{current_date}_{count}.json"
    file_path = os.path.join(directory, file_name)

    #連番付け
    while os.path.exists(file_path):
        count += 1
        file_name = f"{base_name}_{current_date}_{count}.json"
        file_path = os.path.join(directory, file_name)

    #ファイル保存
    with open(file_path, 'w', encoding="utf-8") as f:
        json.dump(result_response, f, indent=4)
    
    #保存完了メッセージ
    print(f"解析結果の保存完了: {file_name}")
    return file_path  #ファイルパスを戻り値

class FileHandler(FileSystemEventHandler):
    def __init__(self, save_directory, log_file_path):
        self.save_directory = save_directory
        self.log_file_path = log_file_path

    def on_created(self, event):
        if not event.is_directory:
            #検出したファイルパス
            file_path = os.path.normpath(event.src_path)
            
            #ファイル名抽出
            file_name = os.path.basename(file_path)
            print(f"ファイル検出: {file_name}")

            #5秒待機
            time.sleep(5)

            #ファイル名ログ追記
            with open(self.log_file_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"{file_name}\n")

            #ファイルアップロード
            upload_response = upload_file(file_path)
            if upload_response is None:
                print(f"アップロードに失敗しました: {file_name}")
                return

            #解析ID取得
            analysis_id = upload_response['data']['id']
            print(f"アップロード成功: {analysis_id}")

            #解析結果待機
            print("30秒ごとに解析状況取得中...")
            while True:
                result_response = check_analysis_status(analysis_id)
                if result_response is None:
                    print(f"解析状態取得に失敗しました: {analysis_id}")
                    return

                status = result_response['data']['attributes']['status']
                print(f"解析状況: {status}")

                if status in ['completed', 'timeout', 'failure']:
                    break

                time.sleep(30)  #30秒待機

            #JSONファイル保存
            base_name = "result_response"
            saved_path = json_name(result_response, base_name, self.save_directory)

            #解釈スクリプト呼び出し
            print("解析結果の解釈開始...")
            subprocess.run(['python', 'interpret_json.py', saved_path])

            #監視続行
            print("監視再開\n終了する場合: Ctrl+C")


log_save_directory = os.environ['log_save_directory']
watch_directory = os.environ['watch_directory']

def main():
    #保存先ディレクトリとログファイルパス
    log_file_path = os.path.join(log_save_directory, "file_name_log.txt")

    #ディレクトリが存在しない場合
    os.makedirs(log_save_directory, exist_ok=True)

    print("監視中...")

    #ファイル監視セットアップ
    observer = Observer()
    event_handler = FileHandler(log_save_directory, log_file_path)
    observer.schedule(event_handler, watch_directory, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("監視停止中...")
        observer.stop()  #KeyboardInterruptの場合
    observer.join()

if __name__ == "__main__":
    main()
