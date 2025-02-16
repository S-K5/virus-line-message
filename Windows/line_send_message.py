import requests
import os
from dotenv import load_dotenv
import sys #引数を取得
import subprocess

#envファイル読み込み
load_dotenv("config.env")

def line_send_message(message):
    line_token = os.environ['line_token']
    url = 'https://api.line.me/v2/bot/message/push'

    headers = {
        'Authorization': f'Bearer {line_token}',
        'Content-Type': 'application/json'
    }

    user_id = os.environ['user_id']

    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print("メッセージ送信完了")
    else:
        print("メッセージ送信失敗")

def line_send_url(json_url):
    line_token = os.environ['line_token']
    url = 'https://api.line.me/v2/bot/message/push'

    headers = {
        'Authorization': f'Bearer {line_token}',
        'Content-Type': 'application/json'
    }

    user_id = os.environ['user_id']

    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": json_url
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print("URL送信完了")
    else:
        print("URL送信失敗")

def line_send_del_message(message):
    line_token = os.environ['line_token']
    url = 'https://api.line.me/v2/bot/message/push'

    headers = {
        'Authorization': f'Bearer {line_token}',
        'Content-Type': 'application/json'
    }

    user_id = os.environ['user_id']

    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print("削除許可判断メッセージ送信完了")
    else:
        print("削除許可判断メッセージ送信失敗")

if __name__ == "__main__":
    #引数からメッセージを取り出す
    message_text = sys.argv[1]
    json_url = sys.argv[2]

    #削除許可判断メッセージがある場合
    if len(sys.argv) > 3:
        del_message = sys.argv[3]
    else:
        del_message = None

    #メッセージを送信
    line_send_message(message_text)
    line_send_url(json_url)

    #削除許可判断メッセージがある場合
    if del_message:
        line_send_del_message(del_message)
        subprocess.run(["python", "reply_read.py"], check=True)