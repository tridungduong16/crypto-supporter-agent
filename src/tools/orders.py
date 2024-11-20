from binance.client import Client
from binance.enums import *

class BinanceOrderHandler:
    def __init__(self, api_key, api_secret):
        """Initializes the Binance client with API credentials."""
        self.client = Client(api_key, api_secret)

    def place_market_order(self, symbol, side, quantity):
        """Place a market order (buy or sell)."""
        try:
            # Side can be 'BUY' or 'SELL'
            order = self.client.order_market(
                symbol=symbol,  # e.g., 'BTCUSDT'
                side=side,  # 'BUY' or 'SELL'
                quantity=quantity  # Amount of the asset to buy/sell
            )
            return order
        except Exception as e:
            return f"Error placing market order: {e}"

    def place_limit_order(self, symbol, side, quantity, price):
        """Place a limit order (buy or sell)."""
        try:
            # Side can be 'BUY' or 'SELL'
            order = self.client.order_limit(
                symbol=symbol,  # e.g., 'BTCUSDT'
                side=side,  # 'BUY' or 'SELL'
                quantity=quantity,  # Amount of the asset to buy/sell
                price=price,  # Limit price (in USDT for example)
                timeInForce=TIME_IN_FORCE_GTC  # GTC means the order will stay open until filled or canceled
            )
            return order
        except Exception as e:
            return f"Error placing limit order: {e}"

    def cancel_order(self, symbol, order_id):
        """Cancel an existing order."""
        try:
            # Cancel the order using the order_id returned when placing an order
            canceled_order = self.client.cancel_order(symbol=symbol, orderId=order_id)
            return canceled_order
        except Exception as e:
            return f"Error canceling order: {e}"

    def get_open_orders(self, symbol):
        """Fetch all open orders for a symbol."""
        try:
            open_orders = self.client.get_open_orders(symbol=symbol)
            return open_orders
        except Exception as e:
            return f"Error fetching open orders: {e}"

    def get_all_orders(self, symbol, limit=10):
        """Fetch the history of all orders for a symbol."""
        try:
            all_orders = self.client.get_all_orders(symbol=symbol, limit=limit)
            return all_orders
        except Exception as e:
            return f"Error fetching all orders: {e}"

    def get_order_status(self, symbol, order_id):
        """Fetch the status of a specific order by order ID."""
        try:
            order_status = self.client.get_order(symbol=symbol, orderId=order_id)
            return order_status
        except Exception as e:
            return f"Error fetching order status: {e}"

    def place_oco_order(self, symbol, side, quantity, price, stop_price):
        """Place an OCO (One Cancels Other) order."""
        try:
            # OCO orders include a stop-limit order and a limit order
            oco_order = self.client.order_oco(
                symbol=symbol,  # e.g., 'BTCUSDT'
                side=side,  # 'BUY' or 'SELL'
                quantity=quantity,
                price=price,  # Limit price
                stopPrice=stop_price,  # Stop price for stop-limit
                stopLimitPrice=stop_price * 0.99,  # Example for stop-limit price (90% of stop price)
                timeInForce=TIME_IN_FORCE_GTC
            )
            return oco_order
        except Exception as e:
            return f"Error placing OCO order: {e}"

    def get_account_info(self):
        """Fetch account information (balances, etc.)."""
        try:
            account_info = self.client.get_account()
            return account_info
        except Exception as e:
            return f"Error fetching account info: {e}"

    def get_recent_trades(self, symbol, limit=5):
        """Fetch the most recent trades for a symbol."""
        try:
            recent_trades = self.client.get_recent_trades(symbol=symbol, limit=limit)
            return recent_trades
        except Exception as e:
            return f"Error fetching recent trades: {e}"

# Example usage
if __name__ == "__main__":
    # Replace with your actual Binance API key and secret
    binance_api_key = "your_binance_api_key_here"
    binance_api_secret = "your_binance_api_secret_here"

    # Initialize BinanceOrderHandler with API credentials
    order_handler = BinanceOrderHandler(binance_api_key, binance_api_secret)

    # 1. Place a market buy order
    symbol = "BTCUSDT"
    side = "BUY"  # Buy order
    quantity = 0.001  # Amount of BTC to buy
    market_order = order_handler.place_market_order(symbol, side, quantity)
    print(f"Market Order Response: {market_order}")

    # 2. Place a limit sell order
    side = "SELL"  # Sell order
    limit_price = 60000  # Sell price for BTC
    limit_order = order_handler.place_limit_order(symbol, side, quantity, limit_price)
    print(f"Limit Order Response: {limit_order}")

    # 3. Cancel a previously placed order (replace with actual order_id)
    order_id = 'order_id_here'  # Replace with the actual order ID
    cancel_response = order_handler.cancel_order(symbol, order_id)
    print(f"Cancel Order Response: {cancel_response}")

    # 4. Fetch open orders for the symbol
    open_orders = order_handler.get_open_orders(symbol)
    print(f"Open Orders: {open_orders}")

    # 5. Fetch all orders for the symbol
    all_orders = order_handler.get_all_orders(symbol, limit=5)
    print(f"All Orders: {all_orders}")

    # 6. Fetch order status using order_id
    order_status = order_handler.get_order_status(symbol, order_id)
    print(f"Order Status: {order_status}")

    # 7. Place an OCO (One Cancels Other) order
    stop_price = 59000
    oco_order = order_handler.place_oco_order(symbol, side, quantity, limit_price, stop_price)
    print(f"OCO Order Response: {oco_order}")

    # 8. Get account info (balances, etc.)
    account_info = order_handler.get_account_info()
    print(f"Account Info: {account_info}")

    # 9. Get recent trades for the symbol
    recent_trades = order_handler.get_recent_trades(symbol, limit=5)
    print(f"Recent Trades: {recent_trades}")
