import asyncio
import random
import var as V
from aioxmpp import PresenceState, PresenceShow
from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import CyclicBehaviour
from spade.behaviour import FSMBehaviour, State

S_RECEIVING_DEV = "S_RECEIVING_DEV"
S_PROCESS_QUEUE = "S_PROCESS_QUEUE"
S_SENDING2_APP = "S_SENDING2_APP"

class KnlAgentIntr(Agent): # kernel_type = 0
    async def setup(self):
        fsm = KnlBehaviour()
        fsm.add_state(name=S_RECEIVING_DEV, state=StateOne(), initial=True)
        fsm.add_state(name=S_PROCESS_QUEUE, state=StateTwo())
        fsm.add_state(name=S_SENDING2_APP, state=StateThree())
        fsm.add_transition(source=S_RECEIVING_DEV, dest=S_RECEIVING_DEV)
        fsm.add_transition(source=S_RECEIVING_DEV, dest=S_PROCESS_QUEUE)
        fsm.add_transition(source=S_RECEIVING_DEV, dest=S_SENDING2_APP)
        fsm.add_transition(source=S_PROCESS_QUEUE, dest=S_RECEIVING_DEV)
        fsm.add_transition(source=S_PROCESS_QUEUE, dest=S_SENDING2_APP)
        fsm.add_transition(source=S_SENDING2_APP, dest=S_RECEIVING_DEV)
        fsm.add_transition(source=S_SENDING2_APP, dest=S_PROCESS_QUEUE)
        devTemplate = Template()
        devTemplate.set_metadata("msg", "dev")
        self.add_behaviour(fsm, devTemplate)
        if V.kernel_calendar_type == 2:
            self.set("hybrid", True)
            V.kernel_calendar_type = 0
        else:
            self.set("hybrid", False)
        self.set("intrDisabled", False)
        if V.kernel_infering_ll == 1:
            mon = MonCPUS()
            self.add_behaviour(mon)

class MonCPUS(CyclicBehaviour):
    async def on_start(self):
        self.set("DNDcont", 0)

    async def run(self):
        await asyncio.sleep(0.1)  # wait
        if str(self.agent.presence.state.show) == "PresenceShow.DND":
            c = self.agent.get("DNDcont")
            if c >= V.KNL_DNDTH:
                if self.agent.get("hybrid"):
                    V.kernel_calendar_type = 1
                else:
                    self.agent.set("intrDisabled", True)
            else:
                self.agent.set("DNDcont", c+1)
        else:
            self.agent.set("DNDcont", 0)

class KnlBehaviour(FSMBehaviour):
    async def on_start(self):
        self.agent.set("currentDev", 0)
        self.agent.set("ipintrq", list())
        self.agent.set("outputifqueue", list())
        self.agent.presence.set_presence(status="dev00") # default for devAgent.py function

class StateOne(State): # S_RECEIVING_DEV
    async def on_start(self):
        self.agent.presence.set_presence(state=PresenceState(available=True, show=PresenceShow.DND)) # DND = sinterrupt
        if V.kernel_calendar_type == 1:
            cd = self.agent.get("currentDev")
            self.agent.presence.set_presence(status="dev"+str(cd).zfill(2))
            self.agent.set("currentDev", (cd+1) % len(V.devs))

    async def run(self):
        self.set_next_state(S_RECEIVING_DEV)
        msg = await self.receive()
        if msg:
            l = self.agent.get("ipintrq")
            if V.kernel_calendar_type == 0 and V.kernel_infering_ll == 0 and len(l)+1 == V.KNL_IPINTRQLEN: # interrupt calendar, infer w/buffersize
                l.append(msg)
                self.agent.set("ipintrq", l)
                self.set_next_state(S_PROCESS_QUEUE)
                if self.agent.get("hybrid"):
                    V.kernel_calendar_type = 1
                else:
                    self.agent.set("intrDisabled", True)
            elif len(l) < V.KNL_IPINTRQLEN:
                l.append(msg)
                self.agent.set("ipintrq", l)
            else:
                V.KNL_DROPPED += 1
        else:
            l = self.agent.get("outputifqueue")
            if len(l) > 0:
                self.set_next_state(S_SENDING2_APP)
            else:
                l = self.agent.get("ipintrq")
                if len(l) > 0:
                    self.set_next_state(S_PROCESS_QUEUE)

class StateTwo(State): # S_PROCESS_QUEUE
    async def on_start(self):
        self.agent.presence.set_presence(state=PresenceState(available=True, show=PresenceShow.CHAT))

    async def run(self):
        l = self.agent.get("ipintrq")
        msg = l.pop(0)
        data = msg.body.split(":")
        msg2A = Message(to=data[0])
        msg2A.set_metadata("msg", "knl")
        msg2A.body = data[1]
        self.agent.set("ipintrq", l)
        op = 0 # IP fw layer
        for i in range(V.KNL_CYCLEPROC):
            op += i
        l = self.agent.get("outputifqueue")
        l.append(msg2A)
        self.agent.set("outputifqueue", l)
        if self.agent.get("intrDisabled") or (V.kernel_calendar_type == 1 and self.agent.get("hybrid")): # interrupt calendar, infer w/buffersize
            if len(l) > V.KNL_IPINTRQLEN * (V.KNL_BUFFTH/100):
                self.set_next_state(S_SENDING2_APP)
            else:
                self.set_next_state(S_RECEIVING_DEV)
                if V.kernel_calendar_type == 1:
                    V.kernel_calendar_type = 0
                else:
                    self.set("intrDisabled", False)
        else :
            self.set_next_state(S_RECEIVING_DEV)


class StateThree(State): # S_SENDING2_APP
    async def on_start(self):
        self.agent.presence.set_presence(state=PresenceState(available=True, show=PresenceShow.CHAT))

    async def run(self):
        l = self.agent.get("outputifqueue")
        msg2A = l.pop(0)
        self.agent.set("outputifqueue", l)
        await self.send(msg2A)
        if self.agent.get("intrDisabled") and len(l) > V.KNL_IPINTRQLEN * (V.KNL_BUFFTH/100): # interrupt calendar, infer w/buffersize
            self.set_next_state(S_PROCESS_QUEUE)
        else:
            self.set_next_state(S_RECEIVING_DEV)
