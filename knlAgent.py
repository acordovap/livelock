import time
import variables as V
import aioxmpp
import asyncio
from aioxmpp import PresenceState, PresenceShow
from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import FSMBehaviour, State

S_RECEIVING_DEV = "S_RECEIVING_DEV"
S_RECEIVING_APP = "S_RECEIVING_APP"
S_PROCESS_QUEUE = "S_PROCESS_QUEUE"

class KnlAgent(Agent):
    async def setup(self):
        fsm = KnlBehaviour()
        fsm.add_state(name=S_RECEIVING_DEV, state=StateOne(), initial=True)
        fsm.add_state(name=S_RECEIVING_APP, state=StateTwo())
        fsm.add_state(name=S_PROCESS_QUEUE, state=StateThree())
        fsm.add_transition(source=S_RECEIVING_DEV, dest=S_RECEIVING_APP)
        fsm.add_transition(source=S_RECEIVING_APP, dest=S_PROCESS_QUEUE)
        fsm.add_transition(source=S_PROCESS_QUEUE, dest=S_RECEIVING_DEV)
        self.add_behaviour(fsm)

class KnlBehaviour(FSMBehaviour):
    async def on_start(self):
        self.agent.set("buffer", list())
        self.set("queue_procs", list())

class StateOne(State):
    async def run(self):
        self.agent.presence.set_presence(state=PresenceState(True), status="sinterrupt")
        devTemplate = Template()
        devTemplate.set_metadata("msg", "net")
        self.set_template(devTemplate)
        msg = await self.receive()
        if msg:
            while msg: # no hay inptq
                V.K_RECEIVED += 1
                msgA = Message(to=msg.body)
                msgA.body = "appmsg"
                V.K_SENDED += 1
                await self.send(msgA)
                msg = await self.receive()
        else:
            self.set_next_state(S_RECEIVING_APP)

    async def on_start(self):
        devTemplate = Template()
        devTemplate.set_metadata("msg", "net")
        self.set_template(devTemplate)

class StateTwo(State):
    async def run(self):
        self.agent.presence.set_presence(state=PresenceState(True), status="wait")
        appTemplate = Template()
        appTemplate.set_metadata("msg", "proc")
        self.set_template(appTemplate)
        msg = await self.receive()
        if msg:
            l = self.agent.get("queue_procs")
            if  msg.body =="app00@102mcc13.inge.itam.mx":
                print(msg.sender)
            if self.match(msg):
                print("si")
            else:
                print("no")
            l.append(msg.body)
            self.agent.set("queue_procs", l)
        self.set_next_state(S_PROCESS_QUEUE)

    async def on_start(self):
        appTemplate = Template()
        appTemplate.set_metadata("msg", "proc")
        self.set_template(appTemplate)

class StateThree(State):
    async def run(self):
        self.agent.presence.set_presence(state=PresenceState(True), status="running")
        l = self.agent.get("queue_procs")
        if len(l) > 0:
            await asyncio.sleep(int(l.pop(0))) # cambiar por for?
            self.agent.set("queue_procs", l)
        self.set_next_state(S_RECEIVING_DEV)
