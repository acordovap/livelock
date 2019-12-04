# Config variables
XMPPSERVER = "@102mcc13.inge.itam.mx"
DEV_BUFFSIZE = 5
KNL_IPINTRQLEN = 5 # same as outputifqueue for kernel_type=1
KNL_CYCLEPROC = 5
KNL_BUFFTH = 50 # percent for interrrupt or outputifqueue
KNL_DNDTH = int(KNL_IPINTRQLEN/2) # cpu fraction based on KNL_IPINTRQLEN

# Metrics
SND_SENDED = 0
DEV_DROPPED = 0
KNL_DROPPED = 0
APP_RECEIVED = 0
APP_LATENCY = 0.0

devs = list()
apps = list()

# parameters
sender_type = 0 # 0- unif, 1- normal
sender_period = 0.0
sender_devEqApp = True # devEqApp?
kernel_type = 0 # 0- kernel type0, 1- kernel type1
kernel_calendar_type = 0 # 0- interrrupt driven, 1- polling, 2- hybrid
kernel_infering_ll = 0 # 0- buffer overflow, 1- cpu proc
# kernel_reactivate_interrupt = 0 # 0- buffer
