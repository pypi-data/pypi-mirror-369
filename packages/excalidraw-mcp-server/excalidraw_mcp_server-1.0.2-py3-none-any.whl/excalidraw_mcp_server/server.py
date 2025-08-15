#!/usr/bin/env python3
"""
完全按照 HTTP 接口实现的 Excalidraw MCP 服务器
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
import httpx

# Configuration
BASE_URL = "http://127.0.0.1:31337"


class ExcalidrawMCPServer:
    """完全按照 HTTP 接口实现的 MCP 服务器"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
        self.initialized = False

    def get_capabilities(self):
        """获取服务器能力"""
        return {
            "tools": {}
        }

    def get_server_info(self):
        """获取服务器信息"""
        return {
            "name": "excalidraw-http",
            "version": "1.0.0"
        }




    def get_tools(self):
        """获取工具列表 - 对应简化的画布操作接口"""
        return [
            {
                "name": "health_check",
                "description": "检查服务器状态 (GET /health)",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },

            {
                "name": "get_canvas",
                "description": "获取当前画布数据 (GET /canvas)",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "update_canvas",
                "description": "更新画布数据 (PUT /canvas)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "elements": {
                            "type": "array",
                            "description": "Excalidraw 元素数组",
                            "items": {
                                "type": "object"
                            }
                        },
                        "appState": {
                            "type": "object",
                            "description": "应用状态"
                        },
                        "files": {
                            "type": "object",
                            "description": "文件附件"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "clear_canvas",
                "description": "清除画布 (POST /canvas/clear)",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "export_canvas",
                "description": "导出画布为toDataURL格式 (GET /canvas/export)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "description": "导出格式: toDataURL",
                            "enum": ["toDataURL"]
                        },
                        "width": {
                            "type": "integer",
                            "description": "导出宽度（像素）",
                            "minimum": 1,
                            "maximum": 4096
                        },
                        "height": {
                            "type": "integer",
                            "description": "导出高度（像素）",
                            "minimum": 1,
                            "maximum": 4096
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "remove_element",
                "description": "移除指定ID的元素",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "element_id": {
                            "type": "string",
                            "description": "要移除的元素ID"
                        }
                    },
                    "required": ["element_id"]
                }
            },
            {
                "name": "update_element",
                "description": "更新指定ID的元素",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "element_id": {
                            "type": "string",
                            "description": "要更新的元素ID"
                        },
                        "element_data": {
                            "type": "object",
                            "description": "新的元素数据"
                        }
                    },
                    "required": ["element_id", "element_data"]
                }
            }
        ]

    async def handle_request(self, request: dict) -> dict:
        """处理请求"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        if method == "initialize":
            self.initialized = True
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": self.get_capabilities(),
                    "serverInfo": self.get_server_info()
                }
            }

        if not self.initialized:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32002,
                    "message": "Server not initialized"
                }
            }

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": self.get_tools()
                }
            }



        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            try:
                result = await self.call_tool(tool_name, arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"工具执行失败: {str(e)}"
                    }
                }

        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"未知方法: {method}"
                }
            }

    async def call_tool(self, name: str, args: dict) -> str:
        """执行工具 - 对应简化的画布操作接口"""

        # GET /health
        if name == "health_check":
            try:
                response = await self.client.get(f"{BASE_URL}/health")
                if response.status_code == 200:
                    return f"✅ 服务器正常: {response.text}"
                else:
                    return f"❌ 服务器异常: HTTP {response.status_code}"
            except Exception as e:
                return f"❌ 连接失败: {str(e)}"



        # GET /canvas
        elif name == "get_canvas":
            try:
                response = await self.client.get(f"{BASE_URL}/canvas")
                if response.status_code == 200:
                    data = response.json()
                    canvas = data.get("canvas", {})
                    elements_count = len(canvas.get("elements", []) or [])
                    return f"✅ 画布数据\n元素数量: {elements_count}\n更新时间: {canvas.get('updated_at', 'unknown')}"
                else:
                    return f"❌ 获取画布数据失败: HTTP {response.status_code}"
            except Exception as e:
                return f"❌ 获取画布数据失败: {str(e)}"

        # PUT /canvas
        elif name == "update_canvas":
            payload = {
                "elements": args.get("elements"),
                "appState": args.get("appState"),
                "files": args.get("files")
            }
            try:
                response = await self.client.put(f"{BASE_URL}/canvas", json=payload)
                if response.status_code == 200:
                    return "✅ 画布更新成功"
                else:
                    return f"❌ 画布更新失败: HTTP {response.status_code}"
            except Exception as e:
                return f"❌ 画布更新失败: {str(e)}"

        # POST /canvas/clear
        elif name == "clear_canvas":
            try:
                response = await self.client.post(f"{BASE_URL}/canvas/clear")
                if response.status_code == 200:
                    return "✅ 画布清除成功"
                else:
                    return f"❌ 画布清除失败: HTTP {response.status_code}"
            except Exception as e:
                return f"❌ 画布清除失败: {str(e)}"

        # GET /canvas/export
        elif name == "export_canvas":
            format_type = args.get("format", "toDataURL")
            width = args.get("width", 800)
            height = args.get("height", 600)

            # 只支持toDataURL格式
            if format_type != "toDataURL":
                return f"❌ 不支持的格式: {format_type}，仅支持toDataURL格式"

            params = {
                "format": "toDataURL",
                "width": width,
                "height": height
            }

            try:
                response = await self.client.get(f"{BASE_URL}/canvas/export", params=params)
                if response.status_code == 200:
                    content_type = response.headers.get("content-type", "")

                    if "application/json" in content_type:
                        # JSON content with toDataURL
                        json_content = response.text
                        try:
                            data = json.loads(json_content)
                            data_url = data.get("dataURL", "")
                            return f"✅ toDataURL导出成功\n尺寸: {width}x{height}\n数据URL长度: {len(data_url)} 字符\n\n数据URL预览:\n{data_url[:100]}{'...' if len(data_url) > 100 else ''}\n\n完整响应:\n{json_content}"
                        except Exception as e:
                            return f"✅ toDataURL导出成功\n内容长度: {len(json_content)} 字符\n\n预览:\n{json_content[:500]}{'...' if len(json_content) > 500 else ''}"
                    else:
                        return f"❌ 意外的内容类型: {content_type}"
                else:
                    return f"❌ 导出失败: HTTP {response.status_code}"
            except Exception as e:
                return f"❌ 导出请求失败: {str(e)}"

        # 移除元素
        elif name == "remove_element":
            element_id = args.get("element_id")
            if not element_id:
                return "❌ 缺少element_id参数"

            try:
                # 调用后端API移除元素
                response = await self.client.delete(f"{BASE_URL}/canvas/element/{element_id}")

                if response.status_code == 404:
                    return f"❌ 未找到ID为 '{element_id}' 的元素"
                elif response.status_code != 200:
                    return f"❌ 移除元素失败: HTTP {response.status_code}"

                result = response.json()
                return f"✅ {result.get('message', '元素移除成功')}"

            except Exception as e:
                return f"❌ 移除元素失败: {str(e)}"

        # 更新元素
        elif name == "update_element":
            element_id = args.get("element_id")
            element_data = args.get("element_data")

            if not element_id:
                return "❌ 缺少element_id参数"
            if not element_data:
                return "❌ 缺少element_data参数"

            try:
                # 调用后端API更新元素
                payload = {"element": element_data}
                response = await self.client.put(f"{BASE_URL}/canvas/element/{element_id}", json=payload)

                if response.status_code == 404:
                    return f"❌ 未找到ID为 '{element_id}' 的元素"
                elif response.status_code != 200:
                    return f"❌ 更新元素失败: HTTP {response.status_code}"

                result = response.json()
                return f"✅ {result.get('message', '元素更新成功')}"

            except Exception as e:
                return f"❌ 更新元素失败: {str(e)}"

        else:
            raise Exception(f"未知工具: {name}")



    async def run(self):
        """运行服务器"""
        try:
            while True:
                line = sys.stdin.readline()
                if not line:
                    break

                try:
                    request = json.loads(line.strip())
                    response = await self.handle_request(request)
                    print(json.dumps(response, ensure_ascii=False), flush=True)
                except json.JSONDecodeError:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": "Parse error"}
                    }
                    print(json.dumps(error_response, ensure_ascii=False), flush=True)
                except Exception as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                    }
                    print(json.dumps(error_response, ensure_ascii=False), flush=True)

        finally:
            await self.client.aclose()


async def main():
    """主入口"""
    server = ExcalidrawMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())