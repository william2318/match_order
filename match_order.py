import sys
import utils

def getBestPrice(obook, side):
    opp = 'bid' if side == 'ask' else 'ask'
    res = tmp = None
    if obook.limit[side]:
        res = obook.limit[side][0].getPriceInfo()
    if obook.market[side] and obook.limit[opp]:
        tmp = obook.limit[opp][0].getPriceInfo()
        if not res or \
           (side == 'bid' and tmp[0] > res[0]) or \
           (side == 'ask' and tmp[0] < res[0]):
            res = tmp
    return res

def getMaxQuantity(obook, side, price):
    if not price:
        return
    qty = sum([x.qtyRemain for x in obook.market[side]])
    if (side == 'bid' and obook.limit[side]):
        qty += sum([x.qtyRemain if x.price >= price else 0 \
                    for x in obook.limit[side]])
    elif (side == 'ask' and obook.limit[side]):
        qty += sum([x.qtyRemain if x.price <= price else 0 \
                    for x in obook.limit[side]])
    return qty

def getMatchPriceQuantity(obook):
    """
    Find matched price and quantity
    """
    bestBidPrice = getBestPrice(obook, 'bid')
    bestAskPrice = getBestPrice(obook, 'ask')
    if not bestBidPrice or not bestAskPrice:
        return None, 0

    price = None
    if bestBidPrice[0] == bestAskPrice[0]:
        price = bestAskPrice[0]
    if bestBidPrice[0] > bestAskPrice[0]:
        price = sorted([bestBidPrice, bestAskPrice], key = lambda x: x[1])[0][0]
    if not price:
        return None, 0

    maxBidQty = getMaxQuantity(obook, 'bid', price)
    maxAskQty = getMaxQuantity(obook, 'ask', price)
    return price, min(maxBidQty, maxAskQty)

def main():
    orders = [utils.Order(msg) for msg in sys.stdin.readlines()]
    print('ActionType,OrderID,Symbol,Price,Side,OrderQuantity' +
          'FillPrice,FillQuantity')
    obook = {}
    cnt = 1
    for order in orders:
        actType = 'Ack' if order.validate() else 'Reject'
        print('%s,%s,%s,%s,%s,%s' % (
            actType, order.oid, order.sym, order.price, order.side, order.qty))
        if actType == 'Reject':
            continue
        if order.sym not in obook:
            obook[order.sym] = utils.OrderBook()
        obook[order.sym].addOrder(order, cnt)
        cnt += 1
        fPrice, fQty = getMatchPriceQuantity(obook[order.sym])
        while fPrice and fQty:
            fQtyMkt = min(obook[order.sym].sumMktOrderQuantity('bid'),
                          obook[order.sym].sumMktOrderQuantity('ask'))
            for qty in [fQtyMkt, fQty - fQtyMkt]:
                obook[order.sym].popOrderFilled(fPrice, qty, 'bid')
                obook[order.sym].popOrderFilled(fPrice, qty, 'ask')
                obook[order.sym].logTrades()
            fPrice, fQty = getMatchPriceQuantity(obook[order.sym])

if __name__ == '__main__':
    main()
