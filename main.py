import os
import sys

# Setup vendor path for makefun_bars
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

# Strategy Constants
SMA_N = 60
DIP_BPS = 75
EXIT_BPS = 60
SLIPPAGE_BPS = 300
BUY_FRACTION_NUM = 1
BUY_FRACTION_DEN = 1

# Rolling window for CBBTC closes
cbbtc_window = []

def on_batch(state, batch):
    """
    Mean-reversion bot for CBBTC.
    
    1. Update window: append CBBTC close.
    2. Compute SMA: integer division.
    3. Sell: if position open and close >= sma * (10000 + EXIT_BPS) // 10000.
    4. Buy: if no position and close <= sma * (10000 - DIP_BPS) // 10000.
    """
    close = state.close("CBBTC")
    if close is None:
        return []
    
    cbbtc_window.append(close)
    if len(cbbtc_window) > SMA_N:
        cbbtc_window.pop(0)
    
    if len(cbbtc_window) < SMA_N:
        return []
    
    sma = sum(cbbtc_window) // len(cbbtc_window)
    
    holding = state.positions.get("CBBTC")
    
    # 3. Sell logic
    if holding and holding.qty > 0:
        if close >= sma * (10000 + EXIT_BPS) // 10000:
            return [{
                "side": "sell",
                "symbol": "CBBTC",
                "qty": holding.qty,
                "max_slippage_bps": SLIPPAGE_BPS
            }]
    # 4. Buy logic
    else:
        if close <= sma * (10000 - DIP_BPS) // 10000:
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

# Run the strategy
if __name__ == "__main__":
    makefun_bars.run(on_batch)
