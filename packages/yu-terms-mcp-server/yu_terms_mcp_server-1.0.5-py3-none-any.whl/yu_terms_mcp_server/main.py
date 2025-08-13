
import logging

import sys

# 引入FastMCP相关模块
from mcp.server.fastmcp import FastMCP
from pydantic import Field

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(__name__)


class TermsUpdatedTool:
    """Tool for handling terms updates."""

    def __init__(self) -> None:
        """Initialize the TermsUpdatedTool."""
        logger.info("TermsUpdatedTool initialized")

    async def terms_updated(self, query: str) -> str:
        """
        更新条款要素接口
        
        Args:
            query (str): 查询参数
            
        Returns:
            str: 更新结果
        """
        try:
            logger.info(f"Processing terms update with query: {query}")
            result = await self._terms(query)
            return result
        except Exception as e:
            error_msg = f"Error updating terms: {str(e)}"
            logger.error(error_msg)
            return error_msg

    async def _terms(self, query: str) -> str:
        """
        Internal method for processing terms updates.
        
        Args:
            query (str): The query parameter for terms processing
            
        Returns:
            str: Success message indicating the operation completed
        """
        # 等效于Java代码中的 System.out.println("你好");
        print("你好")
        logger.info("Terms processing completed successfully")
        
        # 等效于Java代码中的 return "更新成功！";
        return "更新成功！"


# 初始化FastMCP实例
mcp = FastMCP('yu-terms-mcp-server')


# 使用装饰器定义工具
@mcp.tool(name='terms_updated', description='更新条款要素接口')
async def terms_updated(
    query: str = Field(description='查询参数')
) -> str:
    """更新条款要素接口
    Args:
        query: 查询参数
    Returns:
        更新结果
    """
    terms_tool = TermsUpdatedTool()
    return await terms_tool.terms_updated(query)


def run_server() -> None:
    """
    运行MCP服务器主逻辑
    """
    logger.info("Initializing  Terms MCP Server...")
    
    try:
        # 使用FastMCP运行服务器
        logger.info(" Terms MCP Server 运行成功...")
        mcp.run(transport='stdio')

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}", exc_info=True)
        raise


def main() -> None:
    """
    命令行入口点
    """
    try:
        # 直接运行服务器
        run_server()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()