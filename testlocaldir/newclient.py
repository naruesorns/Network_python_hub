__author__ = 'spacewalker'
import socket
import threading
import os
import os.path
import time
import sys

#host = '127.0.0.1'
#port = 5000
#host = '10.35.247.197'
#host = '192.168.56.1'
#s = socket.socket()
#s.connect((host, port))
print "======== FTP COMMANDS ========\n" + "1) ls or dir = list file in remote directory\n"\
      + "2) lls or ldir = list file in local directory\n" + "3) get = download file\n"\
      + "4) put = upload file\n" + "******SOFTWARE SUPPORTS IPv4 ONLY******\n" + "Please enter in format xxx.xxx.xxx.xxx"
while True:
    try:
        host = raw_input("\nPlease Enter Host IP here: ")
        port = 5000
        s = socket.socket()
        if host == "exit":
            print "You have exit program ..."
            break
        s.connect((host, port))
    except:
        print "There are a few errors occur\n" \
              "1) This software supports IPv4 only!\n" \
              "2) You have entered wrong host IP\n" \
              "3) The host is not existing"
        continue

    if host:
        print 'Client Start ...'
        while True:
            command = raw_input("\nPlease Enter Command here: ")
            if (command[:3] == 'lls' or command[:4] == 'ldir'): #lls command
                startTime = time.time()
                filepath = command.split( ) #filepath = lls, c:\filepath
                if len(filepath) < 2 and command[4:] != "":
                    print 'Invalid Command. lls or dir command need 2 arguments which are lls <filepath> or dir <filepath>'
                    continue
                else:
                    path = filepath.pop() #path = c:\testfolder\

                try:
                    if (command[:3] == 'lls' and command[3:] == "") or (command[:4] == 'ldir' and command[4:] == ""):
                        dirs = os.listdir('./')
                        withpath = 0
                    else:
                        dirs = os.listdir(path) #dirs = README.txt, NEWS.txt, ...
                        withpath = 1
                except:
                    print("There is no such that directory...")
                    continue
                print "Files list in local directory: " + os.path.basename(path)
                for files in dirs:
                    itempath = os.path.join(path, files)
                    if withpath == 0:
                        if os.path.isfile(files):
                            print(" [File]  :"+files+"\t"+str(os.path.getsize(files))+" Bytes\t"+time.ctime(os.path.getmtime(files))) #send 4
                        else:
                            print(" [Folder]:"+files+"\t")
                    else:
                        if os.path.isfile(itempath):
                            print(" [File]  :"+files+"\t"+str(os.path.getsize(itempath))+" Bytes\t"+time.ctime(os.path.getmtime(itempath))) #send 4
                        else:
                            print(" [Folder]:"+files+"\t")
                elapsedTime = time.time() - startTime
                print "Using time: " + str(elapsedTime) + " sec"
            elif (command[:2] == "ls" or command[:3] == "dir"): #ls command
                filepath = command.split( )
                if len(filepath) < 2 and command[3:] != "":
                    print 'Invalid Command. ls or dir command need 2 arguments which are ls <filepath> or dir <filepath>'
                    continue
                s.send('listremotemode')#send 1
                time.sleep(0.1) #delay
                s.send(command) #send 2
                if (command[:2] == 'ls' and command[2:] == "") or (command[:3] == 'dir' and command[3:] == ""):
                    startTime = time.time()
                    filecount = s.recv(1024) #recv 3
                else:
                    startTime = time.time()
                    filecount = s.recv(1024) #recv 3
                print "Listing Files from server...\nmight takes a few sec..."
                s.settimeout(5.0)
                time.sleep(0.05)
                try:
                    fileFromServer = s.recv(1024) #recv 4
                    print "There are " + filecount + " files on server\n" + fileFromServer
                    elapsedTime = time.time() - startTime
                    print "Using time: " + str(elapsedTime) + " sec"
                except:
                    print "There is no such that directory on server..."
                    continue
            elif command[:3] == 'get': #get command
                if(command[3:] == ""):
                    print "Invalid file name"
                    continue
                startTime = time.time()
                s.send(command)#send 1
                data = s.recv(1024) #recv2
                if data[:6] == 'EXISTS':
                    filesize = long(data[6:])
                    message = raw_input("File exists, " + str(filesize) + "Bytes, download? " \
                                                                           "(Y/N)? -> ")
                    if message == 'Y' or message == 'y':
                        s.send("OK")
                        filename = os.path.split(command)
                        try:
                            f = open('new_dl_'+filename[1], 'wb') #file extendsion is gone!!! NOT FIX YET
                        except:
                            print("Unexpected error: ", sys.exc_info()[0])
                            raise
                        data = s.recv(1024) #recv 3
                        totalRecv = len(data)
                        f.write(data)
                        while totalRecv < filesize:
                            data = s.recv(1024) # recv 4
                            totalRecv += len(data)
                            f.write(data)
                            print "\rYou have downloaded " + "{0:2f}".format((totalRecv/float(filesize))*100)+ "% Done",
                        print "\nDownload Complete!\n"
                        f.close()
                    else:
                        s.send("CC")
                        print "You have denied to download"
                        continue
                    elapsedTime = time.time() - startTime
                    print "File size: " + str(filesize) + " Bytes"
                    print "Using time: " + str(elapsedTime) + " Sec"
                    print "Throughput: " + str((filesize/elapsedTime)/1024) + " KB/Sec"
                elif data[:6] == 'NOFILE':
                    print "There is no file you want..."
                    continue
                else:
                    continue
            elif command[:3] == 'put': #get command #s.send(command)
                if(command[3:] == ""):
                    print "Invalid file name"
                    continue
                startTime = time.time()
                s.send(command) # send 1
                filepath = command.split( )
                fileToUpload = filepath.pop()
                if os.path.isfile(fileToUpload):
                    s.send(fileToUpload + "<split>" + str(os.path.getsize(fileToUpload))) #send2
                    message = raw_input("File Exists! " + str(os.path.getsize(fileToUpload)) + " Bytes, upload? "
                                                                            "Y/N? -> ")
                    if message == 'Y' or message == 'y':
                        s.send("OK")#send3
                        with open(fileToUpload, 'rb') as f:
                            bytesToSend = f.read(1024)
                            s.send(bytesToSend) #send4
                            while bytesToSend != "":
                                bytesToSend = f.read(1024)
                                s.send(bytesToSend)
                                totalSend = s.recv(1024)
                                if totalSend[:3] == "100":
                                    print "\rYou have uploaded " + totalSend + "% Done",
                                    break
                            print "\nUpload Complete!\n"
                            elapsedTime = time.time() - startTime
                            print "File size: " + str(os.path.getsize(fileToUpload)) + " Bytes"
                            print "Using time: " + str(elapsedTime) + " Sec"
                            print "Throughput: " + str((os.path.getsize(fileToUpload)/elapsedTime)/1000) + " KB/Sec"
                    else:
                        print "You have denied to upload..."
                        s.send("CC")
                        continue
                else:
                    print "There is no file you want to upload..."
            elif command[:4] == 'exit': #exit command
                s.send("exit")
                print "You have disconnected from server..."
                break
            else:
                print "INVALID COMMAND!"
                continue
s.close()
