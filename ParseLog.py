import json
import struct

"""MAIN PARSING FUNCTIONS"""
def read_message(ba):
    msg_name, rb = get_msg_name(ba)
    msg_structure, parsed_msg, rb = read_structure(rb, msg_name)
    return msg_name, msg_structure, parsed_msg, rb

def read_structure(ba, struct_name):
    structure = get_structure(struct_name)
    v, rb =  parse_fields(structure, ba)
    return structure, v, rb

def read_array(ba, array_type):
    ba, rb = split_bytearray(ba) 
    format_string = get_format_string(ba, array_type)
    v = list(struct.unpack(format_string, ba))
    return v, rb

def read_string(ba):
    ba, rb = split_bytearray(ba)
    v = ba.decode('utf-8')
    return v, rb

def read_direct(ba):
    v = get_format_string(ba[:1], 1)
    rb = ba[1:]
    return v, rb

def parse_fields(structure, ba):
    parsed_fields = {}
    rb = ba
    for fieldname, type in structure.items():
        parsed_field, rb = parse_field(rb, type)
        parsed_fields[fieldname] = parsed_field
    return parsed_fields, rb

def parse_field(ba, type):
    if type[0] == "message":
        _, _, v, rb = read_message(ba)
    elif type[0] == "struct":
        _, v, rb = read_structure(ba, type[1])
    elif type[0] == "array":
        v, rb = read_array(ba, type[1])
    elif type[0] == "string":
        v, rb = read_string(ba)
    elif isinstance(type[0], int):
        v, rb = read_direct(ba)
    return v, rb


"""PARSING HELPERS"""
def convert_to_bytearray(string):
    ba = bytearray(int(x) for x in string.split(','))
    return ba

def split_bytearray(ba): 
    # for datatypes with lengthspecifier 
    l = int.from_bytes(ba[1:5], byteorder='little')
    ba = ba[5:]
    b = ba[:l]  
    rb = ba[l:] #remaining bytes
    return b, rb

def get_format_string(ba, type):
    repeat_count = len(ba) // abs(type)
    if type > 0:  
        format_char = {1: 'B', 2: 'H', 4: 'I', 8: 'Q'}[type] #signed
    else:  
        format_char = {1: 'b', 2: 'h', 4: 'i', 8: 'q'}[abs(type)] #unsigned
    return f'<{repeat_count}{format_char}'

def get_msg_name(ba):
    f = import_file("_opdump.json")
    op = int.from_bytes(ba[1:5], byteorder='little') #opcode
    msg_name = f[str(op)]
    rb = ba[5:]
    return msg_name, rb

def get_structure(name):
    f = import_file("_structures.json")
    structure = f[name]
    return structure


"""OTHER HELPERS"""
def print_msg_name(msg_name):
    print(f"{msg_name}")

def print_structure_info(msg_name, msg_structure):
    print_dict(msg_name, msg_structure)

def print_parsed_msg(msg_name, parsed_msg):
    print_dict(msg_name, parsed_msg)

def print_dict(name, dict):
    print(f"\"{name}\": {{")
    for key, value in dict.items():
        print(f"    {key}: {value}")
    print(f"  }}")

def import_file(filename):
    with open(filename, 'r') as f:
        content = json.load(f)
    return content


"""MAIN LOGIC"""
f = import_file("_log.json")
for fieldname, byte_string in f.items():

    # read message
    ba = convert_to_bytearray(byte_string)
    msg_name, msg_structure, msg, rb = read_message(ba)

    # print message
    print("\n\n")
    print("-" * 100)
    print("-" * 100)
    print(f"{list(convert_to_bytearray(byte_string))}")
    print("---")
    print_msg_name(msg_name)
    print("---")
    print_structure_info(msg_name, msg_structure)
    print("---")
    print_parsed_msg(msg_name, msg)
    print("---")
    print(f"remaining bytes: {list(rb)}")
    print("---")

