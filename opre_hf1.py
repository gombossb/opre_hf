#!/bin/env python3
import sys
from enum import Enum
from typing import List, Deque
from collections import deque

# high prio=1 RR burst=2
# low  prio=0 SRTF

DEBUG = False

class State(Enum):
    CREATED = 0
    WAITING = 1
    # RUNNING = 2
    FINISHED = 3

class Task:
    def __init__(self, letter: str, prio: int, start: int, burst: int):
        self.letter = letter
        self.priority = prio
        self.startTime = start
        self.burstTime = burst
        self.remainingTime = burst
        self.waitTime = 0
        self.state: State = State.CREATED

    def __str__(self) -> str:
        return f'{self.letter} p:{self.priority} s:{self.startTime} {self.state} r:{self.remainingTime} w:{self.waitTime}'
    def finalOutput(self) -> str:
        return f'{self.letter}:{self.waitTime}'

# all the tasks read from stdin
tasks: List[Task] = []
# tasks run in order, added in each clock cycle
runTasks: List[Task] = []
# execOrder = ""

def printTasks(tasks: List[Task]):
    for t in tasks:
        print(t)

for line in sys.stdin:
    arr = line.strip().split(',')
    if (len(arr) == 4):
        t = Task(arr[0], int(arr[1]), int(arr[2]), int(arr[3]))
        tasks.append(t)

def makeCreatedWaitingAt(t: int, tasks: List[Task]):
    for task in tasks:
        if task.state == State.CREATED and task.startTime == t:
            task.state = State.WAITING

def allFinished(tasks: List[Task]) -> bool:
    return len(list(filter(lambda t: t.state != State.FINISHED, tasks))) == 0

def increaseWaitTime(allTasks: List[Task], excluded: Task):
    for t in allTasks:
        if excluded != None and t.state == State.WAITING and t.letter != excluded.letter:
            t.waitTime += 1

def runTask(task: Task):
    if task != None:
        task.remainingTime -= 1
        if task.remainingTime == 0:
            task.state = State.FINISHED

def runOrder(tasks: List[Task]) -> str:
    ret = ""
    for i in range(len(tasks)):
        if tasks[i] != None:
            if len(ret) != 0 and tasks[i].letter == ret[-1]:
                continue
            ret += tasks[i].letter
    return ret

def removeFinished(tasks: Deque[Task]):
    copy = tasks.copy()
    for t in copy:
        if t.state == State.FINISHED:
            tasks.remove(t)

highPrioTasks = list(filter(lambda t: t.priority == 1, tasks))
highPrioQueue = deque()
lowPrioTasks = list(filter(lambda t: t.priority == 0, tasks))
lowPrioQueue = deque()

i = 0
while (True):
    if (DEBUG):
        print('-----')
        print(f'i={i}')
        printTasks(tasks)

    makeCreatedWaitingAt(i, tasks)
    for t in highPrioTasks:
        if t.startTime == i:
            highPrioQueue.append(t)
    for t in lowPrioTasks:
        if t.startTime == i:
            if len(lowPrioQueue) == 0:
                lowPrioQueue.append(t)
            elif t.remainingTime < lowPrioQueue[0].remainingTime:
                lowPrioQueue.appendleft(t)
            else:
                left = lowPrioQueue.popleft()
                lowPrioQueue.append(t)
                lowPrioQueue = deque(sorted(lowPrioQueue, key = lambda t: t.remainingTime))
                lowPrioQueue.appendleft(left)

    if (DEBUG):
        print('::::::::')
        printTasks(tasks)

    selectedTask: Task = None
    if len(highPrioQueue) > 0:
        selectedTask = highPrioQueue.popleft()
        if len(runTasks) == 0 or (len(runTasks) > 0 and runTasks[-1] != selectedTask):
            highPrioQueue.appendleft(selectedTask)
        runTask(selectedTask)
        if selectedTask.remainingTime != 0:
            highPrioQueue.append(selectedTask)

    elif len(lowPrioQueue) > 0:
        selectedTask = lowPrioQueue[0]
        runTask(selectedTask)

    increaseWaitTime(tasks, selectedTask)
    runTasks.append(selectedTask)

    removeFinished(highPrioQueue)
    removeFinished(lowPrioQueue)

    if (DEBUG):
        print('::::::::')
        printTasks(tasks)

    if allFinished(tasks):
        break

    if (DEBUG):
        input()

    i += 1

print(runOrder(runTasks))
fullWaitTime = ','.join(list(map(lambda t: t.finalOutput(), tasks)))
print(fullWaitTime)
