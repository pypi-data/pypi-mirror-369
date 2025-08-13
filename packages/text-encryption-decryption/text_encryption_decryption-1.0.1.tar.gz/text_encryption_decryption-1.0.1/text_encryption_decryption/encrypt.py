def encryption(string):
    encrypted=""
    numbers=""
    twos = []
    for ch in string:
        b=ord(ch)
        ones=(~b) & 0xFF
        tw=(ones+1) & 0xFF
        twos.append(tw)
    for num in twos:
        numbers+=str(num)
    encrypted = (numbers[int(len(numbers)/2):])[::-1] + (numbers[:int(len(numbers)/2)])[::-1]
    return encrypted