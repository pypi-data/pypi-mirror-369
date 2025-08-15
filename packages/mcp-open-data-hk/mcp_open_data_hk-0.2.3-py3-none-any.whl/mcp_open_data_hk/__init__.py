"""MCP server for accessing data.gov.hk open data"""

from .server import mcp  # noqa: F401

__version__ = "0.2.3"
__author__ = "Tony Chan"
__email__ = "chankwongyintony@gmail.com"


def main():
    mcp.run()
