#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云百炼-通义万相图像生成MCP服务器测试用例

本模块包含对图像生成MCP服务器的冒烟测试，验证以下功能：
- 服务器初始化
- 工具注册和列表
- 文生图V2版功能
- 参数验证
- 错误处理
- DashScope SDK集成

作者: SOLO Coding
版本: 1.0.0
"""

import asyncio
import json
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

# 添加源代码路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_server_bailian_image.server import (
    BailianImageServer,
    SUPPORTED_MODELS,
    SUPPORTED_SIZES
)


class TestBailianImageServer(unittest.TestCase):
    """
    阿里云百炼-通义万相图像生成MCP服务器测试类
    
    测试服务器的基本功能，包括初始化、工具注册、API调用等。
    使用mock避免实际的API调用，确保测试可以在没有API密钥的情况下运行。
    """

    def setUp(self):
        """
        测试前的准备工作
        
        创建测试用的服务器实例，使用模拟的API密钥。
        """
        self.test_api_key = "test_api_key_12345"
        
        # 模拟DashScope模块，避免实际导入
        with patch('mcp_server_bailian_image.server.dashscope') as mock_dashscope:
            mock_dashscope.api_key = None
            self.server = BailianImageServer(self.test_api_key)
        
        # 模拟的API响应数据
        self.mock_success_response = MagicMock()
        self.mock_success_response.status_code = 200
        self.mock_success_response.output = MagicMock()
        self.mock_success_response.output.task_id = "test_task_12345"
        self.mock_success_response.output.results = [
            MagicMock(url="https://example.com/generated_image1.jpg"),
            MagicMock(url="https://example.com/generated_image2.jpg")
        ]
        
        self.mock_error_response = MagicMock()
        self.mock_error_response.status_code = 400
        self.mock_error_response.message = "Invalid parameters"

    def test_server_initialization(self):
        """
        测试服务器初始化
        
        验证服务器能够正确初始化，包括API密钥设置和基本属性。
        """
        self.assertEqual(self.server.api_key, self.test_api_key)
        self.assertIsNotNone(self.server.server)
        self.assertEqual(self.server.server.name, "bailian-image")

    def test_supported_models_and_sizes(self):
        """
        测试支持的模型和尺寸常量
        
        验证预定义的模型列表和尺寸列表是否正确。
        """
        # 验证支持的模型
        expected_models = [
            "wan2.2-t2i-flash",
            "wan2.2-t2i-plus",
            "wanx2.1-t2i-turbo",
            "wanx2.1-t2i-plus",
            "wanx2.0-t2i-turbo"
        ]
        self.assertEqual(SUPPORTED_MODELS, expected_models)
        
        # 验证支持的尺寸
        expected_sizes = [
            "512*512", "512*768", "512*1024", "768*512", "768*768", "768*1024",
            "1024*512", "1024*768", "1024*1024", "1024*1440", "1440*1024"
        ]
        self.assertEqual(SUPPORTED_SIZES, expected_sizes)

    @patch('mcp_server_bailian_image.server.dashscope.ImageSynthesis.call')
    async def test_text2imagev2_basic(self, mock_call):
        """
        测试基本的文生图功能
        
        验证能够正确调用文生图V2版API，包括基本参数处理。
        
        Args:
            mock_call: 模拟的DashScope ImageSynthesis.call方法
        """
        # 设置模拟返回值
        mock_call.return_value = self.mock_success_response
        
        # 测试参数
        prompt = "一只可爱的小猫，坐在花园里，阳光明媚"
        
        # 调用方法
        result = await self.server._text2imagev2(prompt=prompt)
        
        # 验证结果
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["model"], "wan2.2-t2i-flash")  # 默认模型
        self.assertEqual(result["input"]["prompt"], prompt)
        self.assertEqual(result["parameters"]["size"], "1024*1024")  # 默认尺寸
        self.assertEqual(result["parameters"]["n"], 1)  # 默认数量
        self.assertEqual(len(result["output"]["results"]), 2)  # 模拟返回2张图片
        
        # 验证API调用参数
        mock_call.assert_called_once_with(
            model="wan2.2-t2i-flash",
            prompt=prompt,
            negative_prompt=None,
            size="1024*1024",
            n=1
        )

    @patch('mcp_server_bailian_image.server.dashscope.ImageSynthesis.call')
    async def test_text2imagev2_with_negative_prompt(self, mock_call):
        """
        测试带反向提示词的文生图功能
        
        验证能够正确处理反向提示词参数。
        
        Args:
            mock_call: 模拟的DashScope ImageSynthesis.call方法
        """
        # 设置模拟返回值
        mock_call.return_value = self.mock_success_response
        
        # 测试参数
        prompt = "一幅美丽的风景画"
        negative_prompt = "低分辨率，模糊，错误，最差质量"
        
        # 调用方法
        result = await self.server._text2imagev2(
            prompt=prompt,
            negative_prompt=negative_prompt
        )
        
        # 验证结果
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["input"]["prompt"], prompt)
        self.assertEqual(result["input"]["negative_prompt"], negative_prompt)
        
        # 验证API调用参数
        mock_call.assert_called_once_with(
            model="wan2.2-t2i-flash",
            prompt=prompt,
            negative_prompt=negative_prompt,
            size="1024*1024",
            n=1
        )

    @patch('mcp_server_bailian_image.server.dashscope.ImageSynthesis.call')
    async def test_text2imagev2_custom_parameters(self, mock_call):
        """
        测试自定义参数的文生图功能
        
        验证能够正确处理自定义模型、尺寸和数量参数。
        
        Args:
            mock_call: 模拟的DashScope ImageSynthesis.call方法
        """
        # 设置模拟返回值
        mock_call.return_value = self.mock_success_response
        
        # 测试参数
        prompt = "科幻城市，未来感，高科技"
        model = "wan2.2-t2i-plus"
        size = "1440*1024"
        n = 3
        
        # 调用方法
        result = await self.server._text2imagev2(
            prompt=prompt,
            model=model,
            size=size,
            n=n
        )
        
        # 验证结果
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["model"], model)
        self.assertEqual(result["parameters"]["size"], size)
        self.assertEqual(result["parameters"]["n"], n)
        
        # 验证API调用参数
        mock_call.assert_called_once_with(
            model=model,
            prompt=prompt,
            negative_prompt=None,
            size=size,
            n=n
        )

    async def test_text2imagev2_invalid_model(self):
        """
        测试无效模型参数的处理
        
        验证当提供不支持的模型时，能够正确返回错误信息。
        """
        # 测试参数
        prompt = "测试图像"
        invalid_model = "invalid_model_name"
        
        # 调用方法
        result = await self.server._text2imagev2(
            prompt=prompt,
            model=invalid_model
        )
        
        # 验证错误结果
        self.assertEqual(result["status"], "error")
        self.assertIn("不支持的模型", result["error"])
        self.assertEqual(result["model"], invalid_model)

    async def test_text2imagev2_invalid_size(self):
        """
        测试无效尺寸参数的处理
        
        验证当提供不支持的图像尺寸时，能够正确返回错误信息。
        """
        # 测试参数
        prompt = "测试图像"
        invalid_size = "999*999"
        
        # 调用方法
        result = await self.server._text2imagev2(
            prompt=prompt,
            size=invalid_size
        )
        
        # 验证错误结果
        self.assertEqual(result["status"], "error")
        self.assertIn("不支持的图像尺寸", result["error"])

    async def test_text2imagev2_invalid_count(self):
        """
        测试无效数量参数的处理
        
        验证当提供超出范围的生成数量时，能够正确返回错误信息。
        """
        # 测试参数
        prompt = "测试图像"
        invalid_n = 10  # 超出1-4的范围
        
        # 调用方法
        result = await self.server._text2imagev2(
            prompt=prompt,
            n=invalid_n
        )
        
        # 验证错误结果
        self.assertEqual(result["status"], "error")
        self.assertIn("生成数量必须在1-4之间", result["error"])

    @patch('mcp_server_bailian_image.server.dashscope.ImageSynthesis.call')
    async def test_text2imagev2_api_error(self, mock_call):
        """
        测试API调用错误的处理
        
        验证当DashScope API返回错误时，能够正确处理并返回错误信息。
        
        Args:
            mock_call: 模拟的DashScope ImageSynthesis.call方法
        """
        # 设置模拟错误返回值
        mock_call.return_value = self.mock_error_response
        
        # 测试参数
        prompt = "测试图像"
        
        # 调用方法
        result = await self.server._text2imagev2(prompt=prompt)
        
        # 验证错误结果
        self.assertEqual(result["status"], "error")
        self.assertIn("API调用失败", result["error"])
        self.assertIn("400", result["error"])  # 状态码

    def test_parameter_validation_edge_cases(self):
        """
        测试参数验证的边界情况
        
        验证各种边界参数值的处理。
        """
        # 测试最小和最大生成数量
        async def test_min_max_count():
            # 最小值：1（有效值，应该成功）
            with patch('mcp_server_bailian_image.server.dashscope.ImageSynthesis.call') as mock_call:
                mock_call.return_value = self.mock_success_response
                result_min = await self.server._text2imagev2(prompt="test", n=1)
                self.assertEqual(result_min["status"], "success")
            
            # 最大值：4（有效值，应该成功）
            with patch('mcp_server_bailian_image.server.dashscope.ImageSynthesis.call') as mock_call:
                mock_call.return_value = self.mock_success_response
                result_max = await self.server._text2imagev2(prompt="test", n=4)
                self.assertEqual(result_max["status"], "success")
            
            # 超出范围：0（无效值，应该失败）
            result_zero = await self.server._text2imagev2(prompt="test", n=0)
            self.assertEqual(result_zero["status"], "error")
            
            # 超出范围：5（无效值，应该失败）
            result_five = await self.server._text2imagev2(prompt="test", n=5)
            self.assertEqual(result_five["status"], "error")
        
        asyncio.run(test_min_max_count())

    def test_all_supported_models(self):
        """
        测试所有支持的模型
        
        验证所有预定义的模型都能正确处理。
        """
        async def test_models():
            with patch('mcp_server_bailian_image.server.dashscope.ImageSynthesis.call') as mock_call:
                mock_call.return_value = self.mock_success_response
                
                for model in SUPPORTED_MODELS:
                    result = await self.server._text2imagev2(
                        prompt="测试",
                        model=model
                    )
                    self.assertEqual(result["status"], "success")
                    self.assertEqual(result["model"], model)
        
        asyncio.run(test_models())

    def test_all_supported_sizes(self):
        """
        测试所有支持的尺寸
        
        验证所有预定义的图像尺寸都能正确处理。
        """
        async def test_sizes():
            with patch('mcp_server_bailian_image.server.dashscope.ImageSynthesis.call') as mock_call:
                mock_call.return_value = self.mock_success_response
                
                for size in SUPPORTED_SIZES:
                    result = await self.server._text2imagev2(
                        prompt="测试",
                        size=size
                    )
                    self.assertEqual(result["status"], "success")
                    self.assertEqual(result["parameters"]["size"], size)
        
        asyncio.run(test_sizes())


class TestAsyncMethods(unittest.IsolatedAsyncioTestCase):
    """
    异步方法测试类
    
    使用IsolatedAsyncioTestCase来测试异步方法，确保异步调用的正确性。
    """

    async def asyncSetUp(self):
        """
        异步测试前的准备工作
        """
        self.test_api_key = "test_api_key_12345"
        
        # 模拟DashScope模块
        with patch('mcp_server_bailian_image.server.dashscope') as mock_dashscope:
            mock_dashscope.api_key = None
            self.server = BailianImageServer(self.test_api_key)
        
        # 模拟成功响应
        self.mock_response = MagicMock()
        self.mock_response.status_code = 200
        self.mock_response.output = MagicMock()
        self.mock_response.output.task_id = "async_test_12345"
        self.mock_response.output.results = [
            MagicMock(url="https://example.com/async_image.jpg")
        ]

    @patch('mcp_server_bailian_image.server.dashscope.ImageSynthesis.call')
    async def test_async_text2imagev2_call(self, mock_call):
        """
        测试异步调用文生图功能
        
        验证异步方法调用的正确性。
        
        Args:
            mock_call: 模拟的DashScope ImageSynthesis.call方法
        """
        # 设置模拟返回值
        mock_call.return_value = self.mock_response
        
        # 测试参数
        prompt = "异步测试图像生成"
        
        # 异步调用方法
        result = await self.server._text2imagev2(prompt=prompt)
        
        # 验证结果
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["input"]["prompt"], prompt)
        self.assertIn("results", result["output"])
        
        # 验证API被调用
        mock_call.assert_called_once()

    @patch('mcp_server_bailian_image.server.dashscope.ImageSynthesis.call')
    async def test_concurrent_calls(self, mock_call):
        """
        测试并发调用
        
        验证多个异步调用能够正确并发执行。
        
        Args:
            mock_call: 模拟的DashScope ImageSynthesis.call方法
        """
        # 设置模拟返回值
        mock_call.return_value = self.mock_response
        
        # 创建多个并发任务
        tasks = []
        for i in range(3):
            task = self.server._text2imagev2(prompt=f"并发测试图像{i}")
            tasks.append(task)
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks)
        
        # 验证所有结果
        self.assertEqual(len(results), 3)
        for i, result in enumerate(results):
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["input"]["prompt"], f"并发测试图像{i}")
        
        # 验证API被调用了3次
        self.assertEqual(mock_call.call_count, 3)


def run_tests():
    """
    运行所有测试用例
    
    执行完整的测试套件，包括同步和异步测试。
    """
    print("开始运行阿里云百炼-通义万相图像生成MCP服务器测试...")
    print("=" * 60)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestBailianImageServer))
    suite.addTests(loader.loadTestsFromTestCase(TestAsyncMethods))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 60)
    if result.wasSuccessful():
        print("✅ 所有测试通过！图像生成MCP服务器功能正常。")
    else:
        print(f"❌ 测试失败：{len(result.failures)} 个失败，{len(result.errors)} 个错误")
        for failure in result.failures:
            print(f"失败: {failure[0]}")
            print(f"详情: {failure[1]}")
        for error in result.errors:
            print(f"错误: {error[0]}")
            print(f"详情: {error[1]}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # 运行测试
    success = run_tests()
    sys.exit(0 if success else 1)