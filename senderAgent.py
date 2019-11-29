import time
import asyncio
import random
import variables as V
from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import FSMBehaviour, State
from spade.behaviour import OneShotBehaviour
from spade.behaviour import CyclicBehaviour

class SenderAgent(Agent):
    async def setup(self):
        b = self.SendCyclicBehav()
        self.add_behaviour(b)

    class SendCyclicBehav(CyclicBehaviour):
        async def on_start(self):
            self.agent.set("counter_out", 0)

        async def run(self):
            msg = Message(to=V.devs[random.randint(0, len(V.devs))-1])     # Instantiate the message
            msg.set_metadata("msg", "net")  # Set the "inform" FIPA
            msg.body = V.apps[random.randint(0, len(V.apps))-1]                # Set the message content
            # print(f"[{self.agent.name}] Message sended: {msg.body}")
            V.SND_SENDED += 1
            await self.send(msg)
            #await asyncio.sleep(1)

            self.agent.set("counter_out", self.agent.get("counter_out")+ 1)
            # await asyncio.sleep(1)

            # stop agent from behaviour
            # await self.agent.stop()

        async def on_end(self):
            print(f"[{self.agent.name}] Behaviour finished with exit code {self.exit_code}")
            # print("Behaviour finished with exit code {}.".format(self.exit_code))
