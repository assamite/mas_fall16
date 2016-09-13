'''
Some test agents to test multiple containers in different subprocesses.
'''
import aiomas

def qualname(cls):
    return "{}.{}".format(cls.__module__, cls.__class__.__name__)

class TestAgent2(aiomas.Agent):
    @aiomas.expose
    async def hello(self):
        msg = "Hello from {}".format(self.addr)
        print("Hello")
        with open("hello_world.txt", 'w+') as f:
            f.write("{}\n".format(msg))
        return msg

class TestAgent(aiomas.Agent):

    @aiomas.expose
    async def test_conn(self, addr='tcp://localhost:5600/0'):
        remote_agent = await self.container.connect(addr)
        ret = await remote_agent.hello()
        print(ret)

    @aiomas.expose
    async def spawn_demand(self, agent_cls, addr='tcp://localhost:5600/0'):
        remote_agent = await self.container.connect(addr)
        agent, addr = await remote_agent.spawn(agent_cls)
        print(agent)
        print(addr)
