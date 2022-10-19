import csv
import os.path
from taxUtils import *
from transaction import *

# Define the data directory
data_directory = "../data"

# Load the user wallets
user_wallets = read_json_file(os.path.join(data_directory, "account_main", "user_wallets.json"))
user_first_wallet = list(user_wallets.keys())[0]

# Load the user baker wallets
baker_wallets = read_json_file(os.path.join(data_directory, "account_main", "baker_wallets.json"))

# Load the exchange wallets
exchange_wallets = read_json_file(os.path.join(data_directory, "account_main", "exchange_wallets.json"))

# Get the user raw transactions and originations information
raw_transactions = get_user_transactions(user_wallets)
raw_originations = get_user_originations(user_wallets)
raw_reveals = get_user_reveals(user_wallets)
raw_delegations = get_user_delegations(user_wallets)

# Get the user mints, swaps, collects, auction bids, art sales and collection sales
user_mints = get_user_mints(user_wallets)
user_swaps = get_user_swaps(user_wallets)
user_collects = get_user_collects(user_wallets)
user_auction_bids = get_user_auction_bids(user_wallets)
user_art_sales = get_user_art_sales(user_wallets)
user_collection_sales = get_user_collection_sales(user_wallets)

# Get the list of FA2 contracts associated to the objkt.com collections
objktcom_collections = get_objktcom_collections()

# Get the list of FA1.2 and FA2 tokens
fa12_tokens = get_fa12_tokens()
fa2_tokens = get_fa2_tokens()

# Get the main tezos tokens and smart contract aliases
token_aliases = {address: name for name, address in TOKENS.items()}
smart_contract_aliases = {address: alias for alias, address in SMART_CONTRACTS.items()}

# Define the burn addresses
burn_addresses = ["tz1burnburnburnburnburnburnburjAYjjX"]

# Process the raw transactions
transactions = []
unprocessed_transactions = []

for t in raw_transactions:
    # Save the most relevant information
    transaction = {
        "timestamp": t["timestamp"],
        "level": t["level"],
        "kind": None,
        "entrypoint": t["parameter"]["entrypoint"] if "parameter" in t else None,
        "parameters": t["parameter"]["value"] if "parameter" in t else None,
        "initiator": t["initiator"]["address"] if "initiator" in t else None,
        "sender": t["sender"]["address"],
        "target": t["target"]["address"],
        "applied": t["status"] == "applied",
        "internal": False,
        "ignore": False,
        "mint": False,
        "collect": False,
        "active_offer": False,
        "art_sale": False,
        "collection_sale": False,
        "staking": False,
        "origination": False,
        "reveal": False,
        "delegation": False,
        "prize": False,
        "donation": False,
        "buy_tez": t["sender"]["address"] in exchange_wallets,
        "sell_tez": t["target"]["address"] in exchange_wallets,
        "amount": t["amount"] / 1e6,
        "fees": ((t["bakerFee"] + t["storageFee"] + t["allocationFee"]) / 1e6) if (t["status"] == "applied") else (t["bakerFee"] / 1e6),
        "tez_to_euros": t["quote"]["eur"],
        "tez_to_usd": t["quote"]["usd"],
        "token_id": None,
        "token_editions": None,
        "token_address": None,
        "hash": t["hash"],
        "comment": ""}

    # Add the information from the known user transactions
    hash = t["hash"]
    
    transaction = clean_transaction(transaction, hash, user_wallets, user_mints, user_swaps, user_collects, user_auction_bids, user_art_sales, user_collection_sales, baker_wallets, objktcom_collections)

    transaction = get_transaction_aliases(transaction, token_aliases, user_wallets, burn_addresses, objktcom_collections, fa12_tokens, fa2_tokens)

    # Save the unprocessed raw transactions
    if transaction["kind"] is None:
        unprocessed_transactions.append(t)

    # Add the processed transaction
    transactions.append(transaction)

# Process the raw originations
originations = []

for o in raw_originations:
    # Save the most relevant information
    origination = {
        "timestamp": o["timestamp"],
        "level": o["level"],
        "kind": "contract origination",
        "entrypoint": None,
        "parameters": None,
        "initiator": o["initiator"]["address"] if "initiator" in o else None,
        "sender": o["sender"]["address"],
        "target": None,
        "applied": o["status"] == "applied",
        "internal": False,
        "ignore": False,
        "mint": False,
        "collect": False,
        "active_offer": False,
        "art_sale": False,
        "collection_sale": False,
        "staking": False,
        "origination": True,
        "reveal": False,
        "delegation": False,
        "prize": False,
        "donation": False,
        "buy_tez": False,
        "sell_tez": False,
        "amount": o["contractBalance"] / 1e6,
        "fees": ((o["bakerFee"] + o["storageFee"] + o["allocationFee"]) / 1e6) if (o["status"] == "applied") else (o["bakerFee"] / 1e6),
        "tez_to_euros": o["quote"]["eur"],
        "tez_to_usd": o["quote"]["usd"],
        "token_id": None,
        "token_editions": None,
        "token_address": None,
        "hash": o["hash"],
        "comment": ""}

    # Add the processed origination
    originations.append(origination)

# Process the raw reveals
reveals = []

for r in raw_reveals:
    # Save the most relevant information
    reveal = {
        "timestamp": r["timestamp"],
        "level": r["level"],
        "kind": "reveal public key",
        "entrypoint": None,
        "parameters": None,
        "initiator": None,
        "sender": r["sender"]["address"],
        "target": None,
        "applied": r["status"] == "applied",
        "internal": False,
        "ignore": False,
        "mint": False,
        "collect": False,
        "active_offer": False,
        "art_sale": False,
        "collection_sale": False,
        "staking": False,
        "origination": False,
        "reveal": True,
        "delegation": False,
        "prize": False,
        "donation": False,
        "buy_tez": False,
        "sell_tez": False,
        "amount": 0,
        "fees": r["bakerFee"] / 1e6,
        "tez_to_euros": r["quote"]["eur"],
        "tez_to_usd": r["quote"]["usd"],
        "token_id": None,
        "token_editions": None,
        "token_address": None,
        "hash": r["hash"],
        "comment": ""}

    # Add the processed reveal
    reveals.append(reveal)

# Process the raw delegations
delegations = []

for d in raw_delegations:
    # Save the most relevant information
    delegation = {
        "timestamp": d["timestamp"],
        "level": d["level"],
        "kind": "delegation",
        "entrypoint": None,
        "parameters": None,
        "initiator": d["initiator"]["address"] if "initiator" in d else None,
        "sender": d["sender"]["address"],
        "target": None,
        "applied": d["status"] == "applied",
        "internal": False,
        "ignore": False,
        "mint": False,
        "collect": False,
        "active_offer": False,
        "art_sale": False,
        "collection_sale": False,
        "staking": False,
        "origination": False,
        "reveal": False,
        "delegation": True,
        "prize": False,
        "donation": False,
        "buy_tez": False,
        "sell_tez": False,
        "amount": 0,
        "fees": d["bakerFee"] / 1e6,
        "tez_to_euros": d["quote"]["eur"],
        "tez_to_usd": d["quote"]["usd"],
        "token_id": None,
        "token_editions": None,
        "token_address": None,
        "hash": r["hash"],
        "comment": ""}

    # Add the processed delegation
    delegations.append(delegation)

# Combine the transactions, originations and reveals in a single array
combined_operations = combine_operations(transactions, originations)
combined_operations = combine_operations(combined_operations, reveals)
combined_operations = combine_operations(combined_operations, delegations)

# Apply the operation corrections specified by the user
operation_corrections = read_json_file(os.path.join(data_directory, "account_main", "operation_corrections.json"))

for operation in combined_operations:
    if operation["hash"] in operation_corrections:
        corrections = operation_corrections[operation["hash"]]

        for key, value in corrections.items():
            if key in operation:
                operation[key] = value

# Get all address aliases
aliases = {}
aliases.update(user_wallets)
aliases.update(baker_wallets)
aliases.update(exchange_wallets)
aliases.update(token_aliases)
aliases.update(smart_contract_aliases)
aliases.update({address: "Burn address" for address in burn_addresses})

for token_address, token_alias in fa12_tokens.items():
    if token_address not in aliases:
        aliases[token_address] = token_alias

for token_address, token_alias in fa2_tokens.items():
    if token_address not in aliases:
        aliases[token_address] = token_alias

# Save the processed data in a csv file
file_name = "operations_%s.csv" % user_first_wallet
columns = [
    "timestamp", "level", "tez_balance", "kind", "entrypoint", "initiator",
    "sender", "target", "is_initiator", "is_sender", "is_target", "applied",
    "internal", "ignore", "mint", "collect", "active_offer", "art_sale",
    "collection_sale", "staking", "origination", "reveal", "delegation",
    "prize", "donation", "buy_tez", "sell_tez", "amount", "fees",
    "received_amount", "art_sale_amount", "collection_sale_amount",
    "staking_rewards_amount", "prize_amount", "buy_tez_amount",
    "received_amount_others", "spent_amount", "collect_amount",
    "active_offer_amount", "donation_amount", "sell_tez_amount",
    "spent_amount_others", "spent_fees", "tez_to_euros", "tez_to_usd",
    "token_name", "token_id", "token_editions", "token_address", "tzkt_link",
    "comment"]
format = [
    "%s", "%i", "%f", "%s", "%s", "%s", "%s", "%s", "%r", "%r", "%r", "%r",
    "%r", "%r", "%r", "%r", "%r", "%r", "%r", "%r", "%r", "%r", "%r", "%r",
    "%r", "%r", "%r", "%f", "%f", "%f", "%f", "%f", "%f", "%f", "%f", "%f",
    "%f", "%f", "%f", "%f", "%f", "%f", "%f", "%f", "%f", "%s", "%s", "%s",
    "%s", "%s", "%s"]

with open(os.path.join(data_directory, "output", file_name), "w", newline="\n") as output_file:
    writer = csv.writer(output_file)

    # Write the header
    writer.writerow(columns)

    # Loop over the combined operations
    tez_balance = 0

    for op in combined_operations:
        # Check if the user is the initiator, the sender or the target
        is_initiator = op["initiator"] in user_wallets
        is_sender = op["sender"] in user_wallets
        is_target = op["target"] in user_wallets

        # Calculate the different received and spent tez amounts
        applied = op["applied"]
        ignore = op["ignore"]
        amount = op["amount"]
        fees = op["fees"]
        received_amount = amount if (is_target and applied and (not ignore)) else 0
        art_sale_amount = amount if (is_target and applied and (not ignore) and op["art_sale"]) else 0
        collection_sale_amount = amount if (is_target and applied and (not ignore) and op["collection_sale"]) else 0
        staking_rewards_amount = amount if (is_target and applied and (not ignore) and op["staking"]) else 0
        prize_amount = amount if (is_target and applied and (not ignore) and op["prize"]) else 0
        buy_tez_amount = amount if (is_target and applied and (not ignore) and op["buy_tez"]) else 0
        received_amount_others = amount if (is_target and applied and (not ignore) and (not (op["art_sale"] or op["collection_sale"] or op["staking"] or op["prize"] or op["buy_tez"]))) else 0
        spent_amount = amount if (is_sender and applied and (not ignore) and (not op["active_offer"])) else 0
        collect_amount = amount if (is_sender and applied and (not ignore) and op["collect"]) else 0
        active_offer_amount = amount if (is_sender and applied and (not ignore) and op["active_offer"]) else 0
        donation_amount = amount if (is_sender and applied and (not ignore) and op["donation"]) else 0
        sell_tez_amount = amount if (is_sender and applied and (not ignore) and op["sell_tez"]) else 0
        spent_amount_others = amount if (is_sender and applied and (not ignore) and (not (op["collect"] or op["active_offer"] or op["donation"] or op["sell_tez"]))) else 0
        spent_fees = fees if (is_initiator or is_sender) else 0

        # Calculate the tez balance
        tez_balance += received_amount - spent_amount - active_offer_amount - spent_fees

        # Get the token alias
        token_address = op["token_address"]
        token_alias = ""

        if token_address in token_aliases:
            token_alias = token_aliases[token_address]
        elif token_address in objktcom_collections:
            token_alias = "objkt.com collection"
        elif token_address in aliases:
            token_alias = aliases[token_address]

        token_alias = token_alias.replace(",", " ")

        # Write the operation data in the output file
        data = [
            op["timestamp"],
            op["level"],
            tez_balance,
            op["kind"],
            op["entrypoint"] if op["entrypoint"] is not None else "",
            aliases.get(op["initiator"], op["initiator"]).replace(",", " ") if op["initiator"] is not None else "",
            aliases.get(op["sender"], op["sender"]).replace(",", " "),
            aliases.get(op["target"], op["target"]).replace(",", " ") if op["target"] is not None else "",
            is_initiator,
            is_sender,
            is_target,
            applied,
            op["internal"],
            ignore,
            op["mint"],
            op["collect"],
            op["active_offer"],
            op["art_sale"],
            op["collection_sale"],
            op["staking"],
            op["origination"],
            op["reveal"],
            op["delegation"],
            op["prize"],
            op["donation"],
            op["buy_tez"],
            op["sell_tez"],
            amount,
            fees,
            received_amount,
            art_sale_amount,
            collection_sale_amount,
            staking_rewards_amount,
            prize_amount,
            buy_tez_amount,
            received_amount_others,
            spent_amount,
            collect_amount,
            active_offer_amount,
            donation_amount,
            sell_tez_amount,
            spent_amount_others,
            spent_fees,
            op["tez_to_euros"],
            op["tez_to_usd"],
            token_alias,
            op["token_id"] if op["token_id"] is not None else "",
            op["token_editions"] if op["token_editions"] is not None else "",
            token_address if token_address is not None else "",
            "https://tzkt.io/%s" % op["hash"],
            op["comment"]]
        writer.writerow(data)

# Save the unprocessed transactions in a json file
unprocessed_file_name = "unprocessed_transactions_%s.json" % user_first_wallet
save_json_file(os.path.join(data_directory, "output", unprocessed_file_name), unprocessed_transactions)

# Print some details
print("\n We discovered %i operations associated to the user wallets." % len(combined_operations))
print(" You can find the processed information in %s\n" % os.path.join(data_directory, "output", file_name))

if len(unprocessed_transactions) > 0:
    print(" Of those, %i operations could not be processed completely." % len(unprocessed_transactions))
    print(" See %s for more details.\n" % os.path.join(data_directory, "output", unprocessed_file_name))
