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
        
        arg = [sp.record(owner = reciever, amount = amount, token_id = id)]
        

        transferHandle = sp.contract(
            sp.TList(sp.TRecord(owner=sp.TAddress, amount = sp.TNat, token_id = sp.TNat)), 
            tokenAddress,
            entry_point='mint_tokens').open_some()

        sp.transfer(arg, sp.mutez(0), transferHandle)
    



class Swap(sp.Contract):
    def __init__(self, _oldTokenAddress, _newTokenAddress, admin, _tokenMapping = sp.map(l = {}, tkey = sp.TNat, tvalue = sp.TNat)): 
        self.init(
            admin = admin,
            oldTokenAddress = _oldTokenAddress, 
            newTokenAddress = _newTokenAddress,
            tokenMapping = _tokenMapping,
            locked = False
        )

    # def getTokenId(self, tokenId):
    #     newTokenid = sp.local('newTokenid', 100)
    #     sp.if tokenId == 1:
    #         newTokenid.value = 0 #busd
    #     sp.if tokenId == 11:
    #         newTokenid.value = 1 #matic
    #     sp.if tokenId == 17:
    #         newTokenid.value = 2 #usdc  
    #     sp.if tokenId == 18:
    #         newTokenid.value = 3 #usdt
    #     sp.if tokenId == 19:
    #         newTokenid.value = 4 #btc
    #     sp.if tokenId == 20:
    #         newTokenid.value = 5 #eth
    #     sp.if tokenId == 10:
    #         newTokenid.value = 6 #link
    #     sp.if tokenId == 5:
    #         newTokenid.value = 7 #dai
    #     return newTokenid.value

    @sp.entry_point
    def swapTokens(self,params):
        sp.set_type(params, sp.TRecord(tokenId = sp.TNat, amount = sp.TNat))
        sp.verify(self.data.tokenMapping.contains(params.tokenId), "ErrorMessage.AssetNotSwapable")
        newTokenId = sp.local('newTokenId', self.data.tokenMapping[params.tokenId])
        ContractLibrary.TransferFATwoTokens(sp.sender, sp.self_address, params.amount, self.data.oldTokenAddress, params.tokenId)
        ContractLibrary.Mint(params.amount, sp.sender, self.data.newTokenAddress, newTokenId.value)

    @sp.entry_point
    def setAddress(self,params):
        sp.set_type(params, sp.TRecord(oldTokenAddress = sp.TAddress, newTokenAddress = sp.TAddress))
        sp.verify(sp.sender == self.data.admin, message = "ErrorMessage.NotAdmin")
        sp.verify(~self.data.locked, message = "ErrorMessage.AlreadySet")
        self.data.locked = True
        self.data.oldTokenAddress = params.oldTokenAddress
        self.data.newTokenAddress = params.newTokenAddress
    
    @sp.entry_point
    def addMapping(self, oldTokenId, newTokenId):
        sp.set_type(oldTokenId, sp.TNat)
        sp.set_type(newTokenId, sp.TNat)
        sp.verify(sp.sender == self.data.admin, message = "ErrorMessage.NotAdmin")
        sp.for x in self.data.tokenMapping.values():
            sp.verify(x !=  newTokenId, message = "ErrorMessage.TokenAlreadyExists")
        sp.verify(~self.data.tokenMapping.contains(oldTokenId), message = "ErrorMessage.MappingAlreadyExists")
        self.data.tokenMapping[oldTokenId] = newTokenId