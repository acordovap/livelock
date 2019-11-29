import time
import asyncio
import variables as V
import aioxmpp
from aioxmpp import PresenceState, PresenceShow
from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import FSMBehaviour, State
from spade.behaviour import OneShotBehaviour
from spade.behaviour import CyclicBehaviour

class KernelAgent(Agent):

    async def setup(self):
        print("init kernel")
        self.set("buffer", list())
        self.set("queue_procs", list())
        dev = self.RecvDevsBehav()
        app = self.RecvAppsBehav()
        proc = self.ProcBehav()
        devTemplate = Template()
        devTemplate.set_metadata("msg", "net")
        appTemplate = Template()
        appTemplate.set_metadata("msg", "proc")
        self.add_behaviour(app, appTemplate)
        self.add_behaviour(dev, devTemplate)
        self.add_behaviour(proc)
        self.presence.set_presence(state=PresenceState(True), status="idle")


    class RecvAppsBehav(CyclicBehaviour):
        async def run(self):
            # print("hearing apps " + self.agent.presence.status[None])
            if self.agent.presence.status[None]=="idle":
                self.agent.presence.set_presence(state=PresenceState(True), status="wait")
                msg = await self.receive()
                if msg:
                    l = self.agent.get("queue_procs")
                    l.append(msg.body)
                    self.agent.set("queue_procs", l)
            if self.agent.presence.status[None]=="wait":
                self.agent.presence.set_presence(state=PresenceState(True), status="idle")


    class ProcBehav(CyclicBehaviour):
        async def run(self):
            if self.agent.presence.status[None]=="idle":
                l = self.agent.get("queue_procs")
                if len(l) > 0:
                    self.agent.presence.set_presence(state=PresenceState(True), status="running")
                    await asyncio.sleep(int(l.pop(0)))
                    self.agent.set("queue_procs", l)
                    self.agent.presence.set_presence(state=PresenceState(True), status="idle")

    class RecvDevsBehav(CyclicBehaviour):

        async def run(self):
            if self.agent.presence.status[None] == "idle":
                self.agent.presence.set_presence(state=PresenceState(True), status="sinterrupt")
            msg = await self.receive()
            while msg:
                V.K_RECEIVED += 1
                for b in self.agent.behaviours: # SOFTWARE INTERRUPT
                    if str(b)=="CyclicBehaviour/RecvAppsBehav" or str(b)=="CyclicBehaviour/ProcBehav":
                        self.agent.remove_behaviour(b)
                l = self.agent.get("buffer")
                l.append(msg.body)
                self.agent.set("buffer", l)
                msg = await self.receive()
            if len(self.agent.behaviours) == 1:
                l = self.agent.get("buffer")
                while len(l) > 0:
                    m = l.pop(0)
                    msg = Message(to=m)     # Instantiate the message
                    msg.body = "appmsg"                  # Set the message content
                    V.K_SENDED += 1
                    await self.send(msg)
                app = self.agent.RecvAppsBehav()
                proc = self.agent.ProcBehav()
                appTemplate = Template()
                appTemplate.set_metadata("msg", "proc")
                self.agent.add_behaviour(app, appTemplate)
                self.agent.add_behaviour(proc)
            if self.agent.presence.status[None] == "sinterrupt":
                self.agent.presence.set_presence(state=PresenceState(True), status="idle")
