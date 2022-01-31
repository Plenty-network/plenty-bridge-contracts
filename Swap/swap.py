import smartpy as sp

class Swap(sp.Contract):
    def __init__(self, _oldTokenAddress, _newTokenAddress, admin): 
        self.init(
            admin = admin,
            oldTokenAddress = _oldTokenAddress, 
            newTokenAddress = _newTokenAddress,
            locked = False
        )

    @sp.entry_point
    def swapTokens(self,params):
        sp.set_type(params, sp.TRecord(tokenId = sp.TNat, amount = sp.TNat))
        ContractLibrary.TransferFATwoTokens(sp.sender, sp.self_address, params.amount, self.data.oldTokenAddress, params.tokenId)
        ContractLibrary.Mint(params.amount, sp.sender, self.data.newTokenAddress, params.tokenId)

    @sp.entry_point
    def setAddress(self,params):
        sp.set_type(params, sp.TRecord(oldTokenAddress = sp.TAddress, newTokenAddress = sp.TAddress))
        sp.verify(sp.sender == self.data.admin, message = "Not Admin")
        sp.verify(~self.data.locked, message = "Already set")
        self.data.locked = True
        self.data.oldTokenAddress = params.oldTokenAddress
        self.data.newTokenAddress = params.newTokenAddress