import asyncio
import random
import time
import math
import numpy as np
import var as V
from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour

class SndAgent(Agent):
    async def setup(self):
        p = V.sender_period
        if V.sender_type == 0: # Constant
            b = self.ConstantB(period=p)
        elif V.sender_type == 1: # Uniform
            b = self.UnifB(period=p)
        elif V.sender_type == 2: # Normal
            b = self.NormalB(period=p)
        elif V.sender_type == 3: # Gamma
            b = self.GammaB(period=p)
        else: # LognormalB
            b = self.LognormalB(period=p)
        self.add_behaviour(b)

    class ConstantB(PeriodicBehaviour):
        async def run(self):
            rndDevApp = random.randint(0, len(V.devs))-1
            msg = Message(to=V.devs[rndDevApp])  # Instantiate the message
            msg.set_metadata("msg", "snd")  # Set the "inform" FIPA
            milis = time.time() * 1000
            if not V.sender_devEqApp:
                rndDevApp = random.randint(0, len(V.apps))-1
            msg.body = V.apps[rndDevApp] + ":" + str(milis)  # Set the message content
            V.SND_SENDED += 1
            await self.send(msg)

    class UnifB(PeriodicBehaviour):
        async def run(self):
            a = 0
            b = 1
            mu = (b-a)/2
            sd = math.sqrt(((b-a)**2)/12)
            x = np.random.uniform(mu, sd, 1)[0]
            if x > (mu - sd) and x < (mu + sd):
                rndDevApp = random.randint(0, len(V.devs))-1
                msg = Message(to=V.devs[rndDevApp])  # Instantiate the message
                msg.set_metadata("msg", "snd")  # Set the "inform" FIPA
                milis = time.time() * 1000
                if not V.sender_devEqApp:
                    rndDevApp = random.randint(0, len(V.apps))-1
                msg.body = V.apps[rndDevApp] + ":" + str(milis)  # Set the message content
                V.SND_SENDED += 1
                await self.send(msg)

    class NormalB(PeriodicBehaviour):
        async def run(self):
            mu = 0
            sd = 0.1
            x = np.random.normal(mu, sd, 1)[0]
            if x > (mu - sd) and x < (mu + sd):
                rndDevApp = random.randint(0, len(V.devs))-1
                msg = Message(to=V.devs[rndDevApp])  # Instantiate the message
                msg.set_metadata("msg", "snd")  # Set the "inform" FIPA
                milis = time.time() * 1000
                if not V.sender_devEqApp:
                    rndDevApp = random.randint(0, len(V.apps))-1
                msg.body = V.apps[rndDevApp] + ":" + str(milis)  # Set the message content
                V.SND_SENDED += 1
                await self.send(msg)

    class GammaB(PeriodicBehaviour):
        async def run(self):
            shape, scale = 2., 2.  # mean=4, std=2*sqrt(2)
            mu = 4
            sd = 2*math.sqrt(2)
            x = np.random.gamma(shape, scale, 1)[0]
            if x > (mu - sd) and x < (mu + sd):
                rndDevApp = random.randint(0, len(V.devs))-1
                msg = Message(to=V.devs[rndDevApp])  # Instantiate the message
                msg.set_metadata("msg", "snd")  # Set the "inform" FIPA
                milis = time.time() * 1000
                if not V.sender_devEqApp:
                    rndDevApp = random.randint(0, len(V.apps))-1
                msg.body = V.apps[rndDevApp] + ":" + str(milis)  # Set the message content
                V.SND_SENDED += 1
                await self.send(msg)

    class LognormalB(PeriodicBehaviour):
        async def run(self):
            mu = 3.
            sd = 1.
            x = np.random.lognormal(mu, sd, 1)[0]
            if x > (mu - sd) and x < (mu + sd):
                rndDevApp = random.randint(0, len(V.devs))-1
                msg = Message(to=V.devs[rndDevApp])  # Instantiate the message
                msg.set_metadata("msg", "snd")  # Set the "inform" FIPA
                milis = time.time() * 1000
                if not V.sender_devEqApp:
                    rndDevApp = random.randint(0, len(V.apps))-1
                msg.body = V.apps[rndDevApp] + ":" + str(milis)  # Set the message content
                V.SND_SENDED += 1
                await self.send(msg)
