import time
import variables as V
import aioxmpp
from aioxmpp import PresenceState, PresenceShow
from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import FSMBehaviour, State

S_RECEIVING = "S_RECEIVING"
S_SENDING = "S_SENDING"

class DevAgent(Agent):
    async def setup(self):
        fsm = DeviceBehaviour()
        fsm.add_state(name=S_RECEIVING, state=StateOne(), initial=True)
        fsm.add_state(name=S_SENDING, state=StateTwo())
        fsm.add_transition(source=S_RECEIVING, dest=S_SENDING)
        fsm.add_transition(source=S_SENDING, dest=S_RECEIVING)
        t = Template()
        t.set_metadata("msg", "snd")
        self.add_behaviour(fsm, t)

class DeviceBehaviour(FSMBehaviour):
    async def on_start(self):
        self.agent.set("buffer", list())

class StateOne(State):
    async def run(self): # MEJORAR tirar paquetes antes de recibirlos?
        msg = await self.receive()
        if msg:
            while msg: # ensure to receive a burst of messages #
                V.DEV_RECEIVED += 1
                l = self.agent.get("buffer")
                if len(l) < V.DEVBUFFSIZE:
                    l.append(msg.body)
                    self.agent.set("buffer", l)
                else: # drop packets
                    V.DEV_DROPPED += 1
                msg = await self.receive()
        else:
            self.set_next_state(S_SENDING)

class StateTwo(State):
    async def run(self):
        l = self.agent.get("buffer")
        if len(l) > 0:
            kernelstatus = self.agent.presence.get_contact(aioxmpp.JID.fromstr("kernel"+V.XMPPSERVER))["presence"].status.any()
            if kernelstatus == "sinterrupt":
                msg = l.pop(0)
                msgtk = Message(to="kernel"+V.XMPPSERVER)  # Instantiate the message
                msgtk.set_metadata("msg", "net")  # Set the "inform" FIPA
                msgtk.body = msg  # Set the message content
                await self.send(msgtk)
                self.agent.set("buffer", l)
        self.set_next_state(S_RECEIVING)
