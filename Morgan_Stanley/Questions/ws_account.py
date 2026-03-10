# QUESTION
#
# Suppose you have a bank account that holds some stocks and some money.
# This amount can be thought of as the end result of all the transactions
# that have happened in your account up until the present day. Types of
# transactions can be:
#
# * deposits of cash
# * withdrawals of cash
# * buys and sells of units of stock.
#
# We'd like to be able to construct the current balances of an account by
# replaying a history of past activities as in the accountTransactions
# variable given below.
#
# The ask is to do the following tasks:
# 1. Calculate the quantity of shares of each stock
# 2. Calculate the remaining cash balance
# 3. Display the balance for every transaction
#
# How would you do this?
#
# { cash: 269.56, quantities: { APPL: 4, SHOP: 0, GOOGL: 2 } }

from decimal import Decimal
from dataclasses import dataclass
from typing import Optional


@dataclass
class Transaction:
    type: str
    net_amount: Optional[float]
    symbol: Optional[str]
    quantity: Optional[float]
    date: str


class Holding:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.quantity = Decimal("0")

    def buy(self, quantity: Decimal):
        self.quantity += quantity

    def sell(self, quantity: Decimal):
        self.quantity += quantity  # quantity is negative for sells

    def __str__(self):
        return f"{self.symbol}: {self.quantity}"


class Account:
    def __init__(self):
        self.cash_flow = Decimal("0")
        self.holdings: dict[str, Holding] = {}

    def buy_holding(self, symbol: str, quantity: Decimal, price: Decimal):
        self.cash_flow += price  # price is negative for buys
        if symbol not in self.holdings:
            self.holdings[symbol] = Holding(symbol)
        self.holdings[symbol].buy(quantity)

    def sell_holding(self, symbol: str, quantity: Decimal, price: Decimal):
        self.cash_flow += price
        if symbol not in self.holdings:
            self.holdings[symbol] = Holding(symbol)
        self.holdings[symbol].sell(quantity)

    def deposit(self, cash: Decimal):
        self.cash_flow += cash

    def withdraw(self, cash: Decimal):
        self.cash_flow += cash  # cash is negative for withdrawals

    def __str__(self):
        quantities = {h.symbol: h.quantity for h in self.holdings.values()}
        return f"cash: {self.cash_flow}, quantities: {quantities}"


if __name__ == "__main__":
    account_transactions = [
        Transaction("DEPOSIT", 700.0, None, None, "2019-01-10"),
        Transaction("BUY", -174.25, "SHOP", 10.0, "2019-01-11"),
        Transaction("BUY", -226.12, "APPL", 10.0, "2019-01-13"),
        Transaction("BUY", -200.25, "GOOGL", 3.0, "2019-01-14"),
        Transaction("SELL", 31.00, "APPL", -1.0, "2019-03-25"),
        Transaction("SELL", 90.85, "APPL", -5.0, "2019-04-15"),
        Transaction("WITHDRAWAL", -200.0, None, None, "2019-04-18"),
        Transaction("SELL", 166.85, "SHOP", -10.0, "2019-04-19"),
        Transaction("SELL", 80.4, "GOOGL", -1.0, "2019-05-25"),
    ]

    account = Account()
    for txn in account_transactions:
        if txn.type == "DEPOSIT":
            account.deposit(Decimal(str(txn.net_amount)))
        elif txn.type == "BUY":
            account.buy_holding(txn.symbol, Decimal(str(txn.quantity)), Decimal(str(txn.net_amount)))
        elif txn.type == "SELL":
            account.sell_holding(txn.symbol, Decimal(str(txn.quantity)), Decimal(str(txn.net_amount)))
        elif txn.type == "WITHDRAWAL":
            account.withdraw(Decimal(str(txn.net_amount)))

    print(account)
