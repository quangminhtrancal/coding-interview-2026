'''
nahh I don’t, level 1-3 were basically the same but 4 was different. 
Mine was that I had create a banking system that stores accounts. 
The first level was creating a create account, transferring money to another account, depositing money. 
The second level was seeing the highest k accounts based on their balances. The 3 was dealing a merge of accounts. 

The 4 was different cuz it dealt with scheduling transfers and making sure in the original methods created, 
any scheduled transfers would happen first(used a helper). I finished it all, besides the last one. I didn’t get all the hidden test passed.

2.2 Banking System Problem
Problem Overview
Design a banking system with progressive complexity:

Level 1: Account creation, deposits, transfers
Level 2: Most active users tracking
Level 3: Pay and cashback system
Level 4: Account merging


'''


class BankingSystem:
    def __init__(self):
        self.accounts = {} # account_id -> balance
        self.transaction_counts = {} # account_id -> outgoing transaction count
        self.pending_cashbacks = {} # payment_id -> {amount, timestamp, account}
        self.payment_counter = 0

    def create_account(self, timestamp, account_id, initial_balance=0):
        if account_id in self.accounts:
            return "false" # Account already exists
        
        self.accounts[account_id] = float(initial_balance)
        self.transaction_counts[account_id] = 0
        return str(int(self.accounts[account_id]))
    
    def deposit(self, timestamp, account_id, amount):
        if account_id not in self.accounts:
            return "" # Account doesn't exist
        self.accounts[account_id] += float(amount)
        return str(int(self.accounts[account_id]))
    
    def transfer(self, timestamp, from_account, to_account, amount):
        amount = float(amount) 

        # Validation
        if (from_account not in self.accounts or to_account not in self.accounts or from_account == to_account or
            self.accounts[from_account] < amount):
            return ""
        
        # Perform transfer
        self.accounts[from_account] -= amount
        self.accounts[to_account] += amount
        self.transaction_counts[from_account] += 1
        return str(int(self.accounts[from_account]))
    
    def top_activity(self, timestamp, n):
        n = int(n)
        if not self.transaction_counts:
            return ""
        
        # Sort by transaction count (desc), then by account_id (asc)
        sorted_accounts = sorted(
        [(acc, count) for acc, count in self.transaction_counts.items() if count > 0],
            key=lambda x: (-x[1], x[0]))
        
        top_accounts = sorted_accounts[:n]
        
        result = ", ".join([f"{acc}({count})" for acc, count in
        top_accounts])
        return result
    
    def pay(self, timestamp, account_id, amount):
        amount = float(amount)
        if (account_id not in self.accounts or
            self.accounts[account_id] < amount):
            return ""
        
        self.accounts[account_id] -= amount
        self.transaction_counts[account_id] += 1
        # Schedule cashback (2% after 24 hours)
        self.payment_counter += 1
        payment_id = f"payment_{self.payment_counter}"
        cashback_amount = amount * 0.02

        self.pending_cashbacks[payment_id] = {
            'amount': cashback_amount,
            'timestamp': timestamp + 86400, # 24 hours later
            'account': account_id
        }
        return str(int(self.accounts[account_id]))
    
    def process_pending_cashbacks(self, current_timestamp):
        """Process all cashbacks that are due"""
        to_remove = []
        for payment_id, cashback in self.pending_cashbacks.items():
            if current_timestamp >= cashback['timestamp']:
                self.accounts[cashback['account']] += cashback['amount']

        to_remove.append(payment_id)
        for payment_id in to_remove:
            del self.pending_cashbacks[payment_id]

# ======================= GEMINI =======================
import heapq

class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, i):
        # If the account is new, it's its own parent
        if i not in self.parent:
            self.parent[i] = i
            return i
        # Path compression: point node directly to the root
        if self.parent[i] != i:
            self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            # Merge root of j into root of i
            self.parent[root_j] = root_i
            return True
        return False

class BankSystem:
    def __init__(self):
        self.balances = {}  # root_id -> balance
        self.uf = UnionFind()
        self.scheduled = [] # Min-heap: (timestamp, from_id, to_id, amount)

    def _get_root(self, acc_id):
        return self.uf.find(acc_id)

    def _process_scheduled(self, current_time):
        """Level 4 Helper: Must be called at the start of every method."""
        while self.scheduled and self.scheduled[0][0] <= current_time:
            ts, f_id, t_id, amt = heapq.heappop(self.scheduled)
            self.transfer(f_id, t_id, amt, ts, is_scheduled=True)

    # Level 1: Basic Ops
    def deposit(self, acc_id, amount, timestamp):
        self._process_scheduled(timestamp)
        root = self._get_root(acc_id) 
        self.balances[root] = self.balances.get(root, 0) + amount
        return self.balances[root]

    def transfer(self, from_id, to_id, amount, timestamp, is_scheduled=False):
        if not is_scheduled:
            self._process_scheduled(timestamp)
            
        root_from = self._get_root(from_id)
        root_to = self._get_root(to_id)
        
        if self.balances.get(root_from, 0) >= amount:
            self.balances[root_from] -= amount
            self.balances[root_to] = self.balances.get(root_to, 0) + amount
            return True
        return False

    # --- UPDATED LEVEL 2: Top K using Heap ---
    def get_top_k(self, k, timestamp):
        self._process_scheduled(timestamp)
        
        # We need to return IDs. 
        # Criteria: Highest balance first. 
        # Tie-break: Lexicographical order of ID (smallest ID first).
        
        # We use a custom key for nlargest:
        # (balance, -id) because nlargest finds the "maximums".
        # To get smallest ID in a tie, we negate the ID string comparison 
        # or handle it via a custom wrapper if IDs are complex.
        
        # Simplified for standard CodeSignal rules:
        top_k_items = heapq.nlargest(
            k, 
            self.balances.items(), 
            key=lambda x: (x[1], [ord(c) * -1 for c in x[0]]) # Balance desc, ID asc
        )
        
        return [item[0] for item in top_k_items]

    # Level 3: Merge
    def merge_accounts(self, acc_id1, acc_id2, timestamp):
        self._process_scheduled(timestamp)
        root1 = self._get_root(acc_id1)
        root2 = self._get_root(acc_id2)
        
        if root1 != root2:
            # Move balance from root2 to root1
            self.balances[root1] = self.balances.get(root1, 0) + self.balances.get(root2, 0)
            self.balances[root2] = 0
            self.uf.union(root1, root2)
        return True

    # Level 4: Scheduling
    def schedule_transfer(self, from_id, to_id, amount, exec_time, current_time):
        self._process_scheduled(current_time)
        # Just push to heap; don't execute yet
        heapq.heappush(self.scheduled, (exec_time, from_id, to_id, amount))
        return "SCHEDULED"
    

'''
https://leetcode.com/discuss/post/5121903/dropbox-online-assessment-banking-syste-tw95w/

Build a python class for a banking system
Level 1: Support creating new accounts, depositing money into accounts, and transferring money between two accounts.
Level 2: Ranking accounts (i.e top_spenders) based on outgoing transactions.
Level 3: The banking system should allow scheduling payments with cashback 
        (2% cashback deposited to account 24 hours after transaction) and checking the status of scheduled payments .
Level 4: The banking system should support merging two accounts while retaining both accounts' balance and transaction histories.

It's important to read the whole question, since in Level 4 it says "retain transaction histories" while you can get away with doing all 
Level 1 and 2 and 3 without building any construct of a transaction history.

That's where they got me.

Signatures of functions are

create_account(timestamp : int, account : str) -> str
deposit(timestamp : int, account : str, amount : int) -> str
transfer(timestamp : int, account1 : str, account2 : str amount : int) -> str
top_spenders(timestamp : int, n : int) -> str
pay(timestamp : int, account : str, amount : int) -> str (returns payment_id)
check_payment_status(timestamp : int, account : str, payment_id : str) -> returns "IN_PROGRESS", "CASHBACK_COMPLETED"
merge_account(timestamp : int, account1 : str, account2 : str) -> str
get_balance(timestamp : int, account : str, time_at : str) -> str
		this should support an account that might've been merged

For Level 1 and Level 2 timestamp is not even necessary, but it becomes important for level 3 and level 4
'''

import heapq
from bisect import bisect_right

class BankSystem:
    def __init__(self):
        # account_id -> [[timestamp, balance_change, cumulative_balance], ...]
        self.history = {} 

        # account_id -> total_outgoing (for Level 2 Top Spenders)
        self.outgoing = {}

        # account_id -> root_account_id (Union-Find for Level 4)
        self.parents = {}

        # payment_id -> {status, amount, account, execute_at}
        self.scheduled_payments = {}

        # Heap for Level 3: (timestamp, payment_id)
        self.cashback_queue = []

        self.payment_counter = 0

    def _get_root(self, account_id):
        if account_id not in self.parents:
            return None
        
        if self.parents[account_id] == account_id:
            return account_id
        
        self.parents[account_id] = self._get_root(self.parents[account_id])
        return self.parents[account_id]

    def _update_history(self, account_id, amount_change, timestamp):
        root = self._get_root(account_id)

        if not self.history[root]:
            new_balance = amount_change
        else:
            new_balance = self.history[root][-1][2] + amount_change
        self.history[root].append([timestamp, amount_change, new_balance])

    def _process_cashback(self, current_time):
        """Processes scheduled 2% cashback exactly 24h (86400s) later."""
        while self.cashback_queue and self.cashback_queue[0][0] <= current_time:
            exec_ts, pay_id = heapq.heappop(self.cashback_queue)
            payment = self.scheduled_payments[pay_id]
            # 2% Cashback logic
            cashback_amt = int(payment['amount'] * 0.02)
            self._update_history(payment['account'], cashback_amt, exec_ts)
            payment['status'] = "CASHBACK_COMPLETED"

    # --- Level 1 ---
    def create_account(self, timestamp, account):

        self._process_cashback(timestamp)
        if account in self.parents:
            return "false"
        
        self.parents[account] = account
        self.history[account] = [[timestamp, 0, 0]]
        self.outgoing[account] = 0
        return "true"

    def deposit(self, timestamp, account, amount):
        self._process_cashback(timestamp)
        root = self._get_root(account)
        if not root:
            return ""
        self._update_history(root, amount, timestamp)
        return str(self.history[root][-1][2])

    def transfer(self, timestamp, account1, account2, amount):
        self._process_cashback(timestamp)
        root1 = self._get_root(account1)
        root2 = self._get_root(account2)
        if not root1 or not root2 or root1 == root2:
            return "false"
        
        if self.history[root1][-1][2] < amount:
            return "false"
        
        self._update_history(root1, -amount, timestamp)
        self._update_history(root2, amount, timestamp)
        self.outgoing[root1] = self.outgoing.get(root1, 0) + amount
        return "true"

    # --- Level 2 ---
    def top_spenders(self, timestamp, n):
        self._process_cashback(timestamp)
        # Sort by outgoing (desc), then account_id (asc)
        sorted_spenders = heapq.nlargest(
            n, 
            self.outgoing.items(), 
            key=lambda x: (x[1], [ord(c)*-1 for c in x[0]])
        )
        return ", ".join([f"{s[0]}({s[1]})" for s in sorted_spenders])

    # --- Level 3 ---
    def pay(self, timestamp, account, amount):
        self._process_cashback(timestamp)
        root = self._get_root(account)
        if not root or self.history[root][-1][2] < amount:
            return ""
        
        self.payment_counter += 1
        pay_id = f"pay{self.payment_counter}"
        
        self._update_history(root, -amount, timestamp)
        self.outgoing[root] = self.outgoing.get(root, 0) + amount
        
        self.scheduled_payments[pay_id] = {
            'status': "IN_PROGRESS", 
            'amount': amount, 
            'account': root,
            'ts': timestamp
        }
        # Schedule cashback for timestamp + 24 hours (86400 seconds)
        heapq.heappush(self.cashback_queue, (timestamp + 86400, pay_id))
        return pay_id

    def check_payment_status(self, timestamp, account, payment_id):
        self._process_cashback(timestamp)
        if payment_id not in self.scheduled_payments:
            return ""
        return self.scheduled_payments[payment_id]['status']

    # --- Level 4 ---
    def merge_account(self, timestamp, account1, account2):
        self._process_cashback(timestamp)
        root1 = self._get_root(account1)
        root2 = self._get_root(account2)
        if not root1 or not root2 or root1 == root2:
            return "false"
        
        # Merge logic: everything from root2 goes into root1
        new_balance = self.history[root1][-1][2] + self.history[root2][-1][2]
        self.history[root1].append([timestamp, self.history[root2][-1][2], new_balance])
        
        # Merge spending history
        self.outgoing[root1] = self.outgoing.get(root1, 0) + self.outgoing.get(root2, 0)
        
        # Point root2 to root1
        self.parents[root2] = root1
        # Clear root2's active status but keep history reachable via root1
        return "true"

    def get_balance(self, timestamp, account, time_at):
        self._process_cashback(timestamp)
        # Note: time_at is a string in the signature, convert to int
        t_at = int(time_at)
        root = self._get_root(account)
        if not root:
            return ""
        
        # Binary search on history to find balance at t_at
        hist = self.history[root]
        idx = bisect_right(hist, [t_at, float('inf'), float('inf')]) - 1
        
        if idx >= 0:
            return str(hist[idx][2])
        return "0"
    
    #=================== BETTER SOLUTION ===================

import heapq
from bisect import bisect_right
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class HistoryEntry:
    timestamp: int
    change: int
    balance: int

    # This magic method allows bisect_right(history, (target_ts, ...))
    # to compare target_ts against self.timestamp automatically.
    def __getitem__(self, index):
        return (self.timestamp, self.change, self.balance)[index]

@dataclass(order=True)
class CashbackTask:
    execute_at: int
    payment_id: str = field(compare=False) # Only sort by execute_at

class BankSystem:
    def __init__(self):
        self.history: Dict[str, List[HistoryEntry]] = {}
        self.parents: Dict[str, str] = {}
        self.outgoing: Dict[str, int] = {}
        self.scheduled_payments = {}
        self.cashback_queue: List[CashbackTask] = []
        self.payment_counter = 0

    def _get_root(self, account_id: str) -> str:
        if account_id not in self.parents:
            return None
        if self.parents[account_id] == account_id:
            return account_id
        # Path compression for efficiency
        self.parents[account_id] = self._get_root(self.parents[account_id])
        return self.parents[account_id]

    def _process_cashback(self, current_time: int):
        while self.cashback_queue and self.cashback_queue[0].execute_at <= current_time:
            task = heapq.heappop(self.cashback_queue)
            pay_info = self.scheduled_payments[task.payment_id]
            
            cashback_amt = int(pay_info['amount'] * 0.02)
            root = self._get_root(pay_info['account'])
            self._add_to_history(root, cashback_amt, task.execute_at)
            pay_info['status'] = "CASHBACK_COMPLETED"

    def _add_to_history(self, root_id: str, amount: int, timestamp: int):
        current_bal = self.history[root_id][-1].balance if self.history[root_id] else 0
        new_entry = HistoryEntry(timestamp, amount, current_bal + amount)
        self.history[root_id].append(new_entry)

    def create_account(self, timestamp: int, account: str) -> str:
        self._process_cashback(timestamp)
        if account in self.parents:
            return "false"
        self.parents[account] = account
        self.history[account] = [HistoryEntry(timestamp, 0, 0)]
        self.outgoing[account] = 0
        return "true"

    def deposit(self, timestamp: int, account: str, amount: int) -> str:
        self._process_cashback(timestamp)
        root = self._get_root(account)
        if not root: return ""
        self._add_to_history(root, amount, timestamp)
        return str(self.history[root][-1].balance)

    def transfer(self, timestamp: int, acc1: str, acc2: str, amount: int) -> str:
        self._process_cashback(timestamp)
        r1, r2 = self._get_root(acc1), self._get_root(acc2)
        if not r1 or not r2 or r1 == r2 or self.history[r1][-1].balance < amount:
            return "false"
        
        self._add_to_history(r1, -amount, timestamp)
        self._add_to_history(r2, amount, timestamp)
        self.outgoing[r1] = self.outgoing.get(r1, 0) + amount
        return "true"

    def top_spenders(self, timestamp: int, n: int) -> str:
        self._process_cashback(timestamp)
        # Use nlargest for O(N log K) efficiency
        top = heapq.nlargest(
            n, 
            self.outgoing.items(), 
            key=lambda x: (x[1], [ord(c)*-1 for c in x[0]])
        )
        return ", ".join([f"{name}({amt})" for name, amt in top])

    def pay(self, timestamp: int, account: str, amount: int) -> str:
        self._process_cashback(timestamp)
        root = self._get_root(account)
        if not root or self.history[root][-1].balance < amount:
            return ""
        
        self.payment_counter += 1
        p_id = f"pay{self.payment_counter}"
        self._add_to_history(root, -amount, timestamp)
        self.outgoing[root] += amount
        
        self.scheduled_payments[p_id] = {'status': "IN_PROGRESS", 'amount': amount, 'account': account}
        heapq.heappush(self.cashback_queue, CashbackTask(timestamp + 86400, p_id))
        return p_id

    def check_payment_status(self, timestamp: int, account: str, payment_id: str) -> str:
        self._process_cashback(timestamp)
        if payment_id not in self.scheduled_payments: return ""
        return self.scheduled_payments[payment_id]['status']

    def merge_account(self, timestamp: int, acc1: str, acc2: str) -> str:
        self._process_cashback(timestamp)
        r1, r2 = self._get_root(acc1), self._get_root(acc2)
        if not r1 or not r2 or r1 == r2: return "false"
        
        # Merge balance and spending
        bal2 = self.history[r2][-1].balance
        self._add_to_history(r1, bal2, timestamp)
        self.outgoing[r1] += self.outgoing.get(r2, 0)
        self.parents[r2] = r1 # Union
        return "true"

    def get_balance(self, timestamp: int, account: str, time_at: str) -> str:
        self._process_cashback(timestamp)
        root = self._get_root(account)
        if not root: return ""
        
        target_t = int(time_at)
        hist = self.history[root]
        
        # --- HERE IS WHERE __getitem__ IS USED ---
        # bisect_right looks at hist[mid], calls hist[mid].__getitem__(0) 
        # to get the timestamp, and compares it to target_t.
        
        idx = bisect_right(hist, (target_t, float('inf'), float('inf'))) - 1
        
        return str(hist[idx].balance) if idx >= 0 else "0"
    

# =========== EASIER no get_item ==============

import heapq
from bisect import bisect_right

class HistoryEntry:
    def __init__(self, timestamp, balance):
        self.timestamp = timestamp
        self.balance = balance

class Account:
    def __init__(self, account_id, timestamp):
        self.account_id = account_id
        # History stores the balance state at various timestamps
        self.history = [HistoryEntry(timestamp, 0)]
        self.outgoing = 0
        # For Level 4: Points to self by default; points to another Account if merged
        self.parent = self 

    def get_root(self):
        """Finds the ultimate active account (Union-Find Find)."""
        if self.parent == self:
            return self
        # Path compression: point directly to the root for speed
        self.parent = self.parent.get_root()
        return self.parent

    def add_history(self, timestamp, amount):
        """Update balance and record it in history."""
        # Note: This should be called on the ROOT account
        new_balance = self.history[-1].balance + amount
        self.history.append(HistoryEntry(timestamp, new_balance))

    def get_balance_at(self, time_at):
        """Binary search to find the balance at a specific point in time."""
        target_t = int(time_at)
        # Find the last entry where entry.timestamp <= target_t
        idx = bisect_right(self.history, target_t, key=lambda x: x.timestamp) - 1
        return self.history[idx].balance if idx >= 0 else 0

class BankSystem:
    def __init__(self):
        self.accounts = {} # account_id -> Account object
        self.scheduled_payments = {}
        self.cashback_queue = [] # Min-heap: (execute_at, payment_id)
        self.pay_count = 0

    def _process_cashback(self, current_time):
        while self.cashback_queue and self.cashback_queue[0][0] <= current_time:
            exec_ts, p_id = heapq.heappop(self.cashback_queue)
            pay_info = self.scheduled_payments[p_id]
            
            root = self.accounts[pay_info['account']].get_root()
            cashback = int(pay_info['amount'] * 0.02)
            root.add_history(exec_ts, cashback)
            pay_info['status'] = "CASHBACK_COMPLETED"

    def create_account(self, timestamp, account_id):
        self._process_cashback(timestamp)
        if account_id in self.accounts: return "false"
        self.accounts[account_id] = Account(account_id, timestamp)
        return "true"

    def deposit(self, timestamp, account_id, amount):
        self._process_cashback(timestamp)
        if account_id not in self.accounts: return ""
        root = self.accounts[account_id].get_root()
        root.add_history(timestamp, amount)
        return str(root.history[-1].balance)

    def transfer(self, timestamp, acc1, acc2, amount):
        self._process_cashback(timestamp)
        if acc1 not in self.accounts or acc2 not in self.accounts: return "false"
        
        r1, r2 = self.accounts[acc1].get_root(), self.accounts[acc2].get_root()
        if r1 == r2 or r1.history[-1].balance < amount: return "false"
        
        r1.add_history(timestamp, -amount)
        r2.add_history(timestamp, amount)
        r1.outgoing += amount
        return "true"

    def top_spenders(self, timestamp, n):
        self._process_cashback(timestamp)
        # Level 2 Logic: Get outgoing from all root accounts
        # Note: We only count accounts that are 'roots' to avoid double counting
        spender_data = []
        for acc in self.accounts.values():
            if acc.parent == acc: # Only roots hold the combined 'outgoing' total
                spender_data.append((acc.account_id, acc.outgoing))
        
        top = heapq.nlargest(
            n, 
            spender_data, 
            key=lambda x: (x[1], [ord(c)*-1 for c in x[0]])
        )
        
        return ", ".join([f"{name}({amt})" for name, amt in top])

    def pay(self, timestamp, account_id, amount):
        self._process_cashback(timestamp)
        if account_id not in self.accounts: return ""
        root = self.accounts[account_id].get_root()
        
        if root.history[-1].balance < amount: return ""
        
        self.pay_count += 1
        p_id = f"pay{self.pay_count}"
        root.add_history(timestamp, -amount)
        root.outgoing += amount
        
        self.scheduled_payments[p_id] = {'status': "IN_PROGRESS", 'amount': amount, 'account': account_id}
        heapq.heappush(self.cashback_queue, (timestamp + 86400, p_id))
        return p_id

    def check_payment_status(self, timestamp, account_id, p_id):
        self._process_cashback(timestamp)
        return self.scheduled_payments.get(p_id, {}).get('status', "")

    def merge_account(self, timestamp, acc1, acc2):
        self._process_cashback(timestamp)
        if acc1 not in self.accounts or acc2 not in self.accounts: return "false"
        
        r1, r2 = self.accounts[acc1].get_root(), self.accounts[acc2].get_root()
        if r1 == r2: return "false"
        
        # Merge balance of r2 into r1
        bal2 = r2.history[-1].balance
        r1.add_history(timestamp, bal2)
        r1.outgoing += r2.outgoing
        
        # Link r2 to r1 (Union)
        r2.parent = r1
        return "true"

    def get_balance(self, timestamp, account_id, time_at):
        self._process_cashback(timestamp)
        if account_id not in self.accounts: return ""
        # Level 4 requirement: account ID might have been merged
        # But we search history based on the root
        root = self.accounts[account_id].get_root()
        return str(root.get_balance_at(time_at))

def run_bank_system_tests():
    bank = BankSystem()
    
    print("--- Level 1: Basic Operations ---")
    # T=1: Create accounts
    print("Create user_a:", bank.create_account(1, "user_a")) # true
    print("Create user_b:", bank.create_account(2, "user_b")) # true
    
    # T=3: Deposits
    print("Deposit 100 to user_a:", bank.deposit(3, "user_a", 100)) # 100
    
    # T=5: Transfer
    print("Transfer 40 from a to b:", bank.transfer(5, "user_a", "user_b", 40)) # true
    print("Balance user_a at T=6:", bank.get_balance(6, "user_a", "6")) # 60
    print("Balance user_b at T=6:", bank.get_balance(6, "user_b", "6")) # 40

    print("\n--- Level 2: Top Spenders ---")
    # Current Outgoing: user_a: 40, user_b: 0
    bank.create_account(10, "user_c")
    bank.deposit(11, "user_c", 200)
    bank.transfer(12, "user_c", "user_b", 150)
    
    # Top 2 spenders: user_c (150), user_a (40)
    print("Top 2 Spenders:", bank.top_spenders(15, 2)) # "user_c(150), user_a(40)"

    print("\n--- Level 3: Scheduled Payments & Cashback ---")
    # user_c balance is 50. 
    # Pay 100 (should fail)
    print("Pay 100 from user_c (insufficient):", bank.pay(20, "user_c", 100)) # ""
    
    # Pay 50 (should succeed)
    pay_id = bank.pay(25, "user_c", 50)
    print(f"Pay 50 from user_c: {pay_id}") # pay1
    print("Status at T=26:", bank.check_payment_status(26, "user_c", pay_id)) # IN_PROGRESS
    
    # Check balance at T=26 (should be 0)
    print("User_c balance at T=26:", bank.get_balance(26, "user_c", "26")) # 0
    
    # Move time forward 24 hours (86400 seconds)
    # T = 25 + 86400 = 86425
    print("Status at T=86425 (Cashback triggered):", bank.check_payment_status(86425, "user_c", pay_id)) # CASHBACK_COMPLETED
    # 2% of 50 is 1. New balance should be 1
    print("User_c balance at T=86426:", bank.get_balance(86426, "user_c", "86426")) # 1

    print("\n--- Level 4: Merging & History Reconstruction ---")
    bank.create_account(90000, "user_d")
    bank.deposit(90001, "user_d", 500) # user_d has 500
    
    # Balance of user_a is currently 60
    # Merge user_d into user_a at T=95000
    print("Merge user_d into user_a:", bank.merge_account(95000, "user_a", "user_d")) # true
    
    # Current balance of merged account user_a
    print("Merged balance (60 + 500):", bank.get_balance(95001, "user_a", "95001")) # 560
    
    # CRITICAL TEST: Reconstruction of history
    # Checking balance of "user_d" at a time BEFORE the merge
    print("Balance of user_d at T=90005 (pre-merge):", bank.get_balance(95005, "user_d", "90005")) # 500
    
    # Checking balance of "user_a" at a time BEFORE it absorbed user_d
    print("Balance of user_a at T=90005 (pre-merge):", bank.get_balance(95005, "user_a", "90005")) # 60

    print("\n--- Final Integrity Check ---")
    # Transfer to a merged account ID should route to the root
    bank.deposit(100000, "user_b", 100)
    bank.transfer(100001, "user_b", "user_d", 50) # Transfers to d, which is now a
    print("Balance user_a after transfer to user_d:", bank.get_balance(100005, "user_a", "100005")) # 610

if __name__ == "__main__":
    run_bank_system_tests()