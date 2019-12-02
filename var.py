# Config variables
XMPPSERVER = "@102mcc13.inge.itam.mx"
DEV_BUFFSIZE = 5
KNL_IPINTRQLEN = 5 # same as outputifqueue for kernel_type=1
KNL_CYCLEPROC = 5

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
sender_devEqApp = True
    # 0: interrrupt driven, 1-
kernel_type = 0
