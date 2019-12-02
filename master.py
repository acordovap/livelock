import asyncio
import time
import var as V
import aioxmpp
from aioxmpp import PresenceState, PresenceShow
from spade.template import Template
from devAgent import DevAgent
from knlAgent import KnlAgent
from appAgent import AppAgent
from sndAgent import SndAgent
from spade import quit_spade

if __name__ == "__main__":

    k = KnlAgent("kernel"+V.XMPPSERVER, "Kernel!")
    k.start().result()
    k.web.start(hostname="127.0.0.1", port="50000")

    ndev = int(input("Ingrese el número de devices a desplegar (1-99)> "))
    napps = int(input("Ingrese el número de apps a desplegar (1-99)> "))
    nsnd = int(input("Ingrese el número de senders a desplegar (1-99)> "))

    # apps init
    for i in range(napps):
        a = AppAgent("app"+str(i).zfill(2)+V.XMPPSERVER, "App"+str(i).zfill(2)+"!")
        V.apps.append("app"+str(i).zfill(2)+V.XMPPSERVER)
        a.start().result()
        # a.web.start(hostname="127.0.0.1", port="300"+str(i).zfill(2))

    # devs init
    for i in range(ndev):
        d = DevAgent("dev"+str(i).zfill(2)+V.XMPPSERVER, "Dev"+str(i).zfill(2)+"!")
        V.devs.append("dev"+str(i).zfill(2)+V.XMPPSERVER)
        d.start().result()
        # d.web.start(hostname="127.0.0.1", port="200"+str(i).zfill(2))

    # snds init
    for i in range(nsnd):
        s = SndAgent("snd"+str(i).zfill(2)+V.XMPPSERVER, "Snd"+str(i).zfill(2)+"!")
        s.start().result()
        # s.web.start(hostname="127.0.0.1", port="100"+str(i).zfill(2))

    # main thread
    print("SND_SENDED,DEV_RECEIVED,DEV_DROPPED,KNL_RECEIVED,KNL_SENDED,APP_RECEIVED")
    while True:
        try:
            mon = str(V.SND_SENDED) + "," + str(V.DEV_RECEIVED) + "," + str(V.DEV_DROPPED) + "," + str(V.KNL_RECEIVED) + "," + str(V.KNL_SENDED) + "," + str(V.APP_RECEIVED)
            print(mon)
            time.sleep(0.5)
        except KeyboardInterrupt:
            quit_spade()
            break
    print("Spade finished")
