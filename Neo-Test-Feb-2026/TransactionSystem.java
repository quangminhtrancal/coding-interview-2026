import lombok.*;
import java.util.*;

/*
  The code maintains all improvements (validation, lazy recalculation, clear naming) but in a format perfect for live coding where you need to type quickly and explain clearly.                          
                                                                                                                                                                                                          
  To run: javac TransactionSystem.java && java TransactionSystem 
*/
public class TransactionSystem {
    private static final double MAX_REVERSIBLE_AMOUNT = 1000.00;

    @Data
    @AllArgsConstructor
    static class Transaction {
        private String userId;
        private double amount;
        private boolean deleted;

        public Transaction(String userId, double amount) {
            if (userId == null || userId.isEmpty())
                throw new IllegalArgumentException("userId cannot be empty");
            if (amount < 0)
                throw new IllegalArgumentException("amount cannot be negative");

            this.userId = userId;
            this.amount = amount;
            this.deleted = false;
        }

        @Override
        public String toString() {
            String status = deleted ? "DELETED" : "ACTIVE";
            return String.format("Transaction: user=%s, amount=$%.2f, status=%s", userId, amount, status);
        }
    }

    static class TransactionManager {
        private List<Transaction> transactions = new ArrayList<>();
        private Map<String, Double> balances = new HashMap<>();
        private boolean balanceDirty = true;

        public void addTransaction(String userId, double amount) {
            transactions.add(new Transaction(userId, amount));
            balanceDirty = true;
        }

        private void recalculateBalances() {
            balances.clear();
            transactions.stream()
                .filter(t -> !t.isDeleted())
                .forEach(t -> balances.merge(t.getUserId(), t.getAmount(), Double::sum));

            balanceDirty = false;
        }

        public double getBalance(String userId) {
            if (balanceDirty) recalculateBalances();
            return balances.getOrDefault(userId, 0.0);
        }

        public boolean reverseLatestTransaction(String userId) {
            for (int i = transactions.size() - 1; i >= 0; i--) {
                Transaction t = transactions.get(i);
                if (t.getUserId().equals(userId) && !t.isDeleted()) {
                    if (t.getAmount() >= MAX_REVERSIBLE_AMOUNT) {
                        System.out.printf("Cannot reverse: amount $%.2f exceeds limit%n", t.getAmount());
                        return false;
                    }
                    
                    t.setDeleted(true);
                    balanceDirty = true;
                    System.out.println("Reversed: " + t);
                    return true;
                }
            }
            System.out.println("No active transaction found for " + userId);
            return false;
        }

        public void printAll() {
            transactions.forEach(System.out::println);
        }
    }

    public static void main(String[] args) {
        TransactionManager manager = new TransactionManager();

        System.out.println("Adding transactions...");
        manager.addTransaction("Cody", 900.10);
        manager.addTransaction("Jose", 200.10);
        manager.addTransaction("Jose", 300.70);
        manager.addTransaction("Cody", 1000.20);

        System.out.println("\nAll transactions:");
        manager.printAll();

        System.out.println("\n--- Initial Balances ---");
        System.out.printf("Cody balance: $%.2f%n", manager.getBalance("Cody"));
        System.out.printf("Jose balance: $%.2f%n", manager.getBalance("Jose"));

        System.out.println("\n--- Reversing Latest Transactions ---");
        manager.reverseLatestTransaction("Cody");
        manager.reverseLatestTransaction("Jose");

        System.out.println("\n--- Balances After Reversal ---");
        System.out.printf("Cody balance: $%.2f%n", manager.getBalance("Cody"));
        System.out.printf("Jose balance: $%.2f%n", manager.getBalance("Jose"));

        System.out.println("\n--- All Transactions (Final State) ---");
        manager.printAll();
    }
}
