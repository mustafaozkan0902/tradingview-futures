from flask import Flask, request
import json
import telebot
from binance.um_futures import UMFutures

app = Flask(__name__)
@app.route("/webhook", methods=['POST'])
def webhook():
    try:
        data = json.loads(request.data)
        ticker = data['ticker']
        exchange = data['exchange']
        price = data['price']
        side = data['side']
        quantity = data['quantity']
        telegramBotApi = data['telegramBotApi']
        telegramUserId = data['telegramUserId']
        binanceApiKey = data['binanceApiKey']
        binanceSecretKey = data['binanceSecretKey']
        um_futures_client = UMFutures(binanceApiKey, binanceSecretKey)

        '''
        # ********************* BURADAN BAŞLA   *******************
        '''
        stp_side = ""
        stp_price = 0
        tp_price = 0
        poz_amount = 0
        def openOrderInfo():
            poz_info = um_futures_client.get_position_risk(symbol=ticker[:-4], recvWindow=2000)
            poz_amount = float(poz_info[0]['positionAmt'])
            if poz_amount == 0:
                stopInfo()
            elif poz_amount > 0:
                um_futures_client.new_order(symbol=ticker[:-4], side="SELL", type="MARKET", quantity=abs(poz_amount))
                um_futures_client.cancel_open_orders(symbol=ticker[:-4], recvWindow=2000, timeInForce="GTC")
                stopInfo()
            elif poz_amount < 0:
                um_futures_client.new_order(symbol=ticker[:-4], side="BUY", type="MARKET", quantity=abs(poz_amount))
                um_futures_client.cancel_open_orders(symbol=ticker[:-4], recvWindow=2000, timeInForce="GTC")
                stopInfo()
        def stopInfo():
            tempprice = float(price)
            if tempprice > 9:
                rnd = 2
            elif tempprice > 1 & price <= 9:
                rnd = 3
            elif tempprice < 1:
                rnd = 4
            if side == "BUY":
                stp_price = float(round((tempprice * 0.975), rnd))
                tp_price = float(round((tempprice * 1.1), rnd))
                stp_side = "SELL"
            elif side == "SELL":
                stp_price = float(round((tempprice * 1.025), rnd))
                tp_price = float(round((tempprice * 0.9), rnd))
                stp_side = "BUY"
            enterOrder(stp_price, stp_side, tp_price)
        def enterOrder(stp_price, stp_side):
            um_futures_client.new_order(symbol=ticker[:-4], side=side, type="MARKET", quantity=quantity, )
            um_futures_client.new_order(symbol=ticker[:-4], side=stp_side, type="STOP_MARKET", stopPrice=stp_price, quantity=quantity,closePosition="true", timeInForce="GTC")
            um_futures_client.new_order(symbol=ticker[:-4], side=stp_side, type="TAKE_PROFIT_MARKET", stopPrice=tp_price, quantity=quantity,closePosition="true", timeInForce="GTC")


        openOrderInfo()
        '''
        # *********************    *******************
        ÇOK YÜKSEK TE OLSA TAKE PROFİT KOYMAK LAZIM
        '''

        telebot.TeleBot(telegramBotApi).send_message(telegramUserId,
                                                     f"{ticker} {side}ING on {exchange} \nQuantity : {quantity} ")
    except:
        pass
    return {
        "code": "success",
    }









