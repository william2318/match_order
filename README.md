# Code Test -- Order Matching

## Overview

The script “match_order.py” organizes the input orders into an order book of market and limit bid/ask queues, according to the order type and side. Each time a new order is added to the book, the script will identify and print orders with filled prices and quatities if any.

## Usage

Execute the code using python3 and the input file (e.g sample_A.csv) is fed through the stdin channel.

> python3 match_order.py < sample_A.csv

## Data Structure

There are 2 data objects defined in the script:
1. “Order” stores the attributes of an order, which are id, symbol, price, side and quantity.
2. “OrderBook” holds four order queues, which are market bid/ask and limit bid/ask.

## Algorithm

### Step 1: Read Inputs in CSV format and save in a list of “Order” objects

Here is an example of the input:
> Order1,0700.HK,610,Sell,20000  
> Order2,0700.HK,610,Sell,10000  
> Order3,0700.HK,610,Buy,10000  
> …

Each order has 5 attributes (order ID, symbol, price, side, order Quantity). The “price” can be numeric or string “MKT”, indicating limit or market order type, respectively. The “side” column can only be “Buy” or “Sell”.

### Step 2: Order Validation

Validate an order using the Order.validate(), which check against the followings:
 - 0 < order quantity < 1,000,000
 - If the order price is numeric, it is >0.
 - If the order price is a string, it is “MKT”
 - If the order side is either “Buy” or “Sell”

If an order fails any of the above tests, it will be rejected.

### Step 3: Order Matching

#### 1) Sort the bid and ask queues by price and arrival time

Each accepted order will be added to the order book according to its order type (market or limit) and side (buy or sell). An index is also given to that order indicating the arrival sequence. Everytime a new order is added to a queue, orders in that queue will be sorted by price (descending if bid, ascending if ask) and then by arrival time to ensure the orders are matched in the priority of price and time.

#### 2) Obtain the best bid and ask prices in the order book

After sorting, the script will determine the best bid and ask price in the order book, considering all market and limit orders. If there are only market orders in the book, there will be no best bid/ask prices and the script will move on to process the next order in the input list.

#### 3) Determine the filled price

In the case of best bid price = best ask price, the filled price of match orders will be that matched price;
In the case of best bid price > best ask price, the filled price will be the price of the order arrived first;
In the case of best bid price < best ask price, there will be no matching and the script will process the next order in the input list.

#### 4) Compute the filled quantity

Once the filled price is found, the code will determine the matched quantity, which is the minimum of the sum of available quantity to be filled at the matched price in the bid and ask queue of the book.

#### 5) Print the matching details

The script will print the filled price and quantity of the matched orders to stdout. For example,

> Fill,Order1,0700.HK,610.0,Sell,20000,610.0,10000  
> Fill,Order3,0700.HK,610.0,Buy,10000,610.0,10000  

#### 6) Remove matched quantites/orders from the book

The matched quantities will be removed from the order's quantity. If all the quantities of an order are matched, it will be removed from the order book. 

#### Note

The script will handle the matching between market orders first, and then the matching involving limit orders.
In addition, only one best bid and one ask price will be considered at one time. After removing the matched quantity/orders from the order book, the whole matching process will be repeated, starting from ***2) Obtain the best bid and ask prices in the order book***, until no matched orders can be found. Then, the script will move on to process the next order in the input list.
