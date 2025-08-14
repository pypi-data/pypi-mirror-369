# -*- coding: utf-8 -*-
"""
MCP服务器实现 - 简单替代版本
"""

class SimpleMCP:
    """简单的MCP服务器实现，用于替代原始的FastMCP"""
    
    def __init__(self, name):
        self.name = name
        self.tools = {}
        self.resources = {}
        print(f"创建MCP服务器: {name}")
    
    def tool(self):
        """工具装饰器"""
        def decorator(func):
            tool_name = func.__name__
            self.tools[tool_name] = func
            print(f"注册工具: {tool_name}")
            return func
        return decorator
    
    def resource(self, path):
        """资源装饰器"""
        def decorator(func):
            self.resources[path] = func
            print(f"注册资源: {path}")
            return func
        return decorator
    
    def run(self, **kwargs):
        """运行服务器"""
        transport = kwargs.get('transport', 'stdio')
        print(f"MCP服务器 '{self.name}' 启动 (transport: {transport})")
        print(f"已注册工具: {list(self.tools.keys())}")
        print(f"已注册资源: {list(self.resources.keys())}")
        
        # 在这里，我们可以实现一个简单的交互式命令行界面
        try:
            while True:
                cmd = input("MCP> ")
                if cmd.lower() in ['exit', 'quit', 'q']:
                    break
                elif cmd.startswith('call '):
                    parts = cmd.split(' ', 2)
                    if len(parts) < 2:
                        print("用法: call <tool_name> [args]")
                        continue
                    
                    tool_name = parts[1]
                    args = parts[2] if len(parts) > 2 else ""
                    
                    if tool_name in self.tools:
                        try:
                            result = self.tools[tool_name](args)
                            print(f"结果: {result}")
                        except Exception as e:
                            print(f"错误: {e}")
                    else:
                        print(f"未知工具: {tool_name}")
                elif cmd == 'list':
                    print("可用工具:")
                    for name in self.tools:
                        print(f"- {name}")
                elif cmd == 'help':
                    print("可用命令:")
                    print("- call <tool_name> [args]: 调用工具")
                    print("- list: 列出所有可用工具")
                    print("- help: 显示帮助信息")
                    print("- exit/quit/q: 退出")
                else:
                    print(f"未知命令: {cmd}. 输入 'help' 获取帮助。")
        except KeyboardInterrupt:
            print("\nMCP服务器已停止")