from typing import List

from algokit_utils import AlgorandClient, AlgoAmount, ABIType

def account_creation(algorand: AlgorandClient, name: str, funds=AlgoAmount(algo=0)):
    account = algorand.account.from_environment(name, fund_with=funds)
    info = algorand.client.algod.account_info(account.address)
    print(
        f"Name\t\t: %s \n"
        f"Address\t\t: %s\n"
        f"Created Asset\t: %s\n"
        f"Assets\t\t: %s\n"
        f"Algo\t\t: %.6f"
        % (
            name,
            account.address,
            info["created-assets"],
            info["assets"],
            info["amount"] / 1_000_000,
        )
    )
    if len(info["created-apps"]) > 0:
        print(f"Created-Apps\t: %s \n" % info["created-apps"][0]["id"])
    print("")
    return account


def get_asa_id(ptx):
    if (
        isinstance(ptx, dict)
        and "asset-index" in ptx
        and isinstance(ptx["asset-index"], int)
    ):
        return ptx["asset-index"]
    else:
        raise ValueError("Unexpected response from pending_transaction_info")


def display_info(algorand: AlgorandClient, names: List[str]):
    for name in names:
        account_creation(algorand, name)

