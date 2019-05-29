import hanshu
import socket
import time
import queue,threading
# 创建队列实例， 用于存储任务
Q = queue.Queue()

hosts = hanshu.gethosts()
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)##用于监听客户端
s1 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)##用于监听本体dns服务器
s.bind(('127.0.0.1',53))
byr=('10.3.9.5',53)##北邮DNS服务器地址



# 定义需要线程池执行的任务
def do_job():
    while True:
        (data,addr) = Q.get()##从等待队列中得到一个查询请求

        if data[-4:-2]==b'\x00\x01':##代表请求的是本服务器的host查询，那么先查询本地host
            res = hosts.get(data[12:-4],False)##从host字典中取得相应的IP地址，如果没有返回false
            if res == False:##如果没有IP地址，则向dns本地服务器发送查询请求，存储并转发
                s1.sendto(data,byr)
                bupt_data,bupt_addr = s1.recvfrom(2048)##2048代表缓冲区长度

                url,ip = hanshu.unpack_server(bupt_data)
                hosts.setdefault(url,ip)

                s.sendto(bupt_data,addr)

            else:##如果有IP地址
                print('here')
                id0 = data[:2]
                url = data[12:-4]
                pack_data = hanshu.pack(id0,url,hosts)

                s.sendto(pack_data,addr)
        else:##如果仅仅是转发的请求就直接转发
            s1.sendto(data,byr)
            bupt_data,bupt_addr = s1.recvfrom(2048)
            s.sendto(bupt_data,addr)

        Q.task_done()##结束任务，将它从队列中去除


    # 创建包括10个线程的线程池
for i in range(10):
    t = threading.Thread(target=do_job)
    t.daemon=True # 设置线程daemon  主线程退出，daemon线程也会推出，即使正在运行
    t.start()


while True:##将从客户端收到的请求信息放置到等待队列中
    # time.sleep(0.5)
    data,addr = s.recvfrom(2048)
    Q.put((data,addr))
Q.join()


