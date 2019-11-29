import time
import asyncio
import random
import aioxmpp
from aioxmpp import PresenceState, PresenceShow

import variables as V
from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import FSMBehaviour, State
from spade.behaviour import OneShotBehaviour
from spade.behaviour import CyclicBehaviour

class AppAgent(Agent):
    async def setup(self):
        # self.set("n_procs", 0)
        self.set("procs", list())
        b = self.SendCyclicBehav()
        c = self.GenProcCyclicBehav()
        self.add_behaviour(b)
        self.add_behaviour(c)

    class GenProcCyclicBehav(CyclicBehaviour):
        # async def on_start(self):
        #     print("starting behav app")

        async def run(self):
            msg = await self.receive() # check if message is received
            if msg:# or random.randint(0, 100) > V.APP_PROBPROC:
                l = self.agent.get("procs")
                l.append(random.randint(0, V.APP_MAXTIMEPROC))
                self.agent.set("procs", l)
                # self.agent.set("n_procs", self.agent.get("n_procs") + 1)
                # await asyncio.sleep(random.randint(0, V.APP_TIMEBTWPROCS))

    class SendCyclicBehav(CyclicBehaviour):
        async def on_start(self):
            self.agent.presence.set_presence(state=PresenceState(True), status="ready")
            # self.agent.presence.subscribe("kernel"+V.XMPPSERVER)

        async def run(self):
            l = self.agent.get("procs")
            if len(l) > 0:
                # checar estatus kernel, si puede recibir procesos sacar de cola, generar msg y enviar
                kernelstatus = self.agent.presence.get_contact(aioxmpp.JID.fromstr("kernel"+V.XMPPSERVER))["presence"].status.any()
                # print(kernelstatus)
                if kernelstatus == "wait":
                    msg = Message(to="kernel"+V.XMPPSERVER)     # Instantiate the message
                    msg.set_metadata("msg", "proc")  # Set the "inform" FIPA performative
                    msg.body = str(l.pop(0))                  # Set the message content
                    await self.send(msg)
                    self.agent.set("procs", l)
                # self.agent.set("counter_out", self.agent.get("counter_out")+ 1)
                # await asyncio.sleep(1)

                # stop agent from behaviour
                # await self.agent.stop()

        async def on_end(self):
            print(f"[{self.agent.name}] Behaviour finished with exit code {self.exit_code}")
            # print("Behaviour finished with exit code {}.".format(self.exit_code))
