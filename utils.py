class Order:

    def __init__(self, message):
        """Constructor
        type(message): string

        Message string has the format: OrderID,Symbol,Price,Side,OrderQuantity
        """
        msg = message.rstrip('\n').split(',')
        self.oid = msg[0]
        self.sym = msg[1]
        self.price = val2Float(msg[2])
        self.side = msg[3]
        self.qty = self.qtyRemain = val2Int(msg[4])
        self.priceTraded = None
        self.qtyTraded = 0
        self.idx = None
        self.sortTuple = None

    def validate(self):
        if isinstance(self.qty, str) or self.qty >= 1000000 or self.qty <= 0:
            return False
        if isinstance(self.price, str) and self.price != 'MKT':
            return False
        if isinstance(self.price, float) and self.price <= 0:
            return False
        if self.side not in ('Buy', 'Sell'):
            return False
        return True

    def setIdx(self, idx):
        self.idx = idx

    def setSortTuple(self, side):
        self.sortTuple = (self.price * (1 if side == 'ask' else -1), self.idx)

    def getPriceInfo(self):
        return (self.price, self.idx)

    def recordTrade(self, fPrice, fQty):
        self.priceTraded = fPrice
        self.qtyTraded = fQty
        self.qtyRemain -= max(fQty, 0)

    def clearTradeRecord(self):
        self.priceTraded = None
        self.qtyTraded = 0

class OrderBook:

    def __init__(self):
        self.market = {'bid': [], 'ask': []}
        self.limit = {'bid': [], 'ask': []}
        self.traded = []

    def addOrder(self, order, idx):
        side = 'bid' if order.side == 'Buy' else 'ask'
        order.setIdx(idx)
        if order.price == 'MKT':
            self.market[side].append(order)
        else:
            order.setSortTuple(side)
            self.limit[side].append(order)
            self.limit[side].sort(key = lambda x: x.sortTuple)

    def popOrderFilled(self, fPrice, fQty, side):
        if not fPrice or not fQty:
            return
        remain = fQty
        for que in [self.market[side], self.limit[side]]:
            while remain:
                if que:
                    que[0].recordTrade(fPrice, min(remain, que[0].qtyRemain))
                    remain -= que[0].qtyTraded
                    self.traded.append(que[0])
                    if not que[0].qtyRemain:
                        que.pop(0)
                else:
                    break

    def logTrades(self):
        if not self.traded:
            return
        self.traded.sort(key = lambda x: x.idx)
        while self.traded:
            order = self.traded.pop(0)
            print('Fill,%s,%s,%s,%s,%g,%s,%g' % (
                order.oid, order.sym, order.price, order.side, order.qty,
                order.priceTraded, order.qtyTraded))
            order.clearTradeRecord()

    def sumMktOrderQuantity(self, side):
        return sum([x.qty for x in self.market[side]])

def val2Float(val):
    try:
        return float(val) if val else None
    except:
        return val

def val2Int(val):
    try:
        return int(val) if val else None
    except:
        return val
