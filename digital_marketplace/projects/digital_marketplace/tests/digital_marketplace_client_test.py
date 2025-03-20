import algokit_utils as au
import algosdk
import pytest
from algokit_utils import (
    AlgoAmount,
    AlgorandClient,
    AssetCreateParams,
    PaymentParams,
    SigningAccount,
)
from algosdk.atomic_transaction_composer import TransactionWithSigner

from smart_contracts.artifacts.digital_marketplace.digital_marketplace_client import (
    DigitalMarketplaceClient as cl,  # noqa: N813
)
from smart_contracts.artifacts.digital_marketplace.digital_marketplace_client import (
    DigitalMarketplaceFactory,
    OptInToAssetArgs,
)


@pytest.fixture(scope="session")
def algorand() -> AlgorandClient:
    return AlgorandClient.from_environment()


# Retourne un objet SigningAccount possèdant 10 ALGO nommé "account"
@pytest.fixture(scope="session")
def deployer(algorand_client: AlgorandClient) -> SigningAccount:
    account = algorand_client.account.from_environment("DEPLOYER")
    algorand_client.account.ensure_funded_from_environment(
        account_to_fund=account.address, min_spending_balance=AlgoAmount.from_algo(10)
    )
    return account


@pytest.fixture(scope="session")
def test_asset_id(deployer: SigningAccount, algorand_client: AlgorandClient) -> int:
    create_tst_result = algorand_client.send.asset_create(
        AssetCreateParams(
            sender=deployer.address,
            total=10,
        )
    )
    return int(create_tst_result.confirmation["asset-index"])


@pytest.fixture(scope="session")
def digital_marketplace_client(
    algorand_client: AlgorandClient, deployer: SigningAccount, test_asset_id: int
) -> cl:
    factory = algorand_client.client.get_typed_app_factory(
        DigitalMarketplaceFactory, default_sender=deployer.address
    )

    client, _ = factory.deploy(
        on_schema_break=au.OnSchemaBreak.AppendApp,
        on_update=au.OnUpdate.AppendApp,
    )
    factory.send.create.create_application(
        client.CreateApplicationArgs(
            asset_id=test_asset_id, unitary_price=au.AlgoAmount(algo=1).micro_algo
        )
    )
    return client


def test_opt_in_to_asset(
    digital_marketplace_client: cl,
    deployer: SigningAccount,
    test_asset_id: int,
    algorand_client: AlgorandClient,
):
    pytest.raises(
        algosdk.error.AlgodHTTPError,
        lambda: algorand_client.asset.get_account_information(
            digital_marketplace_client.app_address, test_asset_id
        ),
    )

    mbr_pay_txn = algorand_client.create_transaction.payment(
        PaymentParams(
            sender=deployer.address,
            receiver=digital_marketplace_client.app_address,
            amount=200_000,
            extra_fee=1_000,
        )
    )
    factory = algorand_client.client.get_typed_app_factory(
        DigitalMarketplaceFactory, default_sender=deployer.address
    )
    app_id = digital_marketplace_client.app_id
    ac = factory.get_app_client_by_id(app_id, default_sender=deployer.address)
    result = ac.send.opt_in_to_asset(
        OptInToAssetArgs(
            mbr_pay=TransactionWithSigner(txn=mbr_pay_txn, signer=deployer.signer)
        ),
        send_params=au.SendParams(populate_app_call_resources=True),
    )

    assert result.confirmation["confirmed_round"]

    assert (
        algorand_client.account.get_asset_information(
            digital_marketplace_client.app_address, test_asset_id
        )["asset-holding"]["amount"]
        == 0
    )


# def test_says_hello(digital_marketplace_client: cl) -> None:
#     result = digital_marketplace_client.send.hello(args=("World",))
#     assert result.abi_return == "Hello, World"


# def test_simulate_says_hello_with_correct_budget_consumed(
#     digital_marketplace_client: cl,
# ) -> None:
#     result = (
#         digital_marketplace_client.new_group()
#         .hello(args=("World",))
#         .hello(args=("Jane",))
#         .simulate()
#     )
#     assert result.returns[0].value == "Hello, World"
#     assert result.returns[1].value == "Hello, Jane"
#     assert result.simulate_response["txn-groups"][0]["app-budget-consumed"] < 100
