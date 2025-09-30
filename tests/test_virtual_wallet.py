import pytest

pytest.importorskip("numpy")
pytest.importorskip("pandas")

from ov_trader.samples.quickstart import run_demo
from ov_trader.utils.wallet import VirtualWallet


def test_virtual_wallet_tracks_balance():
    wallet = VirtualWallet(starting_balance=100.0)
    wallet.apply_return(0.10, "day1")
    wallet.apply_return(-0.05, "day2")

    assert wallet.balance == pytest.approx(104.5, rel=1e-3)
    assert wallet.history[0] == ("initial", 100.0)
    assert wallet.history[-1][0] == "day2"


def test_run_demo_produces_wallet():
    results = run_demo()
    wallet = results["wallet"]

    assert isinstance(wallet, VirtualWallet)
    assert wallet.history
    assert wallet.balance > 0
