import threading    # for Threads and Conditions
import time         # for delays
import random       # add some randomness
import pygame       # present the results in a graphical way


queue = []  # main queue with working elements (a sequence of integers)
max_queue_size = 7
condition = threading.Condition()   # main Condition Variable to control the queue
render_condition = threading.Condition()

nConsumeThreads = 4
currentConsumeItem = [-1 for i in range(nConsumeThreads)]
consumeOrder = [0 for i in range(nConsumeThreads)]
nLocked = 0

nMinProduceAtOnce = 2  # minimum number of work items produce during a single produce iteration
nMaxProduceAtOnce = 5  # maximum number of work items produce during a single produce iteration

box_size = 30
consume_scale = 7   # scale of the consume order boxes
gaps_between_boxes = 90     #consumers
margin_between_boxes = 50   # produced queue


def producerThread_func():
    global nLocked
    val = 0
    while True:     # forewer
        sleepDelay = 0.1 + random.random() * 2
        time.sleep(sleepDelay)
        # let it render
        with render_condition:
            render_condition.notify()

        available_capacity = max_queue_size - len(queue)
        if (available_capacity > 0):
            nItemsToAdd = random.randint( min(nMinProduceAtOnce, available_capacity), min(nMaxProduceAtOnce, available_capacity) )   # several items pro iteration

            with condition:

                nLocked += 1

                for i in range(nItemsToAdd):
                    queue.append(val)
                    val += 1

                # report the producing results. Keep it under the condition to make it simple and not use a mutex for print
                nLocked -= 1

                # the producer iteration is over, let the consumers to proceed
                condition.notify_all()

            

def consumeThread_func(id):
    global nLocked

    while True:     # forewer
        with condition:
            # wait for a work item
            while not queue:
                condition.wait()
                if not queue:
                    pass    # print(f"Consumer ({id}) has nothing to do")

            nLocked += 1

            val = queue.pop(0)

            # report the consuming work item. Keep it under the condition to make it simple and not use a mutex for print
            currentConsumeItem[id] = val
            update_consume_order(id)

            nLocked -= 1


        # perform the processing of the work item
        with render_condition:
            render_condition.notify()
        sleepDelay = 0.1 + random.random() * 4
        time.sleep(sleepDelay)
        currentConsumeItem[id] = -2
        with render_condition:
            render_condition.notify()
        # relax after work is done
        sleepDelay = 0.5 + random.random() * 0.5
        time.sleep(sleepDelay)
        currentConsumeItem[id] = -1
        with render_condition:
            render_condition.notify()


# recent = index of the latest updated consumer (its id)
def update_consume_order(recent):
    c = consumeOrder[recent]
    for i in range(len(consumeOrder)):
        if consumeOrder[i] <= c:
            consumeOrder[i] += 1
    consumeOrder[recent] = 0

# draw a single cell in the position with the number
def draw_cell(pos,size,n, hollow):
    # 1) box
    pygame.draw.rect(canvas, box_color, (pos[0]-size/2, pos[1]-size/2, size,size), 1 if hollow else 0)

    # 2) text inside
    if not hollow:
        text_str = str(n)
        text_surface = my_font.render(text_str, False, (255, 255, 255))
        tw, th = text_surface.get_width(), text_surface.get_height()
        canvas.blit(text_surface, (pos[0]-tw/2, pos[1]-th/2))


pygame.init()
canvas_bounds = (1024,512)
canvas_center = (canvas_bounds[0]/2, canvas_bounds[1]/2)
canvas = pygame.display.set_mode(canvas_bounds)
pygame.font.init() # you have to call this at the start, if you want to use this module.
my_font = pygame.font.SysFont('Arial', 16)
back_color = (9,16,35)
box_color = (50,192,70)


# start multiple consumers
consumeThreads = []

for i in range(nConsumeThreads):
    consumeThreads.append(threading.Thread(target=consumeThread_func, args=(i,) ))
    consumeThreads[i].start()

# start the producer
producerThread = threading.Thread(target=producerThread_func)
producerThread.start()


#MAIN: game loop
exit = False
while not exit:

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = True

    x, y = pygame.mouse.get_pos()
    
    # main drawing
    with render_condition:
        while nLocked > 0:
            render_condition.wait()

    # single render update
    canvas.fill(back_color)

    # produced
    for i,n in enumerate(queue):
        draw_cell((canvas_center[0], canvas_bounds[1] - 140 - i * margin_between_boxes), box_size, n, False)

    # consumes
    nc = len(currentConsumeItem)
    px = (canvas_bounds[0] - gaps_between_boxes*(nc-1)) / 2
    for i,n in enumerate(currentConsumeItem):
        if n != -1:
            draw_cell((px + i * gaps_between_boxes, canvas_bounds[1]-box_size-30), box_size + consume_scale*(nc - consumeOrder[i]), n, n==-2)

    #display the results
    pygame.display.update()



# ..wait till the work is done
for i in range(len(consumeThreads)):
    consumeThreads[i].join()
    print(f"Thread {i} finished")
