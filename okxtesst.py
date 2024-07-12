import keys
import asyncio
import okx.Trade as Trade
import okx.MarketData as MarketData
import okx.PublicData as PublicData
import okx.Account as Account

coeff = 1 #по какой цене откупим относительно продажи
limit_orderbook = 3 #сколько заявок отступим при откупе
flag = "1"  # live trading: 0, demo trading: 1
token = 'ETH'
tokenusdt_o = token + '-USDT'

# подрубаемся к API OKX
account_o = Account.AccountAPI(keys.okx_api_key_test, keys.okx_secret_key_test, keys.okx_passphrase, False, flag)
trade_o = Trade.TradeAPI(keys.okx_api_key_test, keys.okx_secret_key_test, keys.okx_passphrase, False, flag)
public = PublicData.PublicAPI(flag=flag)
market_o = MarketData.MarketAPI(keys.okx_api_key_test, keys.okx_secret_key_test, keys.okx_passphrase, False, flag)

# считаем баланс кошелька
t_balance_o = float(account_o.get_account_balance(token)['data'][0]['details'][0]['availBal'])
usdt_balance_o = float(account_o.get_account_balance('USDT')['data'][0]['details'][0]['availBal'])
t_balancez_o = float(t_balance_o)*0.9 # какую долю откупим
print(t_balance_o, usdt_balance_o)

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
    print(f'\n*********{t_balancez_o} – хотим купить *********')


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


async def main():
    await asyncio.wait([
        asyncio.create_task(sueta_o()),
    ])

asyncio.run(main())
