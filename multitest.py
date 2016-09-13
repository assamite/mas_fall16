import time
import random

import aiomas
import asyncio
from creamas.core import Environment, CreativeAgent, Simulation
from creamas.core.environment import MultiEnvironment

addrs = [('localhost', 5555)]

addrs1 = [('localhost', 5555),
          ('localhost', 5556),
          ('localhost', 5557),
          ('localhost', 5558)]

addrs2 = [('localhost', 5565),
          ('localhost', 5566),
          ('localhost', 5567),
          ('localhost', 5568)]

class TestAgent(CreativeAgent):
    @aiomas.expose
    async def add(self, a, b):
        r = random.random()
        await asyncio.sleep(r)
        print(self.addr, r)
        return a+b

    @aiomas.expose
    async def act(self, *args, **kwargs):
        r = random.random()
        await asyncio.sleep(r)
        print(self.addr, r)


class TestAgent2(CreativeAgent):
    @aiomas.expose
    async def test(self, addr, a, b):
        r_agent = await self.connect(addr)
        ret = await r_agent.add(a, b)
        print(self.addr, addr, ret)

    @aiomas.expose
    async def act(self, *args, **kwargs):
        addr = 'tcp://localhost:5555/0'
        r1 = random.random()
        r2 = random.random()
        await self.test(addr, r1, r2)

me1 = MultiEnvironment(addrs1)
me2 = MultiEnvironment(addrs2)

for _ in range(10):
    a = me1.spawn(TestAgent)
    a.qualname()
    print(a.addr)
    a = me2.spawn(TestAgent2)

sim = Simulation(me2, log_folder='logs')
t = time.time()
sim.async_steps(10)
print(time.time() - t)
sim.end()