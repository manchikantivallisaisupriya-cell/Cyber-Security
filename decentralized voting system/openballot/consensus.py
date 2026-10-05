import logging
from typing import List

from openballot.block import Block
from openballot.ledger import Ledger, GENESIS_PREV_HASH


logger = logging.getLogger("openballot.consensus")


class ConsensusEngine:

    def __init__(
        self,
        ledger: Ledger,
        difficulty: int = 1
    ):
        self.ledger = ledger
        self.difficulty = difficulty

    def is_valid_chain(
        self,
        chain: List[Block]
    ) -> bool:

        if not chain:
            return False

        # -----------------------------
        # Validate genesis block
        # -----------------------------

        genesis = chain[0]

        if genesis.index != 0:
            return False

        if genesis.prev_hash != GENESIS_PREV_HASH:
            return False

        if genesis.ballots:
            return False

        if genesis.compute_hash() != genesis.hash:
            return False

        # -----------------------------
        # Validate every following block
        # -----------------------------

        seen_votes = set()

        for i in range(1, len(chain)):

            prev = chain[i - 1]
            curr = chain[i]

            # Correct block index
            if curr.index != i:
                logger.warning(
                    "Invalid block index: %s expected %s",
                    curr.index,
                    i
                )
                return False

            # Correct previous hash
            if curr.prev_hash != prev.hash:
                logger.warning(
                    "Hash mismatch at block %d",
                    curr.index
                )
                return False

            # Correct current hash
            if curr.compute_hash() != curr.hash:
                logger.warning(
                    "Invalid block hash at block %d",
                    curr.index
                )
                return False

            # Proof of work
            target = "0" * self.difficulty

            if not curr.hash.startswith(target):
                logger.warning(
                    "Block %d does not meet difficulty",
                    curr.index
                )
                return False

            # -----------------------------
            # Validate ballots
            # -----------------------------

            for ballot in curr.ballots:

                # Valid signature
                if not ballot.verify():
                    logger.warning(
                        "Invalid ballot signature"
                    )
                    return False

                # Registered voter
                if not self.ledger.is_registered(
                    ballot.voter_id
                ):
                    logger.warning(
                        "Unregistered voter"
                    )
                    return False

                # Duplicate vote
                vote_key = (
                    ballot.proposal_id,
                    ballot.voter_id.lower()
                )

                if vote_key in seen_votes:
                    logger.warning(
                        "Duplicate vote detected"
                    )
                    return False

                seen_votes.add(vote_key)

                # Valid weight
                if ballot.weight <= 0:
                    return False

                # Valid choice
                if ballot.choice not in {"YES", "NO"}:
                    return False

        return True

    def resolve_conflicts(
        self,
        peer_chains: List[List[Block]]
    ) -> bool:

        longest = None
        max_len = len(self.ledger.chain)

        for candidate in peer_chains:

            if len(candidate) <= max_len:
                continue

            if not self.is_valid_chain(candidate):
                continue

            # Candidate must use same genesis
            if (
                self.ledger.chain
                and candidate[0].hash
                != self.ledger.chain[0].hash
            ):
                logger.warning(
                    "Rejected chain with different genesis"
                )
                continue

            max_len = len(candidate)
            longest = candidate

        if longest is not None:

            logger.info(
                "Adopting peer chain of length %d",
                len(longest)
            )

            self.ledger.chain = longest

            return True

        return False
