import algokit_utils as au
import algokit_utils.transactions.transaction_composer as att
from utils import (
    account_creation,
)
import client as cl

algorand = au.AlgorandClient.from_environment()

algod_client = algorand.client.algod
indexer_client = algorand.client.indexer

alice = account_creation(algorand, "ALICE", au.AlgoAmount(algo=10_000))
charly = account_creation(algorand, "CHARLY", au.AlgoAmount(algo=10_000))

sp = algorand.get_suggested_params()

create_result = algorand.send.asset_create(
    au.AssetCreateParams(
        sender=alice.address,
        total=15,
        decimals=0,
        default_frozen=False,
        unit_name="TST",
        asset_name="Token test",
    )
)
tst_id = int(create_result.confirmation["asset-index"])
print(tst_id)

factory = algorand.client.get_typed_app_factory(
    cl.DigitalMarketplaceFactory, default_sender=alice.address
)

result, _ = factory.send.create.create_application(
    cl.CreateApplicationArgs(
        asset_id=tst_id, unitary_price=au.AlgoAmount(algo=1).micro_algo
    )
)
app_id = result.app_id
ac = factory.get_app_client_by_id(app_id, default_sender=alice.address)

mbr_pay_txn = algorand.create_transaction.payment(
    au.PaymentParams(
        sender=alice.address,
        receiver=ac.app_address,
        amount=au.AlgoAmount(algo=0.2),
        extra_fee=au.AlgoAmount(micro_algo=sp.min_fee)
    )
)

ac.send.opt_in_to_asset(
    cl.OptInToAssetArgs(
        mbr_pay=att.TransactionWithSigner(mbr_pay_txn, alice.signer)
    ),
    send_params=au.SendParams(populate_app_call_resources=True)
)

asset_txn = algorand.send.asset_transfer(au.AssetTransferParams(
    sender=alice.address,
    asset_id=tst_id,
    amount=15,
    receiver=ac.app_address
))

composer = algorand.new_group()

composer.add_asset_opt_in(au.AssetOptInParams(
    sender=charly.address,
    asset_id=tst_id
))
amount_to_buy = 3

buyer_txn = algorand.create_transaction.payment(au.PaymentParams(
    sender=charly.address,
    receiver=ac.app_address,
    amount=au.AlgoAmount(micro_algo=algorand.app.get_global_state(ac.app_id)['unitary_price'].value * amount_to_buy),
    extra_fee=au.AlgoAmount(micro_algo=sp.min_fee)
))

composer.add_app_call_method_call(
    ac.params.buy(
        cl.BuyArgs(
            buyer_txn=att.TransactionWithSigner(buyer_txn, charly.signer),
            quantity=amount_to_buy
        ),
        au.CommonAppCallParams(
            sender=charly.address,
            signer=charly.signer,
            asset_references=[tst_id],
        )
    )
)

composer.send()

ac.send.delete.delete_application(
    cl.DigitalMarketplaceMethodCallDeleteParams(
        sender=alice.address,
        signer=alice.signer,
        asset_references=[tst_id],
        extra_fee=au.AlgoAmount(micro_algo=sp.min_fee*2)
    )
)