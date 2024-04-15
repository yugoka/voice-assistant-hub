from voicechat import stream_voice_chat
import librosa
import os
from eff_word_net.streams import SimpleMicStream
from eff_word_net.engine import HotwordDetector
from eff_word_net.audio_processing import Resnet50_Arc_loss
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
    relaxation_time=2.0  # トリガー間の最小時間（秒）
)

# マイクストリームの設定
mic_stream = SimpleMicStream(
    window_length_secs=1.5,  # ウィンドウの長さ（秒）
    sliding_window_secs=0.5,  # スライディングウィンドウの長さ（秒）
)

# マイクストリームを開始
mic_stream.start_stream()

def standby():
    print("「alpha」と言ってください")
    try:
        while True:
            frame = mic_stream.getFrame()  # マイクからのフレームを取得
            result = alpha_hw.scoreFrame(frame)  # フレームを評価
            if result is None:
                # 音声活動がない場合は続行
                continue
            if result["match"]:
                # ウェイクワードが検出された場合
                print("'alpha'が検出されました", result["confidence"])

    except KeyboardInterrupt:
        print("Listening stopped by user.")

    except Exception as e:
        print("エラーが発生しました。スタンバイを再開します...")
        print(e)
        standby()

if __name__ == "__main__":
    standby()