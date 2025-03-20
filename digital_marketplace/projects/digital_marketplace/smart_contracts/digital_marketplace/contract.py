from algopy import ARC4Contract, Asset, Global, String, UInt64, gtxn, itxn
from algopy.arc4 import abimethod


class DigitalMarketplace(ARC4Contract):
    asset_id: UInt64  # We want to store the ID for the asset we are selling
    unitary_price: UInt64  # We want to store the price for the asset we are selling

    @abimethod()
    def hello(self, name: String) -> String:
        return "Hello, " + name

    @abimethod(allow_actions=["NoOp"], create="require")
    # There are certain actions that a contract call can do
    # Some examples are UpdateApplication, DeleteApplication, and NoOp
    # NoOp is a call that does nothing special after it is executed
    # Require that this method is only callable when creating the app
    def create_application(self, asset_id: Asset, unitary_price: UInt64) -> None:
        self.asset_id = asset_id.id  # The ID of the asset we're selling
        self.unitary_price = unitary_price  # The initial sale price

    # Before any account can receive an asset, it must opt-in to it
    # This method enables the application to opt-in to the asset
    @abimethod
    def opt_in_to_asset(
        self, mbr_pay: gtxn.PaymentTransaction
    ) -> None:  # Need to send a payment to cover data usage
        # We want to make sure that the application address is not already opted in
        assert not Global.current_application_address.is_opted_in(Asset(self.asset_id))
        assert mbr_pay.receiver == Global.current_application_address
        # Every accounts has an MBR of 0.1 ALGO (Global.min_balance)
        # Opting into an asset increases the MBR by 0.1 ALGO (Global.asset_opt_in_min_balance)
        assert mbr_pay.amount == Global.min_balance + Global.asset_opt_in_min_balance
        itxn.AssetTransfer(
            xfer_asset=self.asset_id,
            asset_receiver=Global.current_application_address,
            asset_amount=0,
        ).submit()
