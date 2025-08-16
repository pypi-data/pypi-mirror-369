# pl-snippet-toolkit-utils-001

高品質なPython/TypeScriptユーティリティ集。データ処理、API通信、可視化、型検証などを網羅。

## 機能一覧
- CSV処理（pandas/numpy）
- チャート生成（matplotlib/seaborn）
- REST APIクライアント（requests）
- JSON型検証（Zod）
- GraphQLクライアント（axios）

## セットアップ
```bash
python3 -m venv venv
pip install -e .
pip install pytest pytest-cov build twine
npm install
```

## テスト
```bash
pytest

# TypeScriptのテストは、src/__tests__ や src/配下に test ファイルを追加してください。
npm run test # テストファイルが無い場合はエラーになります

chmod +x scripts/publish.sh
./scripts/publish.sh
```

## ライセンス
MIT
