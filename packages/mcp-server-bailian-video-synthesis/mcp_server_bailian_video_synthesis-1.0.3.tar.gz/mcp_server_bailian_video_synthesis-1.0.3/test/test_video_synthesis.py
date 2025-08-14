#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云百炼-通义万相视频合成MCP服务器测试用例

本模块包含对视频合成MCP服务器的冒烟测试，验证以下功能：
- 服务器初始化
- 工具注册和列表
- 各种视频合成任务创建
- 任务结果查询
- 参数验证
- 错误处理

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

from mcp_server_bailian_video_synthesis.server import BailianVideoSynthesisServer


class TestBailianVideoSynthesisServer(unittest.TestCase):
    """
    阿里云百炼-通义万相视频合成MCP服务器测试类
    
    测试服务器的基本功能，包括初始化、工具注册、API调用等。
    使用mock避免实际的API调用，确保测试可以在没有API密钥的情况下运行。
    """

    def setUp(self):
        """
        测试前的准备工作
        
        创建测试用的服务器实例，使用模拟的API密钥。
        """
        self.test_api_key = "test_api_key_12345"
        self.server = BailianVideoSynthesisServer(self.test_api_key)
        
        # 模拟的API响应数据
        self.mock_task_response = {
            "output": {
                "task_id": "test_task_12345",
                "task_status": "PENDING"
            },
            "request_id": "test_request_12345"
        }
        
        self.mock_result_response = {
            "output": {
                "task_id": "test_task_12345",
                "task_status": "SUCCEEDED",
                "results": [
                    {
                        "url": "https://example.com/generated_video.mp4"
                    }
                ]
            },
            "request_id": "test_request_12345"
        }

    def test_server_initialization(self):
        """
        测试服务器初始化
        
        验证服务器能够正确初始化，包括API密钥设置和基本属性。
        """
        self.assertEqual(self.server.api_key, self.test_api_key)
        self.assertIsNotNone(self.server.server)
        self.assertIsNotNone(self.server.client)
        self.assertEqual(self.server.server.name, "bailian-video-synthesis")

    @patch('mcp_server_bailian_video_synthesis.server.BailianVideoSynthesisServer._make_request')
    async def test_create_task_image_reference(self, mock_request):
        """
        测试多图参考视频生成任务创建
        
        验证能够正确创建多图参考视频生成任务，包括参数处理和API调用。
        
        Args:
            mock_request: 模拟的API请求方法
        """
        # 设置模拟返回值
        mock_request.return_value = self.mock_task_response
        
        # 测试参数
        prompt = "一个美丽的花园场景，阳光明媚"
        ref_images_url = [
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg"
        ]
        obj_or_bg = ["obj", "bg"]
        size = "1280*720"
        
        # 调用方法
        result = await self.server._create_task_image_reference(
            prompt=prompt,
            ref_images_url=ref_images_url,
            obj_or_bg=obj_or_bg,
            size=size
        )
        
        # 验证结果
        self.assertEqual(result, self.mock_task_response)
        
        # 验证API调用参数
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "/api/v1/services/aigc/video-generation/video-synthesis")
        
        payload = call_args[0][1]
        self.assertEqual(payload["model"], "wanx2.1-vace-plus")
        self.assertEqual(payload["input"]["function"], "image_reference")
        self.assertEqual(payload["input"]["prompt"], prompt)
        self.assertEqual(payload["input"]["ref_images_url"], ref_images_url)
        self.assertEqual(payload["parameters"]["obj_or_bg"], obj_or_bg)
        self.assertEqual(payload["parameters"]["size"], size)

    @patch('mcp_server_bailian_video_synthesis.server.BailianVideoSynthesisServer._make_request')
    async def test_create_task_video_repainting(self, mock_request):
        """
        测试视频重绘任务创建
        
        验证能够正确创建视频重绘任务，包括参数处理和API调用。
        
        Args:
            mock_request: 模拟的API请求方法
        """
        # 设置模拟返回值
        mock_request.return_value = self.mock_task_response
        
        # 测试参数
        prompt = "将视频转换为卡通风格"
        video_url = "https://example.com/input_video.mp4"
        control_condition = "depth"
        strength = 0.8
        
        # 调用方法
        result = await self.server._create_task_video_repainting(
            prompt=prompt,
            video_url=video_url,
            control_condition=control_condition,
            strength=strength
        )
        
        # 验证结果
        self.assertEqual(result, self.mock_task_response)
        
        # 验证API调用参数
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        payload = call_args[0][1]
        self.assertEqual(payload["input"]["function"], "video_repainting")
        self.assertEqual(payload["input"]["prompt"], prompt)
        self.assertEqual(payload["input"]["video_url"], video_url)
        self.assertEqual(payload["parameters"]["control_condition"], control_condition)
        self.assertEqual(payload["parameters"]["strength"], strength)

    @patch('mcp_server_bailian_video_synthesis.server.BailianVideoSynthesisServer._make_request')
    async def test_create_task_video_edit(self, mock_request):
        """
        测试视频局部编辑任务创建
        
        验证能够正确创建视频局部编辑任务，包括参数处理和API调用。
        
        Args:
            mock_request: 模拟的API请求方法
        """
        # 设置模拟返回值
        mock_request.return_value = self.mock_task_response
        
        # 测试参数
        prompt = "将选中区域替换为蓝天白云"
        video_url = "https://example.com/input_video.mp4"
        mask_url = "https://example.com/mask.png"
        
        # 调用方法
        result = await self.server._create_task_video_edit(
            prompt=prompt,
            video_url=video_url,
            mask_url=mask_url
        )
        
        # 验证结果
        self.assertEqual(result, self.mock_task_response)
        
        # 验证API调用参数
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        payload = call_args[0][1]
        self.assertEqual(payload["input"]["function"], "video_edit")
        self.assertEqual(payload["input"]["prompt"], prompt)
        self.assertEqual(payload["input"]["video_url"], video_url)
        self.assertEqual(payload["input"]["mask_url"], mask_url)

    @patch('mcp_server_bailian_video_synthesis.server.BailianVideoSynthesisServer._make_request')
    async def test_create_task_video_extension(self, mock_request):
        """
        测试视频延展任务创建
        
        验证能够正确创建视频延展任务，包括参数处理和API调用。
        
        Args:
            mock_request: 模拟的API请求方法
        """
        # 设置模拟返回值
        mock_request.return_value = self.mock_task_response
        
        # 测试参数
        prompt = "延续视频中的动作和场景"
        video_url = "https://example.com/input_video.mp4"
        duration = 8.0
        
        # 调用方法
        result = await self.server._create_task_video_extension(
            prompt=prompt,
            video_url=video_url,
            duration=duration
        )
        
        # 验证结果
        self.assertEqual(result, self.mock_task_response)
        
        # 验证API调用参数
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        payload = call_args[0][1]
        self.assertEqual(payload["input"]["function"], "video_extension")
        self.assertEqual(payload["input"]["prompt"], prompt)
        self.assertEqual(payload["input"]["video_url"], video_url)
        self.assertEqual(payload["parameters"]["duration"], duration)

    @patch('mcp_server_bailian_video_synthesis.server.BailianVideoSynthesisServer._make_request')
    async def test_create_task_video_expansion(self, mock_request):
        """
        测试视频画面扩展任务创建
        
        验证能够正确创建视频画面扩展任务，包括参数处理和API调用。
        
        Args:
            mock_request: 模拟的API请求方法
        """
        # 设置模拟返回值
        mock_request.return_value = self.mock_task_response
        
        # 测试参数
        prompt = "向右扩展画面，显示更多的风景"
        video_url = "https://example.com/input_video.mp4"
        expand_direction = "right"
        
        # 调用方法
        result = await self.server._create_task_video_expansion(
            prompt=prompt,
            video_url=video_url,
            expand_direction=expand_direction
        )
        
        # 验证结果
        self.assertEqual(result, self.mock_task_response)
        
        # 验证API调用参数
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        payload = call_args[0][1]
        self.assertEqual(payload["input"]["function"], "video_expansion")
        self.assertEqual(payload["input"]["prompt"], prompt)
        self.assertEqual(payload["input"]["video_url"], video_url)
        self.assertEqual(payload["parameters"]["expand_direction"], expand_direction)

    @patch('mcp_server_bailian_video_synthesis.server.BailianVideoSynthesisServer._make_request')
    async def test_get_task_result(self, mock_request):
        """
        测试任务结果查询
        
        验证能够正确查询任务执行结果。
        
        Args:
            mock_request: 模拟的API请求方法
        """
        # 设置模拟返回值
        mock_request.return_value = self.mock_result_response
        
        # 测试参数
        task_id = "test_task_12345"
        
        # 调用方法
        result = await self.server._get_task_result(task_id=task_id)
        
        # 验证结果
        self.assertEqual(result, self.mock_result_response)
        
        # 验证API调用参数
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], f"/api/v1/tasks/{task_id}")
        self.assertEqual(call_args[1]["method"], "GET")

    @patch('httpx.AsyncClient.post')
    async def test_make_request_post(self, mock_post):
        """
        测试POST请求方法
        
        验证_make_request方法能够正确发送POST请求。
        
        Args:
            mock_post: 模拟的HTTP POST方法
        """
        # 设置模拟响应
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_task_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # 测试参数
        endpoint = "/api/v1/test"
        payload = {"test": "data"}
        
        # 调用方法
        result = await self.server._make_request(endpoint, payload)
        
        # 验证结果
        self.assertEqual(result, self.mock_task_response)
        
        # 验证HTTP调用
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertTrue(call_args[1]["url"].endswith(endpoint))
        self.assertEqual(call_args[1]["json"], payload)
        self.assertIn("Authorization", call_args[1]["headers"])
        self.assertIn("Bearer", call_args[1]["headers"]["Authorization"])

    @patch('httpx.AsyncClient.get')
    async def test_make_request_get(self, mock_get):
        """
        测试GET请求方法
        
        验证_make_request方法能够正确发送GET请求。
        
        Args:
            mock_get: 模拟的HTTP GET方法
        """
        # 设置模拟响应
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_result_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # 测试参数
        endpoint = "/api/v1/tasks/test_task_12345"
        
        # 调用方法
        result = await self.server._make_request(endpoint, method="GET")
        
        # 验证结果
        self.assertEqual(result, self.mock_result_response)
        
        # 验证HTTP调用
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertTrue(call_args[1]["url"].endswith(endpoint))
        self.assertIn("Authorization", call_args[1]["headers"])

    def test_default_parameters(self):
        """
        测试默认参数处理
        
        验证各种方法的默认参数是否正确设置。
        """
        # 测试多图参考的默认obj_or_bg参数
        with patch.object(self.server, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = self.mock_task_response
            
            async def test_default_obj_or_bg():
                await self.server._create_task_image_reference(
                    prompt="test",
                    ref_images_url=["url1", "url2"]
                )
                
                call_args = mock_request.call_args
                payload = call_args[0][1]
                # 默认应该是 ["obj", "bg"]
                self.assertEqual(payload["parameters"]["obj_or_bg"], ["obj", "bg"])
            
            asyncio.run(test_default_obj_or_bg())


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
        self.server = BailianVideoSynthesisServer(self.test_api_key)

    async def test_all_create_methods_async(self):
        """
        测试所有创建任务方法的异步调用
        
        验证所有创建任务的方法都能正确进行异步调用。
        """
        with patch.object(self.server, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"task_id": "test_12345"}
            
            # 测试所有创建任务的方法
            methods_and_args = [
                ("_create_task_image_reference", {
                    "prompt": "test",
                    "ref_images_url": ["url1"]
                }),
                ("_create_task_video_repainting", {
                    "prompt": "test",
                    "video_url": "video_url"
                }),
                ("_create_task_video_edit", {
                    "prompt": "test",
                    "video_url": "video_url",
                    "mask_url": "mask_url"
                }),
                ("_create_task_video_extension", {
                    "prompt": "test",
                    "video_url": "video_url"
                }),
                ("_create_task_video_expansion", {
                    "prompt": "test",
                    "video_url": "video_url"
                }),
                ("_get_task_result", {
                    "task_id": "test_12345"
                })
            ]
            
            for method_name, args in methods_and_args:
                method = getattr(self.server, method_name)
                result = await method(**args)
                self.assertIsNotNone(result)
                self.assertIn("task_id", str(result))


def run_tests():
    """
    运行所有测试用例
    
    执行完整的测试套件，包括同步和异步测试。
    """
    print("开始运行阿里云百炼-通义万相视频合成MCP服务器测试...")
    print("=" * 60)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestBailianVideoSynthesisServer))
    suite.addTests(loader.loadTestsFromTestCase(TestAsyncMethods))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 60)
    if result.wasSuccessful():
        print("✅ 所有测试通过！视频合成MCP服务器功能正常。")
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