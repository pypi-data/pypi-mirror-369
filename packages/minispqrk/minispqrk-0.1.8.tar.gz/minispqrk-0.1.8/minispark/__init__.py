"""
MiniSpark - 一个轻量级的Python数据处理库
"""

__version__ = "0.1.8"

from .minispark import MiniSpark
from .connectors.csv_connector import CSVConnector
from .connectors.excel_connector import ExcelConnector
from .connectors.json_connector import JSONConnector
from .connectors.mysql_connector import MySQLConnector
from .connectors.sqlite_connector import SQLiteConnector
from .connectors.duckdb_connector import DuckDBConnector

__all__ = [
    "MiniSpark",
    "CSVConnector",
    "ExcelConnector",
    "JSONConnector",
    "MySQLConnector",
    "SQLiteConnector",
    "DuckDBConnector"
]