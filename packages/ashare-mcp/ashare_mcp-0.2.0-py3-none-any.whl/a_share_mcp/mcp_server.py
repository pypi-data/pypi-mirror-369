# Main MCP server file
import logging
from datetime import datetime

from mcp.server.fastmcp import FastMCP

# Import the interface and the concrete implementation
from .data_source_interface import FinancialDataSource
from .baostock_data_source import BaostockDataSource
from .utils import setup_logging

# 导入各模块工具的注册函数
from .tools.stock_market import register_stock_market_tools
from .tools.financial_reports import register_financial_report_tools
from .tools.indices import register_index_tools
from .tools.market_overview import register_market_overview_tools
from .tools.macroeconomic import register_macroeconomic_tools
from .tools.date_utils import register_date_utils_tools
from .tools.analysis import register_analysis_tools

# --- Logging Setup ---
# Call the setup function from utils
# You can control the default level here (e.g., logging.DEBUG for more verbose logs)
setup_logging(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Dependency Injection ---
# Instantiate the data source - easy to swap later if needed
active_data_source: FinancialDataSource = BaostockDataSource()

# --- Get current date for system prompt ---
current_date = datetime.now().strftime("%Y-%m-%d")

# --- FastMCP App Initialization ---
app = FastMCP(
    "a_share_data_provider",
    f"""今天是{current_date}。提供中国A股市场数据分析工具。此服务提供客观数据分析，用户需自行做出投资决策。数据分析基于公开市场信息，不构成投资建议，仅供参考。

⚠️ 重要说明:
1. 最新交易日不一定是今天，需要从 get_latest_trading_date() 获取
2. 请始终使用 get_latest_trading_date() 工具获取实际当前最近的交易日，不要依赖训练数据中的日期认知
3. 当分析"最近"或"近期"市场情况时，必须首先调用 get_market_analysis_timeframe() 工具确定实际的分析时间范围
4. 任何涉及日期的分析必须基于工具返回的实际数据，不得使用过时或假设的日期
""",
    # Specify dependencies for installation if needed (e.g., when using `mcp install`)
    # dependencies=["baostock", "pandas"]
)

# --- 注册各模块的工具 ---
register_stock_market_tools(app, active_data_source)
register_financial_report_tools(app, active_data_source)
register_index_tools(app, active_data_source)
register_market_overview_tools(app, active_data_source)
register_macroeconomic_tools(app, active_data_source)
register_date_utils_tools(app, active_data_source)
register_analysis_tools(app, active_data_source)

def main():
    """Main entry point for the MCP server."""
    logger.info(
        f"Starting A-Share MCP Server via stdio... Today is {current_date}")
    # Run the server using stdio transport, suitable for MCP Hosts like Claude Desktop
    app.run(transport='stdio')

# --- Main Execution Block ---
if __name__ == "__main__":
    main()
