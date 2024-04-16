import pygame
import io

# pygameの初期化
pygame.init()

# pygameの終了
def quit_pygame():
    pygame.quit()

# バイナリデータからmp3を再生する関数
def play_mp3_from_binary(binary_data):
    pygame.init()
    # バイナリデータをメモリ上で扱うためのバッファを作成
    buffer = io.BytesIO(binary_data)
    # pygameにメモリ上の音声データを読み込ませる
    pygame.mixer.music.load(buffer)
    # 音声の再生
    pygame.mixer.music.play()
    # 音声の再生が終わるまで待つ
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.quit()

def play_mp3_from_path(file_path):
    pygame.init()
    # pygameにファイルパスから音声データを読み込ませる
    pygame.mixer.music.load(file_path)
    # 音声の再生
    pygame.mixer.music.play()
    # 音声の再生が終わるまで待つ
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.quit()
    
