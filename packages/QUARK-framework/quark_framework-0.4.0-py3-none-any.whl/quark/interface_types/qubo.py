from __future__ import annotations


class Qubo:
    """A class for representing a quadratic unconstrained binary optimization (QUBO) problem."""

    # Every entry represents a coefficient of the qubo matrix
    _q: dict

    def as_dict(self) -> dict:
        """Create a dictionary where TODO: how exactly?. Keys are labels for qubits, can be anything"""
        return self._q

    @staticmethod
    def from_dict(q: dict) -> Qubo:
        """Create a Qubo object from a dictionary where TODO: how exactly?."""
        v = Qubo()
        v._q = q
        return v

    # def as_matrix(self):
    #     pass

    # @staticmethod
    # def from_matrix(matrix: np.ndarray) -> Qubo:
    #     pass

    # def as_ising(self):
    #     pass

    # @staticmethod
    # def from_ising(ising: Ising) -> Qubo:
    #     pass
