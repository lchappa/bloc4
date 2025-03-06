import algokit_utils as au
import algosdk as sdk
from utils import (
    account_creation,
    display_info,
)

algorand = au.AlgorandClient.from_environment()

algod_client = algorand.client.algod
indexer_client = algorand.client.indexer

# print(algod_client.block_info(0))
# print(indexer_client.health())

alice = account_creation(algorand, "ALICE", au.AlgoAmount(algo=10_000))
bob = account_creation(algorand, "BOB", au.AlgoAmount(algo=100))
# print(sdk.mnemonic.from_private_key(alice.private_key))
# print(sdk.mnemonic.from_private_key(bob.private_key))
transaction = algorand.create_transaction.payment(
    au.PaymentParams(
        sender=alice.address,
        receiver=bob.address,
        amount=au.AlgoAmount(algo=1)
    )
)
transaction_signed = transaction.sign(alice.private_key)
transaction_id = algorand.client.algod.send_transaction(transaction_signed)
res = sdk.transaction.wait_for_confirmation(algod_client, transaction_id)
print(res)

payback_txn = algorand.send.payment(
    au.PaymentParams(
        sender=bob.address,
        receiver=alice.address,
        amount=au.AlgoAmount(algo=1),
        signer=bob.signer
    )
)

display_info(algorand, ["ALICE", "BOB"])