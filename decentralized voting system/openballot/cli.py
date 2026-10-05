def cmd_serve(args):

    registry = set()

    if args.registry:

        try:
            with open(args.registry, "r") as f:
                registry_data = json.load(f)

            # voter_registry.json format:
            # {
            #     "public_key": "alice",
            #     ...
            # }

            if isinstance(registry_data, dict):
                registry = set(
                    registry_data.keys()
                )

        except FileNotFoundError:

            print(
                f"Warning: Registry file not found: "
                f"{args.registry}"
            )

        except json.JSONDecodeError:

            print(
                f"Error: Invalid registry JSON: "
                f"{args.registry}"
            )

            sys.exit(1)

    ledger = Ledger(
        voter_registry=registry
    )

    ledger.create_genesis_block()

    server = NodeServer(
        ("0.0.0.0", args.port),
        NodeHandler,
        ledger=ledger,
        difficulty=args.difficulty
    )

    print(
        f"[*] OpenBallot node running on "
        f"http://127.0.0.1:{args.port}"
    )

    print(
        f"[*] Registered voters: {len(registry)}"
    )

    print(
        f"[*] Mining difficulty: {args.difficulty}"
    )

    try:
        server.serve_forever()

    except KeyboardInterrupt:

        print(
            "\n[*] Shutting down node."
        )

        server.server_close()
