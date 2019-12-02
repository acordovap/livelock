# Config variables
XMPPSERVER = "@102mcc13.inge.itam.mx"
DEV_BUFFSIZE = 5
KNL_IPINTRQLEN = 5 # same as outputifqueue for kernel_type=1
KNL_CYCLEPROC = 5
KNL_BUFFTH = 50 # percent for interrrupt or outputifqueue

# Metrics
SND_SENDED = 0
DEV_DROPPED = 0
KNL_DROPPED = 0
APP_RECEIVED = 0
APP_LATENCY = 0.0

devs = list()
apps = list()

# parameters
    # sent# 0 - unif, 1 - normal
sender_type = 0
    # devEqApp?
sender_devEqApp = True
    # 0- kernel type0, 1- kernel type1
kernel_type = 0
    # 0- interrrupt driven, 1- polling, 2- hybrid
kernel_calendar_type = 0
    # 0- buffer overflow, 1- cpu proc
kernel_infering_ll = 0
    # 0- buffer, 1- timer
kernel_reactivate_interrupt = 0
