"""MCP feet Master - A Model Context Protocol server for animal feet calculations."""

__version__ = "0.1.0"
__author__ = "ThomasYang"
__email__ = "tom19860526@gmail.com"

from .server import create_server

__all__ = ["create_server"]