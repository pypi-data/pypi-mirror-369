import memory_graph as mg
import inspect

def fun():
    x = 100
    frame = inspect.currentframe()
    print(type(frame))
    frameInfos= inspect.getouterframes(frame)
    print(type(frameInfos))
    for f in frameInfos:
        print(' ',type(f))    
    mg.show( mg.stack_slice(frameInfos=frameInfos))

fun()
