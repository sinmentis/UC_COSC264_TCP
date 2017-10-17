import hashlib

def main():
    
    data_len = 2331234234
    hash_h = hashlib.md5(data_len.to_bytes(4, 'big')).hexdigest()
    print(len(hash_h))


main()