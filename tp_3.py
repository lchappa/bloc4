import client as cl
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
charly = account_creation(algorand, "CHARLY")

sp = algorand.get_suggested_params()

factory = algorand.client.get_typed_app_factory(
    cl.DigitalMarketplaceFactory, default_sender=alice.address
)

result, _ = factory.send.create.create_application(
    cl.CreateApplicationArgs(
        asset_id=1003, unitary_price=au.AlgoAmount(algo=1).micro_algo
    )
)
app_id = result.app_id
ac = factory.get_app_client_by_id(app_id, default_sender=alice.address)

# Transfer ASA to DigitalMarketplace

composer = algorand.new_group()

composer.add_payment(au.PaymentParams(
    sender=alice.address,
    receiver=ac.app_address,
    amount=au.AlgoAmount.from_algo(0.2),
    signer=alice.signer,
    extra_fee=sp.fee * 2
))

composer.add_asset_opt_in(au.AssetOptInParams(
    sender=ac.app_address,
    asset_id=1003
))

print(composer.send())

asset_txn = algorand.send.asset_transfer(au.AssetTransferParams(
    sender=alice.address,
    asset_id=1003,
    amount=15,
    receiver=ac.app_address
))