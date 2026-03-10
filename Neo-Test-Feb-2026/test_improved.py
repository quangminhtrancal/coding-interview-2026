from collections import defaultdict

'''
Credit card transaction system - Improved version

  The improved version (test_improved.py) addresses:                                                                                                                                                      
                                                                                                                                                                                                          
  1. Lazy Recalculation: Only recalculates balances when dirty flag is set                                                                                                                                
  2. Encapsulation: All logic in TransactionManager class                                                                                                                                                 
  3. Clear Naming: Fixed variable names (jose_balance vs cody_balance)                                                                                                                                    
  4. Constants: MAX_REVERSIBLE_AMOUNT instead of magic number                                                                                                                                             
  5. Validation: Input validation in Transaction constructor                                                                                                                                              
  6. Better Return Values: reverse_latest_transaction() returns boolean                                                                                                                                   
  7. Better Messages: Clear feedback on reversal success/failure                                                                                                                                          
  8. Single Responsibility: Each method has one clear purpose                                                                                                                                             
  9. Testability: Easy to unit test with the class structure                                                                                                                                              
                                                                                                                                                                                                          
  The main performance improvement is the _balance_dirty flag pattern, which avoids recalculating on every get_balance() call while still maintaining correctness.     
'''

MAX_REVERSIBLE_AMOUNT = 1000.00


class Transaction:
    def __init__(self, user_id, amount, is_deleted=False):
        if not user_id:
            raise ValueError("user_id cannot be empty")
        if amount < 0:
            raise ValueError("amount cannot be negative")

        self.user_id = user_id
        self.amount = amount
        self.is_deleted = is_deleted

    def __repr__(self):
        status = "DELETED" if self.is_deleted else "ACTIVE"
        return f'Transaction: user={self.user_id}, amount=${self.amount:.2f}, status={status}'


class TransactionManager:
    def __init__(self):
        self.transactions = []
        self._balances = defaultdict(float)
        self._balance_dirty = True

    def add_transaction(self, user_id, amount):
        """Add a new transaction"""
        transaction = Transaction(user_id, amount)
        self.transactions.append(transaction)
        self._balance_dirty = True
        return transaction

    def _recalculate_balances(self):
        """Recalculate all balances from scratch"""
        self._balances.clear()
        for transaction in self.transactions:
            if not transaction.is_deleted:
                self._balances[transaction.user_id] += transaction.amount
        self._balance_dirty = False

    def get_balance(self, user_id):
        """Get current balance for a user"""
        if self._balance_dirty:
            self._recalculate_balances()
        return self._balances.get(user_id, 0.0)

    def reverse_latest_transaction(self, user_id):
        """
        Reverse the latest transaction for a user.
        Returns True if successful, False if no reversible transaction found.
        """
        for transaction in reversed(self.transactions):
            if transaction.user_id == user_id and not transaction.is_deleted:
                if transaction.amount >= MAX_REVERSIBLE_AMOUNT:
                    print(f"Cannot reverse transaction: amount ${transaction.amount:.2f} exceeds limit")
                    return False

                transaction.is_deleted = True
                self._balance_dirty = True
                print(f"Reversed: {transaction}")
                return True

        print(f"No active transaction found for user {user_id}")
        return False

    def print_all_transactions(self):
        """Print all transactions"""
        for transaction in self.transactions:
            print(transaction)


# Example usage
if __name__ == "__main__":
    manager = TransactionManager()

    # Add transactions
    print("Adding transactions...")
    manager.add_transaction('Cody', 900.10)
    manager.add_transaction('Jose', 200.10)
    manager.add_transaction('Jose', 300.70)
    manager.add_transaction('Cody', 1000.20)

    print("\nAll transactions:")
    manager.print_all_transactions()

    # Calculate balances
    print("\n--- Initial Balances ---")
    cody_balance = manager.get_balance('Cody')
    print(f'Cody balance: ${cody_balance:.2f}')

    jose_balance = manager.get_balance('Jose')  # Fixed variable name
    print(f'Jose balance: ${jose_balance:.2f}')

    # Reverse transactions
    print("\n--- Reversing Latest Transactions ---")
    manager.reverse_latest_transaction('Cody')
    manager.reverse_latest_transaction('Jose')

    # Recalculate balances after reversal
    print("\n--- Balances After Reversal ---")
    cody_balance = manager.get_balance('Cody')
    print(f'Cody balance: ${cody_balance:.2f}')

    jose_balance = manager.get_balance('Jose')
    print(f'Jose balance: ${jose_balance:.2f}')

    print("\n--- All Transactions (Final State) ---")
    manager.print_all_transactions()
