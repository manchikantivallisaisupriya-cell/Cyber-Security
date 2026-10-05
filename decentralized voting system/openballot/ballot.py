import hashlib
from typing import Dict, Any
from openballot.crypto import verify_signature, public_key_from_hex


class Ballot:
    def __init__(
        self,
        voter_id: str,
        proposal_id: str,
        choice: str,
        signature: str = "",
        weight: int = 1
    ):
        self.voter_id = voter_id.strip()
        self.proposal_id = proposal_id.strip()
        self.choice = choice.strip().upper()
        self.signature = signature.strip()

        try:
            self.weight = int(weight)
        except (ValueError, TypeError):
            raise ValueError("Weight must be an integer")

        if not self.voter_id:
            raise ValueError("Voter ID cannot be empty")

        if not self.proposal_id:
            raise ValueError("Proposal ID cannot be empty")

        if not self.choice:
            raise ValueError("Choice cannot be empty")

        if self.choice not in {"YES", "NO"}:
            raise ValueError("Choice must be YES or NO")

        if self.weight <= 0:
            raise ValueError("Weight must be greater than 0")

    def get_digest(self) -> bytes:
        """
        Data included in the digital signature.

        proposal_id is included so a valid vote for one
        proposal cannot be moved to another proposal.
        """
        payload = (
            f"{self.voter_id}:"
            f"{self.proposal_id}:"
            f"{self.choice}:"
            f"{self.weight}"
        )

        return hashlib.sha256(payload.encode("utf-8")).digest()

    def verify(self) -> bool:
        if not self.signature or not self.voter_id:
            return False

        try:
            pubkey = public_key_from_hex(self.voter_id)
            sig_bytes = bytes.fromhex(self.signature)

            return verify_signature(
                pubkey,
                sig_bytes,
                self.get_digest()
            )

        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "voter_id": self.voter_id,
            "proposal_id": self.proposal_id,
            "choice": self.choice,
            "signature": self.signature,
            "weight": self.weight
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Ballot":
        if not isinstance(data, dict):
            raise ValueError("Ballot data must be a JSON object")

        return cls(
            voter_id=data.get("voter_id", ""),
            proposal_id=data.get("proposal_id", ""),
            choice=data.get("choice", ""),
            signature=data.get("signature", ""),
            weight=data.get("weight", 1)
        )

    def __repr__(self) -> str:
        return (
            f"<Ballot voter={self.voter_id[:8]}... "
            f"prop={self.proposal_id} choice={self.choice}>"
        )
