# Convert file to list

def toArray(file):
    return [line.rstrip('\n') for line in open(file)]