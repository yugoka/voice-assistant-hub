import requests
import json
from soundplayer import play_mp3_from_binary, init_pygame, quit_pygame
from dotenv import load_dotenv
import os

# 環境変数をロード
load_dotenv()

def stream_voice_chat(payload):
    url = os.getenv('CHAT_API_URL') + "/speech"
    response = requests.post(url, json=payload, stream=True)
    
    if response.status_code != 200:
        print("Error:", response.text)
        return

    init_pygame()
    
    # レスポンスからチャンク単位でデータを受け取り、処理する
    try:
        for chunk in response.iter_lines():
            if chunk:  
                data = json.loads(chunk.decode('utf-8'))
                message = data["message"]
                binary = bytes(data["audioBinary"]["data"])
                print("received message:", message)

                # 音声再生
                play_mp3_from_binary(binary)

    except KeyboardInterrupt:
        print("Streaming stopped by user.")

    finally:
        quit_pygame()