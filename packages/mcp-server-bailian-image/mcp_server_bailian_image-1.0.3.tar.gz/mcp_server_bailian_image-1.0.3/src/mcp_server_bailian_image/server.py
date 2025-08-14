#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云百炼-通义万相图像生成MCP服务器

本MCP服务器实现了通义万相文生图V2版API的功能，包括：
- 文生图功能（支持正向和反向提示词）
- 多种模型选择（万相2.2、2.1、2.0系列）
- 自定义图像尺寸和生成数量
- 同步调用方式

官方文档：https://help.aliyun.com/zh/model-studio/text-to-image-v2-api-reference

Author: John Chen
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional

try:
    import dashscope
except ImportError:
    print("错误: 请安装DashScope SDK: pip install dashscope")
    sys.exit(1)

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.lowlevel import NotificationOptions
from mcp.types import (
    Tool,
)

# 阿里云百炼API配置
IMAGE_SYNTHESIS_SERVICE = "aigc"
IMAGE_SYNTHESIS_TASK = "text2image"

# 支持的模型列表
SUPPORTED_MODELS = [
    "wan2.2-t2i-flash",  # 推荐：万相2.2极速版，当前最新模型
    "wan2.2-t2i-plus",   # 推荐：万相2.2专业版，当前最新模型
    "wanx2.1-t2i-turbo", # 万相2.1极速版
    "wanx2.1-t2i-plus",  # 万相2.1专业版
    "wanx2.0-t2i-turbo", # 万相2.0极速版
]

# 支持的图像尺寸
SUPPORTED_SIZES = [
    "512*512", "512*768", "512*1024", "768*512", "768*768", "768*1024",
    "1024*512", "1024*768", "1024*1024", "1024*1440", "1440*1024"
]


class BailianImageServer:
    """
    阿里云百炼-通义万相图像生成MCP服务器

    提供以下功能：
    1. 文生图V2版 - 基于文本提示词生成高质量图像
    2. 支持正向和反向提示词
    3. 多种模型选择（万相2.2、2.1、2.0系列）
    4. 自定义图像尺寸和生成数量
    5. 同步调用方式，快速获取结果

    官方文档：https://help.aliyun.com/zh/model-studio/text-to-image-v2-api-reference
    """

    def __init__(self, api_key: str):
        """
        初始化服务器

        Args:
            api_key: 阿里云百炼API密钥
        """
        self.api_key = api_key
        self.server = Server("bailian-image")
        
        # 配置DashScope
        dashscope.api_key = api_key

        # 注册工具
        self._register_tools()

    def _register_tools(self):
        """
        注册所有MCP工具
        """

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """
            列出所有可用的工具
            """
            return [
                Tool(
                    name="text2imagev2",
                    description="通义万相文生图V2版API。根据文本提示词生成高质量图像，支持正向和反向提示词、多种模型选择、自定义尺寸和生成数量。\n\n示例1 - 基础文生图：\n输入：prompt='一间有着精致窗户的花店，漂亮的木质门，摆放着花朵', model='wan2.2-t2i-flash', size='1024*1024'\n\n示例2 - 使用反向提示词：\n输入：prompt='雪地，白色小教堂，极光，冬日场景，柔和的光线', negative_prompt='人物', model='wan2.2-t2i-flash', size='1024*1024'\n\n官方文档：https://help.aliyun.com/zh/model-studio/text-to-image-v2-api-reference",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "正向提示词，用来描述生成图像中期望包含的元素和视觉特点。支持中英文，长度不超过800个字符，每个汉字/字母占一个字符，超过部分会自动截断。示例：一只坐着的橘黄色的猫，表情愉悦，活泼可爱，逼真准确。",
                            },
                            "negative_prompt": {
                                "type": "string",
                                "description": "（可选）反向提示词，用来描述不希望在画面中看到的内容，可以对画面进行限制。支持中英文，长度不超过500个字符，超过部分会自动截断。示例值：低分辨率、错误、最差质量、低质量、残缺、多余的手指、比例不良等。",
                            },
                            "model": {
                                "type": "string",
                                "description": "（必选）模型名称。示例值：wan2.2-t2i-turbo。支持的模型包括：万相2.2系列（wan2.2-t2i-flash推荐极速版、wan2.2-t2i-plus推荐专业版）、万相2.1系列（wanx2.1-t2i-turbo极速版、wanx2.1-t2i-plus专业版）、万相2.0系列（wanx2.0-t2i-turbo极速版）。",
                                "enum": SUPPORTED_MODELS,
                                "default": "wan2.2-t2i-flash",
                            },
                            "size": {
                                "type": "string",
                                "description": "（可选）输出图像的分辨率。默认值是1024*1024。图像宽高边长的像素范围为：[512, 1440]，单位像素。可任意组合以设置不同的图像分辨率，最高可达200万像素。",
                                "enum": SUPPORTED_SIZES,
                                "default": "1024*1024",
                            },
                            "n": {
                                "type": "integer",
                                "description": "（可选）生成图片的数量。取值范围为1~4张",
                                "minimum": 1,
                                "maximum": 4,
                                "default": 1,
                            },
                        },
                        "required": ["prompt"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
            """
            调用指定的工具
            """
            if name == "text2imagev2":
                return await self._text2imagev2(**arguments)
            else:
                raise ValueError(f"未知的工具名称: {name}")

    async def _text2imagev2(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        model: str = "wan2.2-t2i-flash",
        size: str = "1024*1024",
        n: int = 1,
    ) -> Dict[str, Any]:
        """
        通义万相文生图V2版API

        Args:
            prompt: 正向提示词，描述期望生成的图像内容
            negative_prompt: 反向提示词，描述不希望出现的内容
            model: 模型名称，默认为wan2.2-t2i-flash
            size: 输出图像尺寸，默认为1024*1024
            n: 生成图片数量，默认为1

        Returns:
            图像生成结果，包含图像URL列表

        Raises:
            Exception: 当API调用失败时抛出异常
        """
        try:
            # 验证模型名称
            if model not in SUPPORTED_MODELS:
                raise ValueError(f"不支持的模型: {model}，支持的模型: {', '.join(SUPPORTED_MODELS)}")

            # 验证图像尺寸
            if size not in SUPPORTED_SIZES:
                raise ValueError(f"不支持的图像尺寸: {size}，支持的尺寸: {', '.join(SUPPORTED_SIZES)}")

            # 验证生成数量
            if not (1 <= n <= 4):
                raise ValueError(f"生成数量必须在1-4之间，当前值: {n}")

            # 根据官方文档，直接传递参数给DashScope SDK
            # 官方示例：ImageSynthesis.call(api_key=os.getenv("DASHSCOPE_API_KEY"), model="wan2.2-t2i-flash", prompt=prompt, n=1, size='1024*1024')
            call_params = {
                "api_key": self.api_key,
                "model": model,
                "prompt": prompt,
                "n": n,
                "size": size,
            }
            
            # 添加反向提示词（如果提供）
            if negative_prompt:
                call_params["negative_prompt"] = negative_prompt

            # 调用DashScope SDK进行同步调用
            response = dashscope.ImageSynthesis.call(**call_params)

            # 检查响应状态
            if response.status_code != 200:
                error_msg = f"API调用失败，状态码: {response.status_code}"
                if hasattr(response, 'message'):
                    error_msg += f"，错误信息: {response.message}"
                raise Exception(error_msg)

            # 解析响应结果
            result = {
                "status": "success",
                "model": model,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "size": size,
                "n": n,
                "output": {
                    "task_id": getattr(response.output, "task_id", ""),
                    "results": []
                }
            }

            # 提取图像URL - 根据DashScope SDK的实际响应结构
            if hasattr(response, 'output') and hasattr(response.output, 'results'):
                results = response.output.results
                if isinstance(results, list):
                    for item in results:
                        if hasattr(item, 'url'):
                            result["output"]["results"].append({
                                "url": item.url
                            })
                        elif isinstance(item, dict) and 'url' in item:
                            result["output"]["results"].append({
                                "url": item['url']
                            })
            
            # 如果没有找到results，检查是否有直接的URL字段
            elif hasattr(response, 'output') and hasattr(response.output, 'url'):
                result["output"]["results"].append({
                    "url": response.output.url
                })

            return result

        except Exception as e:
            # 返回错误信息
            return {
                "status": "error",
                "error": str(e),
                "model": model,
                "input": {
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                },
                "parameters": {
                    "size": size,
                    "n": n,
                }
            }

    async def run(self):
        """
        运行MCP服务器
        """
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="bailian-image",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(
                            tools_changed=True,
                            resources_changed=False,
                            prompts_changed=False
                        ),
                        experimental_capabilities={}
                    ),
                ),
            )


async def async_main():
    """
    异步主函数，启动MCP服务器
    """
    # 从环境变量或命令行参数获取API密钥
    api_key = os.getenv("DASHSCOPE_API_KEY")

    if not api_key and len(sys.argv) > 1:
        # 检查是否是帮助参数
        if sys.argv[1] in ["--help", "-h"]:
            print("阿里云百炼-通义万相图像生成MCP服务器")
            print("")
            print("使用方法:")
            print(
                "  方式1: export DASHSCOPE_API_KEY=your_api_key && mcp-server-bailian-image"
            )
            print("  方式2: mcp-server-bailian-image your_api_key")
            print("")
            print("支持的功能:")
            print("  - 文生图V2版（支持正向和反向提示词）")
            print("  - 多种模型选择（万相2.2、2.1、2.0系列）")
            print("  - 自定义图像尺寸和生成数量")
            print("  - 同步调用方式")
            print("")
            print("支持的模型:")
            for model in SUPPORTED_MODELS:
                print(f"  - {model}")
            print("")
            print(
                "官方文档: https://help.aliyun.com/zh/model-studio/text-to-image-v2-api-reference"
            )
            return
        else:
            api_key = sys.argv[1]

    if not api_key:
        print("错误: 请提供DASHSCOPE_API_KEY")
        print("使用方法:")
        print(
            "  方式1: export DASHSCOPE_API_KEY=your_api_key && mcp-server-bailian-image"
        )
        print("  方式2: mcp-server-bailian-image your_api_key")
        print("  方式3: mcp-server-bailian-image --help (查看帮助)")
        sys.exit(1)

    # 创建并运行服务器
    server = BailianImageServer(api_key)
    await server.run()


def main():
    """
    同步主函数，用于console_scripts入口点
    """
    asyncio.run(async_main())


if __name__ == "__main__":
    main()