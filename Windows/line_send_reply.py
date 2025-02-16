import requests
import sys
import os
from dotenv import load_dotenv

#envファイル読み込み
load_dotenv("config.env")

def send_line_message(message):
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

if __name__ == "__main__":
        message = sys.argv[1]
        send_line_message(message)