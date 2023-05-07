#!/bin/env python3
import sys
from collections import deque
from typing import List, Deque

frameCount = 3

def frameIndexToString(idx: int) -> str:
    return chr(ord('A') + idx)

class FIFOEntry:
    # frame: 0->A, 1->B, 2->C
    # page: 1-99
    def __init__(self, frame: int, page: int):
        self.frameIndex = frame
        self.page = page
        self.freezeCounter = 3
        self.refBit = False
    def setRefBit(self):
        self.freezeCounter = 0
        self.refBit = True
    def decreaseFreezeCounter(self):
        if self.freezeCounter != 0:
            self.freezeCounter -= 1
    def __str__(self):
        return f'{frameIndexToString(self.frameIndex)} {self.page} freeze={self.freezeCounter} refBit={"1" if self.refBit else "0"}'

accessedPages: List[int] = []
pageFaults = ""
queue: Deque[FIFOEntry] = deque(maxlen=frameCount)

def printQueue():
    global queue
    for x in queue:
        print(str(x))

def getFrameIndexOfPageInQueue(page: int) -> int:
    global queue
    for x in queue:
        if x.page == page:
            return x.frameIndex
    return None

def getFrameAtIndex(frameIdx: int) -> FIFOEntry:
    global queue
    for x in queue:
        if x.frameIndex == frameIdx:
            return x
    return None

def ageFrames(excluded: FIFOEntry = None):
    global queue
    for x in queue:
        if not x == excluded:
            x.decreaseFreezeCounter()

# def swapOutNotFreezedAndNotRef() -> FIFOEntry:
#     global queue
#     for i, x in enumerate(queue):
#         if x.freezeCounter == 0 and x.refBit == 0:
#             return x
#     return None

for line in sys.stdin:
    arr = line.strip().split(',')
    if len(arr) > 0:
        for x in arr:
            accessedPages.append(abs(int(x)))

for t, requestedPage in enumerate(accessedPages):
    # if t != 0:
    #     print(f't={t}')
    #     print(pageFaults[-1])
    #     printQueue()
    # fifo queue not empty and page not in queue
    if len(queue) != frameCount and getFrameIndexOfPageInQueue(requestedPage) == None:
        queue.append(FIFOEntry(len(queue), requestedPage))
        x = queue[len(queue)-1]
        ageFrames(x)
        pageFaults += frameIndexToString(x.frameIndex)
        continue
    
    # if page is in queue
    if getFrameIndexOfPageInQueue(requestedPage) != None:
        fIdx = getFrameIndexOfPageInQueue(requestedPage)
        f = getFrameAtIndex(fIdx)
        f.setRefBit()
        ageFrames(f)
        pageFaults += "-"
        continue

    toSwapOut = None
    tmpQueue = deque()

    for i, x in enumerate(queue):
        if x.freezeCounter > 0:
            continue
        elif x.refBit:
            x.refBit = False
            tmpQueue.append(x)
        elif not x.refBit:
            toSwapOut = x
            break
    for x in tmpQueue:
        queue.remove(x)
    queue += tmpQueue

    # try again with all non freezed's ref set to 0
    if toSwapOut == None:
        for i, x in enumerate(queue):
            if x.freezeCounter == 0 and not x.refBit:
                toSwapOut = x
                break

    ageFrames()
    
    if toSwapOut != None:
        queue.remove(toSwapOut)
        queue.append(FIFOEntry(toSwapOut.frameIndex, requestedPage))
        pageFaults += frameIndexToString(queue[len(queue)-1].frameIndex)
        continue
    else:
        pageFaults += "*"

# print('t=final')
# print(pageFaults[-1])
# printQueue()

def countPageFault(s: str) -> int:
    return len([c for c in s if c != "-"])

print(pageFaults)
print(countPageFault(pageFaults))
