import asyncio
import random
import var as V
from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import CyclicBehaviour

class SndAgent(Agent):
    async def setup(self):
        b = self.SendCyclicBehav()
        self.add_behaviour(b)

    class SendCyclicBehav(CyclicBehaviour):
        async def run(self):
            msg = Message(to=V.devs[random.randint(0, len(V.devs))-1])  # Instantiate the message
            msg.set_metadata("msg", "snd")  # Set the "inform" FIPA
            msg.body = V.apps[random.randint(0, len(V.apps))-1]  # Set the message content
            V.SND_SENDED += 1
            await self.send(msg)
            await asyncio.sleep(2)  # wait
