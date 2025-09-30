"""Utility classes for tracking virtual trading balances."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class VirtualWallet:
    """Simple virtual wallet used to track backtest equity."""

    starting_balance: float
    label: str = "USD"
    history: List[Tuple[str, float]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.balance = float(self.starting_balance)
        self.history.append(("initial", self.balance))

    def apply_return(self, return_pct: float, timestamp: str | None = None) -> float:
        """Apply a percentage return to the wallet and record the new balance."""

        self.balance *= 1 + return_pct
        label = timestamp or f"step-{len(self.history)}"
        self.history.append((label, self.balance))
        return self.balance

    def deposit(self, amount: float, timestamp: str | None = None) -> float:
        """Increase the wallet balance by a fixed amount."""

        self.balance += amount
        label = timestamp or f"deposit-{len(self.history)}"
        self.history.append((label, self.balance))
        return self.balance

    def withdraw(self, amount: float, timestamp: str | None = None) -> float:
        """Decrease the wallet balance by a fixed amount."""

        self.balance -= amount
        label = timestamp or f"withdraw-{len(self.history)}"
        self.history.append((label, self.balance))
        return self.balance

    def summary(self) -> str:
        """Return a human readable summary of the wallet performance."""

        change = self.balance - self.starting_balance
        change_pct = (change / self.starting_balance) * 100 if self.starting_balance else 0.0
        direction = "gained" if change >= 0 else "lost"
        return (
            f"Virtual wallet {direction} {abs(change):.2f} {self.label} "
            f"({change_pct:+.2f}%) and now holds {self.balance:.2f} {self.label}."
        )

