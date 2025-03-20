import client as cl
import algokit_utils as au
from utils import account_creation
import algokit_utils.transactions.transaction_composer as att

algorand = au.AlgorandClient.from_environment()
algod_client = algorand.client.algod
indexer_client = algorand.client.indexer

user = account_creation(algorand, "ALICE", au.AlgoAmount(algo=10_000))
print(user)

factory = algorand.client.get_typed_app_factory(
    cl.EvalFactory, default_sender=user.address
)

result, _ = factory.send.create.bare()
app_id = result.app_id
ac = factory.get_app_client_by_id(app_id, default_sender=user.address)
print(f"App {app_id} deployed with address {ac.app_address}")

algorand.send.payment(
    au.PaymentParams(
        sender=user.address,
        receiver=ac.app_address,
        amount=au.AlgoAmount(algo=1),
        signer=user.signer
    )
)

ac.send.add_students(
    args=cl.AddStudentsArgs(
        account=user.address
    ),
    send_params=au.SendParams(
        populate_app_call_resources=True
    )
)

def claim_algo():
    ac.send.claim_algo(
        au.CommonAppCallParams(
            sender=user.address,
            signer=user.signer
        ),
        au.SendParams(
            populate_app_call_resources=True
        )
    )

def opt_in_to_asset():
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

def sum():
    ac.send.sum(
        cl.SumArgs(
            array=bytes([1,2])
        ),
        send_params=au.SendParams(populate_app_call_resources=True)
    )

def update_box():
    ac.send.update_box(
        cl.UpdateBoxArgs(
            value="update"
        ),
        send_params=au.SendParams(populate_app_call_resources=True)
    )


def check_score():
    score = 1
    for i in range(1,5):
        try:
            algorand.app.get_box_value(app_id, box_name=bytes("q"+str(i), 'utf-8')+user.public_key)
            score += 1
        except Exception as e:
            continue
    print("Score : ",score)

claim_algo()
opt_in_to_asset()
sum()
update_box()
check_score()