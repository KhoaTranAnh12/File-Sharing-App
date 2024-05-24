from ftplib import FTP
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer
from threading import Thread
import socket
import os
import time
import json
import sys
import random
def separate(a:str):
    count=0
    Header = ''
    Type = ''
    Content = ''
    for i in a:
        if i == ' ':
            count +=1
            if count > 2: Content += ' '
        else:
            if count == 0: Header +=i
            elif count == 1: Type +=i
            else: Content +=i
    return Header, Type, Content
        
        
class FTPServerSide(Thread):
    def __init__(self, host_ip):
        Thread.__init__(self)
        self.host_ip = host_ip
        
        # Initialize FTP server
        authorizer = DummyAuthorizer()
        authorizer.add_user('admin', 'admin', './repository', perm="elradfmwMT")
        authorizer.add_user('requester', 'requester', './repository', perm='r')
        handler = FTPHandler
        handler.authorizer = authorizer
        handler.banner = "Connection Success"
        
        self.server = ThreadedFTPServer((self.host_ip, 21), handler)
        self.server.max_cons = 256
        self.server.max_cons_per_ip = 5
    
    def run(self):
        self.server.serve_forever()
    
    def stop(self):
        self.server.close_all()
class Client:
    def __init__(self,sHost,sPort):
        self.stopThreads=False
        self.sHost=sHost
        self.sPort=sPort
        self.username=""
        self.password=""

        self.listenSock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.host='127.0.0.1'
        self.port = 5001
        self.listenSock.bind((self.host,self.port))

        #Muon luu 1 file published trong local computer de sau xai:
        self.published_path="./Jsons/published.json"
        if not os.path.exists(self.published_path) or os.path.exists(self.published_path) and os.path.getsize(self.published_path) == 0:
            with open(self.published_path,'w') as file:
                file.write('{}')

        with open(self.published_path,'r') as file:
                self.published_files = json.load(file)

        #luu 2 bien connect va login
        self.__connected=False
        self.__loggedIn=False

        #Tao 2 thread:
        self.__t: dict[str, Thread] = {}
        self.__t['ftp'] = FTPServerSide(self.host)
        self.__t['listen'] = Thread(target=self.listen)
        self.__t['reqs'] = Thread(target=self.sendRequest)
        self.run()
    def run(self):
        if not self.__connected:
            for thread in self.__t.values():
                thread.start()
            self.__connected = True
    def listen(self):
        print('client listening')
        self.listenSock.listen()
        if self.stopThreads==True:
            return
        while True:
            print(self.stopThreads)
            try:
                connectedSock,connectedAddr=self.listenSock.accept()
                if self.stopThreads==True:
                    print('stop listen')
                    self.listenSock.close()
                    return
                handleThread=Thread(target=self.handleConnections,args=(connectedSock,connectedAddr))
                handleThread.run()
            except OSError:
                break
    def handleConnections(self,connectedSock:socket.socket,connectedAddr:str):
        try:
            if self.stopThreads==True:
                print('stop handle')
                connectedSock.close()
                return
            print('connected')
            connectedSock.settimeout(10)
            message = connectedSock.recv(2048).decode()
            print(message)
            Type=separate(message)[1]
            if Type == 'PING':
                self.handlePing(connectedSock)
            if Type == 'DISCOVER':
                self.handleDiscover(connectedSock)
            if Type == 'RETRIEVE':
                Content=separate(message)[2]
                print(Content)
                self.handleRetrieve(connectedSock,Content)
        except Exception as e:
            print(f'error in handleConnection {e}')
        finally:
            connectedSock.close()
    def handlePing(self,connectedSock):
        response = f'RESPONSE PING OK'
        connectedSock.send(response.encode())
    def handleDiscover(self,connectedSock):
        response = f'RESPONSE DISCOVER {self.published_files}'
        connectedSock.send(response.encode())
    def handleRetrieve(self,connectedSock,fname):
        fname=fname.replace("ZDAKSNDSAJDN"," ")
        a=FTP(self.host)
        a.login(user='admin',passwd='admin')
        file_exists = False
        file_list = []
        a.retrlines('LIST', file_list.append)
        for line in file_list:
            print(line)
            if fname in line:
                file_exists = True
                break
        if not file_exists:
            res = 'DENIED'
        else: res = 'OK'
        print(res)
        connectedSock.send(f'RESPONSE RETRIEVE {res}'.encode())
    def retrieve(self,fname,host):
        fname=fname.replace(" ","ZDAKSNDSAJDN")
        request=f'REQUEST RETRIEVE {fname}'
        fname=fname.replace("ZDAKSNDSAJDN"," ")
        tmpSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        tmpSocket.connect((host,self.port))
        try:
            tmpSocket.send(request.encode())
        except:
            return "CAN'T REACH\n"
        time.sleep(1)
        response=tmpSocket.recv(2048).decode()
        Content=separate(response)[2]
        if Content == 'DENIED':
            return 'DENIED\n'
        else:
            i=0
            dest = f"./downloads/{fname}"
            while os.path.exists(dest):
                i += 1
                dest = f"./downloads/copy ({i}) of {fname}"
        print(dest)
        print(fname)
        print(i)
        ftp=FTP(host)
        ftp.login(user='requester',passwd='requester')
        start = time.time()
        with open(dest,'wb') as file:
            ftp.retrbinary(f'RETR {fname}',file.write)
        end = time.time()
        overall=end-start
        size=os.path.getsize(dest)
        speed=size/overall/1028
        ftp.quit()
        self.publish(dest,fname)
        return f'DOWNLOADED 100%\n'
        #Thêm bước publish nữa

    def sendRequest(self):
        while(1):
            print(self.stopThreads)
            if self.stopThreads==True:
                print('stop req')
                return
            a =input()
            if a == 'PUBLISH':
                b=input('lname: ')
                c=input('fname: ')
                self.publish(b,c)
            if a == 'FETCH':
                b=input('fname: ')
                self.fetch(b)
            if a == 'RETRIEVE':
                b=input('fname: ')
                c=input('host: ')
                print(self.retrieve(b,c))
            if a == 'REGISTER':
                b=input("username: ")
                c=input("password: ")
                print(self.register(b,c))
            if a == 'LOGIN':
                b=input("username: ")
                c=input("password: ")
                print(self.login(b,c))
            if a == 'LOGOUT':
                print(self.logout())
            if a == 'DELETE':
                b=input('fname: ')
                print(self.dele(b))
            if a == 'EXIT':
                self.exit()
    #Riêng publish còn có lưu ý là đưa file lên cái server ftp
    def publish(self,lname,fname):
        try:
            i=1
            dest = f'./repository/{fname}'
            x=fname
            while (x in self.published_files):
                x = f'copy ({i}) of {fname}'
                i += 1
            if i>1: fname=x
            print(lname)
            print(fname)
            lname=lname.replace(" ","ZDAKSNDSAJDN")
            fname=fname.replace(" ","ZDAKSNDSAJDN")
            print(lname)
            print(fname)
            request = f'REQUEST PUBLISH {lname} {fname} {self.host}'
            lname=lname.replace("ZDAKSNDSAJDN"," ")
            fname=fname.replace("ZDAKSNDSAJDN"," ")
            tmpSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            tmpSock.connect((self.sHost,self.sPort))
            try:
                tmpSock.send(request.encode())
            except:
                return 'UNREACHABLE'
            response=tmpSock.recv(2048).decode()
            response=separate(response)[2]
            
            ftp=FTP(self.host)
            ftp.login(user="admin",passwd="admin")
            with open(lname,'rb') as file:
                result = ftp.storbinary(f"STOR {fname}",file)
            print(result)

            self.published_files[fname]=lname
            os.remove(self.published_path)
            with open(self.published_path,'w') as file:
                json.dump(self.published_files,file,indent=4)
            return 'OK'
        except:
            print('WRONG LNAME')
    def dele(self,fname):
        fname=fname.replace(" ","ZDAKSNDSAJDN")
        request = f'REQUEST DELETE {fname} {self.host}'
        tmpSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        tmpSock.connect((self.sHost,self.sPort))
        try:
            tmpSock.send(request.encode())
        except:
            return 'UNREACHABLE\n'
        fname=fname.replace("ZDAKSNDSAJDN"," ")
        if not os.path.exists(f"./repository/{fname}"):
            return f'NO FILE NAMES {fname}\n'
        else:
            os.remove(f"./repository/{fname}")
            self.published_files.pop(fname)
            return f'DELETE {fname} OK\n'


    def fetch(self,fname):
        fname=fname.replace(" ","ZDAKSNDSAJDN")
        print(fname)
        request = f'REQUEST FETCH {fname} {self.host}'
        tmpSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        tmpSock.connect((self.sHost,self.sPort))
        try:
            tmpSock.send(request.encode())
        except:
            return 'UNREACHABLE'
        fname=fname.replace("ZDAKSNDSAJDN"," ")
        response=tmpSock.recv(2048).decode()
        response=separate(response)[2]
        if response != '' or response != None: print(response)
        else: print('Noneeeeee')
        return response

    def register(self,username,password):
        request = f'REQUEST REGISTER {username} {password}'
        tmpSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        tmpSock.connect((self.sHost,self.sPort))
        print(tmpSock)
        try:
            tmpSock.send(request.encode())
        except:
            return 'UNREACHABLE'
        response=tmpSock.recv(2048).decode()
        response=separate(response)[2]
        if response == None: print("None")
        else: print(response)
        return response
    
    def login(self,username,password):
        if not self.__loggedIn:
            request = f'REQUEST LOGIN {username} {password} {self.host}'
            tmpSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            tmpSock.connect((self.sHost,self.sPort))
            try:
                tmpSock.send(request.encode())
            except:
                return 'UNREACHABLE'
            response=tmpSock.recv(2048).decode()
            response=separate(response)[2]
            if response == 'OK':
                self.username=username
                self.password=password
                self.__loggedIn=True
                return 'OK'
            else:
                return response

    def logout(self):
        if self.__loggedIn:
            request = f'REQUEST LOGOUT {self.username}'
            os.remove(self.published_path)
            with open(self.published_path,'w') as file:
                json.dump(self.published_files,file,indent=4)
            tmpSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            tmpSock.connect((self.sHost,self.sPort))
            try:
                tmpSock.send(request.encode())
            except:
                return 'UNREACHABLE'
            response=tmpSock.recv(2048).decode()
            response=separate(response)[2]
            if response == 'OK':
                self.__loggedIn=False
            return response
        else: return "NOTOK"

    def exit(self):
        self.listenSock.close()
        os.remove(self.published_path)
        with open(self.published_path,'w') as file:
            json.dump(self.published_files,file,indent=4)
        if self.__connected:
            print(self.published_path)
            if self.__loggedIn:
                self.logout()
            try:
                self.__t['ftp'].stop()
            except Exception as e:
                print(f'disconnect forbidden {e}')
            self.stopThreads=True
    def showPublishedFiles(self): 
        return self.published_files