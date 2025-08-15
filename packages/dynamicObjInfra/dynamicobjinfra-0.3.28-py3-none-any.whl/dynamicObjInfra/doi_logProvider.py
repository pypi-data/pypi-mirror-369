import logging

logInstane = None

def setAppLogger (logger):
    global logInstane
    logInstane = logger

def logger():
    if (logInstane):
        return logInstane
    else:
        return logging.getLogger("dynamicObjInfra")