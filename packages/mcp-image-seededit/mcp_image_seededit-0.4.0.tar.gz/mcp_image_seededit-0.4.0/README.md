# MCP Image SeedEdit Server

[![PyPI version](https://badge.fury.io/py/mcp-image-seededit.svg)](https://badge.fury.io/py/mcp-image-seededit)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个基于火山引擎视觉能力的MCP服务器，提供图像指令编辑和人物写真生成功能。

## 功能特性

### 🎨 图像指令编辑 (SeedEdit 3.0)
- **智能编辑**：通过自然语言描述直接修改图像内容
- **多样化操作**：支持添加/删除物体、修改风格、颜色调整等
- **高质量输出**：基于火山引擎先进的图像生成技术
- **批量处理**：支持同时处理多张图像

### 📸 人物写真生成
- **人脸保持**：基于单人真人照片，保持面部特征高度相似
- **风格多样**：支持古风、欧美、日系、商务等多种写真风格
- **参数可控**：支持高清处理、美颜效果、匀肤等参数调节
- **场景丰富**：适用于社交、营销、娱乐等多种场景

## 安装

```bash
pip install mcp-image-seededit
```

## 快速开始

### 1. 获取API密钥

前往[火山引擎控制台](https://console.volcengine.com/)获取您的API密钥：
- `VOLC_ACCESS_KEY`：访问密钥
- `VOLC_SECRET_KEY`：秘密密钥

### 2. 配置MCP服务器

在您的MCP配置文件中添加：

```json
{
  "mcpServers": {
    "mcp-image-seededit": {
      "command": "python",
      "args": ["-m", "mcp_image_seededit"],
      "env": {
        "VOLC_ACCESS_KEY": "your_volc_access_key_here",
        "VOLC_SECRET_KEY": "your_volc_secret_key_here"
      }
    }
  }
}
```

### 3. 使用工具

#### 图像编辑示例

```json
{
  "tool": "image_edit",
  "arguments": {
    "image_urls": ["https://example.com/image.jpg"],
    "prompt": "添加一只可爱的小猫",
    "scale": 0.7
  }
}
```

#### 人物写真示例

```json
{
  "tool": "portrait_generation",
  "arguments": {
    "image_urls": ["https://example.com/portrait.jpg"],
    "prompt": "古风写真，汉服，梅花背景",
    "width": 1024,
    "height": 1024
  }
}
```

## 工具详解

### image_edit

图像指令编辑工具，支持通过文本描述修改图像内容。

**参数：**
- `image_urls` (list[str])：图像URL列表，支持本地路径或网络URL
- `prompt` (str)：编辑指令，建议长度 ≤ 120字符
- `seed` (int)：随机种子，默认-1（随机）
- `scale` (float)：文本描述影响程度，范围[0, 1]，默认0.5

**编辑指令示例：**
- 添加物体：`"添加一道彩虹"`
- 删除物体：`"删除背景中的建筑物"`
- 修改风格：`"改成油画风格"`
- 颜色调整：`"把衣服改成红色"`
- 背景替换：`"背景换成海滩"`

### portrait_generation

人物写真生成工具，基于真人照片生成多样化写真。

**参数：**
- `image_urls` (list[str])：单人真人图片URL列表
- `prompt` (str)：写真风格描述
- `width/height` (int)：生成图像尺寸，范围[512, 2048]
- `gpen` (float)：高清处理效果，范围[0, 1]，默认0.4
- `skin` (float)：美颜效果，范围[0, 1]，默认0.3
- `skin_unifi` (float)：匀肤效果，范围[0, 1]，默认0.0
- `gen_mode` (str)：生成模式，可选 "auto"、"creative"、"reference"、"reference_char"
- `seed` (int)：随机种子

**风格示例：**
- 古风写真：`"古典中国风，汉服，竹林背景"`
- 商务形象：`"专业商务照，西装，办公室背景"`
- 时尚大片：`"时尚杂志风格，都市背景"`

## 本地路径支持

服务器支持本地图片路径，会自动上传到临时服务器：

```json
{
  "image_urls": ["/path/to/local/image.jpg"]
}
```

支持格式：PNG, JPG, JPEG, WEBP, GIF, BMP, TIFF

## 开发

### 从源码安装

```bash
git clone https://github.com/yourusername/mcp-image-seededit
cd mcp-image-seededit
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black src/
isort src/
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

### v0.3.0
- 添加本地路径支持和自动上传功能
- 优化错误处理和日志输出
- 修复SOCKS代理兼容性问题
- 完善文档和使用示例

### v0.2.0
- 添加人物写真生成功能
- 改进图像处理流程
- 增强参数验证

### v0.1.0
- 初始版本
- 基础图像编辑功能