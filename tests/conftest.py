import pytest

from lpswarm.alphabet import Alphabet
from lpswarm.oracle import FullOracle, OracleConfig


@pytest.fixture(scope="session")
def latin():
    return Alphabet.latin26()


@pytest.fixture(scope="session")
def oracle(latin):
    return FullOracle(latin, OracleConfig(null_samples=600))


@pytest.fixture(autouse=True)
def _plenty_of_disk(monkeypatch):
    """The overnight disk guard must not depend on the machine running the tests."""
    import lpswarm.diskuse as D
    monkeypatch.setattr(D, "free_gb", lambda path=".": 500.0)
