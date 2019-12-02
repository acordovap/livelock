import asyncio
import random
import var as V
from aioxmpp import PresenceState, PresenceShow
from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import FSMBehaviour, State

S_RECEIVING_DEV = "S_RECEIVING_DEV"
S_PROCESS_QUEUE = "S_PROCESS_QUEUE"
S_SENDING2_APP = "S_SENDING2_APP"

class KnlAgent(Agent):
    async def setup(self):
        fsm = KnlBehaviour()
        fsm.add_state(name=S_RECEIVING_DEV, state=StateOne(), initial=True)
        fsm.add_state(name=S_PROCESS_QUEUE, state=StateTwo())
        fsm.add_state(name=S_SENDING2_APP, state=StateThree())
        fsm.add_transition(source=S_RECEIVING_DEV, dest=S_PROCESS_QUEUE)
        fsm.add_transition(source=S_RECEIVING_DEV, dest=S_SENDING2_APP)
        fsm.add_transition(source=S_PROCESS_QUEUE, dest=S_RECEIVING_DEV)
        fsm.add_transition(source=S_SENDING2_APP, dest=S_RECEIVING_DEV)
        devTemplate = Template()
        devTemplate.set_metadata("msg", "dev")
        self.add_behaviour(fsm, devTemplate)

class KnlBehaviour(FSMBehaviour):
    async def on_start(self):
        self.agent.set("ipintrq", list())
        self.agent.set("outputifqueue", list())
        # print("kernel started")

class StateOne(State): # S_RECEIVING_DEV
    async def on_start(self):
        self.agent.presence.set_presence(state=PresenceState(True), status="sinterrupt")

    async def run(self):
        msg = await self.receive()
        if msg:
            V.KNL_RECEIVED += 1
            msg2A = Message(to=msg.body)
            msg2A.set_metadata("msg", "knl")
            msg2A.body = str(random.randint(0, V.KNL_MAXTIMEPROC))
            l = self.agent.get("ipintrq")
            l.append(msg2A)
            self.agent.set("ipintrq", l)
            self.set_next_state(S_PROCESS_QUEUE)
        else:
            self.set_next_state(S_SENDING2_APP)

class StateTwo(State): # S_PROCESS_QUEUE
    async def on_start(self):
        self.agent.presence.set_presence(state=PresenceState(True), status="running")

    async def run(self):
        l = self.agent.get("ipintrq")
        msg2A = l.pop(0)
        self.agent.set("ipintrq", l)
        await asyncio.sleep(int(msg2A.body)) # cambiar por for ?
        l = self.agent.get("outputifqueue")
        l.append(msg2A)
        self.agent.set("outputifqueue", l)
        self.set_next_state(S_RECEIVING_DEV)

class StateThree(State): # S_SENDING2_APP
    async def on_start(self):
        self.agent.presence.set_presence(state=PresenceState(True), status="wait")

    async def run(self):
        l = self.agent.get("outputifqueue")
        if len(l) > 0:
            msg2A = l.pop(0)
            await self.send(msg2A)
            V.KNL_SENDED += 1
        self.set_next_state(S_RECEIVING_DEV)
