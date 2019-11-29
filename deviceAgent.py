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

import random

class DeviceAgent(Agent):
    async def setup(self):
        b = self.RecvCyclicBehav()
        senderTemplate = Template()
        senderTemplate.set_metadata("msg", "net")
        self.add_behaviour(b, senderTemplate)

    class RecvCyclicBehav(CyclicBehaviour):
        async def on_start(self):
            self.agent.presence.set_presence(state=PresenceState(True), status="ready")
            self.agent.set("buffer", list())

        async def run(self):
            msg = await self.receive()  # check if message is received
            # receiving
            while msg:  # ensure to receive a burst of messages # DEVICE INTERRUPT
                V.DEV_RECEIVED += 1
                self.agent.presence.set_presence(state=PresenceState(True), status="receiving")
                l = self.agent.get("buffer")
                if len(l) < V.DEVBUFFSIZE:
                    l.append(msg.body)
                    self.agent.set("buffer", l)
                else: # DROP PACKETS
                    V.DEV_DROPPED += 1
                msg = await self.receive()
            l = self.agent.get("buffer")
            # waiting
            if len(l) > 0:
                self.agent.presence.set_presence(state=PresenceState(True), status="waiting")
                # checar al kernel y enviar mensaje cuando kernel sinterrupt
                kernelstatus = self.agent.presence.get_contact(aioxmpp.JID.fromstr("kernel"+V.XMPPSERVER))["presence"].status.any()
                if kernelstatus == "sinterrupt":
                    msg = l.pop(0)
                    msgtk = Message(to="kernel"+V.XMPPSERVER)  # Instantiate the message
                    msgtk.set_metadata("msg", "net")  # Set the "inform" FIPA
                    msgtk.body = msg  # Set the message content
                    await self.send(msgtk)
                    self.agent.set("buffer", l)
            # ready
            if len(l) == 0:
                self.agent.presence.set_presence(state=PresenceState(True), status="ready")
