import sys
import getopt
import struct
import socket
import hanshu
import time

s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
myip = socket.gethostbyname(socket.gethostname())
id0 = 1

def hostset(web):
    #print('web',web)
    output = open('hosts', 'a')
    output.write("\n")
    output.write(web)
    #print("done")
    output.close()

def main(argv):
    global id0
    try:
        opts,args = getopt.getopt(sys.argv[1:],'-h-d:-b:-g:-s',['help','postion=','blackweb=','web_url=','hosts_file'])##用于程序运行时接收参数的函数
    except getopt.GetoptError:
        print('错误，请输入-h查看帮助')
        sys.exit(2)
   # print(opts)
    for opt,opt_value in opts:
        #print('p:',opt_value)
        if opt in ('-h','--help'):
            print("-d      :输入网址直接查询ip\n")
            print("-b      :直接输入想要拉黑的网址\n")
            print("-g       :输入想要定向的网址格式为 'www.123.com/10.23.54.78'\n")
            print("-s      :获取目前的hosts")
        if opt in ('-d','--postion'):
            # print(arg)
            '''发送arg到服务器'''
            data = hanshu.pack_query(id0,opt_value)
            id0+=1
            #socket.setdefaulttimeout(20)
            s.sendto(data,('127.0.0.1',53))
            data_recv,addr = s.recvfrom(2048)
            url,ip = hanshu.unpack_client(data_recv)
            print(url.decode())
            print('查询结果为:')
            if ip == {'0.0.0.0'}:
                print("根据相关政策与法律该页面不允许访问")
            else:
                if len(ip)==0:
                    print('域名不存在')
                for each in ip:
                    print(each)
            sys.exit()
        if opt in ('-b','--blackweb'):
            hostset(opt_value+' 0.0.0.0')
            sys.exit()
        if opt in ('-g','--web_url'):
            web=opt_value.split('/')
            hostset(web[0]+' '+web[1])
            sys.exit()
        if opt in ('-s','--hosts_file'):
            r = open('hosts','r')
            file = r.read()
            print(file)
            sys.exit()
if __name__ == "__main__":
    main(sys.argv[1:])
