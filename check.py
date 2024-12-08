import time
sourceContent : str
destContent : str
print("\033c")
while True:
    with open("image.jpg","rb") as source:
        sourceContent = source.read()
    with open("output.jpg" , "rb") as dst:
        destContent = dst.read()
    print(f"Simple check ,Size (SRC) : {len(sourceContent)}, (DST) : {len(destContent)} , (MATCH?) : {len(sourceContent) == len(destContent)}")
    fail = False
    for i in range(len(sourceContent)):
        if (sourceContent[i] != destContent[i]):
            print(f"Error at {i}")
            fail = True
            break
    if not fail:
        print("Check Pass")
        break
    else:
        break

# for i in sourceContent:
