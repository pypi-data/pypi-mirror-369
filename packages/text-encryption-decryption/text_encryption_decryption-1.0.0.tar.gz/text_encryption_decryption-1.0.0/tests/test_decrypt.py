def decryption(string="141141551751751931371"):
    decrypted = ""
    string1 = (string[int(len(string)/2):])[::-1] + (string[:int(len(string)/2)])[::-1]
    for index in range(0,len(string1),3):
        dec1 = int(string1[index:index+3]) & 0xFF
        dec2 = (dec1 - 1) & 0xFF
        dec3 = (~dec2) & 0xFF
        decrypted += chr(dec3)
    assert decrypted == "Success"