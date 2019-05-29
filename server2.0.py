import hanshu
import socket
import gc

def checktext1(data):
    url =  hanshu.geturl1(data[12:-4])
    return hosts.get(url,False)
def gethosts():
    with open('address.txt','r') as f:
        hosts = {}
        for eachline in f:
            data = eachline.replace('\n','').split(' ')
            hosts.setdefault(data[1].encode('utf-8'),set([data[0]]))
    return hosts

hosts = gethosts()

s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

s.bind(('127.0.0.1',53))

byr=('10.3.9.5',53)
while True:
    data,addr = s.recvfrom(1024)
    print(addr)
    if data[-4:-2]==b'\x00\x01':
        res = checktext1(data)
        # if res == False:
        s1 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s1.sendto(data,byr)
        bupt_data,bupt_addr = s1.recvfrom(1024)

        url,ip = hanshu.savetext3(bupt_data)
        hosts.setdefault(url,ip)

        s1.sendto(bupt_data,addr)
        s1.close()
        del s1
        gc.collect()
        # else:
        #     pass




