import pytest

from lpswarm.alphabet import Alphabet
from lpswarm.oracle import FullOracle, OracleConfig


@pytest.fixture(scope="session")
def latin():
    return Alphabet.latin26()


@pytest.fixture(scope="session")
def oracle(latin):
    return FullOracle(latin, OracleConfig(null_samples=600))
