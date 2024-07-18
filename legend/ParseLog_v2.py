import json 

"""UTILITIES"""
def import_file(x):
    with open(x, 'r') as file:
        z = json.load(file)
    return z


class Msg:
    def __init__(self, string):
        self.bytes = self.str_to_bytes(string)
        self.name = self.get_name()
        self.structure = self.get_structure()
        # self.msg, self.rest = self.read_msg()

    def str_to_bytes(self, string):
        bytes = bytearray(int(i) for i in string.split(','))
        return bytes

    def get_name(self):
        file = import_file("_opdump.json")
        opcode = int.from_bytes(self.bytes[1:5], byteorder='little')
        name = file[str(opcode)]
        return name

    @classmethod
    def get_structure(self, name=None):
        if name is None:
            name = self.name
        file = import_file("_log_structs.json")
        structure = file[name]
        return structure

    def read_msg(self):
        parser = Parser(self.bytes, self.structure)
        msg, rest = parser.parse_fields()
        return msg, rest


class Parser:
    def __init__(self, bytes, structure):
        self.bytes = bytes
        self.structure = structure

    def parse_fields(self):
        msg = {}
        for field, type in self.structure.items():
            value, self.bytes = self.parse_field(type, self.bytes)
            msg[field] = value
        return msg, self.bytes
            
    def parse_field(self, type, bytes):
        if type[0] == "message":
            msg = Msg(bytes)
            value, rest = msg.read_msg()
        elif type[0] == "struct":
            struct = Msg.get_structure(type[1])
        elif isinstance(type[0], int):
            pass
        return value, rest





"""MAIN"""
def main():

    # for all msgs in log
    log = import_file("_log.json")
    for k, v in log.items():
        msg = Msg(v)
        print("--------------------")
        print(msg.bytes)
        print(msg.name)
        print(msg.structure)
        # print(msg.msg)
        # print(msg.rest)
main()