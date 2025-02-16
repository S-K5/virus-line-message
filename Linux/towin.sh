#!/bin/bash

#送信先IPアドレス
read -p "送信先IPアドレス: " ip_address

#転送ファイルパス
read -p "転送ファイルパス: " file_path

#環境設定ファイル読み込み
source config.txt
user_name=$user_name
password=$password
save_path=$save_path

# scp転送コマンド
sshpass -p "$password" scp "$file_path" "$user_name@$ip_address:$save_path"

# 転送結果表示
if [ $? -eq 0 ]; then
    echo "ファイル転送完了"
else
    echo "ファイル転送失敗"
fi
