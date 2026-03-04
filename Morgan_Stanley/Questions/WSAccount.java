// QUESTION
//
// Suppose you have a bank account that holds some stocks and some money.
// This amount can be thought of as the end result of all the transactions
// that have happened in your account up until the present day. Types of
// transactions can be:
//
// * deposits of cash
// * withdrawals of cash
// * buys and sells of units of stock.
//
// We'd like to be able to construct the current balances of an account by
// replaying a history of past activities as in the accountTransactions
// variable given below.
//
// The ask is to do the following tasks:
// 1. Calculate the quantity of shares of each stock
// 2. Calculate the remaining cash balance
// 3. Display the balance for every transaction
//
// How would you do this?
//
// { cash: 269.56, quantities: { APPL: 4, SHOP: 0, GOOGL: 2 } }

import java.math.BigDecimal;
import java.util.*;

record Transaction(
    String type,
    Double netAmount,
    String symbol,
    Double quantity,
    String date) {
}

class Holding {
    private final String symbol;
    private BigDecimal quantity;

    public Holding(String symbol) {
        this.symbol = symbol;
        this.quantity = BigDecimal.ZERO;
    }

    public void buy(BigDecimal quantity) {
        this.quantity = this.quantity.add(quantity);
    }

    public void sell(BigDecimal quantity) {
        this.quantity = this.quantity.add(quantity);
    }

    @Override
    public String toString() {
        return symbol + ": " + quantity.toString() + "\n";
    }
}

class Account {
    private BigDecimal cashFlow;
    private Map<String, Holding> holdings;

    public Account() {
        this.cashFlow = BigDecimal.ZERO;
        this.holdings = new HashMap<>();
    }

    public void buyHolding(String symbol, BigDecimal quantity, BigDecimal price) {
        this.cashFlow = this.cashFlow.add(price);
        Holding holding = holdings.computeIfAbsent(symbol, Holding::new);
        holding.buy(quantity);
    }

    public void sellHolding(String symbol, BigDecimal quantity, BigDecimal price) {
        this.cashFlow = this.cashFlow.add(price);
        Holding holding = holdings.computeIfAbsent(symbol, Holding::new);
        holding.sell(quantity);
    }

    public void deposit(BigDecimal cash) {
        this.cashFlow = this.cashFlow.add(cash);
    }

    public void withdraw(BigDecimal cash) {
        this.cashFlow = this.cashFlow.add(cash);
    }

    @Override
    public String toString() {
        String result = "cash: " + this.cashFlow.toString() + "\n, quantities: {";
        for (Holding holding : holdings.values()) {
            result += holding.toString();
        }
        result += "}";
        return result;
    }
}

class Solution {
    public static void main(String[] args) {
        List<Transaction> accountTransactions = Arrays.asList(
            new Transaction("DEPOSIT", 700.0, null, null, "2019-01-10"),
            new Transaction("BUY", -174.25, "SHOP", 10.0, "2019-01-11"),
            new Transaction("BUY", -226.12, "APPL", 10.0, "2019-01-13"),
            new Transaction("BUY", -200.25, "GOOGL", 3.0, "2019-01-14"),
            new Transaction("SELL", 31.00, "APPL", -1.0, "2019-03-25"),
            new Transaction("SELL", 90.85, "APPL", -5.0, "2019-04-15"),
            new Transaction("WITHDRAWAL", -200.0, null, null, "2019-04-18"),
            new Transaction("SELL", 166.85, "SHOP", -10.0, "2019-04-19"),
            new Transaction("SELL", 80.4, "GOOGL", -1.0, "2019-05-25"));

        Account account = new Account();
        for (Transaction transaction : accountTransactions) {
            if (transaction.type().equals("DEPOSIT")) {
                account.deposit(new BigDecimal(transaction.netAmount().toString()));
            } else if (transaction.type().equals("BUY")) {
                account.buyHolding(transaction.symbol(), new BigDecimal(transaction.quantity().toString()),
                    new BigDecimal(transaction.netAmount().toString()));
            } else if (transaction.type().equals("SELL")) {
                account.sellHolding(transaction.symbol(), new BigDecimal(transaction.quantity().toString()),
                    new BigDecimal(transaction.netAmount().toString()));
            } else if (transaction.type().equals("WITHDRAWAL")) {
                account.withdraw(new BigDecimal(transaction.netAmount().toString()));
            }
        }
        System.out.println(account);
    }
}
