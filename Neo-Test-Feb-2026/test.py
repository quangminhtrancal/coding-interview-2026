from collections import defaultdict
'''
credit card transaction system
1) define structure to store credit transaction (user, amount)

Cody 900.10
Jose 200.10
Jose 300.70
Cody 1000.20
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


