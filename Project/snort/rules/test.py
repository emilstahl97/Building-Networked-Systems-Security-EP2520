
with open("standard-rules.txt", "r") as f:
    with open("standard-rules-new.txt", "w") as f1:
        for line in f:
            print(line)
            new = "include " + line
            f1.write(new)
            