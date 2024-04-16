from voicechat import stream_voice_chat
import librosa
import os
from eff_word_net.streams import SimpleMicStream
from eff_word_net.engine import HotwordDetector
from eff_word_net.audio_processing import Resnet50_Arc_loss
from soundplayer import play_mp3_from_path
from soundrecorder import generate_transcription
import time
#from eff_word_net.audio_processing import First_Iteration_Siamese

# モデルのインスタンスを作成
base_model = Resnet50_Arc_loss()
#base_model = First_Iteration_Siamese()

# HotwordDetector のインスタンスを作成
alpha_hw = HotwordDetector(
    hotword="alpha",  # ウェイクワード名
    model=base_model,  # 使用するモデル
    reference_file=os.path.join(os.getcwd(),"refs", "alpha_ref.json"),  # 参照ファイルのパス
    threshold=0.69,  # トリガーとみなす最小の信頼度
    relaxation_time=3.0  # トリガー間の最小時間（秒）
)

# マイクストリームの設定
mic_stream = SimpleMicStream(
    window_length_secs=1.5,  # ウィンドウの長さ（秒）
    sliding_window_secs=0.5,  # スライディングウィンドウの長さ（秒）
)

# マイクストリームを開始
mic_stream.start_stream()

def standby():
    try:
        print("[Alpha] スタンバイを開始します")
        while True:
            frame = mic_stream.getFrame()  # マイクからのフレームを取得
            result = alpha_hw.scoreFrame(frame)  # フレームを評価
            if result is None:
                # 音声活動がない場合は続行
                continue
            if result["match"]:
                # ウェイクワードが検出された場合
                print("[Alpha] ウェイクワードが検出されました:", result["confidence"])
                start_chat()
                mic_stream.close_stream()
                mic_stream.start_stream()
                print("[Alpha] スタンバイを再開します")
            
    except KeyboardInterrupt:
        print("Listening stopped by user.")

    except Exception as e:
        print(e)

def start_chat():

    play_mp3_from_path("resources/finger-snap-joshua-chivers-2-2-00-00.mp3")
    # マイクから音声を拾って文字起こしする
    speech_text = generate_transcription()

    
    if (len(speech_text) >= 2):
        play_mp3_from_path("resources\cartoon-game-collect-point-ni-sound-1-00-01.mp3")

        # 返答を生成して音声を流す
        stream_voice_chat({"text": speech_text})
        start_chat()


if __name__ == "__main__":
    standby()