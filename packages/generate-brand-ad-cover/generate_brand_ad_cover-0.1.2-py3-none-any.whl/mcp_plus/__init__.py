# -*- coding: utf-8 -*-  
"""
MCP广告封面生成器服务器 - 基于CodeBuddy风格设计
"""
import json
import random
import os
from typing import Dict, List, Optional

try:
    from mcp.server.fastmcp import FastMCP
    # 创建MCP服务器实例
    mcp = FastMCP("mcp-plus")
except ImportError:
    print("警告: 无法导入 mcp.server.fastmcp 模块，使用自定义实现")
    # 使用我们的自定义实现
    from .server_impl import SimpleMCP
    mcp = SimpleMCP("mcp-plus")

def main():
    """
    MCP Plus 主函数 - 启动MCP服务器
    """
    import sys
    import asyncio
    
    # 打印当前工作目录
    print(f"当前工作目录: {os.getcwd()}", file=sys.stderr)
    
    # 打印已注册的工具
    print("已注册的工具:", file=sys.stderr)
    print("- generate_brand_ad_cover", file=sys.stderr)
    print("MCP服务器启动中...", file=sys.stderr)
    
    try:
        # 使用异步方式运行MCP服务器
        asyncio.run(mcp.run())
    except KeyboardInterrupt:
        print("MCP服务器已停止", file=sys.stderr)
    except Exception as e:
        print(f"MCP服务器错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

@mcp.tool()
def generate_brand_ad_cover(
    brand_name: str,
    subtitle: str = "",
    slogan: str = "",
    style: str = "简约",
    primary_color: str = "蓝色",
    width: int = 1080,
    height: int = 1080,
    output_path: str = "brand_ad_cover.svg"
) -> str:
    """
    生成品牌广告封面，参考CodeBuddy风格设计。
    
    参数说明：
    - brand_name: 品牌名称
    - subtitle: 副标题（如：AI编程伙伴）
    - slogan: 品牌标语（如：智能代码生成 · 高效开发体验）
    - style: 设计风格（科技/简约/专业/未来）
    - primary_color: 主色调（蓝色/紫色/绿色/橙色）
    - width: 图片宽度（像素）
    - height: 图片高度（像素）
    - output_path: 输出文件路径
    """
    
    try:
        # 确保使用当前工作目录的绝对路径
        current_dir = os.getcwd()
        abs_output_path = os.path.join(current_dir, output_path)
        
        # 颜色方案
        color_schemes = {
            "蓝色": {
                "primary": "#1E40AF", "secondary": "#3B82F6", "accent": "#60A5FA", 
                "light": "#93C5FD", "dark": "#1E3A8A", "text": "#1E3A8A", 
                "bg": "#FFFFFF", "glow": "#3B82F6", "energy": "#F59E0B"
            },
            "紫色": {
                "primary": "#6B21A8", "secondary": "#8B5CF6", "accent": "#A78BFA", 
                "light": "#C4B5FD", "dark": "#581C87", "text": "#581C87",
                "bg": "#FFFFFF", "glow": "#8B5CF6", "energy": "#F59E0B"
            },
            "绿色": {
                "primary": "#047857", "secondary": "#10B981", "accent": "#34D399", 
                "light": "#6EE7B7", "dark": "#064E3B", "text": "#064E3B",
                "bg": "#FFFFFF", "glow": "#10B981", "energy": "#F59E0B"
            },
            "红色": {
                "primary": "#DC2626", "secondary": "#EF4444", "accent": "#F87171", 
                "light": "#FCA5A5", "dark": "#991B1B", "text": "#991B1B",
                "bg": "#FFFFFF", "glow": "#EF4444", "energy": "#F59E0B"
            },
            "橙色": {
                "primary": "#EA580C", "secondary": "#F97316", "accent": "#FB923C", 
                "light": "#FDBA74", "dark": "#9A3412", "text": "#9A3412",
                "bg": "#FFFFFF", "glow": "#F97316", "energy": "#06B6D4"
            }
        }
        
        colors = color_schemes.get(primary_color, color_schemes["蓝色"])
        
        # 根据风格选择不同的模板
        if style == "科技":
            return generate_tech_style_cover(brand_name, subtitle, slogan, colors, width, height, abs_output_path)
        else:  # 默认使用简约风格
            return generate_simple_style_cover(brand_name, subtitle, slogan, colors, width, height, abs_output_path)
    except Exception as e:
        return f"生成封面时出现错误: {str(e)}"

def generate_simple_style_cover(brand_name, subtitle, slogan, colors, width, height, output_path):
    """生成简约风格的品牌广告封面"""
    try:
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="pureWhiteBg" cx="50%" cy="50%" r="80%">
      <stop offset="0%" style="stop-color:#FEFEFE;stop-opacity:1" />
      <stop offset="70%" style="stop-color:#FDFDFD;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#F0F4F8;stop-opacity:1" />
    </radialGradient>
    
    <linearGradient id="brandGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{colors['primary']};stop-opacity:0.6" />
      <stop offset="30%" style="stop-color:{colors['secondary']};stop-opacity:0.7" />
      <stop offset="70%" style="stop-color:{colors['accent']};stop-opacity:0.5" />
      <stop offset="100%" style="stop-color:{colors['light']};stop-opacity:0.3" />
    </linearGradient>
    
    <linearGradient id="brandBrush" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{colors['dark']};stop-opacity:0" />
      <stop offset="20%" style="stop-color:{colors['primary']};stop-opacity:0.8" />
      <stop offset="50%" style="stop-color:{colors['secondary']};stop-opacity:1" />
      <stop offset="80%" style="stop-color:{colors['accent']};stop-opacity:0.8" />
      <stop offset="100%" style="stop-color:{colors['light']};stop-opacity:0" />
    </linearGradient>
    
    <radialGradient id="brandGlow" cx="50%" cy="50%" r="60%">
      <stop offset="0%" style="stop-color:{colors['energy']};stop-opacity:0.4" />
      <stop offset="50%" style="stop-color:{colors['primary']};stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#FEFEFE;stop-opacity:0" />
    </radialGradient>
    
    <filter id="brandGlowFilter" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    
    <filter id="brandShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="{colors['primary']}" flood-opacity="0.15"/>
    </filter>
    
    <filter id="textGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="1" stdDeviation="3" flood-color="{colors['primary']}" flood-opacity="0.2"/>
    </filter>
  </defs>
  
  <rect width="{width}" height="{height}" fill="url(#pureWhiteBg)" />
  
  <!-- 装饰元素 - 左上角 -->
  <text x="150" y="200" font-family="'Courier New', monospace" font-size="48" 
        fill="url(#brandGradient)" opacity="0.6" filter="url(#brandShadow)">&lt;/&gt;</text>
  
  <!-- 装饰元素 - 右上角 -->
  <text x="850" y="180" font-family="'Courier New', monospace" font-size="36" 
        fill="url(#brandGradient)" opacity="0.5" filter="url(#brandShadow)">{{ }}</text>
  
  <!-- 装饰节点 -->
  <circle cx="200" cy="350" r="4" fill="{colors['secondary']}" opacity="0.8" filter="url(#brandGlowFilter)"/>
  <circle cx="280" cy="320" r="3" fill="{colors['accent']}" opacity="0.7" filter="url(#brandGlowFilter)"/>
  <circle cx="320" cy="380" r="3.5" fill="{colors['primary']}" opacity="0.9" filter="url(#brandGlowFilter)"/>
  
  <!-- 连接线 -->
  <line x1="200" y1="350" x2="280" y2="320" 
        stroke="url(#brandBrush)" stroke-width="1.5" opacity="0.6" filter="url(#brandShadow)"/>
  <line x1="280" y1="320" x2="320" y2="380" 
        stroke="url(#brandBrush)" stroke-width="1.5" opacity="0.6" filter="url(#brandShadow)"/>
  <line x1="200" y1="350" x2="320" y2="380" 
        stroke="{colors['light']}" stroke-width="1" opacity="0.4"/>
  
  <!-- 装饰元素 - 右下角 -->
  <path d="M750,700 L850,650 L850,750 Z" 
        fill="url(#brandGradient)" opacity="0.3" filter="url(#brandShadow)"/>
  <rect x="780" y="720" width="40" height="8" 
        fill="{colors['energy']}" opacity="0.6" rx="4" filter="url(#brandGlowFilter)"/>
  
  <!-- 主标题背景装饰 -->
  <ellipse cx="{width//2}" cy="480" rx="280" ry="60" 
           fill="url(#brandGlow)" opacity="0.2" filter="url(#brandShadow)"/>
  
  <!-- 主标题 -->
  <text x="{width//2}" y="500" text-anchor="middle" 
        font-family="'Microsoft YaHei', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif" 
        font-size="72" font-weight="700" 
        fill="{colors['text']}" filter="url(#textGlow)">{brand_name}</text>'''
        
        if subtitle:
            svg_content += f'''
  
  <!-- 副标题装饰线 -->
  <path d="M{width*0.35},540 Q{width//2},530 {width*0.65},540" 
        fill="none" stroke="url(#brandBrush)" stroke-width="2" opacity="0.5" filter="url(#brandGlowFilter)"/>
  
  <!-- 副标题 -->
  <text x="{width//2}" y="570" text-anchor="middle" 
        font-family="'Microsoft YaHei', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif" 
        font-size="36" font-weight="300" 
        fill="{colors['secondary']}" filter="url(#textGlow)">{subtitle}</text>'''
        
        if slogan:
            svg_content += f'''
  
  <!-- Slogan -->
  <text x="{width//2}" y="620" text-anchor="middle" 
        font-family="'Microsoft YaHei', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif" 
        font-size="24" font-weight="200" 
        fill="{colors['accent']}" filter="url(#brandShadow)">{slogan}</text>'''
        
        svg_content += f'''
  
  <!-- 底部装饰 -->
  <path d="M{width*0.28},900 Q{width//2},880 {width*0.72},900" 
        fill="none" stroke="url(#brandBrush)" stroke-width="3" opacity="0.4" filter="url(#brandShadow)"/>
  
  <!-- 品牌标识点 -->
  <circle cx="{width//2}" cy="920" r="6" 
          fill="{colors['energy']}" opacity="0.8" filter="url(#brandGlowFilter)"/>
  
  <!-- 装饰元素 -->
  <text x="100" y="950" font-family="'Courier New', monospace" font-size="14" 
        fill="{colors['light']}" opacity="0.6">console.log("{brand_name}");</text>
  
  <!-- 装饰点 -->
  <circle cx="80" cy="80" r="2" 
          fill="{colors['secondary']}" opacity="0.4" filter="url(#brandGlowFilter)"/>
  <circle cx="1000" cy="1000" r="2.5" 
          fill="{colors['primary']}" opacity="0.5" filter="url(#brandGlowFilter)"/>
</svg>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return f"🚀 品牌广告封面已生成: {output_path} ({width}x{height}px, 简约风格, {colors['primary']}主色调)"
    except Exception as e:
        return f"生成封面时出现错误: {str(e)}"

def generate_tech_style_cover(brand_name, subtitle, slogan, colors, width, height, output_path):
    """生成科技风格的品牌广告封面"""
    try:
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="techBg" cx="30%" cy="20%" r="120%">
      <stop offset="0%" style="stop-color:{colors['glow']};stop-opacity:0.2" />
      <stop offset="30%" style="stop-color:{colors['primary']};stop-opacity:0.5" />
      <stop offset="70%" style="stop-color:#0F172A;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1E293B;stop-opacity:1" />
    </radialGradient>
    
    <linearGradient id="brandGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{colors['secondary']};stop-opacity:0.9" />
      <stop offset="50%" style="stop-color:{colors['glow']};stop-opacity:0.8" />
      <stop offset="100%" style="stop-color:{colors['energy']};stop-opacity:0.7" />
    </linearGradient>
    
    <filter id="neonGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="6" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    
    <filter id="textGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    
    <linearGradient id="lightBeam" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{colors['glow']};stop-opacity:0" />
      <stop offset="50%" style="stop-color:{colors['glow']};stop-opacity:0.8" />
      <stop offset="100%" style="stop-color:{colors['glow']};stop-opacity:0" />
    </linearGradient>
  </defs>
  
  <rect width="{width}" height="{height}" fill="url(#techBg)" />'''
        
        # 添加科技网格背景
        for i in range(0, width, 60):
            svg_content += f'  <line x1="{i}" y1="0" x2="{i}" y2="{height}" stroke="{colors["glow"]}" stroke-width="0.3" opacity="0.2" filter="url(#neonGlow)"/>\n'
        for i in range(0, height, 60):
            svg_content += f'  <line x1="0" y1="{i}" x2="{width}" y2="{i}" stroke="{colors["glow"]}" stroke-width="0.3" opacity="0.2" filter="url(#neonGlow)"/>\n'
        
        # 代码符号装饰
        svg_content += f'''
  
  <!-- 代码符号装饰 -->
  <text x="{width*0.14}" y="{height*0.18}" font-family="'Courier New', monospace" font-size="42" 
        fill="{colors['glow']}" opacity="0.7" filter="url(#neonGlow)">&lt;/&gt;</text>
  <text x="{width*0.79}" y="{height*0.17}" font-family="'Courier New', monospace" font-size="32" 
        fill="{colors['secondary']}" opacity="0.6" filter="url(#neonGlow)">{{ }}</text>
  
  <!-- AI神经网络节点 -->
  <circle cx="{width*0.18}" cy="{height*0.32}" r="5" fill="{colors['glow']}" opacity="0.8" filter="url(#neonGlow)"/>
  <circle cx="{width*0.26}" cy="{height*0.30}" r="4" fill="{colors['secondary']}" opacity="0.7" filter="url(#neonGlow)"/>
  <circle cx="{width*0.30}" cy="{height*0.35}" r="4.5" fill="{colors['energy']}" opacity="0.9" filter="url(#neonGlow)"/>
  <circle cx="{width*0.35}" cy="{height*0.31}" r="3.5" fill="{colors['glow']}" opacity="0.6" filter="url(#neonGlow)"/>
  
  <!-- 神经网络连接线 -->
  <line x1="{width*0.18}" y1="{height*0.32}" x2="{width*0.26}" y2="{height*0.30}" 
        stroke="url(#brandGrad)" stroke-width="2" opacity="0.7" filter="url(#neonGlow)"/>
  <line x1="{width*0.26}" y1="{height*0.30}" x2="{width*0.30}" y2="{height*0.35}" 
        stroke="url(#brandGrad)" stroke-width="2" opacity="0.7" filter="url(#neonGlow)"/>
  <line x1="{width*0.30}" y1="{height*0.35}" x2="{width*0.35}" y2="{height*0.31}" 
        stroke="url(#brandGrad)" stroke-width="1.5" opacity="0.6" filter="url(#neonGlow)"/>
  <line x1="{width*0.18}" y1="{height*0.32}" x2="{width*0.35}" y2="{height*0.31}" 
        stroke="{colors['glow']}" stroke-width="1" opacity="0.4" filter="url(#neonGlow)"/>'''
        
        # 主标题区域
        title_y = height * 0.46
        svg_content += f'''
  
  <!-- 主标题背景光效 -->
  <rect x="{width*0.05}" y="{title_y-70}" width="{width*0.9}" height="140" 
        fill="url(#brandGrad)" opacity="0.1" rx="20" filter="url(#neonGlow)"/>
  <rect x="{width*0.1}" y="{title_y-4}" width="{width*0.8}" height="8" 
        fill="url(#lightBeam)" opacity="0.6" rx="4"/>
  
  <!-- 主标题 -->
  <text x="{width//2}" y="{title_y}" text-anchor="middle" 
        font-family="'SF Pro Display', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif" 
        font-size="84" font-weight="800" 
        fill="{colors['text']}" filter="url(#textGlow)">{brand_name}</text>'''
        
        if subtitle:
            subtitle_y = height * 0.53
            svg_content += f'''
  
  <!-- 副标题背景 -->
  <rect x="{width*0.2}" y="{subtitle_y-25}" width="{width*0.6}" height="50" 
        fill="{colors['primary']}" opacity="0.1" rx="25" filter="url(#neonGlow)"/>
  <line x1="{width*0.25}" y1="{subtitle_y-20}" x2="{width*0.75}" y2="{subtitle_y-20}" 
        stroke="url(#brandGrad)" stroke-width="2" opacity="0.8" filter="url(#neonGlow)"/>
  
  <!-- 副标题 -->
  <text x="{width//2}" y="{subtitle_y}" text-anchor="middle" 
        font-family="'SF Pro Display', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif" 
        font-size="42" font-weight="400" 
        fill="{colors['glow']}" filter="url(#textGlow)">{subtitle}</text>'''
        
        if slogan:
            slogan_y = height * 0.57
            svg_content += f'''
  
  <!-- Slogan -->
  <text x="{width//2}" y="{slogan_y}" text-anchor="middle" 
        font-family="'SF Pro Display', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif" 
        font-size="28" font-weight="300" 
        fill="{colors['light']}" filter="url(#textGlow)">{slogan}</text>'''
        
        # 代码装饰
        svg_content += f'''
  
  <!-- 代码装饰 -->
  <text x="{width*0.09}" y="{height*0.69}" font-family="'Courier New', monospace" font-size="16" 
        fill="{colors['glow']}" opacity="0.6" filter="url(#neonGlow)">function createMagic() {{</text>
  <text x="{width*0.11}" y="{height*0.72}" font-family="'Courier New', monospace" font-size="16" 
        fill="{colors['secondary']}" opacity="0.6" filter="url(#neonGlow)">  return "{brand_name}";</text>
  <text x="{width*0.09}" y="{height*0.75}" font-family="'Courier New', monospace" font-size="16" 
        fill="{colors['glow']}" opacity="0.6" filter="url(#neonGlow)">}}</text>
  
  <!-- 底部装饰 -->
  <rect x="{width*0.35}" y="{height*0.88}" width="{width*0.3}" height="4" 
        fill="url(#brandGrad)" opacity="0.9" rx="2" filter="url(#neonGlow)"/>
  <circle cx="{width*0.4}" cy="{height*0.91}" r="6" fill="{colors['glow']}" opacity="0.8" filter="url(#neonGlow)"/>
  <circle cx="{width*0.6}" cy="{height*0.91}" r="6" fill="{colors['energy']}" opacity="0.8" filter="url(#neonGlow)"/>
  
  <!-- 背景粒子效果 -->
  <circle cx="{width*0.74}" cy="{height*0.28}" r="3" fill="{colors['glow']}" opacity="0.3" filter="url(#neonGlow)"/>
  <circle cx="{width*0.28}" cy="{height*0.74}" r="4" fill="{colors['secondary']}" opacity="0.2" filter="url(#neonGlow)"/>
  <circle cx="{width*0.83}" cy="{height*0.65}" r="2" fill="{colors['energy']}" opacity="0.4" filter="url(#neonGlow)"/>
</svg>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return f"🚀 品牌广告封面已生成: {output_path} ({width}x{height}px, 科技风格, {colors['primary']}主色调)"
    except Exception as e:
        return f"生成封面时出现错误: {str(e)}"

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """
    根据提供的名称，获取一句个性化的问候语。
    """
    return f"Hello, {name}!"

if __name__ == "__main__":
    import sys
    
    # 打印当前工作目录
    print(f"当前工作目录: {os.getcwd()}", file=sys.stderr)
    
    # 打印已注册的工具
    print("已注册的工具:", file=sys.stderr)
    print("- add", file=sys.stderr)
    print("- generate_brand_ad_cover", file=sys.stderr)
    print("MCP服务器启动中...", file=sys.stderr)
    
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print("MCP服务器已停止", file=sys.stderr)
    except Exception as e:
        print(f"MCP服务器错误: {e}", file=sys.stderr)