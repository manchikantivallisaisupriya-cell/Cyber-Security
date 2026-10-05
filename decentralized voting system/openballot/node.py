def do_POST(self):
    parsed = urlparse(self.path)
    path = parsed.path
    data = self._read_json()

    if data is None:
        return self._send_json(
            {"error": "Invalid JSON payload"},
            400
        )

    if path == "/api/v1/ballots":

        # -----------------------------
        # Create ballot safely
        # -----------------------------

        try:
            ballot = Ballot.from_dict(data)

        except (ValueError, TypeError) as e:
            return self._send_json(
                {"error": str(e)},
                400
            )

        # -----------------------------
        # Required fields
        # -----------------------------

        if (
            not ballot.voter_id
            or not ballot.proposal_id
            or not ballot.choice
        ):
            return self._send_json(
                {"error": "Missing required ballot fields"},
                400
            )

        # -----------------------------
        # Verify signature
        # -----------------------------

        if not ballot.verify():
            return self._send_json(
                {
                    "error":
                    "Cryptographic signature verification failed"
                },
                401
            )

        # -----------------------------
        # Verify voter registration
        # -----------------------------

        if not self.node.ledger.is_registered(
            ballot.voter_id
        ):
            return self._send_json(
                {
                    "error":
                    "Voter ID not in authorized voter registry"
                },
                403
            )

        # -----------------------------
        # Check confirmed blockchain
        # -----------------------------

        if self.node.ledger.has_voted(
            ballot.proposal_id,
            ballot.voter_id
        ):
            return self._send_json(
                {
                    "error":
                    "Voter has already cast a ballot "
                    "for this proposal"
                },
                409
            )

        # -----------------------------
        # Check pending mempool
        # -----------------------------

        if self.node.mempool.has_voted(
            ballot.proposal_id,
            ballot.voter_id
        ):
            return self._send_json(
                {
                    "error":
                    "Voter already has a pending ballot "
                    "for this proposal"
                },
                409
            )

        # -----------------------------
        # Add to mempool
        # -----------------------------

        if not self.node.mempool.add(ballot):
            return self._send_json(
                {
                    "error":
                    "Ballot already exists in mempool"
                },
                409
            )

        return self._send_json(
            {
                "status": "accepted",
                "proposal": ballot.proposal_id
            },
            202
        )

    elif path == "/api/v1/mine":

        # Don't create empty blocks
        pending = self.node.mempool.all()

        if not pending:
            return self._send_json(
                {
                    "error":
                    "No pending ballots to mine"
                },
                400
            )

        # Remove only after validation
        pending = self.node.mempool.drain()

        new_block = Block(
            index=len(self.node.ledger.chain),
            prev_hash=self.node.ledger.chain[-1].hash,
            ballots=pending
        )

        new_block.mine(
            difficulty=self.node.difficulty
        )

        self.node.ledger.chain.append(
            new_block
        )

        return self._send_json(
            {
                "status": "mined",
                "block_index": new_block.index,
                "block_hash": new_block.hash,
                "ballots_sealed": len(pending)
            }
        )

    elif path == "/api/v1/peers":

        peer = data.get("peer")

        if peer and peer not in self.node.peers:
            self.node.peers.append(peer)

        return self._send_json(
            {"peers": self.node.peers}
        )

    elif path == "/api/v1/sync":

        candidate_raw = data.get(
            "chain",
            []
        )

        if not candidate_raw:
            return self._send_json(
                {"error": "Empty chain provided"},
                400
            )

        try:
            candidate = [
                Block.from_dict(block)
                for block in candidate_raw
            ]

        except (ValueError, TypeError, KeyError) as e:

            return self._send_json(
                {
                    "error":
                    f"Invalid block format: {e}"
                },
                400
            )

        replaced = (
            self.node.consensus.resolve_conflicts(
                [candidate]
            )
        )

        return self._send_json(
            {
                "chain_replaced": replaced,
                "current_length":
                len(self.node.ledger.chain)
            }
        )

    else:

        return self._send_json(
            {"error": "Endpoint not found"},
            404
        )
