# -*- coding: utf-8 -*-
"""
MCP服务器实现 - 符合MCP协议的标准实现
"""
import asyncio
import json
import sys
from typing import Any, Dict, List, Optional, Callable
import inspect

class SimpleMCP:
    """符合MCP协议的简单服务器实现"""
    
    def __init__(self, name: str):
        self.name = name
        self.tools = {}
        self.resources = {}
        self.version = "0.1.0"
        
    def tool(self):
        """工具装饰器"""
        def decorator(func: Callable):
            tool_name = func.__name__
            
            # 获取函数签名和文档
            sig = inspect.signature(func)
            doc = func.__doc__ or ""
            
            # 构建工具描述
            tool_info = {
                "name": tool_name,
                "description": doc.strip(),
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            
            # 解析参数
            for param_name, param in sig.parameters.items():
                param_type = "string"  # 默认类型
                if param.annotation != inspect.Parameter.empty:
                    if param.annotation == int:
                        param_type = "integer"
                    elif param.annotation == float:
                        param_type = "number"
                    elif param.annotation == bool:
                        param_type = "boolean"
                
                tool_info["inputSchema"]["properties"][param_name] = {
                    "type": param_type
                }
                
                if param.default == inspect.Parameter.empty:
                    tool_info["inputSchema"]["required"].append(param_name)
            
            self.tools[tool_name] = {
                "func": func,
                "info": tool_info
            }
            return func
        return decorator
    
    def resource(self, path: str):
        """资源装饰器"""
        def decorator(func: Callable):
            self.resources[path] = func
            return func
        return decorator
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {},
                            "resources": {}
                        },
                        "serverInfo": {
                            "name": self.name,
                            "version": self.version
                        }
                    }
                }
            
            elif method == "tools/list":
                tools_list = [tool["info"] for tool in self.tools.values()]
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": tools_list
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name not in self.tools:
                    raise Exception(f"Unknown tool: {tool_name}")
                
                tool_func = self.tools[tool_name]["func"]
                
                # 调用工具函数
                if asyncio.iscoroutinefunction(tool_func):
                    result = await tool_func(**arguments)
                else:
                    result = tool_func(**arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": str(result)
                            }
                        ]
                    }
                }
            
            elif method == "resources/list":
                resources_list = [
                    {
                        "uri": uri,
                        "name": uri.split("//")[-1] if "//" in uri else uri
                    }
                    for uri in self.resources.keys()
                ]
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "resources": resources_list
                    }
                }
            
            elif method == "resources/read":
                uri = params.get("uri")
                if uri not in self.resources:
                    raise Exception(f"Unknown resource: {uri}")
                
                resource_func = self.resources[uri]
                # 从URI中提取参数
                if "//" in uri:
                    template_part = uri.split("//")[0] + "//"
                    param_part = uri.replace(template_part, "")
                    result = resource_func(param_part)
                else:
                    result = resource_func()
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": "text/plain",
                                "text": str(result)
                            }
                        ]
                    }
                }
            
            else:
                raise Exception(f"Unknown method: {method}")
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32000,
                    "message": str(e)
                }
            }
    
    async def run(self):
        """运行MCP服务器"""
        print(f"MCP服务器 '{self.name}' 启动", file=sys.stderr)
        print(f"已注册工具: {list(self.tools.keys())}", file=sys.stderr)
        print(f"已注册资源: {list(self.resources.keys())}", file=sys.stderr)
        
        try:
            while True:
                # 从stdin读取请求
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    response = await self.handle_request(request)
                    print(json.dumps(response), flush=True)
                except json.JSONDecodeError as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": f"Parse error: {e}"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                except Exception as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32000,
                            "message": str(e)
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                    
        except KeyboardInterrupt:
            print("MCP服务器已停止", file=sys.stderr)
        except Exception as e:
            print(f"MCP服务器错误: {e}", file=sys.stderr)