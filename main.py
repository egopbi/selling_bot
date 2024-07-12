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
"""
# =======================================================================
# =======================  БЛОК BINANCE  ================================
# =======================================================================

# подрубаемся к API binance
client_b = Client(keys.api_key, keys.secret_key)
client_b.API_URL = 'https://api.binance.com'
#client_b.API_URL = 'https://testnet.binance.vision/api'

# считаем баланс кошелька
t_balance = Decimal(float(client_b.get_asset_balance(asset=token)['free'])).quantize(Decimal('.0001'), rounding=ROUND_DOWN)
usdt_balance = client_b.get_asset_balance(asset='USDT')['free']
print(f"На счету Binance {t_balance} {token} и {usdt_balance} USDT")
tokenusdt = token+'USDT'
t_balancez = Decimal(float(t_balance)*coeff_quant).quantize(Decimal('.001'), rounding=ROUND_DOWN)
"""
"""
buybuy = client_b.order_market_buy(
    symbol=tokenusdt,
    quoteOrderQty=3000
)
"""

# =======================================================================
# =========================  БЛОК OKX  ==================================
# =======================================================================

# подрубаемся к API OKX
account_o = Account.AccountAPI(keys.okx_api_key, keys.okx_secret_key, keys.okx_passphrase, False, flag)
trade_o = Trade.TradeAPI(keys.okx_api_key, keys.okx_secret_key, keys.okx_passphrase, False, flag)
market_o = MarketData.MarketAPI(keys.okx_api_key, keys.okx_secret_key, keys.okx_passphrase, False, flag)
public = PublicData.PublicAPI(flag=flag)

# считаем баланс кошелька
t_balance_o = float(account_o.get_account_balance(token)['data'][0]['details'][0]['availBal'])
usdt_balance_o = float(account_o.get_account_balance('USDT')['data'][0]['details'][0]['availBal'])
t_balancez_o = float(Decimal(float(t_balance_o)*coeff_quant).quantize(Decimal('.0001'), rounding=ROUND_DOWN))
print(f'На счету OKX {t_balance_o} {token} и {usdt_balance_o} USDT')

# =======================================================================
# =======================  БЛОК BINANCE  ================================
# =======================================================================

# асинхронная продажа и покупка на бирже Binance
async def sueta_b(
        coeff=coeff,
        token=token,
        client_b=client_b,
        t_balance=t_balance,
        t_balancez=t_balancez,
        tokenusdt=tokenusdt,
        limit_orderbook=limit_orderbook
):
    # спам ордерами по маркету на продажу
    for i in range(10):
        try:
            if i < 4:
                await asyncio.sleep(0.2)
                raise ValueError('Ошибочка')
            else:
                try:
                    sell_order = client_b.order_market_sell(
                        symbol=tokenusdt,
                        quantity=t_balance,
                    )
                except BinanceAPIException as e:
                    print(e)
        except ValueError:
            print("Ошибочка Binance вышла")


    print(f'продали {t_balance} токенов, ждем 10 секунд')
    sell_price = client_b.get_my_trades(symbol=tokenusdt, limit=2)[0]['id']
    await asyncio.sleep(2)

    t_balance = client_b.get_asset_balance(asset=token)['free']
    usdt_balance = client_b.get_asset_balance(asset='USDT')['free']
    print(f"Теперь на счету {t_balance} {token} и {usdt_balance} USDT")

    await asyncio.sleep(5)

    # ищем цену ордера на покупку
    buy_price = float(client_b.get_order_book(symbol=tokenusdt, limit=limit_orderbook)['asks'][limit_orderbook-1][0])
    print(buy_price, ' – текущая цена покупки\n')

    # ждем подходящую цену
    while buy_price >  sell_price * coeff:
        buy_price = float(client_b.get_order_book(symbol=tokenusdt, limit=limit_orderbook)['asks'][limit_orderbook - 1][0])
        print(buy_price,' – текущая цена покупки')
        await asyncio.sleep(5)
    print(f'\n*********{t_balancez} – хотим купить *********')

    # выставляем лимитку на покупку
    buy_order = client_b.order_limit_buy(
        symbol=tokenusdt,
        quantity=t_balancez,
        price=buy_price
    )

    await asyncio.sleep(10)

    t_balance = client_b.get_asset_balance(asset=token)['free']
    usdt_balance = client_b.get_asset_balance(asset='USDT')['free']
    print(f'купили {t_balance} токенов')
    print(f"В итоге на счету Binance {t_balance} {token} и {usdt_balance} USDT")
    return None

# =======================================================================
# =========================  БЛОК OKX  ==================================
# =======================================================================

async def sueta_o(
    coeff=coeff,
    token=token,
    trade_o=trade_o,
    t_balance_o=t_balance_o,
    t_balancez_o=t_balancez_o,
    tokenusdt_o=tokenusdt_o,
    limit_orderbook=limit_orderbook
):
    # спам ордерами по маркету на продажу
    for i in range(10):
        try:
            if i < 4:
                await asyncio.sleep(0.2)
                raise ValueError('Ошибочка')
            else:
                sell_order = trade_o.place_order(
                    instId=tokenusdt_o,
                    tdMode='cash',
                    side='sell',
                    ordType='market',
                    sz=t_balance_o
                )
        except ValueError:
            print("Ошибочка OKX вышла")
    print(f'продали {t_balance_o} токенов, ждем 10 секунд')

    sell_price = float(trade_o.get_fills(instType='SPOT', instId=tokenusdt_o, )['data'][0]['fillPx'])

    await asyncio.sleep(3)

    t_balance_o = round(float(account_o.get_account_balance(token)['data'][0]['details'][0]['availBal']),3)
    usdt_balance_o = round(float(account_o.get_account_balance('USDT')['data'][0]['details'][0]['availBal']),2)
    print(f'Теперь на счету {t_balance_o} {token} и {usdt_balance_o} USDT')

    # ищем цену ордера на покупку
    buy_price = float(market_o.get_orderbook(instId=tokenusdt_o, sz=3)['data'][0]['asks'][limit_orderbook-1][0])
    print(buy_price, ' – текущая цена покупки\n')

    # ждем подходящую цену
    while buy_price > sell_price * coeff:
        buy_price = float(market_o.get_orderbook(instId=tokenusdt_o, sz=3)['data'][0]['asks'][limit_orderbook-1][0])
        print(buy_price, ' – текущая цена покупки')

        await asyncio.sleep(2)
    print(f'\n##########{t_balancez_o} – хотим купить ##############')


    # выставляем лимитку на покупку
    buy_order = trade_o.place_order(
        instId=tokenusdt_o,
        tdMode='cash',
        side='buy',
        ordType='limit',
        px=buy_price,
        sz=t_balancez_o
    )
    print(buy_order)
    await asyncio.sleep(8)

    t_balance_o = round(float(account_o.get_account_balance(token)['data'][0]['details'][0]['availBal']),3)
    usdt_balance_o = round(float(account_o.get_account_balance('USDT')['data'][0]['details'][0]['availBal']),2)
    print(f'купили {t_balance_o} токенов')
    print(f"В итоге на счету OKX {t_balance_o} {token} и {usdt_balance_o} USDT")

print(t_balancez_o)
print(type(t_balancez_o))

async def main():
    await asyncio.wait([
        asyncio.create_task(sueta_o()),
        #asyncio.create_task(sueta_b())
    ])

asyncio.run(main())


"""
scheduler = AsyncIOScheduler()
scheduler.add_job(sueta_b, trigger='date', run_date=datetime(2024, 5, 15, 9, 54))
scheduler.start()
"""