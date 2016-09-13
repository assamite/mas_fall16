import time
import random

import aiomas
import asyncio
from creamas.core import Environment, CreativeAgent
from creamas import mp

from test_agents import TestAgent, TestAgent2

import logging
logging.basicConfig(level=logging.DEBUG)
#asyncio.get_event_loop().set_debug(True)

class TestAgent(CreativeAgent):
    @aiomas.expose
    async def add(self, a, b):
        r = random.random()
        await asyncio.sleep(r)
        print(self.addr, r)
        return a+b

class TestAgent2(CreativeAgent):
    @aiomas.expose
    async def test(self, addr, a, b):
        r_agent = await self.connect(addr)
        ret = await r_agent.add(a, b)
        print(self.addr, addr, ret)

addrs = [('localhost', 5555),
         ('localhost', 5556),
         ('localhost', 5557),
         ('localhost', 5558)]

menv = mp.MultiEnvironment(addr=('localhost', 5550), env_cls=Environment,
                           mgr_cls=mp.MultiEnvManager, slave_env_cls=Environment,
                           slave_mgr_cls=mp.EnvManager, slave_addrs=addrs)
print(menv.manager.addr)
print("prööt")
for _ in range(4):
    ret = aiomas.run(until=asyncio.ensure_future(menv.spawn('test_agents:TestAgent')))
    print(ret)
for _ in range(4):
    ret = aiomas.run(until=asyncio.ensure_future(menv.spawn('test_agents:TestAgent2')))
    print(ret)
time.sleep(4)
menv.destroy()
#menv.shutdown()

'''
e1 = Environment(addr=('localhost', 5555))
e2 = Environment(addr=('localhost', 5556))
e3 = Environment(addr=('localhost', 5557))
e4 = Environment(addr=('localhost', 5558))
ta = [TestAgent(e1) for e in range(5)]
ta4 = [TestAgent(e4) for e in range(5)]
ta2 = [TestAgent2(e2) for e in range(5)]
ta3 = [TestAgent2(e3) for e in range(5)]

print('waiting...')

tasks = []
for i in range(5):
    tasks.append(asyncio.ensure_future(ta2[i].test(ta[i].addr, i, random.random())))
    tasks.append(asyncio.ensure_future(ta3[i].test(ta4[i].addr, i, random.random())))

aiomas.run(until=asyncio.gather(*tasks))

e1.destroy()
e2.destroy()
e3.destroy()
e4.destroy()

import sys
import daemon
exe = sys.executable
print("jea")
with daemon.DaemonContext():
    task = aiomas.subproc.start(('localhost', 5600))
    aiomas.run(until=task)

print("jea")
'''