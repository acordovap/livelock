import var as V
from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import CyclicBehaviour

class AppAgent(Agent):
    async def setup(self):
        b = self.AppCyclicBehav()

        knlTemplate = Template()
        knlTemplate.set_metadata("msg", "knl")
        self.add_behaviour(b, knlTemplate)

    class AppCyclicBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()
            if msg:
                V.APP_RECEIVED += 1
