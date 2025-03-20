import os
import algosdk as sdk
import algokit_utils as au
from algokit_utils.models.account import SigningAccount
import algokit_utils.transactions.transaction_composer as att

from utils import (
    account_creation,
    # display_info,
    box_abi,
    get_min_balance_required,
    sha256_encode,
    sha256_digest
)


def box(app_id, box_name):
    return algorand.app.get_box_value(app_id, box_name=box_name)


def register(user: SigningAccount, value: str = ""):
    # Find box_key
    box_key = user.public_key
    
    # Find min_balance
    # HINT:
    args = cl.RegisterArgs(name=value)

    param = au.CommonAppCallParams(
                box_references=[box_key],
                sender=user.address,
                signer=user.signer
            )

    min_balance = get_min_balance_required(ac, ac.params.register(args, param))
    composer = algorand.new_group()

    # TODO composer.add_payment(
    composer.add_payment(
        au.PaymentParams(
            sender=user.address,
            receiver=ac.app_address,
            amount=au.AlgoAmount(micro_algo=min_balance),
            signer=user.signer
        )
    )

    # TODO composer.add_app_call_method_call(ac.params.register
    composer.add_app_call_method_call(
        ac.params.register(
            args,
            param
        )
    )
    composer.send()
    box_value = box(app_id, box_name=box_key)
    registered_at, name, balance = box_abi(cl, "User").decode(box_value)
    return registered_at, name, balance


def fund_account(user: SigningAccount, amount: int):
    pay_txn = algorand.create_transaction.payment(
        au.PaymentParams(
            sender=user.address,
            receiver=ac.app_address,
            amount=au.AlgoAmount(micro_algo=amount)
        )
    )
    args = cl.FundAccountArgs(
        payment=att.TransactionWithSigner(
            txn=pay_txn,
            signer=user.signer
        )
    )
    param = au.CommonAppCallParams(box_references=[user.public_key])

    # TODO find args & param
    balance_returned = ac.send.fund_account(
        args, param
    ).abi_return
    return balance_returned


def add_or_update_asset(ac, asset):
    name, _, _ = asset
    box_name = b"asset" + sha256_encode(name)
    # TODO Call ac.send.admin_upsert_asset
    ac.send.admin_upsert_asset(
        cl.AdminUpsertAssetArgs(
            asset=asset
        ),
        au.CommonAppCallParams(
            box_references=[box_name]
        )
    )

    box_value = box(app_id, box_name=box_name)
    return box_abi(cl, "GameAsset").decode(box_value)


def buy_asset(ac, asset_name: str, quantity: int, user: SigningAccount):

    asset_box_name = b"asset" + (
        asset_id := sha256_encode(asset_name)
    )
    _, _, asset_price = box_abi(cl, "GameAsset").decode(
        box(ac.app_id, asset_box_name)
    )

    # Get user balance before buying asset
    user_box_abi = box_abi(cl, "User")
    user_asset_box_name = (
        b"user_asset" + sha256_digest(user.public_key + asset_id)
    )

    # TODO Call ac.send.buy_asset
    ac.send.buy_asset(
        cl.BuyAssetArgs(
            asset_id=asset_id,
            quantity=quantity
        ),
        au.CommonAppCallParams(
            box_references=[
                asset_box_name,
                user.public_key,
                user_asset_box_name,
            ],
            sender=user.address,
            signer=user.signer
        )
    )

    # Get user balance after buying two units of the asset
    _, _, balance_after = user_box_abi.decode(box(app_id, user.public_key))

    # Test user-asset box value
    quantity_after = sdk.abi.UintType(64).decode(
        box(app_id, user_asset_box_name)
    )
    return asset_name, quantity_after


if __name__ == "__main__":
    algorand = au.AlgorandClient.from_environment()

    algod_client = algorand.client.algod
    indexer_client = algorand.client.indexer

    print(algod_client.block_info(0))
    print(indexer_client.health())

    alice = account_creation(algorand, "ALICE", au.AlgoAmount(algo=10000))
    with open(".env", "w") as file:
        file.write(sdk.mnemonic.from_private_key(alice.private_key))
    bob = account_creation(algorand, "BOB", au.AlgoAmount(algo=100))

    os.system("algokit compile py --out-dir ./app app.py")
    os.system(
        "algokit generate client app/Game.arc32.json --output client.py"
    )
    import client as cl

    factory = algorand.client.get_typed_app_factory(
        cl.GameFactory, default_sender=alice.address
    )

    if len(algorand.account.get_information(alice.address).created_apps) > 0:
        app_id = algorand.account.get_information(alice.address).created_apps[0]["id"]
    else:

        result, _ = factory.send.create.bare()
        app_id = result.app_id
    ac = factory.get_app_client_by_id(app_id, default_sender=alice.address)
    print(f"App {app_id} deployed with address {ac.app_address}")

    _, _, _ = register(alice, "Alice")
    _, _, _ = register(bob, "Bob")

    bob_balance = fund_account(bob, 1_000_000)

    assets = [
        ("POKEBALL", "Catches Pokemon", 200),
        ("POTION", "Restores 20 HP", 300),
        ("BICYCLE", "Allows you to travel faster", 1_000_000)
    ]

    for asset in assets:
        add_or_update_asset(ac, asset)

    a, b = buy_asset(ac, "POKEBALL", 1, bob)

    print(a, b)

    try:
        a, b = buy_asset(ac, "BICYCLE", 1, bob)
    except AssertionError:
        print("Sorry, You can't afford it!")