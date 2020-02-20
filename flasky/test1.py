import pickle

def read_enumerator():
    with open("enumerator.bin", "rb") as reader:
        x = pickle.load(reader)
    return x

def write_enumerator(x):
    with open("enumerator.bin", "wb") as writer:
        pickle.dump(x, writer)