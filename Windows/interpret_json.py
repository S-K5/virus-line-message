import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from dotenv import load_dotenv

#envファイル読み込み
load_dotenv("config.env")

log_save_directory = os.environ['log_save_directory']
watch_directory = os.environ['watch_directory']
log_file_name = os.environ['log_file_name']
log_file_path = f"{log_save_directory.rstrip('/')}/{log_file_name}"

def txt_name(content, base_name, directory):
    #ディレクトリ作成
    os.makedirs(directory, exist_ok=True)

    #現在の日付を取得
    current_date = datetime.now().strftime("%Y-%m-%d")

    #初期ファイル名設定
    count = 1
    file_name = f"{base_name}_{current_date}_{count}.txt"
    file_path = os.path.join(directory, file_name)

    #連番付け
    while os.path.exists(file_path):
        count += 1
        file_name = f"{base_name}_{current_date}_{count}.txt"
        file_path = os.path.join(directory, file_name)

    #ファイル保存
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    #保存完了メッセージ
    print(f"マルウェア名保存完了: {file_name}")
    return file_path #ファイルパスを戻り値

def interpret_json(file_path):
    #json読み取り *読み取りモード
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)

    #内容を取得
    analysis_id = data['data']['id']
    stats = data['data']['attributes']['stats']

    #マルウェア名抽出
    malware_names = []
    results = data['data']['attributes']['results']
    for engine in results.values():
        if engine['result']:
            malware_names.append(engine['result'])

    #連番付けで保存
    malware_content = "\n".join(malware_names)
    malware_file_path = txt_name(malware_content, "malware_names", log_save_directory)

    #最後の行から最新のファイル名を取得
    name_with_extension = get_file_name_from_log(log_file_path)

    #隔離が必要かを判断
    isolation_judge = ""
    if stats['malicious'] > 0:
        #悪質な検出数が1件以上
        isolation_directory = f"{watch_directory.rstrip('/')}/isolation" #隔離先ディレクトリ
        os.makedirs(isolation_directory, exist_ok=True) #存在しない場合は作成
        #shutilでファイルを移動
        shutil.move(name_with_extension, os.path.join(isolation_directory, name_with_extension))
        isolation_judge = f"悪質なマルウェアが検出されたためファイルを隔離しました"
    else:
        isolation_judge = "悪質なマルウェアは検出されませんでした\n念のため確認をお願いします"

    #print(analysis_id)
    #print(stats)

    #解釈メッセージ作成
    message_text = f"""
受信ファイルの分析結果です

分析ファイル名:\n{name_with_extension}

分析ID:\n{analysis_id}
    
[スキャン結果]
・悪質な検出数: {stats['malicious']}件
・疑わしい検出数: {stats['suspicious']}件
・未検出数: {stats['undetected']}件
・無害な検出数: {stats['harmless']}件
・タイムアウト数: {stats['timeout']}件
・確認済タイムアウト数: {stats['confirmed-timeout']}件
・失敗した検出数: {stats['failure']}件
・未対応タイプ検出数: {stats['type-unsupported']}件

{isolation_judge}

マルウェア一覧を送付します
"""
    print("解析結果の解釈完了")
    #print(message_text)

    #dropboxアップロード
    txt_upload = subprocess.run(
    ["python", "upload_txt_dropbox.py", malware_file_path],
    capture_output=True,
    text=True
    )

    if txt_upload.returncode == 0:
        txt_url = txt_upload.stdout.strip()  #URL取得
        print("Dropboxアップロード成功:", txt_url)
    else:
        print("アップロード失敗:", txt_upload.stderr)
        return

    #削除許可判断メッセージ作成
    if stats['malicious'] > 0:
        del_message = f"悪意のあるファイルを削除する場合は'1'\n削除しない場合は'2'を送信してください"
    else:
        del_message = None

    #LINE送信スクリプト呼び出し
    if del_message:  #del_messageがある場合のみ送信
        subprocess.run(["python", "line_send_message.py", message_text, txt_url, del_message], check=True)
    else:  #del_messageがない場合は通常のメッセージだけ送信
        subprocess.run(["python", "line_send_message.py", message_text, txt_url], check=True)

def get_file_name_from_log(log_file_path):
    try:
        with open(log_file_path, "r") as log_file:
            lines = log_file.readlines()
            if lines:
                return lines[-1].strip()
            else:
                return None
    except FileNotFoundError:
        print(f"エラー: {log_file_path}が存在しません")
        return None

if __name__ == "__main__":
    file_path = sys.argv[1]
    interpret_json(file_path)