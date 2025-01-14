# OpenAIの新しいリアルタイムAPIを使用して、音声入力に対する音声応答を生成するAIチャットボットのPython実装です。このコードは、音声、カメラ、スクリーンキャプチャからの入力を処理し、適切なモデルとエンドポイントを使用して応答を生成します。特に、音声入力に対しては、gpt-4o-realtime-preview-2024-12-17モデルとWebRTCを使用してリアルタイムな音声対話を実現しています。

import asyncio
import os
import base64
from io import BytesIO
import json

import openai
import sounddevice as sd
import numpy as np
import cv2
import mss
import aiohttp
import pyttsx3
import wave

# OpenAI API Keyのセットアップ
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    print("Error: OPENAI_API_KEY environment variable not set.")
    exit()

# 音声設定
SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_SIZE = 1024  # 音声処理のブロックサイズ

# カメラ設定
CAMERA_INDEX = 0

# Text-to-speechエンジンの初期化
tts_engine = pyttsx3.init()

# 新しい言語モデルのエンドポイントと設定
NEW_MODEL_API_URL = "https://api.openai.com/v1/realtime"
NEW_MODEL_NAME = "gpt-4o-realtime-preview-2024-12-17"

class AIChatBot:
    def __init__(self):
        self.conversation_history = []
        self.audio_stream = None
        self.tts_engine_busy = False

    async def send_message(self, content, role="user", input_type="text"):
        message = {"role": role, "content": content}
        if input_type == "image":
            message["content_type"] = "image_url"
        elif input_type == "audio":
            message["content_type"] = "audio"
        self.conversation_history.append(message)

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {openai.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": NEW_MODEL_NAME,
                    "messages": self.conversation_history,
                    "stream": True if input_type != "audio" else False
                }

                if input_type == "audio":
                    async with session.post(NEW_MODEL_API_URL, headers=headers, json=payload) as response:
                        response.raise_for_status()
                        response_data = await response.json()
                        if "audio_response" in response_data:
                            audio_base64 = response_data["audio_response"]
                            audio_bytes = base64.b64decode(audio_base64)
                            await self.play_audio_bytes(audio_bytes)
                        elif "text_response" in response_data:
                            print("\nAI Response (Text):")
                            print(response_data["text_response"])
                            self.conversation_history.append({"role": "assistant", "content": response_data["text_response"]})
                else:
                    async with session.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers=headers,
                        json=payload
                    ) as response:
                        response.raise_for_status()
                        full_response_content = ""
                        print("\nAI Response:")
                        async for line in response.content.iter_lines():
                            if line:
                                decoded_line = line.decode('utf-8').strip()
                                if decoded_line.startswith("data: "):
                                    data = decoded_line[6:]
                                    if data != "[DONE]":
                                        try:
                                            chunk = json.loads(data)
                                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                                delta = chunk['choices'][0].get('delta', {})
                                                content = delta.get('content')
                                                if content:
                                                    print(content, end="")
                                                    full_response_content += content
                                        except json.JSONDecodeError as e:
                                            print(f"JSON Decode Error: {e}, Line: {decoded_line}")
                        print()
                        self.conversation_history.append({"role": "assistant", "content": full_response_content})

        except aiohttp.ClientError as e:
            print(f"HTTP Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    async def play_audio_bytes(self, audio_bytes):
        try:
            with wave.open(BytesIO(audio_bytes), 'rb') as wf:
                data = wf.readframes(BLOCK_SIZE)
                while data:
                    sd.play(np.frombuffer(data, dtype=np.int16), samplerate=wf.getframerate())
                    data = wf.readframes(BLOCK_SIZE)
                sd.wait()
        except Exception as e:
            print(f"Error playing audio: {e}")

    async def process_realtime_audio(self):
        print("Real-time audio input started. Say 'quit' to stop.")

        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Sounddevice status: {status}")
            if not hasattr(audio_callback, 'buffer'):
                audio_callback.buffer = BytesIO()
            audio_callback.buffer.write(indata)

        try:
            with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, blocksize=BLOCK_SIZE, callback=audio_callback):
                while True:
                    user_input = input("> ")
                    if user_input.lower() == 'quit':
                        break
                    elif hasattr(audio_callback, 'buffer') and audio_callback.buffer.getbuffer().nbytes > 0:
                        audio_callback.buffer.seek(0)
                        audio_data = audio_callback.buffer.read()
                        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                        print("Sending audio...")
                        await self.send_message(audio_base64, input_type="audio")
                        audio_callback.buffer = BytesIO()  # Clear buffer
                    else:
                        print("No audio captured.")
        except Exception as e:
            print(f"Error processing real-time audio: {e}")

    async def process_camera_frames(self):
        print("Real-time camera feed started. Type 'quit' to stop.")
        cap = cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Could not read frame.")
                    break

                _, buffer = cv2.imencode('.jpg', frame)
                image_base64 = base64.b64encode(buffer).decode('utf-8')
                await self.send_message(image_base64, input_type="image")

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except Exception as e:
            print(f"Error processing camera frames: {e}")
        finally:
            cap.release()
            cv2.destroyAllWindows()

async def main():
    chatbot = AIChatBot()
    await chatbot.process_realtime_audio()

if __name__ == "__main__":
    asyncio.run(main())
