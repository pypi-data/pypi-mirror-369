from tradingapi.shoonya import Shoonya, save_symbol_data as save_symbol_data_sh
from tradingapi.fivepaisa import FivePaisa, save_symbol_data as save_symbol_data_fp
from tradingapi.utils import get_pnl_table, calculate_mtm, calc_pnl, get_exit_candidates, place_combo_order
from tradingapi import configure_logging
from tradingapi.error_handling import set_execution_time_logging, set_retry_enabled
import logging
import datetime as dt
import sys

# Configure logging first, before any other operations
# Clear existing handlers and configure with file logging
# Don't configure root logger to avoid duplicate logs
configure_logging(
    level=logging.INFO,
    log_file="/home/psharma/testing.log",
    clear_existing_handlers=True,
    enable_console=True,
    configure_root_logger=False,
)

# Disable execution time logging for easier debugging
set_execution_time_logging(False)
set_retry_enabled(False)
from tradingapi import trading_logger


fp = FivePaisa()
fp.connect(8)
sh = Shoonya()
sh.connect(7)
sh_paper = Shoonya()
sh_paper.connect(4)
combo_symbol = "SENSEX_OPT_20250812_PUT_79700?-20:SENSEX_OPT_20250812_CALL_80300?-20:SENSEX_OPT_20250812_PUT_79500?20:SENSEX_OPT_20250812_CALL_80500?20"
pnl = get_pnl_table(sh, "IRONCONDOR01", refresh_status=False)
place_combo_order(
    sh,
    "IRONCONDOR01",
    symbols=combo_symbol,
    quantities=-6,
    entry=False,
    exchanges="BSE",
    price_types="LMT",
    paper=False,
)

pnl_table = get_pnl_table(sh_paper, "STRADDLE01", refresh_status=False)
open_trades = pnl_table.loc[pnl_table.entry_quantity + pnl_table.exit_quantity != 0]
symbol = open_trades.iloc[0]["symbol"]
quantity = open_trades.iloc[0]["entry_quantity"] + open_trades.iloc[0]["exit_quantity"]
quantity = -quantity
exchange = "BSE" if "SENSEX" in symbol else "NSE"

out = get_exit_candidates(sh, "STRADDLE01", symbol, "SELL")
place_combo_order(
    sh_paper,
    "STRADDLE01",
    symbols=symbol,
    quantities=2,
    entry=True,
    exchanges=exchange,
    price_types="MKT",
    paper=True,
)
print(out)
