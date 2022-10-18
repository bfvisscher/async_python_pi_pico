import uasyncio


import collections
async def f():
    await uasyncio.sleep_ms(10)
    

v = f()
print(v)

print(f.__class__)
print(f.__code__.co_flags)
#print(isinstance(v,collections.abc.Awaitable))


