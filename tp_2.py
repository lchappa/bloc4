import algokit_utils as au
import algosdk as sdk
from utils import (
    account_creation,
    display_info,
)

algorand = au.AlgorandClient.from_environment()

algod_client = algorand.client.algod
indexer_client = algorand.client.indexer

alice = account_creation(algorand, "ALICE")
bob = account_creation(algorand, "BOB")

composer = algorand.new_group()

# create_result = algorand.send.asset_create(
#     au.AssetCreateParams(
#         sender=alice.address,
#         total=15,
#         decimals=0,
#         default_frozen=False,
#         unit_name="TST",
#         asset_name="Token test",
#     )
# )

# print(create_result.confirmation["asset-index"])

composer.add_asset_opt_in(au.AssetOptInParams(
    sender=bob.address,
    asset_id = 1010
))

composer.add_payment(au.PaymentParams(
    sender=bob.address,
    receiver=alice.address,
    amount=au.AlgoAmount.from_algo(1),
    signer=bob.signer
))

composer.add_asset_transfer(au.AssetTransferParams(
    sender=alice.address,
    asset_id=1010,
    amount=1,
    receiver=bob.address
))

print(composer.send())