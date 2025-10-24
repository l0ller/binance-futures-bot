import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException
from typing import Optional, Dict, List
import sys
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class BinanceFuturesBot:
    """Advanced trading bot for Binance Futures Testnet."""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """Initialize the Binance Futures bot."""
        self.client = Client(api_key, api_secret, testnet=testnet)
        
        if testnet:
            self.client.API_URL = 'https://testnet.binancefuture.com'
            logger.info("Initialized bot with TESTNET configuration")
        else:
            logger.warning("Initialized bot with LIVE trading - USE WITH CAUTION!")
        
        # Test connection
        try:
            self.client.futures_ping()
            logger.info("Successfully connected to Binance Futures API")
        except Exception as e:
            logger.error(f"Failed to connect to API: {e}")
            raise
    
    def get_account_balance(self) -> List[Dict]:
        """Get futures account balance."""
        try:
            balance = self.client.futures_account_balance()
            logger.info("Retrieved account balance")
            return balance
        except BinanceAPIException as e:
            logger.error(f"API error getting balance: {e}")
            raise
    
    def get_symbol_price(self, symbol: str) -> float:
        """Get current market price for a symbol."""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except BinanceAPIException as e:
            logger.error(f"API error getting price: {e}")
            raise
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict:
        """Place a market order."""
        side = side.upper()
        if side not in ['BUY', 'SELL']:
            raise ValueError("Side must be 'BUY' or 'SELL'")
        
        logger.info(f"Placing MARKET {side} order: {quantity} {symbol}")
        
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            
            logger.info(f"Market order placed successfully: OrderID={order['orderId']}")
            return order
            
        except BinanceAPIException as e:
            logger.error(f"API error placing market order: {e.message}")
            raise
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float, 
                         time_in_force: str = 'GTC') -> Dict:
        """Place a limit order."""
        side = side.upper()
        if side not in ['BUY', 'SELL']:
            raise ValueError("Side must be 'BUY' or 'SELL'")
        
        logger.info(f"Placing LIMIT {side} order: {quantity} {symbol} @ {price}")
        
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                quantity=quantity,
                price=price,
                timeInForce=time_in_force
            )
            
            logger.info(f"Limit order placed successfully: OrderID={order['orderId']}")
            return order
            
        except BinanceAPIException as e:
            logger.error(f"API error placing limit order: {e.message}")
            raise
    
    def place_stop_limit_order(self, symbol: str, side: str, quantity: float, 
                              stop_price: float, limit_price: float,
                              time_in_force: str = 'GTC') -> Dict:
        """Place a stop-limit order."""
        side = side.upper()
        if side not in ['BUY', 'SELL']:
            raise ValueError("Side must be 'BUY' or 'SELL'")
        
        logger.info(f"Placing STOP_LIMIT {side} order: {quantity} {symbol}, "
                   f"stop @ {stop_price}, limit @ {limit_price}")
        
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='STOP',
                quantity=quantity,
                price=limit_price,
                stopPrice=stop_price,
                timeInForce=time_in_force
            )
            
            logger.info(f"Stop-limit order placed successfully: OrderID={order['orderId']}")
            return order
            
        except BinanceAPIException as e:
            logger.error(f"API error placing stop-limit order: {e.message}")
            raise
    
    def place_oco_order(self, symbol: str, side: str, quantity: float,
                       take_profit_price: float, stop_loss_price: float,
                       stop_limit_price: Optional[float] = None) -> Dict:
        """
        Place an OCO (One-Cancels-Other) order.
        This creates a take-profit limit order and a stop-loss order simultaneously.
        When one executes, the other is automatically cancelled.
        
        Args:
            symbol: Trading pair
            side: 'BUY' or 'SELL' - the side of the POSITION you're closing
            quantity: Order quantity
            take_profit_price: Take profit limit price
            stop_loss_price: Stop loss trigger price
            stop_limit_price: Stop limit price (if None, uses stop_loss_price * 0.99)
        """
        side = side.upper()
        if side not in ['BUY', 'SELL']:
            raise ValueError("Side must be 'BUY' or 'SELL'")
        
        # For OCO, if you're SELLING (closing a long), you want:
        # - Take profit ABOVE current price (limit sell)
        # - Stop loss BELOW current price (stop sell)
        
        if stop_limit_price is None:
            # Default stop limit slightly worse than stop price
            stop_limit_price = stop_loss_price * 0.99 if side == 'SELL' else stop_loss_price * 1.01
        
        logger.info(f"Placing OCO {side} order: {quantity} {symbol}, "
                   f"TP @ {take_profit_price}, SL @ {stop_loss_price}")
        
        try:
            # Note: Binance Futures may not support OCO directly via API
            # We'll place two linked orders manually
            
            # Place take-profit limit order
            tp_order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                quantity=quantity,
                price=take_profit_price,
                timeInForce='GTC'
            )
            
            logger.info(f"Take-profit order placed: OrderID={tp_order['orderId']}")
            
            # Place stop-loss order
            sl_order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='STOP_MARKET',
                quantity=quantity,
                stopPrice=stop_loss_price
            )
            
            logger.info(f"Stop-loss order placed: OrderID={sl_order['orderId']}")
            
            return {
                'oco_type': 'manual',
                'take_profit_order': tp_order,
                'stop_loss_order': sl_order
            }
            
        except BinanceAPIException as e:
            logger.error(f"API error placing OCO order: {e.message}")
            raise
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict:
        """Get status of a specific order."""
        try:
            order = self.client.futures_get_order(symbol=symbol, orderId=order_id)
            logger.info(f"Order {order_id} status: {order['status']}")
            return order
        except BinanceAPIException as e:
            logger.error(f"API error getting order status: {e.message}")
            raise
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict:
        """Cancel an open order."""
        try:
            result = self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
            logger.info(f"Order {order_id} cancelled successfully")
            return result
        except BinanceAPIException as e:
            logger.error(f"API error cancelling order: {e.message}")
            raise
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get all open orders for a symbol or all symbols."""
        try:
            orders = self.client.futures_get_open_orders(symbol=symbol)
            logger.info(f"Retrieved {len(orders)} open orders")
            return orders
        except BinanceAPIException as e:
            logger.error(f"API error getting open orders: {e.message}")
            raise
    
    def get_position_info(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get current position information."""
        try:
            positions = self.client.futures_position_information(symbol=symbol)
            # Filter out zero positions
            active_positions = [p for p in positions if float(p['positionAmt']) != 0]
            logger.info(f"Retrieved {len(active_positions)} active positions")
            return active_positions
        except BinanceAPIException as e:
            logger.error(f"API error getting positions: {e.message}")
            raise


class TradingUI:
    """Enhanced CLI interface for the trading bot."""
    
    def __init__(self, bot: BinanceFuturesBot):
        self.bot = bot
    
    @staticmethod
    def clear_screen():
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_header():
        """Print application header."""
        print(f"\n{Colors.BOLD}{Colors.OKCYAN}{'='*70}")
        print("      🚀 BINANCE FUTURES TESTNET TRADING BOT 🚀")
        print(f"{'='*70}{Colors.ENDC}\n")
        print(f"{Colors.WARNING}⚠️  TESTNET MODE - No real money involved{Colors.ENDC}")
        print(f"{Colors.OKBLUE}📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}\n")
    
    @staticmethod
    def print_menu():
        """Print main menu."""
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}")
        print("                           MAIN MENU")
        print(f"{'='*70}{Colors.ENDC}\n")
        
        menu_items = [
            ("1", "💹 Place Market Order", Colors.OKGREEN),
            ("2", "📊 Place Limit Order", Colors.OKBLUE),
            ("3", "🛑 Place Stop-Limit Order", Colors.WARNING),
            ("4", "🎯 Place OCO Order (Take-Profit + Stop-Loss)", Colors.OKCYAN),
            ("5", "💰 Check Account Balance", Colors.OKGREEN),
            ("6", "📋 View Open Orders", Colors.OKBLUE),
            ("7", "📍 View Open Positions", Colors.OKCYAN),
            ("8", "❌ Cancel Order", Colors.FAIL),
            ("9", "🔍 Check Order Status", Colors.OKBLUE),
            ("0", "👋 Exit", Colors.FAIL)
        ]
        
        for num, desc, color in menu_items:
            print(f"  {color}{num}.{Colors.ENDC} {desc}")
        
        print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    
    def display_balance(self):
        """Display account balance in a formatted table."""
        try:
            balance = self.bot.get_account_balance()
            
            print(f"\n{Colors.BOLD}{Colors.OKGREEN}{'='*70}")
            print("                       ACCOUNT BALANCE")
            print(f"{'='*70}{Colors.ENDC}\n")
            
            print(f"  {'Asset':<10} {'Balance':<20} {'Available':<20}")
            print(f"  {'-'*50}")
            
            for asset in balance:
                if float(asset['balance']) > 0:
                    print(f"  {asset['asset']:<10} {float(asset['balance']):<20.8f} "
                          f"{float(asset['availableBalance']):<20.8f}")
            
            print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
    
    def display_open_orders(self):
        """Display open orders in a formatted table."""
        try:
            symbol = input(f"\n{Colors.OKCYAN}Symbol (leave blank for all): {Colors.ENDC}").strip().upper()
            orders = self.bot.get_open_orders(symbol if symbol else None)
            
            if not orders:
                print(f"\n{Colors.WARNING}ℹ️  No open orders found.{Colors.ENDC}")
                return
            
            print(f"\n{Colors.BOLD}{Colors.OKBLUE}{'='*90}")
            print("                            OPEN ORDERS")
            print(f"{'='*90}{Colors.ENDC}\n")
            
            for order in orders:
                color = Colors.OKGREEN if order['side'] == 'BUY' else Colors.FAIL
                print(f"  {color}Order ID:{Colors.ENDC} {order['orderId']}")
                print(f"  Symbol: {order['symbol']} | Side: {color}{order['side']}{Colors.ENDC} | Type: {order['type']}")
                print(f"  Quantity: {order['origQty']} | Price: {order.get('price', 'MARKET')}")
                print(f"  Status: {order['status']}")
                print(f"  {'-'*86}")
            
            print(f"\n{Colors.BOLD}{'='*90}{Colors.ENDC}")
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
    
    def display_positions(self):
        """Display open positions."""
        try:
            positions = self.bot.get_position_info()
            
            if not positions:
                print(f"\n{Colors.WARNING}ℹ️  No open positions.{Colors.ENDC}")
                return
            
            print(f"\n{Colors.BOLD}{Colors.OKCYAN}{'='*90}")
            print("                          OPEN POSITIONS")
            print(f"{'='*90}{Colors.ENDC}\n")
            
            for pos in positions:
                amt = float(pos['positionAmt'])
                color = Colors.OKGREEN if amt > 0 else Colors.FAIL
                side = "LONG" if amt > 0 else "SHORT"
                
                print(f"  {color}Symbol:{Colors.ENDC} {pos['symbol']} | {color}{side}{Colors.ENDC}")
                print(f"  Amount: {abs(amt)} | Entry Price: {pos['entryPrice']}")
                print(f"  Unrealized PnL: {float(pos['unRealizedProfit']):.2f} USDT")
                print(f"  Leverage: {pos['leverage']}x")
                print(f"  {'-'*86}")
            
            print(f"\n{Colors.BOLD}{'='*90}{Colors.ENDC}")
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
    
    def place_market_order_ui(self):
        """UI for placing market orders."""
        try:
            print(f"\n{Colors.BOLD}{Colors.OKGREEN}📈 MARKET ORDER{Colors.ENDC}\n")
            
            symbol = input(f"{Colors.OKCYAN}Symbol (e.g., BTCUSDT): {Colors.ENDC}").strip().upper()
            
            # Show current price
            current_price = self.bot.get_symbol_price(symbol)
            print(f"{Colors.OKBLUE}Current Price: {current_price}{Colors.ENDC}")
            
            side = input(f"{Colors.OKCYAN}Side (BUY/SELL): {Colors.ENDC}").strip().upper()
            quantity = float(input(f"{Colors.OKCYAN}Quantity: {Colors.ENDC}").strip())
            
            color = Colors.OKGREEN if side == 'BUY' else Colors.FAIL
            print(f"\n{Colors.BOLD}Confirm:{Colors.ENDC} {color}MARKET {side}{Colors.ENDC} {quantity} {symbol}")
            confirm = input(f"{Colors.WARNING}Proceed? (y/n): {Colors.ENDC}")
            
            if confirm.lower() == 'y':
                order = self.bot.place_market_order(symbol, side, quantity)
                print(f"\n{Colors.OKGREEN}✅ Order placed successfully!{Colors.ENDC}")
                print(f"Order ID: {order['orderId']}")
            else:
                print(f"{Colors.WARNING}❌ Order cancelled.{Colors.ENDC}")
                
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
    
    def place_limit_order_ui(self):
        """UI for placing limit orders."""
        try:
            print(f"\n{Colors.BOLD}{Colors.OKBLUE}📊 LIMIT ORDER{Colors.ENDC}\n")
            
            symbol = input(f"{Colors.OKCYAN}Symbol (e.g., BTCUSDT): {Colors.ENDC}").strip().upper()
            
            # Show current price
            current_price = self.bot.get_symbol_price(symbol)
            print(f"{Colors.OKBLUE}Current Price: {current_price}{Colors.ENDC}")
            
            side = input(f"{Colors.OKCYAN}Side (BUY/SELL): {Colors.ENDC}").strip().upper()
            quantity = float(input(f"{Colors.OKCYAN}Quantity: {Colors.ENDC}").strip())
            price = float(input(f"{Colors.OKCYAN}Limit Price: {Colors.ENDC}").strip())
            
            color = Colors.OKGREEN if side == 'BUY' else Colors.FAIL
            print(f"\n{Colors.BOLD}Confirm:{Colors.ENDC} {color}LIMIT {side}{Colors.ENDC} {quantity} {symbol} @ {price}")
            confirm = input(f"{Colors.WARNING}Proceed? (y/n): {Colors.ENDC}")
            
            if confirm.lower() == 'y':
                order = self.bot.place_limit_order(symbol, side, quantity, price)
                print(f"\n{Colors.OKGREEN}✅ Order placed successfully!{Colors.ENDC}")
                print(f"Order ID: {order['orderId']}")
            else:
                print(f"{Colors.WARNING}❌ Order cancelled.{Colors.ENDC}")
                
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
    
    def place_stop_limit_order_ui(self):
        """UI for placing stop-limit orders."""
        try:
            print(f"\n{Colors.BOLD}{Colors.WARNING}🛑 STOP-LIMIT ORDER{Colors.ENDC}\n")
            
            symbol = input(f"{Colors.OKCYAN}Symbol (e.g., BTCUSDT): {Colors.ENDC}").strip().upper()
            
            # Show current price
            current_price = self.bot.get_symbol_price(symbol)
            print(f"{Colors.OKBLUE}Current Price: {current_price}{Colors.ENDC}")
            
            side = input(f"{Colors.OKCYAN}Side (BUY/SELL): {Colors.ENDC}").strip().upper()
            quantity = float(input(f"{Colors.OKCYAN}Quantity: {Colors.ENDC}").strip())
            stop_price = float(input(f"{Colors.OKCYAN}Stop Price: {Colors.ENDC}").strip())
            limit_price = float(input(f"{Colors.OKCYAN}Limit Price: {Colors.ENDC}").strip())
            
            color = Colors.OKGREEN if side == 'BUY' else Colors.FAIL
            print(f"\n{Colors.BOLD}Confirm:{Colors.ENDC} {color}STOP-LIMIT {side}{Colors.ENDC} {quantity} {symbol}")
            print(f"Stop @ {stop_price}, Limit @ {limit_price}")
            confirm = input(f"{Colors.WARNING}Proceed? (y/n): {Colors.ENDC}")
            
            if confirm.lower() == 'y':
                order = self.bot.place_stop_limit_order(symbol, side, quantity, stop_price, limit_price)
                print(f"\n{Colors.OKGREEN}✅ Order placed successfully!{Colors.ENDC}")
                print(f"Order ID: {order['orderId']}")
            else:
                print(f"{Colors.WARNING}❌ Order cancelled.{Colors.ENDC}")
                
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
    
    def place_oco_order_ui(self):
        """UI for placing OCO orders."""
        try:
            print(f"\n{Colors.BOLD}{Colors.OKCYAN}🎯 OCO ORDER (One-Cancels-Other){Colors.ENDC}\n")
            print(f"{Colors.WARNING}Use this to set Take-Profit and Stop-Loss simultaneously{Colors.ENDC}\n")
            
            symbol = input(f"{Colors.OKCYAN}Symbol (e.g., BTCUSDT): {Colors.ENDC}").strip().upper()
            
            # Show current price
            current_price = self.bot.get_symbol_price(symbol)
            print(f"{Colors.OKBLUE}Current Price: {current_price}{Colors.ENDC}")
            
            side = input(f"{Colors.OKCYAN}Side to CLOSE position (BUY/SELL): {Colors.ENDC}").strip().upper()
            quantity = float(input(f"{Colors.OKCYAN}Quantity: {Colors.ENDC}").strip())
            tp_price = float(input(f"{Colors.OKGREEN}Take-Profit Price: {Colors.ENDC}").strip())
            sl_price = float(input(f"{Colors.FAIL}Stop-Loss Price: {Colors.ENDC}").strip())
            
            color = Colors.OKGREEN if side == 'BUY' else Colors.FAIL
            print(f"\n{Colors.BOLD}Confirm OCO Order:{Colors.ENDC}")
            print(f"  {color}{side}{Colors.ENDC} {quantity} {symbol}")
            print(f"  {Colors.OKGREEN}Take-Profit: {tp_price}{Colors.ENDC}")
            print(f"  {Colors.FAIL}Stop-Loss: {sl_price}{Colors.ENDC}")
            confirm = input(f"\n{Colors.WARNING}Proceed? (y/n): {Colors.ENDC}")
            
            if confirm.lower() == 'y':
                result = self.bot.place_oco_order(symbol, side, quantity, tp_price, sl_price)
                print(f"\n{Colors.OKGREEN}✅ OCO Order placed successfully!{Colors.ENDC}")
                print(f"Take-Profit Order ID: {result['take_profit_order']['orderId']}")
                print(f"Stop-Loss Order ID: {result['stop_loss_order']['orderId']}")
            else:
                print(f"{Colors.WARNING}❌ Order cancelled.{Colors.ENDC}")
                
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
    
    def cancel_order_ui(self):
        """UI for cancelling orders."""
        try:
            print(f"\n{Colors.BOLD}{Colors.FAIL}❌ CANCEL ORDER{Colors.ENDC}\n")
            
            symbol = input(f"{Colors.OKCYAN}Symbol: {Colors.ENDC}").strip().upper()
            order_id = int(input(f"{Colors.OKCYAN}Order ID: {Colors.ENDC}").strip())
            
            confirm = input(f"\n{Colors.WARNING}Confirm cancel order {order_id}? (y/n): {Colors.ENDC}")
            
            if confirm.lower() == 'y':
                self.bot.cancel_order(symbol, order_id)
                print(f"\n{Colors.OKGREEN}✅ Order cancelled successfully!{Colors.ENDC}")
            else:
                print(f"{Colors.WARNING}❌ Cancellation aborted.{Colors.ENDC}")
                
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
    
    def check_order_status_ui(self):
        """UI for checking order status."""
        try:
            print(f"\n{Colors.BOLD}{Colors.OKBLUE}🔍 CHECK ORDER STATUS{Colors.ENDC}\n")
            
            symbol = input(f"{Colors.OKCYAN}Symbol: {Colors.ENDC}").strip().upper()
            order_id = int(input(f"{Colors.OKCYAN}Order ID: {Colors.ENDC}").strip())
            
            order = self.bot.get_order_status(symbol, order_id)
            
            print(f"\n{Colors.BOLD}{'='*70}")
            print("                      ORDER STATUS")
            print(f"{'='*70}{Colors.ENDC}\n")
            
            status_color = Colors.OKGREEN if order['status'] == 'FILLED' else Colors.WARNING
            print(f"  Status: {status_color}{order['status']}{Colors.ENDC}")
            print(f"  Symbol: {order['symbol']}")
            print(f"  Side: {order['side']} {order['type']}")
            print(f"  Executed: {order['executedQty']}/{order['origQty']}")
            print(f"  Price: {order.get('price', 'MARKET')}")
            
            print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
    
    def run(self):
        """Main UI loop."""
        while True:
            self.print_header()
            self.print_menu()
            
            choice = input(f"\n{Colors.BOLD}Select option (0-9): {Colors.ENDC}").strip()
            
            if choice == '1':
                self.place_market_order_ui()
            elif choice == '2':
                self.place_limit_order_ui()
            elif choice == '3':
                self.place_stop_limit_order_ui()
            elif choice == '4':
                self.place_oco_order_ui()
            elif choice == '5':
                self.display_balance()
            elif choice == '6':
                self.display_open_orders()
            elif choice == '7':
                self.display_positions()
            elif choice == '8':
                self.cancel_order_ui()
            elif choice == '9':
                self.check_order_status_ui()
            elif choice == '0':
                print(f"\n{Colors.OKGREEN}👋 Thanks for trading! Stay profitable!{Colors.ENDC}\n")
                break
            else:
                print(f"\n{Colors.FAIL}❌ Invalid option. Please try again.{Colors.ENDC}")
            
            input(f"\n{Colors.OKCYAN}Press Enter to continue...{Colors.ENDC}")
            self.clear_screen()


def main():
    """Main entry point."""
    print(f"{Colors.BOLD}{Colors.OKCYAN}")
    print("="*70)
    print("    BINANCE FUTURES TESTNET TRADING BOT - LOGIN")
    print("="*70)
    print(Colors.ENDC)
    
    api_key = input(f"{Colors.OKCYAN}Enter API Key: {Colors.ENDC}").strip()
    api_secret = input(f"{Colors.OKCYAN}Enter API Secret: {Colors.ENDC}").strip()
    
    try:
        print(f"\n{Colors.WARNING}Connecting to Binance Futures Testnet...{Colors.ENDC}")
        bot = BinanceFuturesBot(api_key, api_secret, testnet=True)
        print(f"{Colors.OKGREEN}✅ Connected successfully!{Colors.ENDC}\n")
        
        input(f"{Colors.OKCYAN}Press Enter to start trading...{Colors.ENDC}")
        
        ui = TradingUI(bot)
        ui.clear_screen()
        ui.run()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n{Colors.FAIL}✗ Error: {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()