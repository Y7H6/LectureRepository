# PokerAgent — 設計書（ドラフト）
作成日: 2026-01-04  
対象: テキサスホールデムのブラウザ上プロトタイプ（ユーザー 1 人 + CPU 5 人、合計 6 人）  
目的: ユーザーが画面上で CPU 相手に遊べ、必要時に AI（LLM）から次の手の候補（action + bet_size + reasoning）を得られるようにする。

---
# PokerAgent — 設計書（ドラフト）
作成日: 2026-01-04  
対象: テキサスホールデムのブラウザ上プロトタイプ（ユーザー 1 人 + CPU 5 人、合計 6 人）  
目的: ユーザーが画面上で CPU 相手に遊べ、必要時に AI（LLM）から次の手の候補（action + bet_size + reasoning）を得られるようにする。

---

## 1. ハイレベル要件
- ゲーム: テキサスホールデム（No-Limit は将来的に対応、初期は固定ブラインド/固定スタックでの練習モード）
- プレイヤー構成: 6 人（Human: 1 / CPU: 5）。ディーラーは CPU が担当。
- 表示: ユーザーのホールカードは表向き、対戦相手のホールカードは裏向き（非表示）。
- 助言機能: 画面上の「Help」ボタンで AI に助言を求められる。AIは action (fold/call/raise)、bet_size、および理由を返す。
- 分離責務: ゲームロジック（決定論）と説明生成（LLM）は分離。重要な数値（勝率/EV）は deterministic エンジンで算出（初期は簡易ヒューリスティック／将来的に Monte Carlo）。
- 公開形態: Web アプリ（frontend: TypeScript/React, backend: Python/FastAPI）。リアルタイム更新は WebSocket 推奨（初期はポーリング可）。

---

## 2. ユーザー体験（主要画面 / 要素）
1. ロビー画面
   - 「New Game」「Settings（人数・ブラインド・stack）」「Rules」「Start」ボタン
   - 最近のゲーム履歴（任意）

2. テーブル画面（メイン）
   - 中央: ボードカード（最大 5 枚）
   - 左右/周囲: 6 席のプレイヤーカード（自分のみ表、他は裏）
     - 各プレイヤーに: 名前、スタック (bb)、アクション履歴、コミット額表示
     - ディーラーボタン表示（CPU が常に操作）
   - 画面下: ユーザーのホールカード（表）、インタラクション
     - 「Fold」「Call」「Raise」ボタン（Raise にはスライダー or 事前定義サイズ）
     - 「Help（AIに相談）」ボタン（モード切替: beginner/advanced）
   - 右/左: ハンド履歴 / ログ（ラウンド別）
   - 画面上部: ポットサイズ、現在ベット、残りスタック

3. 助言ダイアログ（Help 押下時）
   - 非同期ローディング → AI の応答表示
   - 表示内容:
     - 推奨 action（fold/call/raise）
     - 推奨 bet_size（例: 25% pot / 3x）
     - 簡潔な理由（数行）
     - 「詳細を見る」ボタンで拡張説明（GTO 観点、相手のレンジ、確率）
   - ユーザーは AI の助言をクリックでそのままアクションに反映可（オプション）

---

## 3. ゲームルールとターンフロー
- ブラインド: 小ブラインド / 大ブラインド（設定可能）
- ディール順: ディーラーボタン → 配牌（各プレイヤー 2 枚）
- ベッティングラウンド: プリフロップ → フロップ → ターン → リバー
- 各ラウンドのアクション順: プレイヤーのポジションに基づく（プリフロップはBBの次、以降はSBの次）
- ベット/レイズ 上限: 初期は No-Limit（ただし UI 上で合理的な上限を設ける）または固定ラウンドとして実装しやすい「ポット上限」も検討
- ショーダウン: 最終ラウンド後、全員の手札を公開して勝者決定（ハンド評価ロジックは deterministic）
- タイムアウト: ユーザーの未応答時は自動フォールドまたは自動コールの設定を選べる
- ディーラー: CPU がディーラー・カード配布・ポット分配を管理

---

## 4. システム構成（アーキテクチャ）
- Frontend (TypeScript + React + Vite)
  - UI コンポーネント: Table, Seat, PlayerInfo, ActionControls, HelpModal, Log
  - State 管理: React Context / Redux（将来的に）または Zustand（軽量）
  - 通信: WebSocket（推奨）または REST ポーリング
- Backend (Python + FastAPI)
  - モジュール:
    - game/ : ゲームステート・ルール・ハンド評価
    - engine/ : CPU プレイヤーの意思決定（初期はヒューリスティック）
    - advisor/ : AI 助言ラッパー（LLM 呼び出し or ダミー）
    - api/ : REST + WebSocket エンドポイント
    - models/ : Pydantic 型定義
    - services/ : 認証（必要なら）、セッション管理、ログ
  - DB: 初期は in-memory（セッションベース）。永続化する場合は PostgreSQL / SQLite。
  - デプロイ: Render/Vercel/Heroku/自ホスト（小規模なら Render、APIは Render・Vercel Serverless、フロントは Vercel/GitHub Pages）

---

## 5. データモデル（主要スキーマ）
- TypeScript / Pydantic（概念）
  - Player {
      id: string,
      name: string,
      seat: number,
      stack_bb: number,
      hole_cards?: string[], // user only visible
      committed: number,
      is_human: boolean,
      is_dealer: boolean,
      status: "active"|"folded"|"allin"
    }
  - GameState {
      id: string,
      players: Player[],
      board: string[], // ["Qs","Jh","3c",...]
      pot: number,
      current_bet: number,
      to_act_seat: number,
      round: "preflop"|"flop"|"turn"|"river"|"showdown",
      history: Action[],
      small_blind: number,
      big_blind: number,
      deck_seed: string
    }
  - ActionPayload (API) {
      player_id: string,
      action: "fold"|"call"|"raise",
      raise_amount?: number
    }
  - AdvisorRequest {
      hand: string[], board: string[], position: string, stack: number, pot: number, opponent_style: string, action_history: string[], mode: "beginner"|"advanced"
    }
  - AdvisorResponse {
      action: "fold"|"call"|"raise",
      bet_size: string,
      reasoning: string[]
    }

---

## 6. API 設計（主要エンドポイント）
- REST:
  - POST /api/game/new -> { game_id }
  - GET /api/game/{id}/state -> GameState
  - POST /api/game/{id}/action -> {result} （人間のアクション）
  - POST /api/game/{id}/help -> AdvisorResponse
    - body: AdvisorRequest（UI の Help ボタンで送る）
- WebSocket:
  - 接続: /ws/game/{game_id}
  - 送受信メッセージ:
    - to client: { type: "state_update", state: GameState }
    - from client: { type: "action", payload: ActionPayload }
    - to client: { type: "advisor_response", payload: AdvisorResponse }

API 例（Help 呼び出し）:
POST /api/game/{id}/help
body:
{
  "hand":["Ah","Kd"], "board":["Qs","Jh","3c"], "position":"BTN",
  "stack":120, "pot":9, "opponent_style":"TAG", "action_history":["UTG fold","MP raise 3bb"], "mode":"beginner"
}
response:
{
  "action":"call", "bet_size":"—",
  "reasoning":[ "ボードはブロードウェイ混合で...","あなたのハンドは...","初心者向け説明..." ]
}

---

## 7. CPU（Bot）設計（段階的）
- 仕様:
  - 5 人の CPU を seat に割り当て、各 CPU にタイプ（Tight/Loose, Aggressive/Passive）を設定可能（ランダム or 設定）。
- 初期（プロトタイプ）:
  - ルールベースヒューリスティック:
    - プリフロップ: ポジション+レンジ表に基づくオープン/フォールド/コール
    - ポストフロップ: ハンドカテゴリ (made hand, draw, miss) + pot odds 簡易計算で判断
  - ステートレスで高速
- 中期（改善）:
  - Monte Carlo による勝率計算（簡易）を用いて EV に基づくアクション
  - 対戦相手のレンジ推定（相手履歴を簡易集計）
- 長期（高精度）:
  - ベルトの GTO 戦略（外部ライブラリ / 学習済みモデル）
  - 状況に応じた混合戦略（確率的アクション）

---

## 8. AI（助言）統合設計
- ポリシー:
  - AI（LLM）は「説明生成と助言の提案」に限定。数値的評価（勝率/EV）は deterministic エンジンが出す。
  - LLM は無料プロトタイプでは Hugging Face Inference API の無料ティア、またはローカル軽量モデル（llama.cpp ベース）のダミーで運用。
  - API キーはバックエンドのみ保持（フロントから直呼び出し厳禁）。
- フロー:
  1. ユーザーが Help を押す → フロントは /api/game/{id}/help へ AdvisorRequest を送信
  2. Backend:
     - (A) deterministic engine が hand/board から勝率・主要数値を算出（例: win% = 42%）
     - (B) prompt template に勝率・レンジ・相手タイプ・履歴などを差し込み LLM に投げる（mode によって出力の粒度を変える）
     - (C) 受け取った LLM 出力を解析し、AdvisorResponse を返す
  3. フロントは結果をモーダル表示
- Prompt テンプレート（例・日本語）:
  - シンプル/必須: 「あなたはポーカーアドバイザーです。状況: {hand}, {board}, pot={pot}, stack={stack}, position={position}, opponent_style={opponent_style}, history={history}. deterministic_engine の結果: win%={win_pct}, best_equity={equity_if_raise}. 推奨アクションを 1 つ選び action, bet_size, 2-3 行の理由を日本語で返してください。初心者向け説明も 1 行で付けてください。」
- 安全策:
  - LLM が数値（勝率等）を嘘で生成しないように、必ず deterministic engine の数値を先に算出して prompt に含める
  - LLM 出力は構造化（JSON）で返却させる。パースに失敗したら fallback message を返す。
- Fallback:
  - LLM が利用不可な場合は backend 内のダミー助言ルール（現在の advisor.advisor.py のロジック）を返す。

---

## 9. SpecKit / テスト方針（仕様駆動）
- Spec の用途: 代表ケース（プリフロップ、フロップ、ターン、リバー）で期待される advisor の出力を定義。CI で失敗を検出する。
- サンプル Spec（json）:
  - case: BTN Ah,Kd (プリフロップ) -> expected: raise (beginner)
  - case: Flop Qs Jh 3c, Hand: Ah Kd -> expected: call / raise conditional
- テストの種類:
  - Unit: ハンド評価、デッキ処理、ポット分配
  - Integration: API エンドポイント（/api/advise）の応答構造
  - E2E: フロントから Help を呼んだときに modal が期待どおりの内容を表示
- 自動化:
  - spec/ 配下に JSON で期待ケースを置き、Node/Python スクリプトで API を叩き検証
  - CI (GitHub Actions): lint -> test -> speckit/spec-run -> build -> deploy（オプション）

---

## 10. 非機能要件
- レイテンシ: Help 呼び出しは LLM 呼び出しを含むので 1–5 秒の応答を想定（無料ティアは遅い場合あり）。UI はローディングインジケータを出す。
- 同時ユーザー: 初期は単一対戦セッションを想定。将来スケールは Session 単位で増やす。
- セキュリティ:
  - LLM/API キーはバックエンドの環境変数 / Secrets に保管
  - CORS を設定して不正アクセスを防ぐ
  - ユーザーデータは必要最小限のみ保存
- 公平性:
  - RNG（シャッフル）は暗号的ハッシュや seed を使い再現可能に（デバッグ用）
  - デバッグのために seed を固定して再現プレイが可能
- ロギング:
  - ゲームイベント・エラー・advisor 呼出しの応答（注意: 個人情報含めない）のみ記録

---

## 11. UI/UX 注意点
- 助言は「推奨」であることを明示（例: “AI の推奨: call — 理由: ...”）
- 初心者モードは説明を易しく（箇条書き）、上級者モードは GTO 観点を短く示す
- ユーザーが AI の指示をそのまま実行できる「Apply」ボタンを optional に提供（誤操作注意）
- 助言は過度に攻撃的な指示（例: 無暗示な all-in を常時推奨）を出さないガードレールを実装

---

## 12. 開発マイルストーン（推奨）
1. M0 — リポジトリ初期コミット（完了: frontend + backend skeleton + spec 雛形）
2. M1 — 基本ゲームループ実装（配牌・ベットラウンド・勝者判定・UI）
   - Acceptance: 手動で 1 ゲームが完走すること
3. M2 — CPU 簡易ヒューリスティック実装（5 CPU）
   - Acceptance: CPU が合理的にプレイすること（プリフロップで raise/call/fold）
4. M3 — Help 機能（advisor の API 組込み。最初は backend 内ダミー）
   - Acceptance: Help ボタンで modal に推奨 action が表示される
5. M4 — LLM 統合（Hugging Face / ローカルモデル）＋ deterministic engine による数値算出
   - Acceptance: Help で LLM 由来の説明が表示され、数値は deterministic engine が供給する
6. M5 — SpecKit テスト群と CI（GitHub Actions）導入
7. M6 — UX 改良、デプロイ（Render/Vercel）、公開

---

## 13. 受け入れ基準（例）
- UI: ユーザーの手札が常に見える。対戦相手カードは非表示。
- ゲーム: 1 ラウンド（プリフロップ→フロップ→ターン→リバー→ショーダウン）が実行可能。
- CPU: 5 CPU がアクションを実行してゲームが進行する。
- Help: ユーザーが Help を押すと 5 秒以内（LLM の状況で変動）に推奨 action が表示される（初期はダミーで構わない）。
- 安全: API キーはフロントに露出しない。

---

## 14. リスクと対策
- LLM レイテンシ/品質:
  - 対策: キャッシュ、ローカルダミーモード、予備の軽量モデル
- 無料 LLM の制限（レート/コスト）:
  - 対策: 無料枠が尽きたらダミーにフォールバック / ユーザーへ通知
- 不正操作（フロントからのキー漏洩）:
  - 対策: キーはバックエンド、CORS、API 認証
- 法的/倫理的問題:
  - 対策: 利用規約・免責の明記（賭博を推奨しない旨）

---

## 15. 開発での次のアクション（短期）
1. M1 の達成: game loop と UI（現状の skeleton を基に）を動作させる  
   - タスク: フロントの Table コンポーネントと backend game model を連携（WebSocket）
2. M2 の達成: CPU の基本戦略を実装（先に簡易ヒューリスティック）
3. M3 の達成: Help の API 実装（最初は advisor.advisor.py の簡易ロジックを使用）
4. Spec の追加: spec/advisor に 5 ケースを追加して CI で自動検証

---

## 16. 付録: 推奨技術スタック（簡潔）
- Frontend: React + Vite + TypeScript + SWR/Socket.io client
- Backend: FastAPI + Uvicorn + Pydantic + websockets / Socket.IO（uvicorn＋fastapi websocket）
- LLM: Hugging Face Inference API（無料枠） or llama.cpp（自己ホスト）
- DB: SQLite（開発）→ PostgreSQL（本番）
- CI/CD: GitHub Actions, Deploy: Render / Vercel
- Testing: Pytest (backend), Jest + React Testing Library (frontend), SpecKit (仕様駆動)

---

必要なら次に、以下を作成します（選択してください）：
- A: 画面ワイヤーフレーム（SVG/簡易画像）と詳細 UI コンポーネント一覧
- B: WebSocket のメッセージ定義と TypeScript 型定義ファイル（雛形）
- C: Advisor の Prompt テンプレート（日本語）と LLM 呼び出しのサンプルコード
- D: SpecKit 用の具体的な JSON ケース群（10 件）
- E: CI (GitHub Actions) ワークフロー雛形（テスト・ビルド・デプロイ）

どれを次に作成しましょうか？（複数可）
