__author__ = 'spacewalker'
import socket
import threading
import os, time

def ServerFunction(name, sock, addr):
    while True:
        try:
            getfilemode = sock.recv(1024) #recv 1
            if getfilemode[:3] == "get":
                filepath = getfilemode.split( )
                fileToDownload = filepath.pop()
                if os.path.isfile(fileToDownload):
                    sock.send("EXISTS" + str(os.path.getsize(fileToDownload))) #send 2
                    userResponse = sock.recv(1024)
                    if userResponse[:2] == 'OK':
                        with open(fileToDownload, 'rb') as f:
                            bytesTosend = f.read(1024)
                            sock.send(bytesTosend) #send 3
                            while bytesTosend != "":
                                bytesTosend = f.read(1024)
                                sock.send(bytesTosend)#send 4
                            print "Client has downloaded " + fileToDownload
                    elif userResponse[:2] == 'CC':
                        print "Client has denied to download"
                        continue
                else:
                    sock.send("NOFILE") #send error
            elif getfilemode[:3] == "put":
                try:
                    filenameandsize = sock.recv(1024) #recv 2
                    splitnameandsize = filenameandsize.split("<split>")
                    filesize = long(splitnameandsize.pop())
                    filename = os.path.split(splitnameandsize.pop())
                except:
                    print "There is no file from client..."
                    continue
                userResponse = sock.recv(1024) #recv3
                if userResponse[:2] == "OK":
                    f = open('new_ul_'+filename[1], 'wb')
                    data = sock.recv(1024) #recv 4
                    totalRecv = len(data)
                    f.write(data)
                    while totalRecv < filesize:
                        data = sock.recv(1024)
                        totalRecv += len(data)
                        f.write(data)
                        totalSend = str((totalRecv/float(filesize))*100)
                        sock.send(totalSend)
                    print "Client has uploaded: " + filename[1]
                    f.close()
                elif userResponse[:2] == "CC":
                    print "Client has denied to upload"
                    continue
            elif getfilemode == "listremotemode":        
                filepath = sock.recv(1024) #recv2
                splittedfilepath = filepath.split( )
                path = splittedfilepath.pop()
                if filepath != 'ls' and filepath != 'dir': #with path
                    try:
                        dirs = os.listdir(path)
                        filecount = len(dirs)
                        sock.send(str(filecount)) #send 3
                        #time.sleep(0.05)
                        for files in dirs:
                            itempath = os.path.join(path, files)
                            if os.path.isfile(itempath):
                                sock.send(" [File]  :"+files+"\t"+str(os.path.getsize(itempath))+" Bytes\t"+time.ctime(os.path.getmtime(itempath))+"\n")
                            else:
                                sock.send(" [Folder]:"+files+"\n")
                        print "Files in directory were sent to client"
                    except:
                        sock.send("[NODIR_ERR] - There is no such that directory") #send error
                else: #with no path (ROOT)
                    dirs = os.listdir('./')
                    filecount = len(dirs)
                    sock.send(str(filecount)) #send 3
                    for files in dirs:
                        if os.path.isfile(files):
                            sock.send(" [File]  :"+files+"\t"+str(os.path.getsize(files))+" Bytes\t"+time.ctime(os.path.getmtime(files))+"\n")
                        else:
                            sock.send(" [Folder]:"+files+"\n")
                    print "Files in directory were sent to client"
            elif getfilemode == "exit":
                print "Client " + "<"+addr+">" + "had been disconnected!"
            else:
                sock.send("Error! There is no command that you want...")
        except:
            print "Client " + str(addr) + " has been disconnected..."
            break
    sock.close()

def Main():
    host = ""
    port = 5000
    s = socket.socket()
    s.bind((host, port))
    s.listen(5)
    print "Server start ..."
    while True:
            c, addr = s.accept()
            print 'There is a connection from', addr
            t = threading.Thread(target=ServerFunction, args=("RetrThread", c, addr))
            t.start()
    s.close()

if __name__ == '__main__':
    Main()
