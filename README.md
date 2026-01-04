# Poker Advisor Agent (Prototype)

概要
- フロントエンド: TypeScript + React (Vite)
- バックエンド: Python + FastAPI
- SpecKit ベースの仕様駆動開発を想定（spec/ に仕様雛形あり）
- LLM: プロトタイプは無料枠の Hugging Face Inference API を推奨。ローカルのダミー応答や自己ホスト（llama.cpp等）にも対応。

注意
- 実際の賭博行為は推奨しません。本プロジェクトは学習・研究目的向けです。
- LLM API キーは必ずバックエンド環境変数／シークレットで管理してください（フロントから直接呼ばない）。

セットアップ（ローカル）
1. フロントエンド
   cd frontend
   npm install
   npm run dev
   -> デフォルト: http://localhost:5173

2. バックエンド
   cd backend
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   export HF_API_TOKEN="..."   # (任意) Hugging Face トークン
   uvicorn app.main:app --reload --port 8000
   -> API: http://localhost:8000/api/advise

LLM（無料で試作する方法）
- 推奨: Hugging Face Inference API の無料ティアを利用
  - Pros: すぐ使える、OSSモデル選択可
  - Cons: 無料枠とレート制限あり
  - 環境変数: HF_API_TOKEN をセットしておくこと

- ローカル代替: llama.cpp / ggml をローカルで使う（CPU 実行可能な軽量モデル）
  - Pros: API 費用不要
  - Cons: 精度/速度に制限。導入・運用の手間あり

SpecKit（仕様ファイル）
- spec/ 配下に意思決定の期待値（入力→期待出力）を置き、実装を追従させます。
- 初期はサンプルのケースを 1–2 件用意しています。

次のステップ（推奨）
1. この雛形で実際にローカル起動し、API に対してフロントからリクエスト・レスポンスの確認
2. SpecKit に具体的なケース（プリフロップ/フロップの代表例）を追加
3. EV 計算エンジン（モンテカルロまたは既存ライブラリ）をバックエンドに追加
4. LLM は説明生成に限定し、重要な数値計算（勝率/EV）は決定論的ライブラリで行う
