from collections import defaultdict
'''
credit card transaction system
1) define structure to store credit transaction (user, amount)

Cody 900.10
Jose 200.10
Jose 300.70
Cody 1000.20

  Critical Issues                                                                                                                                                                                         
                                                                                                                                                                                                          
  1. Performance Problem (line 54)                                                                                                                                                                        
  - calculate_balance() recalculates ALL balances from scratch on every call to calculate_user_balance(). This is O(n) for each user query.                                                               
  - Fix: Calculate balances once, or maintain them incrementally when transactions are added/deleted.                                                                                                     
                                                                                                                                                                                                          
  2. Variable Name Bug (line 60)                                                                                                                                                                          
  cody_balance = calculate_user_balance('Jose')  # Wrong variable name                                                                                                                                    
  print(f'Jose balance {cody_balance}')                                                                                                                                                                   
  - Should be jose_balance for clarity.                                                                                                                                                                   
                                                                                                                                                                                                          
  Design Issues                                                                                                                                                                                           
                                                                                                                                                                                                          
  3. Global State (lines 30, 38)                                                                                                                                                                          
  - Using global transactions list and transaction_map makes the code hard to test and reuse.                                                                                                             
  - Fix: Encapsulate in a TransactionManager or AccountingSystem class.                                                                                                                                   
                                                                                                                                                                                                          
  4. Inefficient Balance Calculation (lines 39-51)                                                                                                                                                        
  def calculate_balance():                                                                                                                                                                                
      for key in transaction_map.keys():                                                                                                                                                                  
          transaction_map[key] = 0  # Unnecessary reset                                                                                                                                                   
  - Resetting to 0 and recalculating is wasteful.                                                                                                                                                         
  - Fix: Update balances incrementally when transactions are added/reversed.                                                                                                                              
                                                                                                                                                                                                          
  5. Unused User Class (line 12-14)                                                                                                                                                                       
  - The User class is defined but never used. Remove it or integrate it properly.                                                                                                                         
                                                                                                                                                                                                          
  6. Magic Number (line 74)                                                                                                                                                                               
  if transaction.amount < 1000:  # Magic number                                                                                                                                                           
  - Fix: Use a constant: MAX_REVERSIBLE_AMOUNT = 1000.00                                                                                                                                                  
                                                                                                                                                                                                          
  Logic Issues                                                                                                                                                                                            
                                                                                                                                                                                                          
  7. Reverse Transaction Logic (line 68-78)                                                                                                                                                               
  - The function name says "reverse" but it only marks as deleted, doesn't actually reverse (subtract) the amount.                                                                                        
  - No return value to indicate success/failure.                                                                                                                                                          
  - Fix: Return boolean or raise exception if reversal fails.                                                                                                                                             
                                                                                                                                                                                                          
  8. No Validation                                                                                                                                                                                        
  - No validation for negative amounts, None values, or empty user IDs.                                                                                                                                   
  - Fix: Add validation in Transaction.__init__().                                                                                                                                                        
                                                      
'''

class User:
    def __init__(self, user_id=None):
        self.user_id = user_id

class Transaction:
    def __init__(self, user_id, amount, is_deleted=False):
        self.user_id = user_id
        self.amount = amount
        self.is_deleted = is_deleted
    
    def __repr__(self):
        return (f'transaction: user: {self.user_id} with amount: {self.amount}')


transaction1 = Transaction('Cody', 900.10)
transaction2 = Transaction('Jose', 200.10)
transaction3 = Transaction('Jose', 300.70)
transaction4 = Transaction('Cody', 1000.20)
transactions = [transaction1, transaction2, transaction3, transaction4]

for transaction in transactions:
    print(transaction)

'''
calculate user balance
'''
transaction_map = defaultdict(int)
def calculate_balance():
    for key in transaction_map.keys():
        transaction_map[key] = 0

    for transaction in transactions:
        if transaction.is_deleted:
            continue

        user_id = transaction.user_id
        amount = transaction.amount

        transaction_map[user_id] += amount
        
    
def calculate_user_balance(user_id):
    calculate_balance() ### need to improve from here since recalculate
    return transaction_map[user_id]

cody_balance = calculate_user_balance('Cody')
print(f'Cody balance {cody_balance}')

cody_balance = calculate_user_balance('Jose')
print(f'Jose balance {cody_balance}')

'''
 reverse transaction
 cannot reverse more than $1000
 for second transaction let reverse
'''
def reverse_latest_transaction(user_id):
    
    for i in range(len(transactions)-1, -1, -1):
        transaction = transactions[i]
        print(f'Current transaction {transaction}')
        if transaction.user_id == user_id:
            if transaction.amount < 1000:
                transaction.is_deleted = True

            break
    

reverse_latest_transaction('Cody')
reverse_latest_transaction('Jose')
print(f'After reverse:::: ')
cody_balance = calculate_user_balance('Cody')
print(f'Cody balance {cody_balance}')

cody_balance = calculate_user_balance('Jose')
print(f'Jose balance {cody_balance}')


