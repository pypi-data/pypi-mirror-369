"""
Schemdraw MCP Server

Electronic circuit diagram drawing server using the Model Context Protocol (MCP).
Provides tools for creating, editing, and exporting circuit diagrams using schemdraw.
"""

import json
import asyncio
import argparse
from typing import Any, Sequence
from pathlib import Path
import tempfile
import base64
from io import BytesIO

import schemdraw
import schemdraw.elements as elm
import schemdraw.logic as logic
import schemdraw.dsp as dsp
from schemdraw import Drawing
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# グローバル変数：現在の回路図
current_drawing = None
components = {}  # コンポーネントのID管理用
_component_map_cache = None  # コンポーネントマップのキャッシュ


def reset_drawing():
    """回路図をリセット"""
    global current_drawing, components
    current_drawing = Drawing()
    
    # 文字の重複を避けるための設定
    current_drawing.config(fontsize=8)   # フォントサイズを小さく
    
    components = {}


def _build_component_map():
    """schemdrawから動的にコンポーネントマップを構築"""
    # 利用可能なモジュールとその名前のマッピング
    modules_to_inspect = [
        (elm, "elm"),
        (logic, "logic"),
        (dsp, "dsp"),
    ]
    
    # 動的にcomponent_mapを生成
    component_map = {}
    
    # 各モジュールからエレメントを取得
    for module, name in modules_to_inspect:
        # モジュール内のクラス名（大文字で始まるもの）を取得
        element_list = [e_name for e_name in dir(module) if e_name[0].isupper()]
        
        for element_name in element_list:
            element_class = getattr(module, element_name)
            # クラスかどうかをチェック
            if isinstance(element_class, type):
                # 小文字に変換してマッピング
                key = element_name.lower()
                component_map[key] = element_class
    
    return component_map


def get_component_class(component_type: str):
    """コンポーネントタイプに基づいて対応するschemdrawクラスを返す"""
    global _component_map_cache
    
    # キャッシュが存在しない場合は構築
    if _component_map_cache is None:
        _component_map_cache = _build_component_map()
    
    return _component_map_cache.get(component_type.lower())


# MCPサーバーの初期化
server = Server("schemdraw-mcp-server")


@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """利用可能なリソースをリストアップ"""
    return [
        Resource(
            uri="circuit://current",
            name="Current Circuit",
            description="現在編集中の回路図",
            mimeType="image/png",
        )
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """リソースを読み取り"""
    if uri == "circuit://current":
        if current_drawing is None:
            return "No circuit available"
        
        # 回路図を画像として出力
        buf = BytesIO()
        current_drawing.save(buf, transparent=False, dpi=150)
        buf.seek(0)
        
        # Base64エンコード
        img_data = base64.b64encode(buf.getvalue()).decode()
        return f"data:image/png;base64,{img_data}"
    
    raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """利用可能なツールをリストアップ"""
    return [
        Tool(
            name="create_circuit",
            description="新しい回路図を作成",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "回路図のタイトル（オプション）"
                    },
                    "size": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "回路図のサイズ [width, height]（オプション）"
                    }
                }
            }
        ),
        Tool(
            name="add_component",
            description="回路図にコンポーネントを追加",
            inputSchema={
                "type": "object",
                "properties": {
                    "component_type": {
                        "type": "string",
                        "description": "コンポーネントのタイプ（resistor, capacitor, diode等）"
                    },
                    "component_id": {
                        "type": "string",
                        "description": "コンポーネントの識別子"
                    },
                    "label": {
                        "type": "string",
                        "description": "コンポーネントのラベル（オプション）"
                    },
                    "value": {
                        "type": "string",
                        "description": "コンポーネントの値（オプション）"
                    },
                    "position": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "位置 [x, y]（オプション）"
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["right", "left", "up", "down"],
                        "description": "コンポーネントの方向（オプション）"
                    }
                },
                "required": ["component_type", "component_id"]
            }
        ),
        Tool(
            name="connect_components",
            description="コンポーネント間を接続",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_component": {
                        "type": "string",
                        "description": "接続元のコンポーネントID"
                    },
                    "to_component": {
                        "type": "string",
                        "description": "接続先のコンポーネントID"
                    },
                    "connection_type": {
                        "type": "string",
                        "enum": ["wire", "dot"],
                        "description": "接続のタイプ（デフォルト: wire）"
                    }
                },
                "required": ["from_component", "to_component"]
            }
        ),
        Tool(
            name="save_circuit",
            description="回路図を画像ファイルとして保存",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "保存するファイル名"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["png", "svg", "pdf"],
                        "description": "出力フォーマット（デフォルト: svg）"
                    },
                    "dpi": {
                        "type": "number",
                        "description": "DPI設定（デフォルト: 150）"
                    }
                },
                "required": ["filename"]
            }
        ),
        Tool(
            name="get_circuit_info",
            description="現在の回路図の情報を取得",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_available_components",
            description="利用可能なコンポーネントタイプの一覧を取得",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="add_spacer",
            description="コンポーネント間にスペースを追加して文字の重複を防ぐ",
            inputSchema={
                "type": "object",
                "properties": {
                    "length": {
                        "type": "number",
                        "description": "スペースの長さ（デフォルト: 1.0）"
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["right", "left", "up", "down"],
                        "description": "スペースの方向（デフォルト: right）"
                    }
                }
            }
        ),
        Tool(
            name="optimize_layout",
            description="回路図のレイアウトを最適化して文字の重複を防ぐ",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="create_loop_circuit",
            description="指定されたコンポーネントで四角形の閉回路を作成",
            inputSchema={
                "type": "object",
                "properties": {
                    "components": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "id": {"type": "string"},
                                "label": {"type": "string"},
                                "value": {"type": "string"}
                            },
                            "required": ["type", "id"]
                        },
                        "description": "回路に含めるコンポーネントのリスト"
                    },
                    "size": {
                        "type": "number",
                        "description": "回路の一辺の長さ（デフォルト: 3）"
                    }
                },
                "required": ["components"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent | ImageContent | EmbeddedResource]:
    """ツールの呼び出しを処理"""
    global current_drawing, components
    
    if arguments is None:
        arguments = {}
    
    try:
        if name == "create_circuit":
            # 新しい回路図を作成
            current_drawing = Drawing()
            
            # 文字の重複を避けるための設定
            current_drawing.config(fontsize=8)   # フォントサイズを小さく
            
            components = {}
            
            title = arguments.get("title", "")
            # タイトル設定は描画後に実装可能
            
            size = arguments.get("size")
            # サイズ設定は必要に応じて後で実装
            
            return [TextContent(type="text", text="新しい回路図を作成しました（文字重複防止設定適用済み）")]
        
        elif name == "add_component":
            if current_drawing is None:
                current_drawing = Drawing()
            
            component_type = arguments["component_type"]
            component_id = arguments["component_id"]
            
            # コンポーネントクラスを取得
            ComponentClass = get_component_class(component_type)
            if ComponentClass is None:
                return [TextContent(type="text", text=f"未知のコンポーネントタイプ: {component_type}")]
            
            # コンポーネントを作成
            component_args = {}
            
            # コンポーネントを作成
            component_args = {}
            
            # ラベルの設定（簡潔に、位置を明確に）
            label = arguments.get("label")
            if label:
                # ラベルが長い場合は短縮
                if len(label) > 4:
                    label = label[:4]
                component_args["label"] = label
            
            # 値の設定（簡潔に、ラベルと重ならないように）
            value = arguments.get("value")
            if value:
                # 値が長い場合は短縮
                if len(value) > 4:
                    value = value[:4]
                component_args["value"] = value
            
            # 方向の設定
            direction = arguments.get("direction", "right")
            direction_map = {
                "right": "right",
                "left": "left", 
                "up": "up",
                "down": "down"
            }
            component_args["d"] = direction_map.get(direction, "right")
            
            # 位置の設定（四角形の配置を可能にする）
            position = arguments.get("position")
            if position and len(position) >= 2:
                component_args["at"] = (position[0], position[1])
            else:
                # 自動配置：四角形の回路を作るための配置戦略
                if len(components) == 0:
                    # 最初のコンポーネントは原点に
                    component_args["at"] = (0, 0)
                elif len(components) == 1:
                    # 2番目のコンポーネントは右に
                    component_args["at"] = (3, 0)
                    component_args["d"] = "down"
                elif len(components) == 2:
                    # 3番目のコンポーネントは下に
                    component_args["at"] = (3, -3)
                    component_args["d"] = "left"
                elif len(components) == 3:
                    # 4番目のコンポーネントは左に（回路を閉じる）
                    component_args["at"] = (0, -3)
                    component_args["d"] = "up"
                else:
                    # 5番目以降は前のコンポーネントから適切な距離で配置
                    last_component = list(components.values())[-1]
                    if hasattr(last_component, 'end'):
                        if direction == "right":
                            component_args["at"] = (last_component.end[0] + 2.0, last_component.end[1])
                        elif direction == "down":
                            component_args["at"] = (last_component.end[0], last_component.end[1] - 2.0)
                        elif direction == "up":
                            component_args["at"] = (last_component.end[0], last_component.end[1] + 2.0)
                        else:  # left
                            component_args["at"] = (last_component.end[0] - 2.0, last_component.end[1])
            
            # コンポーネントを追加
            component = current_drawing.add(ComponentClass(**component_args))
            components[component_id] = component
            
            return [TextContent(type="text", text=f"コンポーネント '{component_id}' ({component_type}) を追加しました")]
        
        elif name == "connect_components":
            if current_drawing is None:
                return [TextContent(type="text", text="回路図が作成されていません")]
            
            from_id = arguments["from_component"]
            to_id = arguments["to_component"]
            connection_type = arguments.get("connection_type", "wire")
            
            if from_id not in components:
                return [TextContent(type="text", text=f"コンポーネント '{from_id}' が見つかりません")]
            
            if to_id not in components:
                return [TextContent(type="text", text=f"コンポーネント '{to_id}' が見つかりません")]
            
            from_component = components[from_id]
            to_component = components[to_id]
            
            # 接続を追加（適切な接続点を使用）
            if connection_type == "wire":
                # 直接接続が難しい場合は、角をつけた配線を使用
                try:
                    current_drawing.add(elm.Line().at(from_component.end).to(to_component.start))
                except:
                    # 直接接続できない場合は、経由点を作る
                    mid_x = (from_component.end[0] + to_component.start[0]) / 2
                    mid_y = (from_component.end[1] + to_component.start[1]) / 2
                    current_drawing.add(elm.Line().at(from_component.end).to((mid_x, from_component.end[1])))
                    current_drawing.add(elm.Line().at((mid_x, from_component.end[1])).to((mid_x, to_component.start[1])))
                    current_drawing.add(elm.Line().at((mid_x, to_component.start[1])).to(to_component.start))
            elif connection_type == "dot":
                # ドット接続
                current_drawing.add(elm.Dot().at(from_component.end))
                try:
                    current_drawing.add(elm.Line().to(to_component.start))
                except:
                    # 経由点を作る
                    mid_x = (from_component.end[0] + to_component.start[0]) / 2
                    mid_y = (from_component.end[1] + to_component.start[1]) / 2
                    current_drawing.add(elm.Line().to((mid_x, from_component.end[1])))
                    current_drawing.add(elm.Line().to((mid_x, to_component.start[1])))
                    current_drawing.add(elm.Line().to(to_component.start))
            
            return [TextContent(type="text", text=f"'{from_id}' と '{to_id}' を接続しました")]
        
        elif name == "save_circuit":
            if current_drawing is None:
                return [TextContent(type="text", text="回路図が作成されていません")]
            
            filename = arguments["filename"]
            format_type = arguments.get("format", "svg")
            dpi = arguments.get("dpi", 150)
            
            # ファイル拡張子を確認・追加
            if not filename.endswith(f".{format_type}"):
                filename = f"{filename}.{format_type}"
            
            # 絶対パスに変換
            filepath = Path(filename).resolve()
            
            try:
                # 空の回路図の場合、最小限の要素を追加
                if len(components) == 0:
                    # 一時的にドットを追加して軸を定義
                    temp_dot = current_drawing.add(elm.Dot().at((0, 0)))
                
                # 図のサイズとパディングを調整して文字の重複を防ぐ
                save_args = {
                    "transparent": False,
                    "dpi": dpi
                }
                
                # PNG/PDFの場合のみDPIを適用、SVGは自動的にベクターとして保存
                if format_type in ["png", "pdf"]:
                    save_args["dpi"] = dpi
                elif format_type == "svg":
                    # SVGの場合はDPIは不要、必要に応じて他のパラメータを設定
                    save_args.pop("dpi", None)
                
                current_drawing.save(str(filepath), **save_args)
                return [TextContent(type="text", text=f"回路図を '{filepath}' に保存しました")]
            except Exception as e:
                return [TextContent(type="text", text=f"保存エラー: {str(e)}")]
        
        elif name == "get_circuit_info":
            if current_drawing is None:
                return [TextContent(type="text", text="回路図が作成されていません")]
            
            info = {
                "components_count": len(components),
                "component_ids": list(components.keys()),
                "drawing_title": getattr(current_drawing, "title", "未設定")
            }
            
            info_text = f"""
現在の回路図情報:
- コンポーネント数: {info['components_count']}
- コンポーネントID: {', '.join(info['component_ids']) if info['component_ids'] else 'なし'}
- タイトル: {info['drawing_title']}
"""
            
            return [TextContent(type="text", text=info_text)]
        
        elif name == "list_available_components":
            # 利用可能なモジュールとその名前のマッピング
            modules_to_inspect = [
                (elm, "elm"),
                (logic, "logic"),
                (dsp, "dsp"),
            ]
            
            components_list = ["--- Schemdraw 全エレメントリスト ---"]
            total_elements = 0
            
            # 各モジュールを順番に処理
            for module, name in modules_to_inspect:
                components_list.append(f"\n--- {name} ({module.__name__}) ---")
                
                # モジュール内のクラス名（大文字で始まるもの）を取得
                element_list = [e_name for e_name in dir(module) if e_name[0].isupper()]
                
                if not element_list:
                    components_list.append("（このモジュールに公開エレメントはありません）")
                    continue
                
                # 'モジュール名.エレメント名' の形式で表示
                for element_name in element_list:
                    element_class = getattr(module, element_name)
                    if isinstance(element_class, type):
                        components_list.append(f"  - {name}.{element_name}")
                
                valid_elements = [e for e in element_list if isinstance(getattr(module, e), type)]
                total_elements += len(valid_elements)
            
            components_list.append(f"\n--- 合計 ---")
            components_list.append(f"全モジュールの合計エレメント数: {total_elements}")
            
            return [TextContent(type="text", text="\n".join(components_list))]
        
        elif name == "add_spacer":
            if current_drawing is None:
                return [TextContent(type="text", text="回路図が作成されていません")]
            
            length = arguments.get("length", 1.0)
            direction = arguments.get("direction", "right")
            
            # 方向に応じてスペーサーを追加
            direction_map = {
                "right": "right",
                "left": "left",
                "up": "up", 
                "down": "down"
            }
            
            spacer_direction = direction_map.get(direction, "right")
            current_drawing.add(elm.Line(length=length, d=spacer_direction, color='white', lw=0))
            
            return [TextContent(type="text", text=f"スペーサー（長さ: {length}, 方向: {direction}）を追加しました")]
        
        elif name == "optimize_layout":
            if current_drawing is None:
                return [TextContent(type="text", text="回路図が作成されていません")]
            
            # 既存の回路図の設定を最適化
            current_drawing.config(fontsize=8)     # 小さなフォント
            
            return [TextContent(type="text", text="回路図のレイアウトを最適化しました（フォントサイズを調整）")]
        
        elif name == "create_loop_circuit":
            # 新しい回路図を作成
            current_drawing = Drawing()
            current_drawing.config(fontsize=8)
            components = {}
            
            component_list = arguments["components"]
            circuit_size = arguments.get("size", 3)
            
            if len(component_list) < 2:
                return [TextContent(type="text", text="ループ回路には最低2つのコンポーネントが必要です")]
            
            # 四角形の各辺の位置を計算
            positions = [
                (0, 0, "right"),        # 上辺左端（右向き）
                (circuit_size, 0, "down"),     # 上辺右端（下向き）
                (circuit_size, -circuit_size, "left"),    # 下辺右端（左向き）
                (0, -circuit_size, "up")       # 下辺左端（上向き）
            ]
            
            # コンポーネントを配置
            for i, comp_info in enumerate(component_list):
                if i >= len(positions):
                    # 4つ以上のコンポーネントの場合は、辺を細分化
                    break
                    
                comp_type = comp_info["type"]
                comp_id = comp_info["id"]
                
                # コンポーネントクラスを取得
                ComponentClass = get_component_class(comp_type)
                if ComponentClass is None:
                    continue
                
                # 位置と方向を設定
                x, y, direction = positions[i]
                component_args = {
                    "at": (x, y),
                    "d": direction
                }
                
                # ラベルと値を設定
                if "label" in comp_info and comp_info["label"]:
                    label = comp_info["label"]
                    if len(label) > 4:
                        label = label[:4]
                    component_args["label"] = label
                
                if "value" in comp_info and comp_info["value"]:
                    value = comp_info["value"]
                    if len(value) > 4:
                        value = value[:4]
                    component_args["value"] = value
                
                # コンポーネントを追加
                component = current_drawing.add(ComponentClass(**component_args))
                components[comp_id] = component
            
            # コンポーネント間を接続してループを作成
            comp_ids = [comp["id"] for comp in component_list]
            for i in range(len(comp_ids)):
                if comp_ids[i] in components and comp_ids[(i + 1) % len(comp_ids)] in components:
                    from_comp = components[comp_ids[i]]
                    to_comp = components[comp_ids[(i + 1) % len(comp_ids)]]
                    
                    try:
                        current_drawing.add(elm.Line().at(from_comp.end).to(to_comp.start))
                    except:
                        # 直接接続できない場合はスキップ
                        pass
            
            return [TextContent(type="text", text=f"四角形のループ回路を作成しました（{len(component_list)}個のコンポーネント）")]
        
        else:
            return [TextContent(type="text", text=f"未知のツール: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"エラーが発生しました: {str(e)}")]


async def main():
    """メイン関数"""
    
    # 初期化時に空の回路図を作成
    reset_drawing()
    
    # STDIOでサーバーを実行
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="schemdraw-mcp-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

def cli_main():
    """CLI entry point for the schemdraw-mcp-server command"""
    asyncio.run(main())

if __name__ == "__main__":
    cli_main()