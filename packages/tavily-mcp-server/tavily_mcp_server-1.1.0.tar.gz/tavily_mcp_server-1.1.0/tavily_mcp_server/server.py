import contextlib
import json
import logging
import os
import sys
from functools import lru_cache
from typing import Annotated, Dict, List, Literal, Optional, Union

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator
from tavily import InvalidAPIKeyError, TavilyClient, UsageLimitExceededError

VERSION = "1.0.0"

# API密钥验证
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 缓存客户端实例
@lru_cache()
def get_tavily_client():
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is required")
    return TavilyClient(api_key=api_key)

@contextlib.asynccontextmanager
async def server_lifespan(app):
    # 加载环境变量
    load_dotenv()
    
    # 验证必要的环境变量
    required_env_vars = ["TAVILY_API_KEY", "MCP_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please create a .env file with the required variables or set them in your environment.")
        logger.info("Example .env file:\n\nTAVILY_API_KEY=your_tavily_api_key\nMCP_API_KEY=your_mcp_api_key")
        sys.exit(1)
    
    logger.info("Environment variables loaded successfully")
    yield

# server_lifespan已经在上面定义为异步上下文管理器

# 初始化FastMCP
mcp = FastMCP(
    "tavily-search",
    lifespan=server_lifespan
)

# API密钥验证依赖
async def verify_api_key(api_key: str = Depends(API_KEY_HEADER)):
    if not api_key or api_key != os.getenv("MCP_API_KEY"):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return api_key

class SearchRequest(BaseModel):
    """Parameters for Tavily search."""
    query: Annotated[str, Field(description="Search query")]
    max_results: Annotated[int, Field(default=5, description="Maximum number of results to return", gt=0, lt=20)] = 5
    search_depth: Annotated[Literal["basic", "advanced"], Field(default="basic", description="Search depth - 'basic' or 'advanced'")] = "basic"
    include_domains: Annotated[list[str] | None, Field(default=None, description="List of domains to include in search results")] = None
    exclude_domains: Annotated[list[str] | None, Field(default=None, description="List of domains to exclude from search results")] = None

class SearchResponse(BaseModel):
    """标准化的搜索响应格式"""
    query: str
    answer: Optional[str] = None
    results: List[Dict[str, str]] = Field(default_factory=list)
    included_domains: List[str] = Field(default_factory=list)
    excluded_domains: List[str] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "query": "人工智能的最新发展",
                "answer": "人工智能领域最近取得了重大突破，包括大型语言模型和多模态AI系统的发展。",
                "results": [
                    {"title": "AI研究进展", "url": "https://example.com/ai-research", "content": "关于AI最新研究的详细内容..."},
                    {"title": "机器学习新方法", "url": "https://example.com/ml-methods", "content": "机器学习领域的创新方法..."}
                ],
                "included_domains": ["research.org", "science.edu"],
                "excluded_domains": ["spam.com"]
            }
        }

def format_results(response: dict, format_type: str = "text") -> dict:
    """格式化Tavily搜索结果
    
    Args:
        response: Tavily API响应
        format_type: 输出格式类型 (text, json, markdown)
        
    Returns:
        dict: 包含格式化文本和原始数据的字典
    """
    logger.debug(f"Formatting Tavily Search Results with format: {format_type}")
    
    # 创建标准化响应对象
    search_response = SearchResponse(
        query=response.get("query", ""),
        answer=response.get("answer"),
        results=response.get("results", []),
        included_domains=response.get("included_domains", []),
        excluded_domains=response.get("excluded_domains", [])
    )
    
    # 如果请求JSON格式，直接返回模型数据
    if format_type == "json":
        return {"text": "", "data": search_response.model_dump()}
    
    # 构建格式化输出
    output = []
    
    # 添加过滤器信息
    if search_response.included_domains or search_response.excluded_domains:
        filters = []
        if search_response.included_domains:
            filters.append(f"Including domains: {', '.join(search_response.included_domains)}")
        if search_response.excluded_domains:
            filters.append(f"Excluding domains: {', '.join(search_response.excluded_domains)}")
        output.append("Search Filters:")
        output.extend(filters)
        output.append("")

    # 添加答案和来源信息
    if search_response.answer:
        if format_type == "markdown":
            output.append(f"### Answer\n{search_response.answer}")
            output.append("\n### Sources")
        else:
            output.append(f"Answer: {search_response.answer}")
            output.append("\nSources:")
        
        # 添加来源列表
        output.extend([f"- {result['title']}: {result['url']}" for result in search_response.results])
        output.append("")

    # 添加详细结果标题
    output.append("### Detailed Results" if format_type == "markdown" else "Detailed Results:")
    
    # 添加每个结果的详细信息
    for result in search_response.results:
        output.append(f"\nTitle: {result['title']}")
        output.append(f"URL: {result['url']}")
        if result.get("published_date"):
            output.append(f"Published: {result['published_date']}")
        if result.get("content") and format_type == "markdown":
            output.append(f"\nContent Preview: {result['content'][:200]}..." if len(result.get('content', '')) > 200 else f"\nContent: {result['content']}")

    # 返回格式化文本和原始数据
    return {"text": "\n".join(output), "data": search_response.model_dump()}

class SearchResult(BaseModel):
    """搜索结果响应模型"""
    text: str
    data: dict

@mcp.tool(
    name="search",
    description="Execute web search using Tavily AI search engine"
)
async def tavily_web_search(
    query: Annotated[str, Field(description="The search query to execute")],
    max_results: Annotated[int, Field(default=5, description="Maximum number of search results to return (1-20)", ge=1, le=20)] = 5,
    search_depth: Annotated[Literal["basic", "advanced"], Field(default="basic", description="Search depth - 'basic' or 'advanced'")] = "basic",
    include_domains: Annotated[list[str] | None, Field(default=None, description="List of domains to include in search results")] = None,
    exclude_domains: Annotated[list[str] | None, Field(default=None, description="List of domains to exclude from search results")] = None,
    api_key: str = Depends(verify_api_key)
) -> SearchResult:
    """Execute web search using Tavily AI search engine"""
    logger.info(f"Tavily Search: {query}")
    
    try:
        args = SearchRequest(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            include_domains=include_domains,
            exclude_domains=exclude_domains
        )
        
        client = get_tavily_client()
        response = await client.search(
            query=args.query,
            max_results=args.max_results,
            search_depth=args.search_depth,
            include_domains=args.include_domains or [],
            exclude_domains=args.exclude_domains or []
        )
        
        if args.include_domains:
            response["included_domains"] = args.include_domains
        if args.exclude_domains:
            response["excluded_domains"] = args.exclude_domains
            
        response["query"] = query
        
        result = format_results(response, "text")
        return SearchResult(**result)
        
    except (InvalidAPIKeyError, UsageLimitExceededError) as e:
        logger.error(f"Tavily API error: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")



def main():
    """Run the MCP server"""
    mcp.run()

if __name__ == "__main__":
    print("Starting Tavily MCP Server...")
    print("Server is running. Press Ctrl+C to stop.")
    main()