# EC2 IB Touch-and-Turn Scalper

A Python-based trading bot scaffold for AWS EC2 that connects to Interactive Brokers, implements the opening-range touch-and-turn scalping strategy, and augments entry decisions with NYSE Arca level 2 market depth.

## Project structure

- `src/trading_bot/` — core bot modules
- `README.md` — project overview and run notes
- `requirements.txt` — Python dependency list
- `.github/copilot-instructions.md` — workspace-specific Copilot guidance

## Getting started

1. Create a Python virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Configure environment variables for IB and strategy settings.
3. Run the bot in paper trading mode:
   ```powershell
   python -m trading_bot.main
   ```

## AWS EC2 deployment notes

- Deploy the bot on an EC2 instance.
- Install and run IB Gateway/TWS on the same host.
- Use AWS Secrets Manager for IB credentials.
- Use CloudWatch Logs for structured logging.

## Next steps

- Implement AWS EC2 bootstrap scripts.
- Add integration tests for IB connection and level 2 confirm logic.
- Extend the strategy with live instrument state and order book signals.
