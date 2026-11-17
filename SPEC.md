# SPEC: main.py — CBBTC/USDC mean-reversion bot

`main.py` (at repo root, Python 3.13, standard library only) implements a bars-replay bot for
`agent-fun/bars-replay/v1` using the vendored shim in `vendor/makefun_bars.py` (a byte-for-byte copy
of the kit SDK; do not edit it).

## Program skeleton

- File starts with imports: `import os, sys`, then
  `sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))`,
  then `import makefun_bars`.
- Define `on_batch(state, batch)` exactly as the shim's docstring describes (returns a list of order
  dicts, or `[]`).
- Register it with `makefun_bars.run(on_batch)` guarded by `if __name__ == "__main__":` is NOT
  required — just call `makefun_bars.run(on_batch)` at module top level (the harness imports nothing;
  it runs the file as a script).
- Deterministic: no wall clock, no environment reads, no unseeded randomness. Print diagnostics to
  stderr only; stdout must carry protocol replies only.

## The single asset

The universe has one symbol, `"CBBTC"`. All strategy state below applies to it.

## Strategy: rolling-SMA band mean reversion

Maintain a rolling window of the symbol's latest close prices (`state.close("CBBTC")`, an int in
raw price units — price scale 8, so ~64.4 USDC). Constants at module top:

- `SMA_N = 60` (window length, in bars)
- `DIP_BPS = 75` (buy band below the SMA)
- `EXIT_BPS = 60` (sell band above the SMA)
- `SLIPPAGE_BPS = 300` (generous max_slippage on every order; the modelled 2 bps plus impact on a
  ~$790k depth pool for a ~$1000 order is far below this)
- `BUY_FRACTION_NUM = 1`, `BUY_FRACTION_DEN = 1` (buy with all available cash)

Per batch (`on_batch`):

1. Append the latest close of CBBTC to the window. If fewer than `SMA_N` closes are collected yet,
   return `[]` (no orders).
2. Compute `sma = sum(window) // len(window)` with integer arithmetic.
3. If there is currently an open CBBTC position (check `state.positions`, a dict keyed by symbol;
   `state.positions.get("CBBTC")` is a `Holding` with `.qty`) and the latest close is
   `>= sma * (10000 + EXIT_BPS) // 10000`, return one sell order for the ENTIRE held quantity:
   `{"side": "sell", "symbol": "CBBTC", "qty": holding.qty, "max_slippage_bps": SLIPPAGE_BPS}`.
4. Else, if there is no CBBTC position and the latest close is
   `<= sma * (10000 - DIP_BPS) // 10000`, return one buy order:
   `{"side": "buy", "symbol": "CBBTC", "notional_quote_units": int(state.cash), "max_slippage_bps":
   SLIPPAGE_BPS}` — spend all cash (the position cap is 100% of equity; spending all cash cannot
   exceed it after the fee is taken from the notional, but to be safe spend at most
   `state.weight_room("CBBTC")` if that helper is smaller than cash; use
   `max(1_000_000, min(state.cash, room))` as the notional and only emit the order if the notional
   is >= 1_000_000 quote units, i.e. >= 1 USDC min notional).
5. Otherwise return `[]`.

At most one open position and at most 1 order per reply: the caps are respected by construction.

## Correctness requirements

- Must run deterministically under `python3 -P -s main.py` with `PYTHONHASHSEED=0`.
- Must never raise on any well-formed batch (guard against missing symbol data: if
  `state.close("CBBTC")` is `None`, return `[]`).
- Quantities: `qty` for sells is the raw Holding qty int; `notional_quote_units` for buys is an int.
- Keep the file compact and readable: module docstring, constants, `on_batch`, run call.
