import os

def iterator(path):
    children = os.listdir(path)
    while children:
        yield children.pop()

for child in iterator(r'C:\studio'):
    print child
