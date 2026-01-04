# SpecKit / Spec 仕様雛形

目的:
- 仕様駆動開発のため、代表的なゲーム状況 (入力) に対する期待出力 (action, bet_size, reasoning) を定義します。
- SpecKit は Node 系のツールを想定しています。backend API に対する E2E 仕様を置くことも可能です。

推奨ワークフロー:
1. spec/ 以下にケースファイルを追加する (例: spec/advisor/raise.spec.json)
2. CI では spec を実行して期待されるレスポンスと実実装を比較する（speckit などを利用）
3. 実装が不足している場合は失敗テストが出るので、実装を追加してパスさせる

サンプル（JSON 形式の仕様ファイル・雛形）:
- spec/advisor/advise_case_1.json

内容例:
{
  "description": "BTN: Ah,Kd on empty board vs TAG -> raise",
  "input": {
    "hand": ["Ah","Kd"],
    "board": [],
    "position": "BTN",
    "stack": 120,
    "pot": 2,
    "opponent_style": "TAG",
    "action_history": [],
    "mode": "beginner"
  },
  "expected": {
    "action": "raise",
    "bet_size": "3x"
  }
}

（具体的な speckit の書き方はプロジェクトの speckit バージョンに合わせて実装してください。最初は単純な JSON シリーズで始め、CI のスクリプトでこれらを読み込んで /api/advise に対して検証するのが堅実です。）
