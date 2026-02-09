# Creational pattern
# Factory method

from abc import ABC, abstractmethod

class Notification(ABC):
    @abstractmethod
    def send(self, message):
        pass

class EmailNotification(Notification):
    def send(self, message):
        print(f'Send email notification: {message}')

class SMSNotification(Notification):
    def send(self, message):
        print(f'Send SNS Notification: {message}')

class NotificationFactory:
    @staticmethod
    def create(type):
        match type:
            case "email":
                return EmailNotification()
            case "sns":
                return SMSNotification()
            case _:
                raise ValueError('Invalid type')

notification = NotificationFactory.create('email')
notification.send('hello')

# unexisting_notification = NotificationFactory.create('unknown')

################## Builder
class HttpRequest:
    def __init__(self):
        self.headers = {}
        self.url = None
        self.method = None
        self.body = None
    
    class Builder():
        def __init__(self):
            self.request = HttpRequest()
        
        def with_url(self, url):
            self.request.url = url
            return self
        
        def with_method(self, method):
            self.request.method = method
            return self
        
        def with_body(self, body):
            self.request.body = body
            return self
        
        def build(self):
            return self.request

# singleton with concurrency
import threading
class DB:
    _instance = None
    def __new__(cls):
        if cls._instance == None:
            with threading.Lock():
                if cls._instance == None:
                    cls._instance = super().__new__(cls)

        return cls._instance

    def query(self, sql):
        print(f'query {sql}')

db = DB()
db.query('SELECT') 

'''
######################## STRUCTURAL
'''

################## Decorator
from abc import ABC, abstractmethod

# NOTE: This is the Decorator design pattern, which is different from Python's
# @decorator syntax. The naming can be confusing since Python decorators (with @)
# are a language feature for function/class modification, while this is an
# object composition pattern for adding behavior at runtime.

class DataSource(ABC):
    @abstractmethod
    def write_data(self, data: str) -> None:
        pass

    @abstractmethod
    def read_data(self) -> str:
        pass

class FileDataSource(DataSource):
    def __init__(self, filename: str):
        self.filename = filename

    def write_data(self, data: str) -> None:
        # Write to file
        pass

    def read_data(self) -> str:
        # Read from file
        return "data from file"

class EncryptionDecorator(DataSource):
    def __init__(self, source: DataSource):
        self._wrapped = source

    def write_data(self, data: str) -> None:
        encrypted = self._encrypt(data)
        self._wrapped.write_data(encrypted)  # Delegate to wrapped object

    def read_data(self) -> str:
        data = self._wrapped.read_data()
        return self._decrypt(data)

    def _encrypt(self, data: str) -> str:
        return f"encrypted:{data}"

    def _decrypt(self, data: str) -> str:
        return data.replace("encrypted:", "")

class CompressionDecorator(DataSource):
    def __init__(self, source: DataSource):
        self._wrapped = source

    def write_data(self, data: str) -> None:
        compressed = self._compress(data)
        self._wrapped.write_data(compressed)  # Delegate to wrapped object

    def read_data(self) -> str:
        data = self._wrapped.read_data()
        return self._decompress(data)

    def _compress(self, data: str) -> str:
        return f"compressed:{data}"

    def _decompress(self, data: str) -> str:
        return data.replace("compressed:", "")

# Usage
source = FileDataSource("data.txt")
source = EncryptionDecorator(source)
source = CompressionDecorator(source)
source.write_data("sensitive info")
# Data gets compressed, then encrypted, then written to file


################## Facade
from enum import Enum

class GameState(Enum):
    IN_PROGRESS = 1
    WON = 2
    DRAW = 3

class Board: # This is the facade class to abstract away logic from Game object
    def place_mark(self, row: int, col: int, mark: str) -> bool:
        # Place mark logic
        return True

    def check_win(self, row: int, col: int) -> bool:
        # Check win logic
        return False

    def is_full(self) -> bool:
        # Check if board is full
        return False

class Player:
    def __init__(self, mark: str):
        self.mark = mark

    def get_mark(self) -> str:
        return self.mark

class Game:
    def __init__(self):
        self.board = Board()
        self.player_x = Player("X")
        self.player_o = Player("O")
        self.current_player = self.player_x
        self.state = GameState.IN_PROGRESS

    def make_move(self, row: int, col: int) -> bool:
        # Coordinates board, player, and state logic
        # Caller doesn't need to understand internal details
        if self.state != GameState.IN_PROGRESS:
            return False
        if not self.board.place_mark(row, col, self.current_player.get_mark()):
            return False

        if self.board.check_win(row, col):
            self.state = GameState.WON
        elif self.board.is_full():
            self.state = GameState.DRAW
        else:
            self.current_player = (
                self.player_o if self.current_player == self.player_x
                else self.player_x
            )
        return True

# Usage - simple interface hides all the coordination
game = Game()
game.make_move(0, 0)
game.make_move(1, 1)


################# ADAPTER
from abc import ABC, abstractmethod

# 1. The Target Interface (What our app expects)
class NotificationTarget(ABC):
    @abstractmethod
    def send_alert(self, user_id: str, message: str):
        pass

# 2. The Adaptee (The Incompatible Library)
class SlackClient:
    """The 3rd party SDK we cannot change."""
    def post_message_to_channel(self, channel_name: str, text: str):
        print(f"Slack [Channel: {channel_name}]: {text}")

# 3. The Adapter
class SlackNotificationAdapter(NotificationTarget):
    def __init__(self, slack_client: SlackClient, channel_map: dict):
        self.slack_client = slack_client
        self.channel_map = channel_map

    def send_alert(self, user_id: str, message: str):
        # The Adapter performs the "Translation" logic
        # Mapping a User ID to a specific Slack Channel
        target_channel = self.channel_map.get(user_id, "#general")
        
        # Call the incompatible method
        self.slack_client.post_message_to_channel(target_channel, message)

# 4. Use in the Business Logic
class BookingEngine:
    def __init__(self, notifier: NotificationTarget):
        self.notifier = notifier

    def complete_booking(self, user_id):
        # High-level logic stays clean
        self.notifier.send_alert(user_id, "Your lodging is confirmed!")

# --- Execution ---
slack_sdk = SlackClient()
# We configure the adapter with the necessary mapping
adapter = SlackNotificationAdapter(slack_sdk, {"user_123": "#ops-alerts"})

engine = BookingEngine(adapter)
engine.complete_booking("user_123")


'''
######################## BEHAVIOR PATTERN
''' 
#############################3 Strategy
from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> bool:
        pass

class CreditCardPayment(PaymentStrategy):
    def __init__(self, card_number: str):
        self.card_number = card_number

    def pay(self, amount: float) -> bool:
        # Credit card processing logic
        print(f"Paid {amount} with credit card")
        return True

class PayPalPayment(PaymentStrategy):
    def __init__(self, email: str):
        self.email = email

    def pay(self, amount: float) -> bool:
        # PayPal processing logic
        print(f"Paid {amount} with PayPal")
        return True

class ShoppingCart:
    def __init__(self):
        self.payment_strategy = None

    def set_payment_strategy(self, strategy: PaymentStrategy) -> None:
        self.payment_strategy = strategy

    def checkout(self, amount: float) -> None:
        self.payment_strategy.pay(amount)

# Usage
cart = ShoppingCart()

cart.set_payment_strategy(CreditCardPayment("1234-5678"))
cart.checkout(100.00)

cart.set_payment_strategy(PayPalPayment("user@example.com"))
cart.checkout(50.00)


# Observer
from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self, symbol: str, price: float) -> None:
        pass

class Subject(ABC):
    @abstractmethod
    def attach(self, observer: Observer) -> None:
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        pass

    @abstractmethod
    def notify_observers(self) -> None:
        pass

class Stock(Subject):
    def __init__(self, symbol: str):
        self._observers: list[Observer] = []
        self.symbol = symbol
        self.price = 0.0

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def set_price(self, price: float) -> None:
        self.price = price
        self.notify_observers()  # Price changed, tell everyone

    def notify_observers(self) -> None:
        for observer in self._observers:
            observer.update(self.symbol, self.price)

class PriceDisplay(Observer):
    def update(self, symbol: str, price: float) -> None:
        print(f"Display updated: {symbol} = ${price}")

class PriceAlert(Observer):
    def __init__(self, threshold: float):
        self.threshold = threshold

    def update(self, symbol: str, price: float) -> None:
        if price > self.threshold:
            print(f"Alert! {symbol} exceeded ${self.threshold}")

# Usage
stock = Stock("AAPL")

display = PriceDisplay()
alert = PriceAlert(150.00)

stock.attach(display)
stock.attach(alert)

stock.set_price(145.00)  # Both observers get notified
stock.set_price(155.00)  # Both observers get notified


# State machine
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

# if TYPE_CHECKING:
#     from __future__ import annotations

class VendingMachineState(ABC):
    @abstractmethod
    def insert_coin(self, machine: 'VendingMachine') -> None:
        pass

    @abstractmethod
    def select_product(self, machine: 'VendingMachine') -> None:
        pass

    @abstractmethod
    def dispense(self, machine: 'VendingMachine') -> None:
        pass

class NoCoinState(VendingMachineState):
    def insert_coin(self, machine: 'VendingMachine') -> None:
        print("Coin inserted")
        machine.set_state(HasCoinState())

    def select_product(self, machine: 'VendingMachine') -> None:
        print("Insert coin first")

    def dispense(self, machine: 'VendingMachine') -> None:
        print("Insert coin first")

class HasCoinState(VendingMachineState):
    def insert_coin(self, machine: 'VendingMachine') -> None:
        print("Coin already inserted")

    def select_product(self, machine: 'VendingMachine') -> None:
        print("Product selected")
        machine.set_state(DispenseState())

    def dispense(self, machine: 'VendingMachine') -> None:
        print("Select product first")

class DispenseState(VendingMachineState):
    def insert_coin(self, machine: 'VendingMachine') -> None:
        print("Please wait, dispensing")

    def select_product(self, machine: 'VendingMachine') -> None:
        print("Please wait, dispensing")

    def dispense(self, machine: 'VendingMachine') -> None:
        print("Dispensing product")
        machine.set_state(NoCoinState())

class VendingMachine:
    def __init__(self):
        self._current_state: VendingMachineState = NoCoinState()

    def insert_coin(self) -> None:
        self._current_state.insert_coin(self)

    def select_product(self) -> None:
        self._current_state.select_product(self)

    def dispense(self) -> None:
        self._current_state.dispense(self)

    def set_state(self, state: VendingMachineState) -> None:
        self._current_state = state

# Usage
machine = VendingMachine()

machine.select_product()  # "Insert coin first"
machine.insert_coin()     # "Coin inserted"
machine.select_product()  # "Product selected"
machine.dispense()        # "Dispensing product"

