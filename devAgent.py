import var as V
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
        fsm.add_transition(source=S_RECEIVING, dest=S_RECEIVING)
        fsm.add_transition(source=S_SENDING, dest=S_RECEIVING)
        sndTemplate = Template()
        sndTemplate.set_metadata("msg", "snd")
        self.add_behaviour(fsm, sndTemplate)

class DeviceBehaviour(FSMBehaviour):
    async def on_start(self):
        self.agent.set("buffer", list())

class StateOne(State): # S_RECEIVING
    async def run(self): # MEJORAR tirar paquetes antes de recibirlos?
        msg = await self.receive()
        if msg:
            while msg: # ensure to receive a burst of messages #
                l = self.agent.get("buffer")
                if len(l) < V.DEV_BUFFSIZE:
                    l.append(msg.body)
                    self.agent.set("buffer", l)
                else: # drop packets
                    V.DEV_DROPPED += 1
                msg = await self.receive()
        else:
            l = self.agent.get("buffer")
            if len(l) > 0:
                self.set_next_state(S_SENDING)
            else:
                self.set_next_state(S_RECEIVING)

class StateTwo(State): # S_SENDING
    async def run(self):
        kernelstatus = self.agent.presence.get_contact(aioxmpp.JID.fromstr("kernel"+V.XMPPSERVER))["presence"].show # DND = sinterrupt
        dev2pol = self.agent.presence.get_contact(aioxmpp.JID.fromstr("kernel"+V.XMPPSERVER))["presence"].status.any()
        if str(kernelstatus) == "PresenceShow.DND" and (V.kernel_calendar_type == 0 or (V.kernel_calendar_type == 1 and dev2pol==self.agent.name) or V.kernel_calendar_type == -1):
            l = self.agent.get("buffer")
            msg = l.pop(0)
            msgtk = Message(to="kernel"+V.XMPPSERVER)  # Instantiate the message
            msgtk.set_metadata("msg", "dev")  # Set the "inform" FIPA
            msgtk.body = msg  # Set the message content
            await self.send(msgtk)
            self.agent.set("buffer", l)
        self.set_next_state(S_RECEIVING)
