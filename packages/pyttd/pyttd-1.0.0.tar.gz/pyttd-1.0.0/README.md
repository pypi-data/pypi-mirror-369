# PyTTD - Python OpenTTD Client Library

[![PyPI version](https://badge.fury.io/py/pyttd.svg)](https://badge.fury.io/py/pyttd)
[![Python versions](https://img.shields.io/pypi/pyversions/pyttd.svg)](https://pypi.org/project/pyttd/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python client library for connecting to [OpenTTD](https://www.openttd.org/) servers. Create AI bots, manage companies, and interact with OpenTTD games programmatically with **real-time data** and **without admin port**.

## Features

todo

## Installation

### From PyPI (Recommended)

```bash
pip install pyttd
```

### From Source

```bash
git clone https://github.com/mssc89/pyttd.git
cd pyttd
pip install -e .
```

## Quick Start

```python
from pyttd import OpenTTDClient

# Connect to OpenTTD server
client = OpenTTDClient("127.0.0.1", 3979, player_name="MyBot")
client.connect()

# Get real-time game information
game_info = client.get_game_info()
print(f"Game Year: {game_info['current_year']}")
print(f"Companies: {game_info['companies']}/{game_info['companies_max']}")
print(f"Clients: {game_info['clients']}/{game_info['clients_max']}")

# Company management
if client.get_our_company():
    finances = client.get_company_finances()
    print(f"Money: £{finances['money']:,}")
    print(f"Loan: £{finances['loan']:,}")
    
    # Take a loan and send a status message
    client.increase_loan(50000)
    client.send_chat("Bot taking loan for expansion!")

# Clean disconnect
client.disconnect()
```

## Real-Time Data Features

PyTTD provides real-time data that matches what other players see in the OpenTTD GUI:

```python
from pyttd import OpenTTDClient

client = OpenTTDClient()
client.connect()

# Real-time game state
game_info = client.get_game_info()
print(f"Current Game Year: {game_info['current_year']}")  # e.g., 1964
print(f"Game Started: {game_info['start_year']}")         # e.g., 1950
print(f"Companies Active: {game_info['companies']}")       # e.g., 8/15
print(f"Players Online: {game_info['clients']}")          # e.g., 12/25

# Company information
companies = client.get_companies()
for company_id, company in companies.items():
    print(f"Company {company_id}: {company['name']}")
    
# Financial analysis  
finances = client.get_company_finances()
performance = client.get_company_performance()
print(f"Net Worth: £{finances['net_worth']:,}")
print(f"Company Value: £{performance['company_value']:,}")
```

## Examples

### Data Monitor
```bash
python examples/data_display.py
```
Displays all available real-time game state information in a clean, organized format.

### Chat Bot
```bash
python examples/chat_bot.py  
```
Basic example showing connection, company creation, and chat interaction.

### Company Manager
```bash
python examples/manager_bot.py
```
Demonstrates company management features and financial tracking.

### Financial Manager
```bash
python examples/finance_bot.py
```
Interactive financial management with chat-based commands.

## API Reference

### OpenTTDClient

The main client class for connecting to OpenTTD servers.

```python
client = OpenTTDClient(
    server="127.0.0.1",        # Server IP address
    port=3979,                 # Server port  
    player_name="MyBot",       # Your bot's name
    company_name="MyCompany"   # Company name (auto-created)
)
```

#### Connection Methods
- `client.connect()` - Connect to server and join game
- `client.disconnect()` - Clean disconnect from server
- `client.is_connected()` - Check connection status

#### Game Information
- `client.get_game_info()` - Complete game state information
- `client.get_map_info()` - Map size and terrain data  
- `client.get_economic_status()` - Economic indicators

#### Company Management
- `client.get_companies()` - List all companies
- `client.get_our_company()` - Our company information
- `client.get_company_finances()` - Financial data
- `client.get_company_performance()` - Performance metrics

#### Financial Operations
- `client.increase_loan(amount)` - Increase company loan
- `client.decrease_loan(amount)` - Decrease company loan  
- `client.give_money(amount, company)` - Transfer money
- `client.can_afford(amount)` - Check affordability

#### Company Customization
- `client.rename_company(name)` - Change company name
- `client.rename_president(name)` - Change manager name
- `client.set_company_colour(scheme, primary, colour)` - Change colors

#### Communication
- `client.send_chat(message)` - Send public chat message
- `client.send_chat_to_company(message, company_id)` - Company chat
- `client.broadcast_status()` - Broadcast bot status

#### Vehicle Management
- `client.get_vehicles()` - List all vehicles
- `client.get_our_vehicles()` - Our company's vehicles
- `client.get_vehicle_statistics()` - Vehicle performance data

## Requirements

- **Python**: 3.11 or higher
- **OpenTTD Server**: Tested with 14.1

## Development

### Setting up Development Environment

```bash
git clone https://github.com/mssc89/pyttd.git
cd pyttd

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black pyttd/
flake8 pyttd/

# Type checking
mypy pyttd/
```

## Protocol Implementation

PyTTD implements OpenTTD's complete network protocol including:

- **CLIENT_JOIN** and **CLIENT_GAME_INFO** packets for connection
- **SERVER_GAME_INFO** parsing for real-time data synchronization  
- **CLIENT_COMMAND** for all game operations (construction, management, etc.)
- **SERVER_FRAME** handling for game synchronization
- **CLIENT_CHAT** and **SERVER_CHAT** for communication

The library automatically handles:
- Map downloading and decompression
- Game state synchronization  
- Command validation and encoding
- Network packet parsing and generation
- Connection management and error handling

## Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/mssc89/pyttd/issues)
- **Documentation**: [Full API documentation](https://github.com/mssc89/pyttd#readme)
- **Examples**: [Comprehensive examples](https://github.com/mssc89/pyttd/tree/main/examples)
