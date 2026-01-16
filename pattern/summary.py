from typing import List, Set, Dict

import csv

def read_csv(self, input_file: str) -> tuple[list[str], list[list[str]]]:
    try:
        with open(input_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            
            # Get the first line as headers
            headers = next(reader)
            
            # Get all remaining lines, filtering out empty ones
            # rows = [row for row in reader if any(cell.strip() for cell in row)]

            rows = []
            for row in reader:
                # This checks if the row actually has text (not just empty spaces or commas)
                if any(cell.strip() for cell in row):
                    rows.append(row)
            
            return headers, rows
            
    except Exception as e:
        raise Exception(f"Failed to read CSV: {e}")
    

def save_to_csv(filename, headers, data):
    try:
        # 'w' mode for writing (overwrites existing file)
        with open(filename, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # 1. Write the header row
            writer.writerow(headers)
            
            # 2. Write all data rows at once
            writer.writerows(data)
            
        print(f"Successfully created {filename}")
    except Exception as e:




def get_numbers() -> List[int]:
    return [1, 2, 3, 4]

def get_unique_words(text: str) -> Set[str]:
    return set(text.split())

def get_word_count(text: str) -> Dict[str, int]:
    words = text.split()
    return {word: words.count(word) for word in set(words)}



# Using ord
print(ord('A'))   # Output: 65
print(ord('€'))   # Output: 8364

# Using chr
print(chr(65))    # Output: 'A'
print(chr(8364))  # Output: '€'


# ======= custom error message =======
class MyCustomError(Exception):
    def __init__(self, message):
        super().__init__(message)

raise MyCustomError("This is a custom error message.")


class MyCustomeErro(Exception):
    def __init__(self, message):
        super().__init__(message)



            # Tuple of (headers, rows)


# ==========================
# Inheritance
class Animal:
    def speak(self):
        print("Animal speaks")

class Dog(Animal):
    def speak(self):
        print("Dog barks")

dog = Dog()
dog.speak()  # Output: Dog barks

# Polymorphism
class Cat(Animal):
    def speak(self):
        print("Cat meows")

def animal_sound(animal):
    animal.speak()

animal_sound(Dog())  # Output: Dog barks
animal_sound(Cat())  # Output: Cat meows
# ==========================
# Abstraction
from abc import ABC, abstractmethod

class Vehicle(ABC):
    @abstractmethod
    def drive(self):
        pass

class Car(Vehicle):
    def drive(self):
        print("Car is driving")

car = Car()
car.drive()  # Output: Car is driving

# Encapsulation

class BankAccount:
    def __init__(self, balance):
        self.__balance = balance  # Private attribute

    def deposit(self, amount):
        self.__balance += amount

    def withdraw(self, amount):
        if amount <= self.__balance:
            self.__balance -= amount
        else:
            print("Insufficient funds")

    def get_balance(self):
        return self.__balance

account = BankAccount(100)
account.deposit(50)
print(account.get_balance())  # Output: 150
account.withdraw(200)         # Output: Insufficient funds


# =============

user_scores = {"alice": 10, "bob": 15}

# Key exists
print(user_scores.get("alice", 0))  # Output: 10

# Key does not exist
print(user_scores.get("charlie", 0)) # Output: 0

from collections import defaultdict

# Every new key will automatically start with an empty list []
group_members = defaultdict(list)

group_members["admin"].append("Alice") 
# No KeyError! It created the list for "admin" on the fly.

print(group_members["admin"])  # Output: ['Alice']
print(group_members["guest"])  # Output: [] (automatically created)

# ==============
# sorted string => return list of characters in order

# >>> s = 'gwea'
# >>> b = sorted(s)
# >>> b
# ['a', 'e', 'g', 'w']





    # """Remove HTML tags from string"""
import re
re.sub(r'<[^>]+>', '', html)

text.find('substring') # returns -1 if not found
text.find('substring', 10) # start searching from index 10  
text.index('substring') # raises ValueError if not found