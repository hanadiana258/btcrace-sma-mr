import os
import sys

# Setup path for vendor library
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

# Constants
SMA_N = 60
DIP_BPS = 75
EXIT_BPS = 60
SLIPPAGE_BPS = 300
BUY_FRACTION_NUM = 1
BUY_FRACTION_DEN = 1

# State
rolling_window = []

def on_batch(state, batch):
    """
    Mean-reversion strategy on CBBTC:
    - Maintain rolling SMA window.
    - Sell if price >= SMA + EXIT_BPS.
    - Buy if price <= SMA - DIP_BPS.
    """
    if state.warming_up:
        return []

    close_price = state.close("CBBTC")
    if close_price is None or close_price <= 0:
        return []

    global rolling_window
    rolling_window.append(close_price)
    if len(rolling_window) > SMA_N:
        rolling_window.pop(0)

    if len(rolling_window) < SMA_N:
        return []

    sma = sum(rolling_window) // len(rolling_window)
    
    # Check position
    position = state.positions.get("CBBTC")
    
    # Try to sell
    if position and position.qty > 0:
        threshold_sell = sma * (10000 + EXIT_BPS) // 10000
        if close_price >= threshold_sell:
            return [{
                "side": "sell",
                "symbol": "CBBTC",
                "qty": position.qty,
                "max_slippage_bps": SLIPPAGE_BPS
            }]
    
    # Try to buy
    elif position is None or position.qty == 0:
        threshold_buy = sma * (10000 - DIP_BPS) // 10000
        if close_price <= threshold_buy:
            room = state.weight_room("CBBTC")
            notional = max(1_000_000, min(state.cash, room))
            
            if notional >= 1_000_000:
                return [{
                    "side": "buy",
                    "symbol": "CBBTC",
                    "notional_quote_units": int(notional),
                    "max_slippage_bps": SLIPPAGE_BPS
                }]
                
    return []

# Run the harness
makefun_bars.run(on_batch)
