from flask import Flask, request
import json
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
                um_futures_client.cancel_open_orders(symbol=ticker[:-4], recvWindow=2000, timeInForce="GTC")
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
            else:
                if tempprice>=1:
                    rnd = 3
                else:
                    if tempprice>=0.1:
                        rnd = 4
                    else:
                        rnd = 5
            if side == "BUY":
                stp_price = float(round((tempprice * 0.975), rnd))
                tp_price = float(round((tempprice * 1.15), rnd))
                stp_side = "SELL"
            elif side == "SELL":
                stp_price = float(round((tempprice * 1.025), rnd))
                tp_price = float(round((tempprice * 0.85), rnd))
                stp_side = "BUY"
            enterOrder(sp = stp_price, ss = stp_side, tp = tp_price )
        def enterOrder(sp, ss, tp):
            um_futures_client.new_order(symbol=ticker[:-4], side=side, type="MARKET", quantity=quantity, )
            um_futures_client.new_order(symbol=ticker[:-4], side=ss, type="STOP_MARKET", stopPrice=sp, quantity=quantity,closePosition="true", timeInForce="GTC")
            um_futures_client.new_order(symbol=ticker[:-4], side=ss, type="TAKE_PROFIT_MARKET", stopPrice=tp, quantity=quantity,closePosition="true", timeInForce="GTC")


        openOrderInfo()
        '''
        # *********************    *******************
        ÇOK YÜKSEK TE OLSA TAKE PROFİT KOYMAK LAZIM
        '''

    except:
        pass
    return {
        "code": "success",
    }









