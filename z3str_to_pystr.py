def z3str_to_pystr(z3str):
    first = ord(z3str[0])
    last = ord(z3str[len(z3str)-1])
    if((first==34)and(last==34))or((first==39)and(last==39)):
        print("quote")
        z3str = z3str[1:-1]
    index = 0
    result = ''
    while(index<len(z3str)):
        hex_index = z3str.find("\\x",index)
        print("hex_index",hex_index)
        if hex_index != -1:
            hex_value = (ord(z3str[hex_index+2]) - 48) * 16 + ord(z3str[hex_index+3]) - 48
            print("high",ord(z3str[hex_index+2]))
            print("low",ord(z3str[hex_index+3]))
            print("hex_value",hex_value)
            hex_char = chr(hex_value)
            result = result + z3str[index:hex_index]
            index = hex_index + 4
            result = result + hex_char
        else:
            result = result + z3str[index:]
            break
    return result

tmp = z3str_to_pystr("'\\x00\\x00\\x30\\x30abc\\x30\\x30youxyz\\x32\\x33'")
print(tmp)
print(len(tmp))
print(tmp[0])
print(tmp[1])
print(tmp[2])
tmp = z3str_to_pystr('"\\x00\\x00\\x30\\x30abc\\x30\\x30youxyz\\x32\\x33"')
print(tmp)
print(len(tmp))
print(tmp[0])
print(tmp[1])
print(tmp[2])


