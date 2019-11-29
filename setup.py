import time
import getpass
import variables as V
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.behaviour import CyclicBehaviour


class Oagent(Agent):
    async def setup(self):
        print("Agent {} running".format(self.name))
        self.add_behaviour(self.Behav1())

    class Behav1(OneShotBehaviour):
        def on_subscribe(self, jid):
            print("[{}] Agent {} asked for subscription. Let's aprove it.".format(self.agent.name, jid.split("@")[0]))
            self.presence.approve(jid)
            # self.kill(exit_code=0)

        def on_subscribed(self, jid):
            print("[{}] Agent {} has accepted the subscription.".format(self.agent.name, jid.split("@")[0]))

        # async def on_end(self):
        #     print("[{}] finished".format(self.agent.name))
        #     await self.agent.stop()


        async def run(self):
            self.presence.on_subscribe = self.on_subscribe
            self.presence.on_subscribed = self.on_subscribed
            self.presence.set_available()
            self.presence.subscribe(self.agent.k)


class Kagent(Agent):
    async def setup(self):
        print("Agent {} running".format(self.name))
        self.add_behaviour(self.Behav2())

    class Behav2(CyclicBehaviour):

        def on_subscribe(self, jid):
            print("[{}] Agent {} asked for subscription. Let's aprove it.".format(self.agent.name, jid.split("@")[0]))
            self.presence.approve(jid)
            self.presence.subscribe(jid)
        def on_subscribed(self, jid):
            print("[{}] Agent {} has accepted the subscription.".format(self.agent.name, jid.split("@")[0]))
            self.agent.contador+=1

        async def run(self):
            self.presence.set_available()
            self.presence.on_subscribe = self.on_subscribe
            self.presence.on_subscribed = self.on_subscribed


if __name__ == "__main__":

    # jid0 = input("kernel> ")+V.XMPPSERVER
    jid0 = "kernel" + V.XMPPSERVER
    passwd0 = "Kernel!"#getpass.getpass()
    ka = Kagent(jid0, passwd0)
    ka.contador = 0
    ka.start()
    ka.web.start(hostname="127.0.0.1", port="50000")

    # inicializamos los devices
    for i in range(30):#V.ndevs):
        jid1 = "dev"+ str(i).zfill(2) + V.XMPPSERVER
        passwd1 = "Dev" + str(i).zfill(2) + "!"
        a1 = Oagent(jid1, passwd1)
        a1.k = jid0
        a1.start()
        a1.web.start(hostname="127.0.0.1", port="100" + str(i).zfill(2))

    # inicializamos las apps
    for i in range(30):#V.napps):
        jid1 = "app"+ str(i).zfill(2) + V.XMPPSERVER
        passwd1 = "App" + str(i).zfill(2) + "!"
        a1 = Oagent(jid1, passwd1)
        a1.k = jid0
        a1.start()
        a1.web.start(hostname="127.0.0.1", port="200" + str(i).zfill(2))

    while True: #ka.contador<V.napps+V.ndevs:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    # quit_spade()
