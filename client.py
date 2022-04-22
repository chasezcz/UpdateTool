import logging
import os
import socket
import struct
import sys
from tkinter import Tk, filedialog, messagebox


from config import *

SERVER_IP = '2400:dd01:103a:2018:4521:2623:99ff:6687'

class Client():
    socket = None
    def build_socket(self, ip):
        try:
            s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            s.connect((ip, SERVER_PORT))
        except socket.error as msg:
            logging.error(msg)
            sys.exit(1)
        self.socket = s
        print("Connect Success")

    def send_file(self, file_path):
        relative_path = file_path[0]
        absolute_path = file_path[1]
        print("Start send file {}, relative: {}".format(absolute_path, relative_path))

        fhead = struct.pack('256sq', relative_path.encode("utf-8"), os.stat(absolute_path).st_size)
        self.socket.send(fhead)
        fp = open(absolute_path, 'rb')
        while True:
            data = fp.read(BUFFER_SIZE)
            if not data:
                print('File {} send over.'.format(absolute_path.split('/')[-1]))
                break
            self.socket.send(data)
        
    
    def close(self):
        self.socket.send(b'\0000000')
        self.socket.close()


def get_file_paths():
    root = Tk()
    root.withdraw()
    option = messagebox.askyesno("提示", "是否要传输文件夹？")
    paths = []
    if option:
        target_path = filedialog.askdirectory()
        for root, _, files in os.walk(target_path):
            root = root.replace('\\', '/')
            for f in files:
                relative_path = root.strip(target_path.rstrip('/'))
                if not relative_path:
                    relative_path = '.'
                paths.append((relative_path + '/' + f, root  + '/' + f))
    else:
        target_path = filedialog.askopenfilenames()
        for p in target_path:
            paths.append(('./' + os.path.basename(p), p))
    return paths



if __name__ == '__main__':
    
    client = Client()
    client.build_socket(SERVER_IP)
    paths = get_file_paths()
    for file_path in paths:
        client.send_file(file_path)

    # head = struct.pack('512sl', "123".encode("utf-8"), os.stat("d:/Workspace/src/UpdateTool/client.py").st_size)

    # f = get_file_paths()
    # print(f)
    # paths = []
    # for root, _, files in os.walk("D:/Games/uTorrent"):
    #     for f in files:
    #         print(root, os.path.curdir)
            # paths.append((f, os.path.join(root, f)))
    # print(paths)