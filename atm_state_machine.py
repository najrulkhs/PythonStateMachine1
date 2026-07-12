"""
ATM State Machine Implementation

This module implements a state machine that simulates an ATM (Automated Teller Machine)
with various states and transitions for typical ATM operations.
"""

from enum import Enum, auto
from typing import Optional, Dict, Any


class ATMState(Enum):
    """Enum representing all possible states of the ATM."""
    IDLE = auto()              # Waiting for card insertion
    CARD_INSERTED = auto()     # Card inserted, waiting for PIN
    PIN_ENTERED = auto()       # PIN entered, waiting for selection
    WITHDRAWAL_SELECTED = auto()  # Withdrawal option selected
    DEPOSIT_SELECTED = auto()     # Deposit option selected
    BALANCE_CHECK_SELECTED = auto()  # Balance check option selected
    PROCESSING_TRANSACTION = auto()  # Transaction being processed
    DISPENSING_CASH = auto()   # Cash being dispensed
    COMPLETING_TRANSACTION = auto()  # Finalizing transaction
    EJECTING_CARD = auto()     # Card being ejected
    ERROR_STATE = auto()       # Error occurred


class ATMStateMachine:
    """
    State machine implementation for an ATM.
    
    Handles state transitions and actions for typical ATM operations
    including card insertion, PIN verification, balance inquiry,
    withdrawal, and deposit operations.
    """
    
    def __init__(self, initial_balance: float = 1000.0):
        """
        Initialize the ATM state machine.
        
        Args:
            initial_balance: Starting account balance (default: 1000.0)
        """
        self.current_state = ATMState.IDLE
        self.account_balance = initial_balance
        self.card_inserted = False
        self.pin_verified = False
        self.transaction_amount = 0.0
        self.pin_attempts = 0
        self.max_pin_attempts = 3
        self.correct_pin = "1234"  # Simulated correct PIN
        self.transaction_history = []
        
    def get_state_name(self) -> str:
        """Return the name of the current state."""
        return self.current_state.name
    
    def _transition_to(self, new_state: ATMState) -> bool:
        """
        Attempt to transition to a new state.
        
        Args:
            new_state: The state to transition to
            
        Returns:
            True if transition is valid, False otherwise
        """
        valid_transitions = {
            ATMState.IDLE: [ATMState.CARD_INSERTED, ATMState.ERROR_STATE],
            ATMState.CARD_INSERTED: [ATMState.PIN_ENTERED, ATMState.EJECTING_CARD, ATMState.ERROR_STATE],
            ATMState.PIN_ENTERED: [ATMState.WITHDRAWAL_SELECTED, ATMState.DEPOSIT_SELECTED, 
                                   ATMState.BALANCE_CHECK_SELECTED, ATMState.EJECTING_CARD, ATMState.ERROR_STATE],
            ATMState.WITHDRAWAL_SELECTED: [ATMState.PROCESSING_TRANSACTION, ATMState.PIN_ENTERED, ATMState.ERROR_STATE],
            ATMState.DEPOSIT_SELECTED: [ATMState.PROCESSING_TRANSACTION, ATMState.PIN_ENTERED, ATMState.ERROR_STATE],
            ATMState.BALANCE_CHECK_SELECTED: [ATMState.PROCESSING_TRANSACTION, ATMState.PIN_ENTERED, ATMState.ERROR_STATE],
            ATMState.PROCESSING_TRANSACTION: [ATMState.DISPENSING_CASH, ATMState.COMPLETING_TRANSACTION, 
                                              ATMState.PIN_ENTERED, ATMState.ERROR_STATE],
            ATMState.DISPENSING_CASH: [ATMState.COMPLETING_TRANSACTION, ATMState.EJECTING_CARD, ATMState.ERROR_STATE],
            ATMState.COMPLETING_TRANSACTION: [ATMState.EJECTING_CARD, ATMState.ERROR_STATE],
            ATMState.EJECTING_CARD: [ATMState.IDLE, ATMState.ERROR_STATE],
            ATMState.ERROR_STATE: [ATMState.EJECTING_CARD, ATMState.IDLE]
        }
        
        if new_state in valid_transitions.get(self.current_state, []):
            self.current_state = new_state
            return True
        else:
            print(f"Invalid transition from {self.current_state.name} to {new_state.name}")
            return False
    
    def insert_card(self) -> Dict[str, Any]:
        """
        Simulate inserting a card into the ATM.
        
        Returns:
            Dictionary with status and message
        """
        if self.current_state != ATMState.IDLE:
            return {"status": "error", "message": "ATM is not ready for card insertion"}
        
        if self._transition_to(ATMState.CARD_INSERTED):
            self.card_inserted = True
            self.pin_attempts = 0
            return {"status": "success", "message": "Card inserted. Please enter your PIN."}
        else:
            return {"status": "error", "message": "Failed to process card insertion"}
    
    def enter_pin(self, pin: str) -> Dict[str, Any]:
        """
        Simulate entering a PIN.
        
        Args:
            pin: The PIN entered by the user
            
        Returns:
            Dictionary with status and message
        """
        if self.current_state != ATMState.CARD_INSERTED and self.current_state != ATMState.PIN_ENTERED:
            return {"status": "error", "message": "Please insert card first"}
        
        self.pin_attempts += 1
        
        if pin == self.correct_pin:
            self.pin_verified = True
            if self._transition_to(ATMState.PIN_ENTERED):
                return {"status": "success", "message": "PIN verified. Please select an operation."}
            else:
                return {"status": "error", "message": "Failed to verify PIN"}
        else:
            remaining_attempts = self.max_pin_attempts - self.pin_attempts
            
            if remaining_attempts > 0:
                return {"status": "error", 
                        "message": f"Incorrect PIN. {remaining_attempts} attempts remaining."}
            else:
                self._transition_to(ATMState.ERROR_STATE)
                return {"status": "error", 
                        "message": "Maximum PIN attempts exceeded. Card will be ejected."}
    
    def select_withdrawal(self, amount: float) -> Dict[str, Any]:
        """
        Select withdrawal operation.
        
        Args:
            amount: Amount to withdraw
            
        Returns:
            Dictionary with status and message
        """
        if self.current_state != ATMState.PIN_ENTERED:
            return {"status": "error", "message": "Please verify PIN first"}
        
        if amount <= 0:
            return {"status": "error", "message": "Amount must be positive"}
        
        if amount > self.account_balance:
            return {"status": "error", "message": "Insufficient funds"}
        
        self.transaction_amount = amount
        
        if self._transition_to(ATMState.WITHDRAWAL_SELECTED):
            return {"status": "success", 
                    "message": f"Withdrawal of ${amount:.2f} selected. Processing..."}
        else:
            return {"status": "error", "message": "Failed to select withdrawal"}
    
    def select_deposit(self, amount: float) -> Dict[str, Any]:
        """
        Select deposit operation.
        
        Args:
            amount: Amount to deposit
            
        Returns:
            Dictionary with status and message
        """
        if self.current_state != ATMState.PIN_ENTERED:
            return {"status": "error", "message": "Please verify PIN first"}
        
        if amount <= 0:
            return {"status": "error", "message": "Amount must be positive"}
        
        self.transaction_amount = amount
        
        if self._transition_to(ATMState.DEPOSIT_SELECTED):
            return {"status": "success", 
                    "message": f"Deposit of ${amount:.2f} selected. Processing..."}
        else:
            return {"status": "error", "message": "Failed to select deposit"}
    
    def select_balance_check(self) -> Dict[str, Any]:
        """
        Select balance check operation.
        
        Returns:
            Dictionary with status and message
        """
        if self.current_state != ATMState.PIN_ENTERED:
            return {"status": "error", "message": "Please verify PIN first"}
        
        if self._transition_to(ATMState.BALANCE_CHECK_SELECTED):
            return {"status": "success", "message": "Balance check selected. Processing..."}
        else:
            return {"status": "error", "message": "Failed to select balance check"}
    
    def process_transaction(self) -> Dict[str, Any]:
        """
        Process the selected transaction.
        
        Returns:
            Dictionary with status and message
        """
        if self.current_state not in [ATMState.WITHDRAWAL_SELECTED, 
                                      ATMState.DEPOSIT_SELECTED, 
                                      ATMState.BALANCE_CHECK_SELECTED]:
            return {"status": "error", "message": "No transaction selected"}
        
        if not self._transition_to(ATMState.PROCESSING_TRANSACTION):
            return {"status": "error", "message": "Failed to process transaction"}
        
        result = {"status": "processing", "message": "Transaction is being processed..."}
        
        # Automatically proceed based on transaction type
        if self.current_state == ATMState.PROCESSING_TRANSACTION:
            if self.transaction_amount > 0 and self.current_state in [ATMState.WITHDRAWAL_SELECTED, ATMState.DEPOSIT_SELECTED]:
                # This would be handled by the specific transaction methods
                pass
        
        return result
    
    def complete_withdrawal(self) -> Dict[str, Any]:
        """
        Complete a withdrawal transaction.
        
        Returns:
            Dictionary with status and message
        """
        if self.current_state != ATMState.WITHDRAWAL_SELECTED:
            return {"status": "error", "message": "No withdrawal selected"}
        
        if self.transaction_amount > self.account_balance:
            return {"status": "error", "message": "Insufficient funds"}
        
        # Process withdrawal
        self.account_balance -= self.transaction_amount
        self.transaction_history.append({
            "type": "withdrawal",
            "amount": self.transaction_amount,
            "balance_after": self.account_balance
        })
        
        if self._transition_to(ATMState.PROCESSING_TRANSACTION):
            if self._transition_to(ATMState.DISPENSING_CASH):
                return {"status": "success", 
                        "message": f"Please take your cash: ${self.transaction_amount:.2f}"}
            else:
                return {"status": "error", "message": "Failed to dispense cash"}
        else:
            return {"status": "error", "message": "Failed to process withdrawal"}
    
    def complete_deposit(self) -> Dict[str, Any]:
        """
        Complete a deposit transaction.
        
        Returns:
            Dictionary with status and message
        """
        if self.current_state != ATMState.DEPOSIT_SELECTED:
            return {"status": "error", "message": "No deposit selected"}
        
        # Process deposit
        self.account_balance += self.transaction_amount
        self.transaction_history.append({
            "type": "deposit",
            "amount": self.transaction_amount,
            "balance_after": self.account_balance
        })
        
        if self._transition_to(ATMState.PROCESSING_TRANSACTION):
            if self._transition_to(ATMState.COMPLETING_TRANSACTION):
                return {"status": "success", 
                        "message": f"Deposit of ${self.transaction_amount:.2f} completed successfully."}
            else:
                return {"status": "error", "message": "Failed to complete deposit"}
        else:
            return {"status": "error", "message": "Failed to process deposit"}
    
    def complete_balance_check(self) -> Dict[str, Any]:
        """
        Complete a balance check transaction.
        
        Returns:
            Dictionary with status and message
        """
        if self.current_state != ATMState.BALANCE_CHECK_SELECTED:
            return {"status": "error", "message": "No balance check selected"}
        
        if self._transition_to(ATMState.PROCESSING_TRANSACTION):
            if self._transition_to(ATMState.COMPLETING_TRANSACTION):
                return {"status": "success", 
                        "message": f"Your current balance is: ${self.account_balance:.2f}"}
            else:
                return {"status": "error", "message": "Failed to check balance"}
        else:
            return {"status": "error", "message": "Failed to process balance check"}
    
    def finalize_transaction(self) -> Dict[str, Any]:
        """
        Finalize the current transaction and prepare to eject card.
        
        Returns:
            Dictionary with status and message
        """
        if self.current_state not in [ATMState.COMPLETING_TRANSACTION, ATMState.DISPENSING_CASH]:
            return {"status": "error", "message": "No transaction to finalize"}
        
        if self._transition_to(ATMState.EJECTING_CARD):
            return {"status": "success", "message": "Transaction completed. Please take your card."}
        else:
            return {"status": "error", "message": "Failed to finalize transaction"}
    
    def eject_card(self) -> Dict[str, Any]:
        """
        Eject the card and return to idle state.
        
        Returns:
            Dictionary with status and message
        """
        if self.current_state not in [ATMState.EJECTING_CARD, ATMState.ERROR_STATE]:
            return {"status": "error", "message": "Card cannot be ejected in current state"}
        
        if self._transition_to(ATMState.IDLE):
            self.card_inserted = False
            self.pin_verified = False
            self.transaction_amount = 0.0
            self.pin_attempts = 0
            return {"status": "success", "message": "Card ejected. Thank you for using our ATM."}
        else:
            return {"status": "error", "message": "Failed to eject card"}
    
    def cancel_transaction(self) -> Dict[str, Any]:
        """
        Cancel the current transaction and eject card.
        
        Returns:
            Dictionary with status and message
        """
        if self.current_state == ATMState.IDLE:
            return {"status": "error", "message": "No transaction to cancel"}
        
        # Reset transaction data
        self.transaction_amount = 0.0
        
        if self._transition_to(ATMState.EJECTING_CARD):
            return self.eject_card()
        else:
            return {"status": "error", "message": "Failed to cancel transaction"}
    
    def get_balance(self) -> float:
        """Return the current account balance."""
        return self.account_balance
    
    def get_transaction_history(self) -> list:
        """Return the transaction history."""
        return self.transaction_history.copy()
    
    def reset(self) -> None:
        """Reset the ATM to its initial state."""
        self.current_state = ATMState.IDLE
        self.card_inserted = False
        self.pin_verified = False
        self.transaction_amount = 0.0
        self.pin_attempts = 0
        self.transaction_history = []


def demo_atm():
    """Demonstrate the ATM state machine with various operations."""
    print("=" * 60)
    print("ATM STATE MACHINE DEMONSTRATION")
    print("=" * 60)
    
    atm = ATMStateMachine(initial_balance=5000.0)
    
    print(f"\nInitial State: {atm.get_state_name()}")
    print(f"Initial Balance: ${atm.get_balance():.2f}")
    
    # Insert card
    print("\n--- Inserting Card ---")
    result = atm.insert_card()
    print(f"State: {atm.get_state_name()}")
    print(f"Result: {result['message']}")
    
    # Enter correct PIN
    print("\n--- Entering PIN ---")
    result = atm.enter_pin("1234")
    print(f"State: {atm.get_state_name()}")
    print(f"Result: {result['message']}")
    
    # Check balance
    print("\n--- Checking Balance ---")
    result = atm.select_balance_check()
    print(f"State: {atm.get_state_name()}")
    print(f"Result: {result['message']}")
    
    result = atm.complete_balance_check()
    print(f"State: {atm.get_state_name()}")
    print(f"Result: {result['message']}")
    
    result = atm.finalize_transaction()
    print(f"State: {atm.get_state_name()}")
    print(f"Result: {result['message']}")
    
    result = atm.eject_card()
    print(f"State: {atm.get_state_name()}")
    print(f"Result: {result['message']}")
    
    # Withdrawal example
    print("\n" + "=" * 60)
    print("WITHDRAWAL EXAMPLE")
    print("=" * 60)
    
    atm.insert_card()
    atm.enter_pin("1234")
    
    print("\n--- Withdrawing $500 ---")
    result = atm.select_withdrawal(500.0)
    print(f"State: {atm.get_state_name()}")
    print(f"Result: {result['message']}")
    
    result = atm.complete_withdrawal()
    print(f"State: {atm.get_state_name()}")
    print(f"Result: {result['message']}")
    
    result = atm.finalize_transaction()
    print(f"State: {atm.get_state_name()}")
    print(f"Result: {result['message']}")
    
    result = atm.eject_card()
    print(f"State: {atm.get_state_name()}")
    print(f"Result: {result['message']}")
    
    print(f"\nFinal Balance: ${atm.get_balance():.2f}")
    
    # Deposit example
    print("\n" + "=" * 60)
    print("DEPOSIT EXAMPLE")
    print("=" * 60)
    
    atm.insert_card()
    atm.enter_pin("1234")
    
    print("\n--- Depositing $1000 ---")
    result = atm.select_deposit(1000.0)
    print(f"State: {atm.get_state_name()}")
    print(f"Result: {result['message']}")
    
    result = atm.complete_deposit()
    print(f"State: {atm.get_state_name()}")
    print(f"Result: {result['message']}")
    
    result = atm.finalize_transaction()
    print(f"State: {atm.get_state_name()}")
    print(f"Result: {result['message']}")
    
    result = atm.eject_card()
    print(f"State: {atm.get_state_name()}")
    print(f"Result: {result['message']}")
    
    print(f"\nFinal Balance: ${atm.get_balance():.2f}")
    
    # Show transaction history
    print("\n" + "=" * 60)
    print("TRANSACTION HISTORY")
    print("=" * 60)
    for i, transaction in enumerate(atm.get_transaction_history(), 1):
        print(f"{i}. {transaction['type'].capitalize()}: ${transaction['amount']:.2f} "
              f"(Balance after: ${transaction['balance_after']:.2f})")
    
    # Error handling example
    print("\n" + "=" * 60)
    print("ERROR HANDLING EXAMPLE - WRONG PIN")
    print("=" * 60)
    
    atm.insert_card()
    
    for attempt in range(4):
        result = atm.enter_pin("wrong")
        print(f"Attempt {attempt + 1}: {result['message']}")
        if result['status'] == 'error' and 'exceeded' in result['message']:
            break
    
    result = atm.eject_card()
    print(f"State: {atm.get_state_name()}")
    print(f"Result: {result['message']}")
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    demo_atm()
