#! /usr/bin/env python3

# Echo server program

import socket, sys, re, os
sys.path.append("../lib")       # for params
import params

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )



progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

listenPort = paramMap['listenPort']
listenAddr = ''       # Symbolic name meaning all available interfaces

pidAddr = {} #for active connections. mapping the pid to the client address

if paramMap['usage']:
    params.usage()

#method for reading and giving back
def communicate(connAddr):
    sock, addr = connAddr
    print('Connected by', addr)
    while 1:
        data = sock.recv(1024)
        if len(data) == 0:
            print("Zero length read, nothing to send, terminating")
            break
        sendMsg = data
        print("Received tar contents, sending it back")
        while len(sendMsg):
            bytesSent = sock.send(sendMsg)
            sendMsg = sendMsg[bytesSent:0]
        sock.shutdown(socket.SHUT_WR)
    sys.exit(0)
    

listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# listener socket will unbind immediately on close
listenSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# accept will block for no more than 5s
listenSock.settimeout(5)          
# bind listener socket to port
listenSock.bind((listenAddr, listenPort))
# set state to listen
listenSock.listen(1)              # allow only one outstanding request

# s is a factory for connected sockets

while True:
    # reap zombie children (if any)
    while pidAddr.keys():
        # Check for exited children (zombies).  If none, don't block (hang)
        if (waitResult := os.waitid(os.P_ALL, 0, os.WNOHANG | os.WEXITED)): 
            zPid, zStatus = waitResult.si_pid, waitResult.si_status
            print(f"""zombie reaped:
            \tpid={zPid}, status={zStatus}
            \twas connected to {pidAddr[zPid]}""")
            del pidAddr[zPid]
        else:
            break               # no zombies; break from loop
    print(f"Currently {len(pidAddr.keys())} clients")

    try:
        connSockAddr = listenSock.accept() # accept connection from a new client
    except TimeoutError:
        connSockAddr = None 

    if connSockAddr is None:
        continue
    forkResult = os.fork()     # fork child for this client 
    if (forkResult == 0):        # child
        listenSock.close()         # child doesn't need listenSock
        communicate(connSockAddr)
    # parent
    sock, addr = connSockAddr
    sock.close()   # parent closes its connection to client
    pidAddr[forkResult] = addr
    print(f"spawned off child with pid = {forkResult} at addr {addr}")

