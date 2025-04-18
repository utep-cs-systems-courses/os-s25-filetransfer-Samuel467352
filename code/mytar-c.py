import os, sys

args = sys.argv[1:]

#newPath = 'foogoo.muda'

#rfd = os.open(newPath, os.O_CREAT | os.O_WRONLY | os.O_APPEND)

for arg in args:
    #print(arg)
    fd = os.open(arg, os.O_RDONLY)

    #get the title and title size
    title = arg
    title_size = str(len(title)).rjust(6, '0')

    #print(title_size)
    #print(title)
    #write title size and title into stdout
    os.write(1, title_size.encode())
    os.write(1, title.encode())

    #get file size and get contents
    bys = os.path.getsize(arg)
    cont_size = str(bys).rjust(6, '0')
    os.write(1, cont_size.encode())

    #buffered reader
    chunk_size = bys // 4
    while(True):
        chunk = os.read(fd, chunk_size)
        if chunk == b"":
            break
        os.write(1, chunk)
    #conts = os.read(fd, bys)
    #os.write(1, conts)
    os.close(fd)

#os.close(rfd)


    
