from taxUtils import lookup_token_from_quipu_pool

class Tokens:
    """Lazy load token metadata from Quipu contracts."""

    data = {}
    DEBUG = False

    def get(self, quipu_contract):

        if quipu_contract not in self.data:
            if self.DEBUG:
                print("Lookup %s" % quipu_contract)
            if quipu_contract.startswith("KT") == False:
                return None
            self.data[quipu_contract] = lookup_token_from_quipu_pool(quipu_contract, True)
            if self.DEBUG:
                print(self.data[quipu_contract])
        
        return self.data[quipu_contract]