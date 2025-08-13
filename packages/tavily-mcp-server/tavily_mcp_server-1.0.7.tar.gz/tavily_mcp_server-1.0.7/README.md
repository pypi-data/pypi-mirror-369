# Tavily MCP Server

🚀 **Tavily搜索MCP服务智能体** - 为AI智能体提供强大的网络搜索能力

## 📖 简介

Tavily MCP Server是一个基于FastAPI和FastMCP构建的智能搜索服务，集成了Tavily AI搜索引擎，为AI智能体提供高质量的网络搜索功能。支持综合搜索、答案生成和新闻搜索等多种搜索模式。

## ✨ 特性

- 🔍 **综合网络搜索** - 使用Tavily AI引擎进行全面的网络搜索
- 🤖 **智能答案生成** - 基于搜索结果生成直接答案
- 📰 **新闻搜索** - 专门的新闻内容搜索功能
- 🎯 **域名过滤** - 支持包含/排除特定域名
- 📅 **时间范围控制** - 可指定搜索的时间范围
- 🌍 **地区限制** - 支持按国家/地区进行搜索
- 📊 **多种输出格式** - 支持文本、JSON、Markdown格式输出
- 🔐 **API密钥验证** - 安全的API访问控制
- 📝 **完整日志记录** - 详细的操作日志

## 🚀 快速开始

### 安装

```bash
pip install tavily-mcp-server
```

### 环境配置

创建 `.env` 文件并配置必要的环境变量：

```env
# Tavily API密钥 (必需)
TAVILY_API_KEY=your_tavily_api_key_here

# MCP API密钥 (必需)
MCP_API_KEY=your_mcp_api_key_here
```

### 启动服务

```bash
# 使用命令行工具启动
tavily-mcp

# 或者直接运行Python模块
python -m tavily_mcp_server.server
```

服务将在 `http://localhost:8083` 启动。

## 📚 API文档

启动服务后，可以访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8083/docs
- **ReDoc**: http://localhost:8083/redoc

## 🔧 使用方法

### 1. 综合网络搜索

```python
import requests

response = requests.post(
    "http://localhost:8083/tavily_web_search",
    headers={"X-API-Key": "your_mcp_api_key"},
    json={
        "query": "人工智能最新发展",
        "max_results": 5,
        "search_depth": "advanced",
        "format_type": "markdown"
    }
)

result = response.json()
print(result["text"])
```

### 2. 智能答案搜索

```python
response = requests.post(
    "http://localhost:8083/tavily_answer_search",
    headers={"X-API-Key": "your_mcp_api_key"},
    json={
        "query": "什么是大语言模型？",
        "max_results": 3,
        "format_type": "text"
    }
)

result = response.json()
print(result["text"])
```

### 3. 新闻搜索

```python
response = requests.post(
    "http://localhost:8083/tavily_news_search",
    headers={"X-API-Key": "your_mcp_api_key"},
    json={
        "query": "科技新闻",
        "max_results": 10,
        "days": 7,
        "format_type": "json"
    }
)

result = response.json()
print(result["data"])
```

## 🛠️ 高级配置

### 域名过滤

```python
# 只搜索特定域名
response = requests.post(
    "http://localhost:8083/tavily_web_search",
    headers={"X-API-Key": "your_mcp_api_key"},
    json={
        "query": "Python教程",
        "include_domains": ["python.org", "docs.python.org"],
        "max_results": 5
    }
)

# 排除特定域名
response = requests.post(
    "http://localhost:8083/tavily_web_search",
    headers={"X-API-Key": "your_mcp_api_key"},
    json={
        "query": "编程学习",
        "exclude_domains": ["spam-site.com"],
        "max_results": 5
    }
)
```

### 地区和时间限制

```python
response = requests.post(
    "http://localhost:8083/tavily_web_search",
    headers={"X-API-Key": "your_mcp_api_key"},
    json={
        "query": "本地新闻",
        "country": "CN",
        "days": 30,
        "max_results": 10
    }
)
```

## 🔐 安全性

- 所有API端点都需要有效的API密钥验证
- 支持CORS配置，可根据需要调整
- 详细的错误处理和日志记录
- 输入参数验证和清理

## 🧪 开发

### 本地开发环境设置

```bash
# 克隆项目
git clone https://github.com/mcp-team/tavily-mcp-server.git
cd tavily-mcp-server

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black .

# 类型检查
mypy tavily_mcp_server
```

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

如有问题或建议，请通过以下方式联系：

- 提交 [GitHub Issue](https://github.com/mcp-team/tavily-mcp-server/issues)
- 发送邮件至 support@mcp.dev

## 🔗 相关链接

- [Tavily API文档](https://docs.tavily.com/)
- [FastMCP文档](https://github.com/jlowin/fastmcp)
- [FastAPI文档](https://fastapi.tiangolo.com/)

---

**让AI智能体拥有强大的搜索能力！** 🚀