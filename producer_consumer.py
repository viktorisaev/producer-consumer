import threading    # for Threads and Conditions
import time         # for delays
import random       # add some randomness

queue = []  # main queue with working elements (a sequence of integers)
condition = threading.Condition()   # main Condition Variable to control the queue

nProduceAtOnce = 5  # number of work items produce during a single produce iteration


def producerThread_func():
    val = 0
    print("Start producing...")
    while True:     # forewer
        sleepDelay = 0.1 + random.random() * 2
        time.sleep(sleepDelay)
        nItemsToAdd = random.randint(1,nProduceAtOnce)   # 1..4 items pro iteration

        with condition:
            for i in range(nItemsToAdd):
                queue.append(val)
                val += 1

            # report the producing results. Keep it under the condition to make it simple and not use a mutex for print
            print(f"Produce={val-nItemsToAdd}-{val-1}({nItemsToAdd}), total={len(queue)}")

            # the producer iteration is over, let the consumers to proceed
            condition.notify_all()

            

def consumeThread_func(id):
    while True:     # forewer
        with condition:
            # wait for a work item
            while not queue:
                condition.wait()
                if not queue:
                    print(f"Consumer ({id}) has nothing to do")
            
            val = queue.pop(0)

            # report the consuming work item. Keep it under the condition to make it simple and not use a mutex for print
            print('(',id,') ', '-' * (1+id), val)

        # perform the processing of the work item
        # relax after work is done
        sleepDelay = 0.1 + random.random() * 4
        time.sleep(sleepDelay)


print('Producer-Consumer example')

# start multiple consumers
consumeThreads = []
nConsumeThreads = 5

for i in range(nConsumeThreads):
    consumeThreads.append(threading.Thread(target=consumeThread_func, args=(i,) ))
    consumeThreads[i].start()

# start the producer
producerThread = threading.Thread(target=producerThread_func)
producerThread.start()

# ..wait till the work is done
for i in range(len(consumeThreads)):
    consumeThreads[i].join()
    print(f"Thread {i} finished")


print("We are done!!!")
