# Schemdraw MCP Server

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

回路図描画ライブラリ `schemdraw` のための Model Context Protocol (MCP) サーバーです。Claude や他の AI アシスタントが電子回路図を作成・編集できるようになります。

## 🌟 機能

- **回路図作成**: 基本的な電子回路素子（抵抗、コンデンサ、ダイオード等）の配置
- **自動レイアウト**: コンポーネント間の接続と最適な配置
- **多様な出力形式**: PNG、SVG、PDF 形式での回路図出力
- **柔軟な構成**: シンプルな回路からループ回路まで対応
- **リアルタイム編集**: 回路の動的な変更と更新

## 📋 必要条件

- Python 3.10+
- uv (推奨) または pip

## 🚀 インストール

### uv を使用（推奨）

```bash
# プロジェクトのクローン
git clone https://github.com/fukayatti/schemdraw-mcp-server.git
cd schemdraw-mcp-server

# 依存関係のインストール
uv sync

# 開発用依存関係も含める場合
uv sync --all-extras
```

### pip を使用

```bash
# プロジェクトのクローン
git clone https://github.com/fukayatti/schemdraw-mcp-server.git
cd schemdraw-mcp-server

# インストール
pip install -e .

# 開発用依存関係も含める場合
pip install -e ".[dev]"
```

## 🔧 使用方法

### 1. MCP サーバーとして起動

```bash
# 標準入出力で MCP サーバーを起動
uv run python server.py

# または JSON-RPC over stdio で起動
python server.py --stdio
```

### 2. Claude Desktop での設定

`claude_desktop_config.json` ファイルに以下を追加：

```json
{
  "mcpServers": {
    "schemdraw": {
      "command": "uv",
      "args": ["run", "python", "/path/to/schemdraw-mcp-server/server.py"],
      "cwd": "/path/to/schemdraw-mcp-server"
    }
  }
}
```

### 3. 基本的な使用例

Claude で以下のようにリクエストできます：

> 抵抗とコンデンサと LED を使ったシンプルな回路図を作成してください

## 🛠️ 開発

### 開発環境セットアップ

```bash
# 開発用依存関係のインストール
uv sync --all-extras

# コードフォーマット
uv run black .
uv run isort .

# リントチェック
uv run flake8 .
uv run mypy .

# テスト実行
uv run pytest
```

## 📚 サポートされる回路素子

### 基本素子

- `resistor` - 抵抗器
- `capacitor` - コンデンサ
- `inductor` - インダクタ
- `diode` - ダイオード

### 電源

- `voltage_source` - 電圧源
- `current_source` - 電流源
- `battery` - バッテリー

### 半導体

- `bjt_npn` - NPN バイポーラトランジスタ
- `bjt_pnp` - PNP バイポーラトランジスタ
- `mosfet_n` - N-ch MOSFET
- `mosfet_p` - P-ch MOSFET

### 演算増幅器

- `opamp` - オペアンプ

### ロジックゲート

- `and_gate` - AND ゲート
- `or_gate` - OR ゲート
- `not_gate` - NOT ゲート
- `nand_gate` - NAND ゲート
- `nor_gate` - NOR ゲート
- `xor_gate` - XOR ゲート

### その他

- `ground` - グラウンド
- `vdd` - 電源
- `vss` - 負電源
- `label` - ラベル

## 🔌 提供される MCP ツール

### `create_circuit`

新しい回路図を作成します。

**パラメータ:**

- `title` (オプション): 回路図のタイトル
- `size` (オプション): [幅, 高さ] の配列

### `add_component`

回路に素子を追加します。

**パラメータ:**

- `component_type` (必須): 素子のタイプ
- `component_id` (必須): 素子の識別子
- `label` (オプション): 素子のラベル
- `value` (オプション): 素子の値
- `direction` (オプション): 配置方向 (`right`, `left`, `up`, `down`)
- `position` (オプション): [x, y] 座標

### `connect_components`

素子間を接続します。

**パラメータ:**

- `from_component` (必須): 接続元の素子 ID
- `to_component` (必須): 接続先の素子 ID
- `connection_type` (オプション): 接続タイプ (`wire`, `dot`)

### `create_loop_circuit`

ループ回路を作成します。

**パラメータ:**

- `components` (必須): コンポーネントのリスト
- `size` (オプション): 回路の一辺の長さ

### `save_circuit`

回路図を保存します。

**パラメータ:**

- `filename` (必須): 保存ファイル名
- `format` (オプション): 出力形式 (`png`, `svg`, `pdf`)
- `dpi` (オプション): 解像度

### `get_circuit_info`

現在の回路図の情報を取得します。

### `list_available_components`

利用可能な素子タイプの一覧を取得します。

### `add_spacer`

コンポーネント間にスペースを追加します。

### `optimize_layout`

回路図のレイアウトを最適化します。

## 📸 使用例

### シンプルな RC 回路

Claude への指示例:

> 抵抗（1kΩ）とコンデンサ（100µF）を直列に接続した RC 回路を作成してください

この指示により、以下のような回路図が生成されます：

```text
[電源] ――[R1: 1kΩ]――[C1: 100µF]――[GND]
```

## ⚙️ 設定

### 環境変数

- `SCHEMDRAW_DPI`: デフォルトの出力解像度 (デフォルト: 150)
- `SCHEMDRAW_FORMAT`: デフォルトの出力形式 (デフォルト: svg)

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📝 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 🙏 謝辞

- [schemdraw](https://github.com/cdelker/schemdraw) - 優れた回路図描画ライブラリ
- [Model Context Protocol](https://modelcontextprotocol.io/) - AI との統合を可能にするプロトコル

## 📞 サポート

問題や質問がある場合は、[Issues](https://github.com/fukayatti/schemdraw-mcp-server/issues) でお知らせください。
