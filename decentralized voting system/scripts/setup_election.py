#!/usr/bin/env python3

"""
Utility script to generate sample voters
for an OpenBallot election demo.
"""

import json
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).parent.parent)
)

from openballot.crypto import (
    generate_keypair,
    public_key_to_hex,
    private_key_to_hex
)


def main():

    voters = [
        "alice",
        "bob",
        "charlie",
        "dave",
        "eve"
    ]

    registry = {}
    keyring = {}

    for name in voters:

        private_key, public_key = generate_keypair()

        public_hex = public_key_to_hex(
            public_key
        )

        private_hex = private_key_to_hex(
            private_key
        )

        keyring[name] = {
            "voter_id": public_hex,
            "secret_key": private_hex
        }

        registry[public_hex] = name

    project_root = (
        Path(__file__).parent.parent
    )

    # -----------------------------
    # Save private key information
    # -----------------------------

    keyring_file = (
        project_root / "sample_voters.json"
    )

    with open(
        keyring_file,
        "w"
    ) as f:

        json.dump(
            keyring,
            f,
            indent=2
        )

    # -----------------------------
    # Save voter registry
    # -----------------------------

    registry_file = (
        project_root / "voter_registry.json"
    )

    with open(
        registry_file,
        "w"
    ) as f:

        json.dump(
            registry,
            f,
            indent=2
        )

    print(
        f"Generated {len(voters)} voter keypairs."
    )

    print(
        f"Keyring written to: {keyring_file}"
    )

    print(
        f"Registry written to: {registry_file}"
    )

    print("\nSample voters:")

    for name, data in keyring.items():

        print(
            f"  {name.capitalize():<8}: "
            f"ID={data['voter_id'][:16]}... "
            f"Secret={data['secret_key'][:16]}..."
        )


if __name__ == "__main__":
    main()
