import memory_graph as mg


def fun1():
    print('fun1')
    print(fun2())
    return 'fun1 return'


def fun2():
    print('fun2')
    print(fun3())
    return 'fun2 return'


def fun3():
    print('fun3')
    print(fun4())
    return 'fun3 return'


def fun4():
    print('fun4')
    return 'fun4 return'


l = [i for i in range(4)]
print(fun1())

def gen(n):
    for i in range(n):
        yield i

for i in gen(3):
    print(i)

dic = {}
for i in range(3):
    try:
        print(dic[i])
    except KeyError as  e:
        print(e)
