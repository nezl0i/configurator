class ICommand:

    TEST = ['00']
    OPEN_SESSION = ['01']
    CLOSE_SESSION = ['02']
    GET_IDENTIFIER = ['08 05']
    GET_SERIAL = ['08 00']
    GET_EXECUTION = ['08 01 00']
    GET_DESCRIPTOR = ['06 04 1A 04 02']
    GET_VECTORS = ['06 04']
    UPDATE_FIRMWARE = ['07 05']
    GET_PASSWD = ['06 02']
    SET_PASSWD = ['03 1F']
    SET_SPODES = ['03 12']
    GET_EVENT = ['04']
    SET_DATA = ['07']
    SET_METERS = ['07 02']
    GET_SHUNT = ['06 04']
    SET_SHUNT = ['07 01 F4 00 0A']
    SET_SERIAL = ['07 01 EC 00 08']
    CLEAR_METERS = ['03 20']
    GET_TIME = ['04 00']
    SET_TIME = ['03 0C']
    LAST_PROFILE = ['08 13']
    WRITE_BANK_1 = ['07 03']
    WRITE_BANK_2 = ['07 04']

    @staticmethod
    def set_id(new_id):
        for k, v in ICommand.__dict__.items():
            if isinstance(v, list):
                v.insert(0, new_id)

    @staticmethod
    def replace_id(new_id):
        for k, v in ICommand.__dict__.items():
            if isinstance(v, list):
                v[0] = new_id
