import json
import struct

"""MAIN PARSING FUNCTIONS"""
def read_message(ba):
    msg_name, rb = get_msg_name(ba)
    msg_structure, parsed_msg, rb = read_structure(rb, msg_name)
    return msg_name, msg_structure, parsed_msg, rb

def read_structure(ba, struct_name):
    structure = get_structure(struct_name)
    print(struct_name)
    v, rb =  parse_fields(structure, ba)
    return structure, v, rb

def read_array(ba, dt):
    l = interpret_length_specifier(ba)
    ba, rb = split_bytearray(ba[5:], l) 
    format_string = get_format_string(dt, ba)
    v = list(struct.unpack(format_string, ba))
    return v, rb

def read_string(ba):
    l = interpret_length_specifier(ba)
    ba, rb = split_bytearray(ba[5:], l)
    v = ba.decode('utf-8')
    return v, rb

def parse(ba, t):
    for x in t:
        l = format_length(x)
        ba, rb = split_bytearray(ba, l)
        format_string = get_format_string(x)
        v = struct.unpack(format_string, ba)[0]
    return v, rb

def parse_fields(structure, ba):
    parsed_fields = {}
    rb = ba
    for fieldname, dt in structure.items():
        print(structure)
        parsed_field, rb = parse_field(rb, dt)
        parsed_fields[fieldname] = parsed_field
    return parsed_fields, rb

def parse_field(ba, dt):
    print(f"dt: {dt}, type: {type(dt)}")
    print(list(ba))
    if dt[0] == "message":
        _, _, v, rb = read_message(ba)
    elif dt[0] == "struct":
        _, v, rb = read_structure(ba, dt[1])
    elif dt[0] == "array":
        v, rb = read_array(ba, dt[1])
    elif dt[0] == "string":
        v, rb = read_string(ba)
    elif isinstance(dt[0], list):
        v, rb = read_direct(ba, dt[0])
    return v, rb


"""PARSING HELPERS"""
def convert_to_bytearray(string):
    ba = bytearray(int(x) for x in string.split(','))
    return ba

def split_bytearray(ba, l): 
    b = ba[:l]  
    rb = ba[l:] #remaining bytes
    return b, rb

def interpret_length_specifier(ba): 
    return int.from_bytes(ba[1:5], byteorder='little')

def get_format_string(format_char, ba=None):
    repeat_count = get_repeat_count(dt, ba)
    return f'<{repeat_count}{format_char}'

def format_length(fc):
    formats = {
        'B': 1, 'H': 2, 'I': 4, 'Q': 8, 'f': 4, 'd': 8,  # unsigned and floats
        'b': -1, 'h': -2, 'i': -4, 'q': -8,  # signed}
        'c': 1}  # char
    return formats[fc]

def get_repeat_count(dt, ba):
    if ba is None: return 1
    else: return len(ba) // abs(dt)
        
def get_msg_name(ba):
    f = import_file("_opdump.json")
    op = int.from_bytes(ba[1:5], byteorder='little') #opcode
    msg_name = f[str(op)]
    rb = ba[5:]
    return msg_name, rb

def get_structure(name):
    f = import_file("_claude_structs.json")
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

