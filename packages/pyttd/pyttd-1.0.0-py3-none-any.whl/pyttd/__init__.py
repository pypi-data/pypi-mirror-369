"""
PyTTD - Python OpenTTD Client Library
=====================================

A modern Python client library for connecting to and playing on OpenTTD servers.
Create AI bots, manage companies, and interact with OpenTTD games programmatically
with real-time data.

Usage:
    from pyttd import OpenTTDClient

    client = OpenTTDClient("127.0.0.1", 3979)
    client.connect()

    # Get real-time game data
    game_info = client.get_game_info()
    print(f"Game year: {game_info['current_year']}")
    print(f"Companies: {game_info['companies']}")
"""

from .client import OpenTTDClient
from .protocol import Packet, PacketType
from .game_state import GameState, CompanyInfo, ClientInfo, VehicleInfo, MapInfo
from .commands import Commands, CommandBuilder, CommandPacket, CompanyID

__version__ = "1.0.0"
__author__ = "mssc89"
__description__ = "Python OpenTTD Client Library"
__url__ = "https://github.com/mssc89/pyttd"

__all__ = [
    "OpenTTDClient",
    "Packet",
    "PacketType",
    "GameState",
    "CompanyInfo",
    "ClientInfo",
    "VehicleInfo",
    "MapInfo",
    "Commands",
    "CommandBuilder",
    "CommandPacket",
    "CompanyID",
]
