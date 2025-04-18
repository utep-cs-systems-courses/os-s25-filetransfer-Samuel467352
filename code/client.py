#! /usr/bin/env python3

# Echo client program
import socket, sys, re, os
sys.path.append("../lib")       # for params
import params

switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage  = paramMap["server"], paramMap["usage"]

if usage:
    params.usage()

try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server, file=sys.stderr)
    sys.exit(1)

s = None
for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto), file=sys.stderr)
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        print(" error: %s" % msg)
        s = None
        continue
    try:
        print(" attempting to connect to %s" % repr(sa), file=sys.stderr)
        s.connect(sa)
    except socket.error as msg:
        print(" error: %s" % msg)
        s.close()
        s = None
        continue
    break

if s is None:
    print('could not open socket')
    sys.exit(1)

#send data to server
print("give input to send", file=sys.stderr)
chunks = []
while True:
    chunk = os.read(0, 1000)
    if not chunk:
        break
    chunks.append(chunk)
outMessage = b''.join(chunks)
while len(outMessage):
    print("sending out tar", file=sys.stderr)
    bytesSent = os.write(s.fileno(), outMessage)
    outMessage = outMessage[bytesSent:]

s.shutdown(socket.SHUT_WR)      # no more output

chunkData = []

while 1:
    data = s.recv(1024)
    if len(data) == 0:
        break
    chunkData.append(data)
os.write(1, b''.join(chunkData))
print("Zero length read.  Closing", file=sys.stderr)

s.close()
