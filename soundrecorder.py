import numpy as np
from dotenv import load_dotenv
from google.cloud import speech
import pyaudio
import queue
import time
import threading

# 環境変数を読み込む
load_dotenv()

# オーディオ録音の設定
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

class MicrophoneStream(object):
    """マイクからの生のオーディオデータを取得するためのストリームクラスです。"""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True
        self._last_sound_time = time.time() + 2  # 最後に音声が検出された時刻。最初だけ余裕を持たせるために+2秒
        self._silent_duration_limit = 2  # 無音とみなす時間の上限（秒）
        self._base_amplitude = -1

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        self.start_silence_detector() 
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """バッファにオーディオデータを追加するコールバック関数です。"""
        self._buff.put(in_data)
        # 振幅が閾値以上であれば、最後に音声が検出された時刻を更新
        amplitude = self._get_amplitude(in_data)

        # ベースの閾値が設定されていないなら今の音量で取る
        if self._base_amplitude == -1:
            self._base_amplitude = amplitude * 1.5

        if amplitude > self._base_amplitude: 
            self._last_sound_time = time.time()
        return None, pyaudio.paContinue

    def _get_amplitude(self, buffer):
        audio_data = np.frombuffer(buffer, dtype=np.int16)
        # 音声の振幅（絶対値の平均）を計算
        amplitude = np.mean(np.abs(audio_data))
        return amplitude

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)

    def start_silence_detector(self):
        print("処理開始")
        """無音検出スレッドを開始します。"""
        def detect_silence():
            while not self.closed:
                print("checking", self._last_sound_time)
                if time.time() - self._last_sound_time > self._silent_duration_limit:
                    print("無音状態が続いたため、処理を終了します。")
                    self.closed = True  # ストリームを閉じることで処理を終了
                    # ストリームのクリーンアップ
                    self.__exit__(None, None, None)
                    break
                time.sleep(0.5)  # CPU使用率を抑えるためにスリープ

        threading.Thread(target=detect_silence).start()


def listen_print_loop(responses):
    """サーバーからのレスポンスを処理する関数です。一定時間音声が検出されない場合に終了します。"""

    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue
        
        print(u'Transcript: {}'.format(result.alternatives[0].transcript))

def main():
    # GCPクライアントライブラリを初期化
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code='ja-JP',
        max_alternatives=1,
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
    )

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (speech.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        # レスポンスを処理
        listen_print_loop(responses)

if __name__ == '__main__':
    main()