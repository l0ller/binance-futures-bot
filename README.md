# 🚀 Binance Futures Trading Bot

A professional-grade trading bot for Binance Futures Testnet with advanced order management and risk controls.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Binance](https://img.shields.io/badge/Binance-Testnet-yellow)](https://testnet.binancefuture.com)

## 📋 Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Order Types](#order-types)
- [Project Structure](#project-structure)
- [Logging](#logging)
- [Screenshots](#screenshots)
- [Troubleshooting](#troubleshooting)
- [Disclaimer](#disclaimer)

## ✨ Features

### Core Functionality
- ✅ **Market Orders** - Instant execution at current market price
- ✅ **Limit Orders** - Execute at specific price levels
- ✅ **Stop-Limit Orders** - Advanced conditional orders
- ✅ **OCO Orders** - One-Cancels-Other (Take-Profit + Stop-Loss simultaneously)
- ✅ **Position Tracking** - Real-time PnL monitoring
- ✅ **Order Management** - View, cancel, and track order status

### Technical Features
- 🎨 **Enhanced CLI Interface** - Color-coded, intuitive menu system
- 📊 **Live Price Display** - Real-time market data before order placement
- 💰 **Account Balance** - View available funds and positions
- 📝 **Comprehensive Logging** - All API calls, responses, and errors logged
- ⚠️ **Error Handling** - Robust exception handling for all operations
- 🔒 **Input Validation** - User input sanitization and confirmation prompts

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Binance Futures Testnet account
- API credentials from Binance Testnet

### Step 1: Clone the Repository
```bash
git clone https://github.com/l0ller/binance-futures-bot.git
cd binance-futures-bot
```

### Step 2: Install Dependencies
```bash
pip install python-binance
```

### Step 3: Get Testnet API Credentials
1. Visit [Binance Futures Testnet](https://testnet.binancefuture.com)
2. Register/Login
3. Generate API Key and Secret
4. (Optional) Get free test USDT from the testnet faucet

## ⚙️ Configuration

The bot automatically connects to Binance Futures Testnet using:
- **Base URL**: `https://testnet.binancefuture.com`
- **Testnet Mode**: Enabled by default (no real funds at risk)

No configuration file needed - just enter your API credentials when prompted!

## 🚀 Usage

### Starting the Bot
```bash
python trading_bot.py
```

### Login
When prompted, enter:
- **API Key**: Your Binance Testnet API Key
- **API Secret**: Your Binance Testnet API Secret

### Main Menu Options

```
1. 💹 Place Market Order          - Instant execution
2. 📊 Place Limit Order           - Set your price
3. 🛑 Place Stop-Limit Order      - Conditional orders
4. 🎯 Place OCO Order             - TP + SL combined
5. 💰 Check Account Balance       - View funds
6. 📋 View Open Orders            - Active orders
7. 📍 View Open Positions         - Current positions
8. ❌ Cancel Order                - Cancel pending order
9. 🔍 Check Order Status          - Track order execution
0. 👋 Exit                        - Close application
```

## 📊 Order Types

### 1. Market Order
Execute immediately at current market price.
```
Symbol: BTCUSDT
Side: BUY/SELL
Quantity: 0.01
```

### 2. Limit Order
Execute only at specified price or better.
```
Symbol: BTCUSDT
Side: BUY/SELL
Quantity: 0.01
Price: 67000
```

### 3. Stop-Limit Order
Triggers when stop price is reached, executes as limit order.
```
Symbol: BTCUSDT
Side: BUY/SELL
Quantity: 0.01
Stop Price: 66000
Limit Price: 65900
```

### 4. OCO Order (One-Cancels-Other)
Set take-profit and stop-loss simultaneously. When one executes, the other cancels.
```
Symbol: BTCUSDT
Side: SELL (to close long position)
Quantity: 0.01
Take-Profit: 70000
Stop-Loss: 65000
```

## 📁 Project Structure

```
binance-futures-bot/
│
├── trading_bot.py           # Main bot implementation
├── trading_bot.log          # Execution logs
├── README.md                # This file
├── requirements.txt         # Python dependencies
└── LICENSE                  # MIT License
```

### Code Architecture

```python
# Core Classes
BinanceFuturesBot          # Trading logic and API interactions
├── place_market_order()
├── place_limit_order()
├── place_stop_limit_order()
├── place_oco_order()
├── get_account_balance()
├── get_position_info()
└── cancel_order()

TradingUI                  # User interface and interaction
├── print_header()
├── print_menu()
├── display_balance()
├── display_positions()
└── run()                  # Main UI loop
```

## 📝 Logging

All operations are logged to both console and `trading_bot.log`:

```
2025-10-24 16:23:21 - INFO - Initialized bot with TESTNET configuration
2025-10-24 16:23:22 - INFO - Successfully connected to Binance Futures API
2025-10-24 16:24:15 - INFO - Placing MARKET BUY order: 0.01 BTCUSDT
2025-10-24 16:24:16 - INFO - Market order placed successfully: OrderID=12345678
```

Log levels:
- `INFO` - Successful operations
- `WARNING` - Non-critical issues
- `ERROR` - API errors and exceptions

## 🎨 Screenshots

### Main Menu
```
======================================================================
      🚀 BINANCE FUTURES TESTNET TRADING BOT 🚀
======================================================================

⚠️  TESTNET MODE - No real money involved
📅 2025-10-24 16:23:21

======================================================================
                           MAIN MENU
======================================================================

  1. 💹 Place Market Order
  2. 📊 Place Limit Order
  3. 🛑 Place Stop-Limit Order
  4. 🎯 Place OCO Order (Take-Profit + Stop-Loss)
  ...
```

### Order Execution
```
✅ Order placed successfully!
Order ID: 87654321
```

## 🔧 Troubleshooting

### Common Issues

**"Invalid symbol" error**
- Use full trading pair: `BTCUSDT` not `BTC`
- Common pairs: BTCUSDT, ETHUSDT, BNBUSDT

**"Insufficient balance" error**
- Check balance with option 5
- Get test funds from Binance testnet faucet

**API Connection Failed**
- Verify API credentials are correct
- Check if testnet account is active
- Ensure internet connection is stable

**"API key not found" error**
- Regenerate API keys on testnet
- Ensure you're using testnet credentials, not mainnet

## 🧪 Testing

Tested on:
- ✅ Python 3.8, 3.9, 3.10, 3.11
- ✅ Windows, macOS, Linux
- ✅ All order types verified on testnet
- ✅ Error handling validated with invalid inputs

## 🎯 Use Cases

1. **Learning Trading** - Practice without financial risk
2. **Strategy Testing** - Test trading strategies safely
3. **API Integration** - Learn Binance API structure
4. **Risk Management** - Practice with OCO orders
5. **Portfolio Management** - Track positions and PnL

## 🔐 Security Notes

- ⚠️ Never commit API keys to GitHub
- 🔒 Use environment variables for production
- 🧪 Always test on testnet first
- 📝 Review all orders before confirming

## 📚 Resources

- [Binance Futures Testnet](https://testnet.binancefuture.com)
- [Binance API Documentation](https://binance-docs.github.io/apidocs/futures/en/)
- [python-binance Library](https://python-binance.readthedocs.io/)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push and create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**This bot is for TESTNET use only.**

- ✅ Safe for learning and testing
- ✅ No real money involved
- ⚠️ Not financial advice
- ⚠️ Use at your own risk for live trading

Trading cryptocurrencies carries risk. Never trade with money you can't afford to lose.

---

## 👨‍💻 Author

Developed as part of a trading bot development assignment.

For questions or support, please open an issue on GitHub.

---

**⭐ If you find this project helpful, please consider giving it a star!**
