import threading
import time #for delays
import random

def consumeThread_func(id):
    val = 0
    while True:
        print('(',id,') ', '-' * (1+id), val)
        sleepDelay = 0.1 + random.random() * 4
        time.sleep(sleepDelay)
        val += 1


print('Producer-Consumer example')

consumeThreads = []
nConsumeThreads = 10

for i in range(nConsumeThreads):
    consumeThreads.append(threading.Thread(target=consumeThread_func, args=(i,) ))
    consumeThreads[i].start()
