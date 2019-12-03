import asyncio
import random
import time
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
            rndDevApp = random.randint(0, len(V.devs))-1
            msg = Message(to=V.devs[rndDevApp])  # Instantiate the message
            msg.set_metadata("msg", "snd")  # Set the "inform" FIPA
            milis = time.time() * 1000
            if not V.sender_devEqApp:
                rndDevApp = random.randint(0, len(V.apps))-1
            msg.body = V.apps[rndDevApp] + ":" + str(milis)  # Set the message content
            V.SND_SENDED += 1
            await self.send(msg)
            await asyncio.sleep(0.1)  # wait
