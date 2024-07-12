from binance.client import Client
import keys
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import asyncio
import okx.Trade as Trade
import okx.MarketData as MarketData
import okx.PublicData as PublicData
import okx.Account as Account
from decimal import *

# Настраиваемые параметры
limit_orderbook = 3 #сколько заявок отступим при откупе
coeff = 1.01 #по какой цене откупим относительно продажи
token = 'ETH' #какой токен продаем
flag = '0' #1 - демоторговля на okx, 0 - настоящая торговля
coeff_quant = 0.8 #на какую долю полученных долларов перезайдем

tokenusdt_o = token + '-USDT'

# =======================================================================
# =======================  БЛОК BINANCE  ================================
# =======================================================================

# подрубаемся к API binance
client_b = Client(keys.api_key, keys.secret_key)
client_b.API_URL = 'https://api1.binance.com'
#client_b.API_URL = 'https://testnet.binance.vision/api'

# считаем баланс кошелька
t_balance = client_b.get_all_tickers()
usdt_balance = client_b.get_asset_balance(asset='USDT')['free']
print(f"На счету Binance {t_balance} {token} и {usdt_balance} USDT")
tokenusdt = token+'USDT'
t_balancez = Decimal(float(t_balance)*coeff_quant).quantize(Decimal('.001'), rounding=ROUND_DOWN)
print(t_balance)
"""
print(time.ctime())
datime = datetime(2024, 5, 15, 11, 0)
async def promt():
    print('goool')
    time.sleep(5)
    print('goool*********')

async def pipka():
    print('goida')
    time.sleep(2)
    print('goidaa*******')

scheduler = AsyncIOScheduler()
scheduler.add_job(promt, 'date', run_date=datime)
scheduler.add_job(pipka, 'date', run_date=datime)

scheduler.start()
asyncio.get_event_loop().run_forever()
"""