import os
import re
import threading
import socket
import struct
import sys
import time

from tqdm import tqdm

from config import BUFFER_SIZE, DOWNLOAD_PATH, SERVER_IP, SERVER_PORT, get_suitable_size_unit


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
    if not os.path.exists(DOWNLOAD_PATH):
        print("Create Download folder")
        os.makedirs(DOWNLOAD_PATH)

    while True:
        fileinfo_size = struct.calcsize('256sq')
        buf = conn.recv(fileinfo_size)

        if buf:
            fn, filesize = struct.unpack('256sq', buf)
            relative_path = fn.strip(b'\00')
            relative_path = relative_path.decode()

            # relative_path = relative_path.encode("utf-8")
            print('File new name is {0}, filesize is {1}'.format(str(relative_path), get_suitable_size_unit(filesize)))
            
            # 定义已接收文件的大小
            recvd_size = 0 
            filename = os.path.basename(relative_path)
            save_path = DOWNLOAD_PATH + '/' + relative_path.rstrip(filename)
            absolute_path = DOWNLOAD_PATH + '/' + relative_path
            if not os.path.exists(save_path):    
                os.makedirs(save_path)

            fp = open(absolute_path, 'wb')
            print('Start receiving...')

            with tqdm(total=filesize, unit='B', unit_divisor=1024, unit_scale=True) as pbar:
                pbar.set_description("Processing:")
                while recvd_size != filesize:
                    rest_size = filesize - recvd_size
                    cur_recv_size = BUFFER_SIZE if rest_size >= BUFFER_SIZE else rest_size 
                    
                    data = conn.recv(cur_recv_size)
                    recvd_size += cur_recv_size
                    pbar.update(cur_recv_size) 
                      
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
    return result[0][0]


if __name__ == "__main__":
    ip = get_ipv6_address
    ip = SERVER_IP
    print("Get ipv6 address success, " + ip)
    socket_service(ip)
