import smartpy as sp

FA2_TOKEN = sp.io.import_script_from_url("file:./Tokens/FA2_multi_minter.py")

SWAP = sp.io.import_script_from_url("file:./Swap/swap.py")

class TestClass(sp.Contract): 
    def __init__(self): 
        self.init(
            balance = sp.nat(0), 
            balanceOf = sp.none,
        )

    @sp.entry_point
    def getBalance(self, params, tokenAddress):
        sp.set_type(params, sp.TRecord(owner = sp.TAddress,token_id = sp.TNat).layout(("owner", "token_id")))
        sp.set_type(tokenAddress, sp.TAddress)
        balance = sp.view("get_balance_view", tokenAddress, params,  t = sp.TNat).open_some("Invalid view")
        self.data.balance = balance

    @sp.entry_point
    def getBalanceOf(self, params, tokenAddress):
        sp.set_type(params, sp.TRecord(owner = sp.TAddress,token_id = sp.TNat).layout(("owner", "token_id")))
        sp.set_type(tokenAddress, sp.TAddress)
        balanceOf = sp.view("balance_of_view", tokenAddress, params,  t = sp.TRecord(request = sp.TRecord(owner = sp.TAddress,token_id = sp.TNat), balance = sp.TNat)).open_some("Invalid view")
        self.data.balanceOf = sp.some(balanceOf)

def global_parameter(env_var, default):
    try:
        if os.environ[env_var] == "true" :
            return True
        if os.environ[env_var] == "false" :
            return False
        return default
    except:
        return default

if "templates" not in __name__:
    @sp.add_test(name = "SwapTests")
    def test():
        admin = sp.test_account("Admin")
        alice = sp.test_account("Alice")
        bob = sp.test_account("Bob")
        cat = sp.test_account("Cat")
        minter1 = sp.test_account("Minter1")
        minter2 = sp.test_account("Minter2")
        
        config = FA2_TOKEN.FA2_config(
                debug_mode = global_parameter("debug_mode", False),
                single_asset = global_parameter("single_asset", False),
                non_fungible = global_parameter("non_fungible", False),
                add_mutez_transfer = global_parameter("add_mutez_transfer", False),
                readable = global_parameter("readable", True),
                force_layouts = global_parameter("force_layouts", True),
                support_operator = global_parameter("support_operator", True),
                assume_consecutive_token_ids =
                    global_parameter("assume_consecutive_token_ids", True),
                store_total_supply = global_parameter("store_total_supply", False),
                lazy_entry_points = global_parameter("lazy_entry_points", False),
                allow_self_transfer = global_parameter("allow_self_transfer", False),
                use_token_metadata_offchain_view = global_parameter("use_token_metadata_offchain_view", True),
            )
        scenario = sp.test_scenario()

        scenario.h1("Initializing swap")
        c1 = SWAP.Swap(
            _oldTokenAddress = sp.address("KT1VoHhkb6wXnoPDvcpbnPFYGTcpJaPfRoEh"),
            _newTokenAddress = sp.address("KT1EZBn43coqL6xfT5xL6e49nhEPLp9B8m4n"),
            admin = admin.address,
            _tokenMapping = {1: 0, 17: 2, 18: 3, 19: 4, 20: 5, 10: 6, 5: 7}
        )

        scenario += c1

        scenario.h1("Creating old token")
        oldToken = FA2_TOKEN.FA2(config = config,
                 metadata = sp.utils.metadata_of_url("https://example.com"),
                 admin = admin.address,
                 minter1 = minter1.address,
                 minter2 = minter2.address)
        scenario += oldToken

        scenario.h1("Creating new token")
        newToken = FA2_TOKEN.FA2(config = config,
                 metadata = sp.utils.metadata_of_url("https://example.com"),
                 admin = admin.address,
                 minter1 = minter1.address,
                 minter2 = c1.address)
        scenario += newToken
        
        scenario.h1("Setting addresses")
        c1.setAddress(sp.record(oldTokenAddress = oldToken.address, newTokenAddress = newToken.address)).run(sender = admin)

        scenario.h1("Minting/Creating old token id = 0")
        oldTok1_md = FA2_TOKEN.FA2.make_metadata(
            name = "wAave",
            decimals = 18,
            symbol= "wAave")
        oldToken.mint(address = bob.address,
                            amount = 100,
                            metadata = oldTok1_md,
                            token_id = 0).run(sender = minter1)

        scenario.h1("Minting/Creating old token id = 1")
        oldTok2_md = FA2_TOKEN.FA2.make_metadata(
            name = "wUSDT",
            decimals = 18,
            symbol= "wUSDT")
        oldToken.mint(address = bob.address,
                            amount = 100,
                            metadata = oldTok2_md,
                            token_id = 1).run(sender = minter1)

        scenario.h1("Minting/Creating new token id = 0")
        newTok1_md = FA2_TOKEN.FA2.make_metadata(
            name = "USDT.e",
            decimals = 6,
            symbol= "USDT.e")
        newToken.mint(address = admin.address,
                            amount = 0,
                            metadata = newTok1_md,
                            token_id = 0).run(sender = minter1)

        scenario.h1("Minting/Creating new token id = 1")
        newTok2_md = FA2_TOKEN.FA2.make_metadata(
            name = "UAave.e",
            decimals = 6,
            symbol= "UAave.e")
        newToken.mint(address = admin.address,
                            amount = 0,
                            metadata = newTok2_md,
                            token_id = 1).run(sender = minter1)

        scenario.h1("Setting Swap as opreator for bob's old token --> 0")
        oldToken.update_operators([
                sp.variant("add_operator", oldToken.operator_param.make(
                    owner = bob.address,
                    operator = c1.address,
                    token_id = 0
                ))
            ]).run(sender = bob, valid = True)

        scenario.h1("Setting Swap as opreator for bob's old token --> 1")
        oldToken.update_operators([
                sp.variant("add_operator", oldToken.operator_param.make(
                    owner = bob.address,
                    operator = c1.address,
                    token_id = 1
                ))
            ]).run(sender = bob, valid = True)

        scenario.h1("Swapping old token for new one")
        c1.swapTokens(sp.record(tokenId = 1, amount = 50)).run(sender = bob)

        scenario.h1("Adding mapping")
        c1.addMapping(sp.record(oldTokenId = 0, newTokenId = 1)).run(sender = admin)

        scenario.h1("Locking Minter 1")
        newToken.lockMinter1().run(sender = admin)

        scenario.h1("Trying to mint from locked minter")
        newToken.mint(address = admin.address,
                            amount = 0,
                            metadata = newTok2_md,
                            token_id = 1).run(sender = minter1, valid = False)

        scenario.h1("Locking Minter 2")
        newToken.lockMinter2().run(sender = admin)

        scenario.h1("Swapping old token for new one --> 0, when minter is locked")
        c1.swapTokens(sp.record(tokenId = 0, amount = 50)).run(sender = bob, valid = False)

        scenario.h1("unLocking Minter 2")
        newToken.unlockMinter2().run(sender = admin)

        scenario.h1("Swapping old token for new one --> 0")
        c1.swapTokens(sp.record(tokenId = 0, amount = 50)).run(sender = bob)

        scenario.h1("unLocking Minter 1")
        newToken.unlockMinter1().run(sender = admin)
        
        scenario.h1("Testing views")
        c2 = TestClass()
        scenario += c2

        scenario.h1("Testing balance view")
        c2.getBalance(sp.record(params = sp.record(owner = bob.address, token_id = 0), tokenAddress = oldToken.address))
        scenario.verify(c2.data.balance == oldToken.data.ledger[sp.pair(bob.address, sp.nat(0))].balance)

        scenario.h1("Testing balanceOf view")
        c2.getBalanceOf(sp.record(params = sp.record(owner = bob.address, token_id = 0), tokenAddress = oldToken.address))
        scenario.verify(c2.data.balanceOf == sp.some(sp.record(request = sp.record(owner = bob.address, token_id = 0), balance = oldToken.data.ledger[sp.pair(bob.address, sp.nat(0))].balance)))
