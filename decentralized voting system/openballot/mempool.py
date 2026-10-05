from typing import List, Optional
from openballot.ballot import Ballot


class Mempool:
    """
    In-memory transaction pool for unconfirmed ballots.
    """

    def __init__(self):
        self._pool: List[Ballot] = []

    def has_voted(self, proposal_id: str, voter_id: str) -> bool:
        """
        Check whether this voter already has a pending ballot
        for this proposal.
        """
        voter_id = voter_id.strip().lower()
        proposal_id = proposal_id.strip()

        for ballot in self._pool:
            if (
                ballot.proposal_id == proposal_id
                and ballot.voter_id.lower() == voter_id
            ):
                return True

        return False

    def add(self, ballot: Ballot) -> bool:
        """
        Add ballot only if voter has not already submitted
        a pending ballot for this proposal.
        """
        if self.has_voted(
            ballot.proposal_id,
            ballot.voter_id
        ):
            return False

        self._pool.append(ballot)
        return True

    def drain(self, limit: Optional[int] = None) -> List[Ballot]:
        if limit is None or limit >= len(self._pool):
            items = self._pool[:]
            self._pool.clear()
            return items

        items = self._pool[:limit]
        self._pool = self._pool[limit:]

        return items

    def all(self) -> List[Ballot]:
        return list(self._pool)

    def size(self) -> int:
        return len(self._pool)

    def clear(self):
        self._pool.clear()
