import copy
import struct
import socket

def urltohex(data):#把网址反人性化
    url_split = data.split('.')
    target = b''
    for each in url_split:
        target+=struct.pack('b',len(each))+each.encode('utf-8')##查询数据包中的网址是每个点号隔开，前面带一个每个部分的长度
    target+=b'\x00'
    return target

# def gethosts2():#读取本地hosts文件，加入cache
#     with open('hosts','r') as f:
#         hosts = {}
#         for eachline in f:
#             data = eachline.replace('\n','').split(' ')
#             target = urltohex(data[0])
#             hosts.setdefault(target,set([socket.inet_aton(data[1])]))
#     return hosts

def gethosts():#同一域名允许保存多个ip
    with open('hosts','r') as f:
        hosts = {}
        for eachline in f:
            data = eachline.replace('\n','').split(' ')##将所有的换行符删除，并以空格为标志切开
            target = urltohex(data[0])
            i = 1
            while i < len(data):
                data[i] = socket.inet_aton(data[i])
                i+=1
            hosts.setdefault(target,set(data[1:]))
    return hosts

def pack_query(id,url):#客户端网址打包
    target = urltohex(url)
    return struct.pack('>H',id) +  b'\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' + target + b'\x00\x01\x00\x01'



def geturl(data):#将网址格式人性化
    length = data[0]
    url=b''
    i=1
    while length!=0:
        url+=data[i:i+length]+b'.'
        i = i+length+1
        length = data[i-1]
    url = url[:-1]
    return url

def unpack_client(data):#对收到的数据进行处理，网站和ip格式人性化
    i=0
    #print(data)
    while True:##从12位开始往后找直到找到0就可以找到域名（未进行人性化，是16进制和带有长度的形式）
        if data[12+i]==0:
            break
        i+=1  
    name = data[12:12+i+1]##找到url并且翻译为字符串
    url = geturl(name)
    if data[3] == 133:##接收的是错误信号，不用读取直接返回url和0.0.0.0
        return url,{'0.0.0.0'}
    
    result = set([])
    num = int(data[6:8].hex(),16)
    counti = 0
    for i in range(num):
        if i==0:
            tmp = data[-16:]
        else:
            tmp = data[-16*(i+1):-16*i]
        if tmp[2:4]==b'\x00\x01':##如果是ipv4的数据包
            counti+=1
            ip = tmp[-4:]
            a = ''
            for each in ip:
                a += str(each) + '.'
            a = a[:-1]
            result.add(copy.deepcopy(a))
    
    return url,result

def unpack_server(data):#对收到的数据进行处理，网站和ip格式为改变，仍为16进制
    result = set([])
    num = int(data[6:8].hex(),16)
    counti = 0
    for i in range(num):
        if i==0:
            tmp = data[-16:]
        else:
            tmp = data[-16*(i+1):-16*i]
        if tmp[2:4]==b'\x00\x01':##如果是ipv4的数据包
            counti+=1
            ip = tmp[-4:]
            result.add(copy.deepcopy(ip))

    i=0
    while True:##从12位开始往后找直到找到0就可以找到域名（未进行人性化，是16进制和带有长度的形式）
        if data[12+i]==0:
            break
        i+=1  
    name = data[12:12+i+1]##找到url保持为16进制
    return name,result


def pack(id,url,hosts):#服务端打包发送给客户
    ip_set = hosts[url]
    ip_num = len(ip_set)
    Answers = b''
    for each in ip_set:
        Answers += b'\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x8a\x00\x04' + each
    if ip_set == {b'\x00\x00\x00\x00'}:
        return id + b'\x81\x85\x00\x01\x00\x00\x00\x00\x00\x00'+ url + b'\x00\x01\x00\x01'
    return id + b'\x81\x80\x00\x01' + struct.pack('>H', ip_num) + b'\x00\x00\x00\x00' + url + b'\x00\x01\x00\x01' + Answers
