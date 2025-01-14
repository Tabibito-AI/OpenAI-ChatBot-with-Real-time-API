# AI ChatBot with Real-time Audio, Camera, and Screen Input

このPythonコードは、OpenAIのAPIライブラリを使用して、リアルタイムの音声コミュニケーション、カメラ映像認識、スクリーン認識ができるAIチャットボットの基本的な機能を実装したものです。イヤホンの使用を推奨します。

## 機能概要
- **リアルタイム音声処理**: マイクからの音声入力をリアルタイムで処理し、AIからの音声応答を再生します。
- **カメラ映像認識**: カメラからの映像をキャプチャし、AIに送信して内容を解析します。
- **スクリーン認識**: スクリーンショットを取得し、AIに送信して内容を解析します。
- **テキストチャット**: テキスト入力によるAIとの対話をサポートします。

## 必要なライブラリ
以下のライブラリをインストールしてください。

```bash
pip install openai sounddevice numpy opencv-python mss pyttsx3 aiohttp
```

## 環境変数の設定
.envファイルを作成し、以下のようにOpenAIのAPIキーの環境変数を設定して下さい。

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## コードの説明

### 1. **必要なライブラリのインポート**
- `asyncio`: 非同期処理
- `os`: 環境変数の取得
- `json`: JSONデータの処理
- `base64`: 画像データのBase64エンコード
- `io.BytesIO`: メモリ上のバイナリデータを扱う
- `openai`: OpenAI Pythonライブラリ
- `sounddevice`: リアルタイム音声入出力
- `numpy`: 数値計算 (画像処理で使用)
- `cv2` (opencv-python): カメラ映像の取得と処理
- `mss`: スクリーンショットの取得
- `pyttsx3`: テキストを音声に変換
- `aiohttp`: 非同期HTTPリクエスト

### 2. **OpenAI APIキーのセットアップ**
環境変数 `OPENAI_API_KEY` からAPIキーを取得します。設定されていない場合はエラーを出力して終了します。

### 3. **音声設定**
- サンプリングレート (`SAMPLE_RATE`): 16000 Hz
- チャンネル数 (`CHANNELS`): 1 (モノラル)
- ブロックサイズ (`BLOCK_SIZE`): 1024 (音声処理のブロックサイズ)

### 4. **カメラ設定**
- カメラのインデックス (`CAMERA_INDEX`): 通常は0がデフォルトのカメラです。

### 5. **`AIChatBot` クラス**
- **`__init__(self)`**:
  - 会話履歴を保存するリスト `conversation_history` を初期化します。
  - 音声ストリームとTTSエンジンの状態を管理します。

- **`async def send_message(self, content, role="user", input_type="text")`**:
  - 会話履歴に新しいメッセージを追加し、OpenAI APIに送信します。
  - 音声、テキスト、画像の入力タイプに応じて適切なモデルとエンドポイントを使用します。
  - レスポンスを処理し、音声またはテキストとして出力します。

- **`async def play_audio_bytes(self, audio_bytes)`**:
  - Base64エンコードされた音声データをデコードし、再生します。

- **`async def process_realtime_audio(self)`**:
  - マイクからの音声入力をリアルタイムで処理し、AIに送信します。
  - ユーザーが `quit` と入力すると終了します。

- **`async def process_camera_frames(self)`**:
  - カメラからの映像をキャプチャし、AIに送信して内容を解析します。
  - ユーザーが `q` キーを押すと終了します。

- **`async def process_screen_capture(self)`**:
  - スクリーンショットを取得し、AIに送信して内容を解析します。
  - ユーザーが `quit` と入力すると終了します。

- **`async def process_text_input(self)`**:
  - テキスト入力を処理し、AIに送信して内容を解析します。
  - ユーザーが `quit` と入力すると終了します。

### 6. **`async def main()`**
- `AIChatBot` のインスタンスを作成し、`process_realtime_audio` メソッドを呼び出してチャットボットを開始します。

### 7. **`if __name__ == "__main__":`**
- スクリプトが直接実行された場合に `main()` 関数を非同期で実行します。

## 使用方法

1. **必要なライブラリをインストール**:
   ```bash
   pip install openai sounddevice numpy opencv-python mss pyttsx3 aiohttp
   ```

2. **環境変数を.envファイルに設定**:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **スクリプトを実行**:
   ```bash
   python ai_chatbot.py
   ```

4. **機能の選択**:
   - リアルタイム音声処理: マイクからの音声入力をリアルタイムで処理します。
   - カメラ映像認識: カメラからの映像をAIに送信して解析します。
   - スクリーン認識: スクリーンショットを取得し、AIに送信して解析します。
   - テキストチャット: テキスト入力によるAIとの対話をサポートします。

## トラブルシューティング

### 一般的なエラーと解決方法

1. **APIキーが設定されていない**:
   - エラーメッセージ: `Error: OPENAI_API_KEY environment variable not set.`
   - 解決方法: `.env` ファイルに正しいAPIキーを設定してください。

2. **カメラが認識されない**:
   - エラーメッセージ: `Error: Could not open camera.`
   - 解決方法: カメラが正しく接続されていることを確認し、他のアプリケーションがカメラを使用していないことを確認してください。

3. **音声がキャプチャされない**:
   - エラーメッセージ: `No audio captured.`
   - 解決方法: マイクが正しく接続されていることを確認し、システムの音声設定を確認してください。

4. **HTTPエラー**:
   - エラーメッセージ: `HTTP Error: <error_message>`
   - 解決方法: ネットワーク接続を確認し、APIエンドポイントが正しいことを確認してください。

5. **予期しないエラー**:
   - エラーメッセージ: `Unexpected error: <error_message>`
   - 解決方法: エラーメッセージを確認し、必要に応じてコードをデバッグしてください。

## 注意点
- カメラやマイクのデバイスが正しく接続されていることを確認してください。
- OpenAI APIの利用料金に注意してください。リアルタイム音声処理や画像認識は高コストになる可能性があります。
