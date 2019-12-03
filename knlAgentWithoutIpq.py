import asyncio
import random
import var as V
from aioxmpp import PresenceState, PresenceShow
from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import FSMBehaviour, State

S_RECDEV_PROC = "S_RECDEV_PROC"
S_SENDING2_APP = "S_SENDING2_APP"

class KnlAgentWithoutIpq(Agent):
    async def setup(self):
        fsm = KnlBehaviour()
        fsm.add_state(name=S_RECDEV_PROC, state=StateOne(), initial=True)
        fsm.add_state(name=S_SENDING2_APP, state=StateTwo())
        fsm.add_transition(source=S_RECDEV_PROC, dest=S_RECDEV_PROC)
        fsm.add_transition(source=S_RECDEV_PROC, dest=S_SENDING2_APP)
        fsm.add_transition(source=S_SENDING2_APP, dest=S_RECDEV_PROC)
        devTemplate = Template()
        devTemplate.set_metadata("msg", "dev")
        self.add_behaviour(fsm, devTemplate)


class KnlBehaviour(FSMBehaviour):
    async def on_start(self):
        self.agent.set("currentDev", 0)
        self.agent.set("outputifqueue", list())

class StateOne(State): # S_RECDEV_PROC
    async def on_start(self):
        self.agent.presence.set_presence(state=PresenceState(available=True, show=PresenceShow.DND)) # DND = sinterrupt
        # print(self.agent.presence.state.show)
        # self.agent.presence.set_presence(state=PresenceState(True), status="sinterrupt")
        if V.kernel_calendar_type == 1:
            cd = self.agent.get("currentDev")
            devTemplate = Template()
            devTemplate.set_metadata("msg", "dev")
            devTemplate.sender = V.devs[cd]
            self.agent.behaviours[0].set_template(devTemplate)
            self.agent.set("currentDev", (cd+1) % len(V.devs))

    async def run(self):
        self.set_next_state(S_RECDEV_PROC)
        msg = await self.receive()
        if msg:
            data = msg.body.split(":")
            msg2A = Message(data[0])
            msg2A.set_metadata("msg", "knl")
            msg2A.body = str(data[1])
            op = 0 # IP fw layer
            for i in range(V.KNL_CYCLEPROC):
                op += i
            l = self.agent.get("outputifqueue")
            if len(l) < V.KNL_IPINTRQLEN:
                l.append(msg2A)
                self.agent.set("outputifqueue", l)
            else:
                V.KNL_DROPPED += 1
        else:
            l = self.agent.get("outputifqueue")
            if len(l) > 0:
                self.set_next_state(S_SENDING2_APP)

class StateTwo(State): # S_SENDING2_APP
    async def on_start(self):
        self.agent.presence.set_presence(state=PresenceState(available=True, show=PresenceShow.CHAT))
        # self.agent.presence.set_presence(state=PresenceState(True), status="S_SENDING2_APP")

    async def run(self):
        self.set_next_state(S_RECDEV_PROC)
        l = self.agent.get("outputifqueue")
        msg2A = l.pop(0)
        self.agent.set("outputifqueue", l)
        await self.send(msg2A)
