import os
import algokit_utils as au
import algosdk

algorand = au.AlgorandClient.testnet()
algod_client = algorand.client.algod
indexer_client = algorand.client.indexer

if not (os.path.exists(".env")):
    private_key, address = algosdk.account.generate_account()
    with open(".env", "w") as file:
        file.write(algosdk.mnemonic.from_private_key(private_key))
with open(".env", "r") as file:
    mnemonic = file.read()

alice = algorand.account.from_mnemonic(mnemonic=mnemonic)
print(alice)