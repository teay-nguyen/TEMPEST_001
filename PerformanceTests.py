import time

def timeit():
    start = time.time()
    for i in range(10**8):
        continue

    print(time.time() - start)

if __name__ == '__main__':
    timeit()
