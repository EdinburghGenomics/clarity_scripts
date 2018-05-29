def start_proportion(line):
    return int(line.split('\t')[6])/int(line.split('\t')[3])

if __name__ == "__main__":
    print("I am being run as a script!")
else:
    print("I am being imported as a module!")