

class IBModelFactory:

    def __init__(self, ref_data_mgr):
        self.__ref_data_mgr = ref_data_mgr

    def create_ib_order(self, order):
        pass

    def create_ib_contract(self, inst_id):
        pass