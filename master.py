"""Master.
Usage:
  master.py -k N -n N -p N -s N (-q N | -d N -a N) [-t N]
  master.py interrupt -i N -k N -n N -p N -s N (-q N | -d N -a N) [-t N]
  master.py polling -k N -n N -p N -s N (-q N | -d N -a N) [-t N]
  master.py hybrid -i N -k N -n N -p N -s N (-q N | -d N -a N) [-t N]
  master.py --help

Options:
  -i N, --infering-type           0|1         infering type.
  -k N, --kernel-type             0|1         kernel type.
  -n N, --sender-type             0|1|2|3|4   sender type.
  -p N, --sender-period           0.1-1.0     sender period.
  -s N, --senders                 1-99        number of senders.
  -q N, --devs-equal-to-apps      1-99        number of devs = number of apps.
  -d N, --devs                    1-99        number of devs.
  -a N, --apps                    1-99        number of apps.
  -t N, --time-to-run             >=0.1       time to run (minutes).
"""

try:
    from docopt import docopt
except ImportError:
    exit("This program requires that `docopt` library")

try:
    from spade.template import Template
    from spade import quit_spade
except ImportError:
    exit("This program requires that `spade` library")

try:
    from schema import Schema, And, Or, Use, SchemaError
except ImportError:
    exit("This program requires that `schema` library")

try:
    import numpy
except ImportError:
    exit("This program requires that `numpy` library")

# import aioxmpp
# from aioxmpp import PresenceState, PresenceShow
# from spade.template import Template
# from spade import quit_spade
import asyncio
import time
import var as V
from knlAgentIntr import KnlAgentIntr
from knlAgentWithoutIpq import KnlAgentWithoutIpq
from devAgent import DevAgent
from appAgent import AppAgent
from sndAgent import SndAgent

if __name__ == "__main__":

    args = docopt(__doc__)
    schema = Schema({
        '--kernel-type': And(Use(int), lambda n: 0 <= n <= 1, error='--kernel-type should be 0 or 1'),
        '--infering-type': Or(None, And(Use(int), lambda n: 0 <= n <= 1), error='--infering-type should be 0 or 1'),
        '--sender-type': And(Use(int), lambda n: 0 <= n <= 4, error='--sender-type should between 0 and 4'),
        '--sender-period': And(Use(float), lambda n: 0.1 <= n <= 1.0, error='--sender-period should be 0 or 1'),
        '--senders': And(Use(int), lambda n: 0 <= n <= 99, error='--senders should between 1 and 99'),
        '--devs-equal-to-apps': Or(None, And(Use(int), lambda n: 0 <= n <= 99), error='--devs-equal-to-apps should between 1 and 99'),
        '--devs': Or(None, And(Use(int), lambda n: 0 <= n <= 99), error='--devs should between 1 and 99'),
        '--apps': Or(None, And(Use(int), lambda n: 0 <= n <= 99), error='--apps should between 1 and 99'),
        '--time-to-run': Or(None, And(Use(float), lambda n: 0.1 <= n), error='--time-to-run should greater than 0.1'),
        str: object })

    try:
        args = schema.validate(args)
    except SchemaError as e:
        exit(e)

    # Asignación de variables globales por parámetros
    V.sender_type = args['--sender-type'] # 0- unif, 1- normal
    V.sender_period = args['--sender-period']
    nsnd = args['--senders']
    if args['--devs-equal-to-apps'] != None:
        ndevs = napps = args['--devs-equal-to-apps']
        V.sender_devEqApp = True
    else:
        ndevs = args['--devs']
        napps = args['--apps']
        V.sender_devEqApp = False
    V.kernel_type = args['--kernel-type'] # 0- kernel type0, 1- kernel type1
    if args['hybrid']: # 0- interrrupt driven, 1- polling, 2- hybrid
        V.kernel_calendar_type = 2
    elif args['interrupt']:
        V.kernel_calendar_type = 0
    elif args['polling']:
        V.kernel_calendar_type = 1
    else:
        V.kernel_calendar_type = -1

    V.kernel_infering_ll = args['--infering-type'] if args['--infering-type'] != None else 0 # 0- buffer overflow, 1- cpu proc
    # Fin de asignación de variables

    ### INITIALIZATION OF AGENTS ###
    # devs init
    for i in range(ndevs):
        d = DevAgent("dev"+str(i).zfill(2)+V.XMPPSERVER, "Dev"+str(i).zfill(2)+"!")
        V.devs.append("dev"+str(i).zfill(2)+V.XMPPSERVER)
        d.start().result()
        d.web.start(hostname="127.0.0.1", port="200"+str(i).zfill(2))

    # kernel init
    if V.kernel_type == 0:
        k = KnlAgentIntr("kernel"+V.XMPPSERVER, "Kernel!")
    else:
        k = KnlAgentWithoutIpq("kernel"+V.XMPPSERVER, "Kernel!")
    k.start().result()
    k.web.start(hostname="127.0.0.1", port="50000")

    # apps init
    for i in range(napps):
        a = AppAgent("app"+str(i).zfill(2)+V.XMPPSERVER, "App"+str(i).zfill(2)+"!")
        V.apps.append("app"+str(i).zfill(2)+V.XMPPSERVER)
        a.start().result()
        # a.web.start(hostname="127.0.0.1", port="300"+str(i).zfill(2))

    # nsnd init
    for i in range(nsnd):
        s = SndAgent("snd"+str(i).zfill(2)+V.XMPPSERVER, "Snd"+str(i).zfill(2)+"!")
        s.start().result()
        # s.web.start(hostname="127.0.0.1", port="100"+str(i).zfill(2))

    # main thread
    if args['--time-to-run'] != None:
        mins2run = args['--time-to-run']
        t_end = time.time() + 60 * mins2run
    print("SND_SENDED,DEV_DROPPED,KNL_DROPPED,APP_RECEIVED,APP_LATENCY")
    while args['--time-to-run'] == None or time.time() < t_end:
        try:
            time.sleep(0.2)
            mon = str(V.SND_SENDED) + "," + str(V.DEV_DROPPED) + "," + str(V.KNL_DROPPED) + "," + str(V.APP_RECEIVED) + "," + str(V.APP_LATENCY/V.APP_RECEIVED)
            print(mon)
        except KeyboardInterrupt:
            quit_spade()
            break
    quit_spade()
