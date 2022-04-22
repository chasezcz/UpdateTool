import os
import re
import threading
import socket
import struct
import sys

from config import BUFFER_SIZE, DOWNLOAD_PATH, SERVER_PORT


def socket_service(ip):
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((ip, SERVER_PORT))
        print("Start listen on [{}]:{}".format(ip, SERVER_PORT))
        s.listen()

    except socket.error as msg:
        print(msg)
        sys.exit(1)

    print('Waiting connection...')
    while 1:
        conn, addr = s.accept()
        t = threading.Thread(target=deal_data, args=(conn, addr))
        t.start()


def deal_data(conn, addr):
    print('Accept new connection from {0}'.format(addr))
    # conn.settimeout(500)

    while True:
      
        fileinfo_size = struct.calcsize('256sq')
        buf = conn.recv(fileinfo_size)

        if buf:
            fn, filesize = struct.unpack('256sq', buf)
            relative_path = fn.strip(b'\00')

            relative_path = relative_path.decode()

            # relative_path = relative_path.encode("utf-8")
            print('File new name is {0}, filesize is {1}'.format(str(relative_path), filesize))
            
            # 定义已接收文件的大小
            recvd_size = 0 
            
            if not os.path.exists(DOWNLOAD_PATH):
                os.makedirs(DOWNLOAD_PATH)
            if not relative_path.startswith('./'):
                os.makedirs(DOWNLOAD_PATH + '/' + relative_path.rstrip('/' + relative_path.split('/')[-1]))
            # filename = relative_path.split('/')[-1]
            # prepath = relative_path.rstrip(filename)


            # 存储在该脚本所在目录下面
            fp = open(DOWNLOAD_PATH + '/' + relative_path, 'wb')
            print('Start receiving...')

            # 将分批次传输的二进制流依次写入到文件
            while not recvd_size == filesize:
                if filesize - recvd_size > BUFFER_SIZE:
                    data = conn.recv(BUFFER_SIZE)
                    recvd_size += len(data)
                else:
                    data = conn.recv(filesize - recvd_size)
                    recvd_size = filesize
                fp.write(data)
            fp.close()
            print('End receive...')
        # 传输结束断开连接
        elif buf == b'\0000000':
            print("Close connection.")
            conn.close()
        

def get_ipv6_address():
    # 获取本地ipv6 地址
    output = os.popen("ipconfig /all").read()
    # print(output)
    output = output.split("以太网适配器 以太网:")[1]

    result = re.findall(r"(([a-f0-9]{1,4}:){7}[a-f0-9]{1,4})", output, re.I)
    # return result[0][0]
    return "2400:dd01:103a:2018:4521:2623:99ff:6687"


if __name__ == "__main__":
    ip = get_ipv6_address()
    print("Get ipv6 address success, " + ip)
    socket_service(ip)
