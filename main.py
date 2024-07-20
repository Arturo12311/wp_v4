



"""IMPORTS"""
import struct
import json
import re
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('_names.json', 'r') as f:
    names = json.load(f)
with open('_structs.json', 'r') as f:
    structs = json.load(f)
with open('_log.json', 'r') as f:
    log = json.load(f)


"""MAIN CODE"""
class Msg:
    def __init__(self, ba):
        """
        maps bytes to opcode, then finds the structure
        sends the structure and bytes to parser
        """
        self.nb, self.rb = self.split_null(ba)
        if self.is_null(self.nb):
            self.op = None; self.name = None; self.struct = None; self.msg = None; self.rb = ba[1:]
        else:
            self.hb, self.rb = self.split_header(self.rb)
            self.op = self.read_header(self.hb)
            self.name = names[str(self.op)]
            self.struct = structs[self.name]
            self.msg, self.rb = self.parse_struct(self.name, self.rb)

    
    def split_null(self, ba):
        return ba[:1], ba[1:]
    def is_null(self, nb):
        if struct.unpack("?", nb)[0] == 1:
            return True

    def split_header(self, ba):
        return ba[:4], ba[4:]
    def read_header(self, hb):
        return struct.unpack("<I", hb)[0]

    def parse_struct(self, name, rb):
        # print(name)
        if name[-1] == "0":
            nb, rb = self.split_null(rb)
            if nb not in [b'\x00', b'\x01']: exit()
            if self.is_null(nb): return None, rb
            struct = structs[name[:-1]]
        else:
            struct = structs[name]
        ps = {}
        for k, v in struct.items():
            # print(k)
            pf, rb = self.parse(v, rb)
            ps[k] = pf
        return ps, rb

    def parse(self, x, rb):
        # print(x)
        # print(list(rb[:50]))
        if x == "msg":
            msg = Msg(rb); pf = msg.msg; rb = msg.rb
        elif isinstance(x, dict):
            pf, rb = self.pm(x, rb)
        elif isinstance(x, list):
            pf, rb = self.pa(x, rb)
        elif re.match("FTz.*", x):
            pf, rb = self.parse_struct(x[3:], rb)
        elif isinstance(x, str):
            pf, rb = self.p(x, rb)
        return pf, rb
    
    def pm(self, x, rb):
        nb, rb = self.split_null(rb)
        if nb not in [b'\x00', b'\x01']: exit()
        if self.is_null(nb):
            # print("NULL")
            return None, rb
        else:
            pm = {}
            hb, rb = self.split_header(rb)
            l = self.read_header(hb)
            t1, t2 = next(iter(x.items()))
            for _ in range(0, l):
                v1, rb = self.parse(t1, rb)
                v2, rb = self.parse(t2, rb)
                pm[v1] = v2
        return pm, rb
    
    def pa(self, x, rb):
        nb, rb = self.split_null(rb)
        if nb not in [b'\x00', b'\x01']: exit()
        if self.is_null(nb):
            print("NULL")
            return None, rb
        else:
            pa = []
            hb, rb = self.split_header(rb)
            l = self.read_header(hb)
            t = x[0]
            for _ in range (0, l):
                v, rb = self.parse(t, rb)
                pa.append(v)
        return pa, rb
    
    def p(self, x, rb):
        if x == "s":
            v, rb = self.ps(rb)
            return v, rb
        elif x[-1] == "0":
            nb, rb = self.split_null(rb)
            
            if self.is_null(nb):
    
                # print("NULL")
                return None, rb
            else:
                fs = f"<{x[:-1]}"
        elif re.match(r"ETzBuildingAccessPermissionKindType|ETzAffectSourceSystemCastKindType|ETzResultCodeType|ETzCharacterStateType|ETzConnectionStatusType|ETzMountInteractionStateType|ETzContaminationNaturalDecreaseType|ETzBuildingAccessPermissionKindType", x):
            fs = "<I"
        elif re.match("ETz.*", x):
            fs = "<B"
        elif x == "?":
            if rb[:1] not in [b'\x00', b'\x01']: exit()
            fs = f"<{x}"
        else:
            fs = f"<{x}"
        size = struct.calcsize(fs)
        v = struct.unpack(fs, rb[:size])
        if len(v) == 1: v = v[0]
        return v, rb[size:]
    
    def ps(self, rb):
        nb, rb = self.split_null(rb)
        if nb not in [b'\x00', b'\x01']: exit()
        if self.is_null(nb):
            # print("NULL")
            return None, rb
        
        hb, rb = self.split_header(rb)
        l = self.read_header(hb)
        fs = f"{l}s"
        size = struct.calcsize(fs)
        v = struct.unpack(fs, rb[:size])
        if len(v) == 1: v = v[0]
        return v.decode('utf-8', errors='ignore'), rb[size:]
    



"""HELPERS"""

def convert_to_bytearray(string):
    ba = bytearray(int(x) for x in string.split(','))
    return ba

def print_dict(name, dict):
    print(f"\"{name}\": {{")
    for key, value in dict.items():
        print(f"    {key}: {value}")
    print(f"  }}")


"""RUN"""
def main():
    output = {}
    for k, v in log.items():
        # if k != "PlayerInitializeInfoNotify":
        #     continue


        # read message
        ba = convert_to_bytearray(v)
        msg = Msg(ba)

        # store message data
        output[msg.name] = {
            "msg": msg.msg,
            "remainder": list(msg.rb or [])
        }

        # print debugging
        print("\n\n")
        print("-" * 100)
        print("-" * 100)
        print(f"{list(ba)}")
        print("---")
        print(msg.name)
        print("---")
        print_dict(msg.name, msg.struct)
        print("---")
        print_dict(msg.name, msg.msg)
        print("---")
        print(f"remaining bytes: {list(msg.rb or [])}")
        print("---")

            
    # Write all output to JSON file at once
    # with open('output.json', 'w') as f:
    #     json.dump(output, f, indent=2)
main()