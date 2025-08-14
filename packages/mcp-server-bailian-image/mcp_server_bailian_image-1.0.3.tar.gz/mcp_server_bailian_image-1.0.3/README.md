# MCP Server Bailian Image

阿里云百炼-通义万相图像生成MCP服务器

## 功能特性

- 🎨 **文生图功能**: 基于通义万相2.1/2.2文生图V2版API
- 🚀 **多模型支持**: 支持wan2.2-t2i-flash、wan2.2-t2i-plus等多种模型
- 🎯 **精确控制**: 支持正向提示词、反向提示词、图像尺寸、生成数量等参数
- ⚡ **同步调用**: 使用DashScope SDK进行同步调用，简化使用流程
- 🔧 **易于集成**: 标准MCP协议，可与支持MCP的AI助手无缝集成

## 安装

### 从PyPI安装

```bash
pip install mcp-server-bailian-image
```

### 从源码安装

```bash
git clone https://github.com/aliyun/mcp-server-bailian-image.git
cd mcp-server-bailian-image
pip install -e .
```

## 配置

### 1. 获取API Key

1. 访问[阿里云百炼控制台](https://bailian.console.aliyun.com/)
2. 创建应用并获取API Key
3. 确保已开通通义万相文生图服务

### 2. 设置环境变量

```bash
# Windows
set DASHSCOPE_API_KEY=your_api_key_here

# Linux/macOS
export DASHSCOPE_API_KEY=your_api_key_here
```

## 使用方法

### 启动MCP服务器

```bash
# 使用uvx启动（推荐）
uvx mcp-server-bailian-image

# 或者直接传入API Key
uvx mcp-server-bailian-image --api-key your_api_key_here
```

### 在Claude Desktop中配置

在Claude Desktop的配置文件中添加以下配置：

```json
{
  "mcpServers": {
    "bailian-image": {
      "command": "uvx",
      "args": ["mcp-server-bailian-image"],
      "env": {
        "DASHSCOPE_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## 支持的工具

### text2imagev2

基于通义万相文生图V2版API的文生图工具。

**参数说明：**

- `prompt` (必填): 正向提示词，描述期望生成的图像内容
- `negative_prompt` (可选): 反向提示词，描述不希望出现的内容
- `model` (可选): 模型名称，默认为 `wan2.2-t2i-flash`
- `size` (可选): 图像尺寸，默认为 `1024*1024`
- `n` (可选): 生成图片数量，取值范围1-4，默认为1

**支持的模型：**

- `wan2.2-t2i-flash`: 万相2.2极速版（推荐）
- `wan2.2-t2i-plus`: 万相2.2专业版（推荐）
- `wanx2.1-t2i-turbo`: 万相2.1极速版
- `wanx2.1-t2i-plus`: 万相2.1专业版
- `wanx2.0-t2i-turbo`: 万相2.0极速版

**支持的图像尺寸：**

- `1024*1024` (默认)
- `720*1280`
- `1280*720`
- `1024*576`
- `576*1024`

**使用示例：**

```python
# 基础文生图
result = await call_tool("text2imagev2", {
    "prompt": "一只坐着的橘黄色的猫，表情愉悦，活泼可爱，逼真准确"
})

# 使用反向提示词
result = await call_tool("text2imagev2", {
    "prompt": "雪地，白色小教堂，极光，冬日场景，柔和的光线",
    "negative_prompt": "人物",
    "model": "wan2.2-t2i-plus",
    "size": "1280*720",
    "n": 2
})
```

## 错误处理

常见错误及解决方案：

1. **API Key未设置**
   ```
   错误: DASHSCOPE_API_KEY environment variable is required
   解决: 设置环境变量或通过命令行参数传入API Key
   ```

2. **模型不支持**
   ```
   错误: Unsupported model: xxx
   解决: 使用支持的模型名称
   ```

3. **图像尺寸不支持**
   ```
   错误: Unsupported size: xxx
   解决: 使用支持的图像尺寸
   ```

## 开发

### 环境要求

- Python 3.8+
- DashScope SDK
- MCP SDK

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/aliyun/mcp-server-bailian-image.git
cd mcp-server-bailian-image

# 安装依赖
pip install -e .

# 运行测试
python -m pytest

# 启动开发服务器
python -m mcp_server_bailian_image.server
```

## 许可证

MIT License

## 相关链接

- [通义万相文生图V2版API文档](https://help.aliyun.com/zh/model-studio/text-to-image-v2-api-reference)
- [阿里云百炼控制台](https://bailian.console.aliyun.com/)
- [DashScope SDK文档](https://help.aliyun.com/zh/dashscope/)
- [MCP协议文档](https://github.com/modelcontextprotocol/specification)

## 支持

如有问题或建议，请提交[Issue](https://github.com/aliyun/mcp-server-bailian-image/issues)。