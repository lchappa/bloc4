import client as cl
import algokit_utils as au
import algokit_utils.transactions.transaction_composer as att

algorand = au.AlgorandClient.testnet()

with open("./.env", "r") as file:
    mnemonic = file.read()

user = algorand.account.from_mnemonic(mnemonic=mnemonic)

factory = algorand.client.get_typed_app_factory(
    cl.EvalFactory, default_sender=user.address
)
app_id = 736038676
ac = factory.get_app_client_by_id(app_id, default_sender=user.address)

ac.send.claim_algo(
        au.CommonAppCallParams(
            sender=user.address,
            signer=user.signer
        ),
        au.SendParams(
            populate_app_call_resources=True
        )
    )

create_result = algorand.send.asset_create(
    au.AssetCreateParams(
        sender=user.address,
        total=15,
        decimals=0,
        default_frozen=False,
        unit_name="TST",
        asset_name="Token test",
    )
)
tst_id = int(create_result.confirmation["asset-index"])
print(tst_id)

mbr_pay_txn = algorand.create_transaction.payment(
    au.PaymentParams(
        sender=user.address,
        receiver=ac.app_address,
        amount=au.AlgoAmount(algo=0.2),
        extra_fee=au.AlgoAmount(micro_algo=algorand.get_suggested_params().min_fee)
    )
)

ac.send.opt_in_to_asset(
    cl.OptInToAssetArgs(
        mbr_pay=att.TransactionWithSigner(mbr_pay_txn, user.signer),
        asset=tst_id
    ),
    send_params=au.SendParams(populate_app_call_resources=True)
)

ac.send.sum(
    cl.SumArgs(
        array=bytes([1,2])
    ),
    send_params=au.SendParams(populate_app_call_resources=True)
)

ac.send.update_box(
    cl.UpdateBoxArgs(
        value="update"
    ),
    send_params=au.SendParams(populate_app_call_resources=True)
)