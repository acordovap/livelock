# livelock

Implementación en python3 haciendo uso de spade para simular livelock, descrito en el artículo "Eliminating receive livelock in an interrupt-driven kernel" de los autores: Mogul, Jeffrey C and Ramakrishnan, KK

## Configuración y ejecución

A continuación se detallan los requisitos y configuraciones para ejecutar el proyecto

### Prerrequisitos

El proyecto fué generado haciendo uso de python3 con las librerías: spade, schema, numpy, docopt y un servidor XMPP.

El servidor XMPP se encentra configurado para: permitir el registro automático de clientes, no requerir encripción cliente-servidor

### Prerrequisitos

No olvidar cambiar el nombre del servidor XMPP en la variable XMPPSERVER del archivo var.py
De igual forma se pueden mover más configuraciones en ese mismo archivo.

XMPPSERVER = "@102mcc13.inge.itam.mx"      # servidor XMPP
DEV_BUFFSIZE = 5         # tamaño de los dispositivos
KNL_IPINTRQLEN = 5     # tamaño de las colas de salida y/o entrada del kernel
KNL_CYCLEPROC = 5    # simulación del procesamiento de los mensajes en el kernel
KNL_BUFFTH = 50          # el umbral de la cola de mensajes para habilitar de nuevo las interrupciones aplica en el modelo híbrido y en el de interrupciones
KNL_DNDTH = int(KNL_IPINTRQLEN/2) # es el parámetro para inferir si hay livelock, y este se genera por muestreo del uso en interrupciones en el CPU


### Ejecución

La forma de invocar el programa es:

```
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
```

Definición de los parámetros:

-i : Es 0 cuando se sobrecarga la cola del kernel y 1 cuando se desea usar el muestreo del uso del CPU para interrupciones

-k : k0 es el kernel con cola de entrada y salida y el K1 es el kernel sin cola de entrada

-n : Toma valores de 0 al 4, y representan las distintas distribuciones mencionadas con anterioridad

-p : Es el periodo en el cual se ejecutan las rutinas de los agentes snds

-s : El número de agentes snds a desplegar

-q : El número de aplicaciones y dispositivos a desplegar. Se establece la relación de 1:1 de envío de mensajes.

-d : Si no se usa la bandera q, es el número de dispositivos a desplegar. La aplicación destino es designada aleatoriamente.

-a : Si no se usa la bandera q, es el número de número de aplicaciones a desplegar.

-t : Si se especifica el parámetro indica el tiempo de ejecución del programa
