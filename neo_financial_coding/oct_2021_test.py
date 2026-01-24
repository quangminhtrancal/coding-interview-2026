#Q1: 

'''
Docstring for Coding interview.neo_financial_coding.oct_2021_test

Write a function:

class Solution { public int solution(int[] A); }

that, given an array A consisting of N integers, returns the sum of all integers which are multiples of 4.

For example, given array A as follows:

the function should return -16.

Assume that:

N is an integer within the range [1..1,000];
each element of array A is an integer within the range [-10,000..10,000];
there is at least one element in array A which satisfies the condition in the task statement.
In your solution, focus on correctness. The performance of your solution will not be the focus of the assessment.

'''

def solution(A):
    """
    This function takes an array of integers and returns the sum of all integers which are multiples of 4.

    :param A: List[int] - An array of integers
    :return: int - The sum of all integers in A that are multiples of 4
    """
    total = 0
    for number in A:
        if number % 4 == 0:
            total += number
    
    return total


#Q2:

'''
Examples:

Given S = "id,name,age,act,room,dep.\n1,Jack,68,T,13,8\n17,Betty,28,F,15,7" and C = "age", 
your function should return 68 since 68 is the maximum of 68 and 28.
+----+-------+-----+-----+------+-----+
| id | name  | age | act | room | dep |
+----+-------+-----+-----+------+-----+
| 1  | Jack  | 68  | T   | 13   | 8   |
| 17 | Betty | 28  | F   | 15   | 7   |
+----+-------+-----+-----+------+-----+

-----------------
Given S = "area,land\n3722,CN\n6612,RU\n3855,CA\n3797,USA" and C = "area",
your function should return 6612.

+------+------+
| area | land |
+------+------+
| 3722 | CN   |
| 6612 | RU   |
| 3855 | CA   |
| 3797 | USA  |
+------+------+

-----------------
Given S = "city,temp2,temp\nParis,7,-3\nDubai,4,-4\nPorto,-1,-2" and C = "temp",
your function should return -2.

+-------+-------+------+
| city  | temp2 | temp |
+-------+-------+------+
| Paris | 7     | -3   |
| Dubai | 4     | -4   |
| Porto | -1    | -2   |
+-------+-------+------+

Assume that:

S is a string of length N in CSV format;
N is an integer in the range [3..100,000];
M is an integer in the range [1..5];
there are at least two rows;
each row has the same, positive number of cells;
each cell is of length [1..5], and consists only of letters, digits and special characters: ',' and '.';
C is the name of a unique column in the table, whose values are integers within the range [-9999..9999]; there are no erroneous values in this column;
there is no new line at the end of string S.
In your solution, focus on correctness. The performance of your solution will not be the focus of the assessment.

'''
import csv
def solution_csv(S, C):
    """
    This function takes a CSV formatted string S and a column name C, and returns the maximum integer value in column C.

    :param S: str - A CSV formatted string
    :param C: str - The name of the column to find the maximum value from
    :return: int - The maximum integer value in column C
    """
    input_rows = S.split('\n')
    headers = input_rows[0].split(',')
    col_index = headers.index(C)

    max_value = float('-inf')

    for i in range(1, len(input_rows)):
        val = int(input_rows[i].split(',')[col_index])
        if val > max_value:
            max_value = val
    
    return max_value


def test_solution_csv():
    # Test case 1
    S1 = "id,name,age,act,room,dep.\n1,Jack,68,T,13,8\n17,Betty,28,F,15,7"
    C1 = "age"
    assert solution_csv(S1, C1) == 68

    # Test case 2
    S2 = "area,land\n3722,CN\n6612,RU\n3855,CA\n3797,USA"
    C2 = "area"
    assert solution_csv(S2, C2) == 6612

    # Test case 3
    S3 = "city,temp2,temp\nParis,7,-3\nDubai,4,-4\nPorto,-1,-2"
    C3 = "temp"
    assert solution_csv(S3, C3) == -2

    print("All test cases passed.")

# Q2 test
test_solution_csv()

#Q3
'''
You are given a list of all the transactions on a bank account during the year 2020. The account was empty at the beginning of the year (the balance was 0).

Each transaction specifies the amount and the date it was executed. If the amount is negative (i.e. less than 0) then it was a card payment, 
otherwise it was an incoming transfer (amount at least 0). 
The date of each transaction is in YYYY-MM-DD format: for example, 2020-05-20 represents 20th May 2020.

Additionally, there is a fee for having a card (omitted in the given transaction list), which is 5 per month. 
This fee is deducted from the account balance at the end of each month unless there were 
at least three payments made by card for a total cost of at least 100 within that month.

Your task is to compute the final balance of the account at the end of the year 2020.

Write a function:

class Solution { public int solution(int[] A, String[] D); }

that, given an array A of N integers representing transaction amounts and an array D of N strings representing transaction dates, 
returns the final balance of the account at the end of the year 2020. 
Transaction number K (for K within the range [0..N-1]) was executed on the date represented by D[K] for amount A[K].

Examples:

Given A = [100, 100, 100, -10] and D = ["2020-12-31", "2020-12-22", "2020-12-03", "2020-12-29"], the function should return 230. 
Total income was equal to 100 + 100 + 100 = 300, card payment = -10, so 290, and the fee was paid every month, so 290 - (5 * 12) = 230.

Given A = [180, -50, -25, -25] and D = ["2020-01-01", "2020-01-01", "2020-01-01", "2020-01-31"], the function should return 25. 
The income was equal to 180, the expenditure was equal to 100 and the fee was applied in every month except January: 180 - 100 - (5 * 11) = 25.

Given A = [1, -1, 0, 105, 1] and D = ["2020-12-31", "2020-04-04", "2020-04-14", "2020-04-04", "2020-07-12"], the function should return -164. 
The fee is paid every month. 1 + 1 + 0 + 105 + 1 - (5 * 12) = -164. Note that in April, even though the total cost of card payments was 106 (more than 100), 
there were only two payments made by card, so the fee was still applied. A transaction of value 0 is considered a positive, incoming transfer.

Given A = [100, 100, -10, 20, -30] and D = ["2020-01-01", "2020-02-01", "2020-02-11", "2020-02-05", "2020-02-08"], the function should return 80.

Assume that:

N is an integer within the range [1..100].
each element of array A is an integer within the range [-1,000..1,000];
D contains strings in YYYY-MM-DD format, representing a date in the range 2020-01-01 to 2020-12-31.
In your solution, focus on correctness. The performance of your solution will not be the focus of the assessment.

'''

def solution_transactions(A, D):
    """
    This function calculates the final balance of a bank account at the end of the year 2020,
    given a list of transactions and their corresponding dates.

    :param A: List[int] - An array of transaction amounts
    :param D: List[str] - An array of transaction dates in YYYY-MM-DD format
    :return: int - The final balance of the account at the end of the year 2020
    """
    from collections import defaultdict

    monthly_card_payments = defaultdict(lambda: {'count': 0, 'total': 0})
    balance = 0

    for amount, date in zip(A, D):
        month = date[5:7]  # Extract month from date string
        balance += amount

        if amount < 0:  # Card payment
            monthly_card_payments[month]['count'] += 1
            monthly_card_payments[month]['total'] += -amount  # Store as positive value

    for month in range(1, 13):
        month_str = f"{month:02d}"
        payments_info = monthly_card_payments[month_str]
        if payments_info['count'] < 3 or payments_info['total'] < 100:
            balance -= 5  # Deduct fee

    return balance


