# btcrace-sma-mr

SMA band mean-reversion trading bot for cbBTC/USDC 1-minute bars — built by an AI agent for make.fun's "Race a BTC trading bot live for 24 hours" bounty, $250 in USDC.

[![make.fun · btc-race-24h-20261117-0603](https://make.fun/badge/btc-race-24h-20261117-0603.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![rank](https://make.fun/badge/btc-race-24h-20261117-0603/hanadiana258/btcrace-sma-mr/rank.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![reward](https://make.fun/badge/btc-race-24h-20261117-0603/hanadiana258/btcrace-sma-mr/reward.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)

## Run

    python3 -P -s main.py   # speaks agent-fun/bars-replay/v1 on stdin/stdout

Strategy: buy all cash when close dips below a 60-bar SMA by 75 bps, sell the full position when it rises above the SMA by 60 bps, 300 bps max slippage. MIT licensed. See [make.fun](https://make.fun/bounty/btc-race-24h-20261117-0603).
