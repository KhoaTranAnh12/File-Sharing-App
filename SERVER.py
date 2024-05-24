from threading import Thread, Lock
import socket
import os
import time
import json
from queue import Queue
global stop_threads 
stop_threads=False
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
        

class Server:
    def __init__(self,port):
        self.stop_threads=False
        self.host=socket.gethostbyname(socket.gethostname())
        self.port=port
        print(self.host)
        self.hostnameToIP={}
        self.ipToHostname={}
    
        if not os.path.exists("hostname_info.json") or os.path.getsize("hostname_info.json") == 0:
                with open("hostname_info.json", "w") as fp:
                    fp.write("[]")
        with open("hostname_info.json", "r") as fp:
            self.hostname_info = json.load(fp)
        for i in self.hostname_info:
            self.hostnameToIP[i['username']]=None
        self.listenSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.listenSocket.bind((self.host,self.port))
        self.__t: dict[str, Thread] = {}
        self.__t['listen'] = Thread(target=self.listen)
        # self.__t['reqs'] = Thread(target=self.sendRequest)
        self.stop_threads = False
        self.start()

        self.output_queue = Queue(maxsize=100)
        self.queue_mutex = Lock()

    def start(self):
        for thread in self.__t.values():
            thread.start()
    # def sendRequest(self):
    #     if self.stop_threads == True:
    #         return
    #     while(1):
    #         print(self.stop_threads)
    #         if self.stop_threads==True:
    #             print("it's ended")
    #             return
    #         request=input("request:")
    #         if request=="EXIT":
    #             self.exit()
    #         request='REQUEST '+request
    #         Type=separate(request)[1]
    #         hostname=separate(request)[2]
    #         if Type == "PING":
    #             output=self.ping(hostname)
    #             print(output)
    #         if Type == 'DISCOVER':
    #             output=self.discover(hostname)
    #             print(output)
    def ping(self,hostname):
        tmpSock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            tmpSock.settimeout(2)
            tmpSock.connect((self.hostnameToIP[hostname],5001))
            start =time.time()
            tmpSock.send(f'REQUEST PING {hostname}'.encode())
            output=tmpSock.recv(2048).decode()
            output=separate(output)[2]
            end = time.time()
            if output == 'OK':
                return f'Ping {hostname} ok, time is: {round((end-start)*1000,2)}ms\n'
            else:
                return f"Can't connect to {hostname}"
        except:
            return f"Can't connect to {hostname}"
    def discover(self,hostname):
        tmpSock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            tmpSock.connect((self.hostnameToIP[hostname],5001))
            tmpSock.send(f'REQUEST DISCOVER {hostname}'.encode())
            output=tmpSock.recv(2048).decode()
            print(output)
            output=separate(output)[2]
            #Để dành dùng sau
            x="'"
            y='"'
            output = output.replace(x,y)
            fileList=json.loads(output)
            print(fileList)
            for info in self.hostname_info:
                if info['username'] == hostname:
                    info['files'] = fileList
            os.remove("./hostname_info.json")
            with open("./hostname_info.json",'w') as file:
                json.dump(self.hostname_info,file,indent=4)
            return ('OK',fileList)
        except:
            return (f'Discover {hostname} failure',None)
    def listen(self):
        if self.stop_threads == True:
            print("listen ended")
            return
        self.listenSocket.listen()
        print('listening')
        if self.stop_threads==True:
            self.listenSocket.close()
            print("listen ended")
            return
        while True:
            if self.stop_threads==True:
                return
            print(self.stop_threads)
            try:
                clientSock,clientHost = self.listenSocket.accept()
                print(clientSock)
                if self.stop_threads==True:
                    clientSock.close()
                    print(clientSock)
                    return
                print('how?')
                handleThread=Thread(target=self.handle,args=(clientSock,clientHost))
                handleThread.run()
            except:
                print('listen error')
    def handle(self,clientSock:socket.socket,clientHost):
        try:
            if self.stop_threads==True:
                print('stop handle')
                return
            print('connected')
            clientSock.settimeout(10)
            message = clientSock.recv(2048).decode()
            print(message)
            Type=separate(message)[1]
            if Type == 'REGISTER':
                output=self.handleRegister(clientSock,message)
            if Type == 'LOGIN':
                output=self.handleLogin(clientSock,message)
            if Type == 'PUBLISH':
                output=self.handlePublish(clientSock,message)
            if Type == 'FETCH':
                output=self.handleFetch(clientSock,message)
            if Type == 'LOGOUT':
                output=self.handleLogout(clientSock,message)
            if Type == 'DELETE':
                output=self.handleDelete(clientSock,message)
            if Type == 'EXIT':
                self.exit()
        except Exception as e:
            print(f'error in handleConnection {e}')
        finally:
            self.queue_mutex.acquire()
            if not self.output_queue.full():
                self.output_queue.put(output)
            self.queue_mutex.release()
            clientSock.close()
            print('closed')
    def handleDelete(self,clientSock,message):
        Content=separate(message)[2]
        fname=separate(Content)[0]
        host=separate(Content)[1]
        username=self.ipToHostname[host]
        for info in self.hostname_info:
            if info['username'] == username:
                info['files'].pop(fname)
                return f'{username} removed {fname} from his/her repository'
        return f'{username} tried to remove {fname} from his/her repository, but no {fname} found'
    def handleRegister(self,clientSock,message):
        Content=separate(message)[2]
        username=separate(Content)[0]
        password=separate(Content)[1]
        for info in self.hostname_info:
            if info['username'] == username:
                clientSock.send('RESPONSE REGISTER DUPLICATE'.encode())
                output = f"someone tried register {username}, but it's registered"
                return output
        self.hostname_info.append({'username': username, 'password': password, 'files': {}})
        self.hostnameToIP[username]=None
        clientSock.send('RESPONSE REGISTER OK'.encode())
        print(self.hostname_info)
        os.remove("./hostname_info.json")
        with open("./hostname_info.json",'w') as file:
            json.dump(self.hostname_info,file,indent=4)
        output = f" {username} registered"
        return output
    def handleLogin(self,clientSock,message):
        Content=separate(message)[2]
        username=separate(Content)[0]
        password=separate(Content)[1]
        host=separate(Content)[2]
        for info in self.hostname_info:
            if info['username'] == username:
                if info ['password'] == password:
                    print(self.hostnameToIP[username])
                    if self.hostnameToIP[username]!=None:
                        clientSock.send('RESPONSE LOGIN LOGGED'.encode())
                        output = f"someone tried login {username}, but it's logged"
                        return output
                    clientSock.send('RESPONSE LOGIN OK'.encode())
                    output = f" {username} logged"
                    self.hostnameToIP[username]=host
                    self.ipToHostname[host]=username
                    self.discover(username)
                    print(self.hostname_info)
                    print(self.hostnameToIP)
                    print(self.ipToHostname)
                else:
                    clientSock.send('RESPONSE LOGIN FALSE1'.encode())
                    output = output = f"someone tried login {username}, but wrong password"
                return output
        clientSock.send('RESPONSE LOGIN FALSE2'.encode())
        output = f"someone tried login {username}, but no {username} in database"
        return output
    def handleLogout(self,clientSock,message):
        username=separate(message)[2]
        print(username)
        self.ipToHostname.pop(self.hostnameToIP[username])
        self.hostnameToIP[username]=None
        print('ok')
        clientSock.send('RESPONSE LOGOUT OK'.encode())
        output = f"{username} logged out"
        return output
    def handlePublish(self,clientSock,message):
        Content=separate(message)[2]
        lname=separate(Content)[0]
        fname=separate(Content)[1]
        host=separate(Content)[2]
        lname=lname.replace("ZDAKSNDSAJDN"," ")
        fname=fname.replace("ZDAKSNDSAJDN"," ")
        print(fname)
        print(Content)
        for info in self.hostname_info:
            if info['username'] == self.ipToHostname[host]:
                info['files'][fname] = lname
        print(self.hostname_info)
        clientSock.send('RESPONSE PUBLISH OK'.encode())
        output = f"{self.ipToHostname[host]} published {fname}"
        os.remove("./hostname_info.json")
        with open("./hostname_info.json",'w') as file:
            json.dump(self.hostname_info,file,indent=4)
        print(output)
        return output
    def handleFetch(self,clientSock,message):
        response = ''
        tmpdict=None
        found=False        
        fname,host,dummy=separate(separate(message)[2])
        fname=fname.replace("ZDAKSNDSAJDN"," ")
        print(fname)
        for info in self.hostname_info:
            x: dict = info['files']
            for f in info['files'].keys():
                print(f)
                if f == fname:
                    found=True
                    tmpdict={info['username'] : self.hostnameToIP[info['username']]}
                    print('ok1234')
        if found == True: response += str(tmpdict)
        if response != '': print(response)
        else: print('NONEeEEE')
        print('done fetch')
        clientSock.send(f'RESPONSE FETCH {response}'.encode())
        output = f"{self.ipToHostname[host]} fetched {fname}"
        return output
    def savehosts(self):
        os.remove("hostname_info.json")
        with open("hostname_info.json", "w") as fp:
            json.dump(self.hostname_info,fp,indent=4)
        print('saved')
    def exit(self):
        self.savehosts()
        print('stopping threads')
        self.listenSocket.close()
        self.stop_threads=True
        for thread in self.__t.values():
            thread.join()