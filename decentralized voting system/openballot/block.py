import hashlib
import json
import time
from typing import List, Dict, Any

from openballot.ballot import Ballot


class Block:

    def __init__(
        self,
        index: int,
        prev_hash: str,
        ballots: List[Ballot],
        timestamp: float = None,
        nonce: int = 0
    ):
        self.index = int(index)
        self.prev_hash = prev_hash
        self.ballots = ballots
        self.timestamp = (
            timestamp
            if timestamp is not None
            else time.time()
        )
        self.nonce = int(nonce)

        self.hash = self.compute_hash()

    def compute_hash(self) -> str:

        payload = {
            "index": self.index,
            "prev_hash": self.prev_hash,
            "ballots": [
                ballot.to_dict()
                for ballot in self.ballots
            ],
            "timestamp": round(self.timestamp, 4),
            "nonce": self.nonce
        }

        raw = json.dumps(
            payload,
            sort_keys=True
        )

        return hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()

    def mine(self, difficulty: int = 1):

        target = "0" * difficulty

        while not self.hash.startswith(target):

            self.nonce += 1

            self.hash = self.compute_hash()

    def to_dict(self) -> Dict[str, Any]:

        return {
            "index": self.index,
            "prev_hash": self.prev_hash,
            "ballots": [
                ballot.to_dict()
                for ballot in self.ballots
            ],
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "hash": self.hash
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any]
    ) -> "Block":

        if not isinstance(data, dict):
            raise ValueError("Block data must be an object")

        required = [
            "index",
            "prev_hash",
            "ballots",
            "timestamp",
            "nonce"
        ]

        for field in required:
            if field not in data:
                raise ValueError(
                    f"Missing block field: {field}"
                )

        ballots = [
            Ballot.from_dict(ballot)
            for ballot in data["ballots"]
        ]

        block = cls(
            index=data["index"],
            prev_hash=data["prev_hash"],
            ballots=ballots,
            timestamp=data["timestamp"],
            nonce=data["nonce"]
        )

        calculated_hash = block.compute_hash()

        supplied_hash = data.get("hash")

        if supplied_hash is not None:
            if supplied_hash != calculated_hash:
                raise ValueError(
                    "Invalid block hash"
                )

        block.hash = calculated_hash

        return block

    def __repr__(self) -> str:

        return (
            f"<Block #{self.index} "
            f"hash={self.hash[:10]}... "
            f"txs={len(self.ballots)}>"
        )
