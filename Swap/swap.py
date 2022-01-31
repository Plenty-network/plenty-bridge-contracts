import smartpy as sp

class ContractLibrary(sp.Contract):
    
    def TransferFATwoTokens(sender,reciever,amount,tokenAddress,id):

        arg = [
            sp.record(
                from_ = sender,
                txs = [
                    sp.record(
                        to_         = reciever,
                        token_id    = id , 
                        amount      = amount 
                    )
                ]
            )
        ]

        transferHandle = sp.contract(
            sp.TList(sp.TRecord(from_=sp.TAddress, txs=sp.TList(sp.TRecord(amount=sp.TNat, to_=sp.TAddress, token_id=sp.TNat).layout(("to_", ("token_id", "amount")))))), 
            tokenAddress,
            entry_point='transfer').open_some()

        sp.transfer(arg, sp.mutez(0), transferHandle)

    def Mint(amount, reciever, tokenAddress,id):
        
        arg = sp.record(address = reciever, amount = amount, token_id = id, metadata = sp.map(l={}))
        

        transferHandle = sp.contract(
            sp.TRecord(address=sp.TAddress, amount = sp.TNat, token_id = sp.TNat, metadata = sp.TMap(sp.TString, sp.TBytes)), 
            tokenAddress,
            entry_point='mint').open_some()

        sp.transfer(arg, sp.mutez(0), transferHandle)
        
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
