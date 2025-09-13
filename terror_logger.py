import os
import re
import glob
import tkinter as tk
import requests

latest_file_path = None
last_position = 0
log_folder = os.path.join(os.environ["USERPROFILE"], r"AppData\Locallow\VRChat\VRChat")

round_type_map = {
    "Classic": "クラシック",
    "BloodBath": "ブラッドバス",
    "Fog": "霧",
    "Alternate": "オルタネイト",
    "Sabotage": "サボタージュ",
    "Punished": "パニッシュ",
    "Cracked": "狂気",
    "Midnight": "ミッドナイト",
    "Ghost": "ゴースト",
    "Unbound": "アンバウンド",
    "8 Pages": "8ページ",
    "Ghost (Alternate)": "ゴースト (Alternate)",
}

def check_latest_file():
    global latest_file_path
    pattern = os.path.join(log_folder, "output_log_*.txt")
    files = glob.glob(pattern)

    if files:
        latest_file_path = max(files, key=os.path.getctime)
    else:
        url = entry_url.get()
        if url:
            try:
                requests.post(url, json={"content": "OSCを有効にしてください."})
            except Exception as e:
                print("送信エラー:", e)

    root.after(30000, check_latest_file)

def get_terror():
    global last_position

    if latest_file_path:
        try:
            with open(latest_file_path, "r", encoding="utf-8") as f:
                f.seek(last_position)
                new_lines = f.read()
                last_position = f.tell()

            if new_lines.strip():
                if "Killers have been set" in new_lines:
                    match = re.search("Killers have been set - (.+) // Round type is (.+)", new_lines)

                    terror = match.group(1)
                    round_type = match.group(2)
                    round_type_display = round_type_map.get(round_type, round_type)

                    url = entry_url.get()
                    if url:
                        requests.post(url, json={"content": f"{round_type_display}\n{terror}"})
        except Exception as e:
            print("ログ読み込みエラー:", e)
    root.after(100, get_terror)

# ウィンドウ作成
root = tk.Tk()
root.title("TerrorLogger")

tk.Label(root, text="Webhook URL:").pack(padx=10, pady=5)
entry_url = tk.Entry(root, width=60)
entry_url.pack(padx=10, pady=5)

root.after(1000, check_latest_file)

root.after(1000, get_terror)
root.mainloop()
