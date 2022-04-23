import logging
import os
import socket
import struct
import sys
from tkinter import Tk, filedialog, messagebox

from tqdm import tqdm

from config import *

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
        filesize = os.stat(absolute_path).st_size
        fhead = struct.pack('256sq', relative_path.encode("utf-8"), filesize)
        self.socket.send(fhead)
        fp = open(absolute_path, 'rb')

        with tqdm(total=filesize, unit='B', unit_divisor=1024, unit_scale=True) as pbar:
            while True:
                data = fp.read(BUFFER_SIZE)
                if not data:
                    print('File {} send over.'.format(absolute_path.split('/')[-1]))
                    break
                self.socket.send(data)
                pbar.update(len(data))
        
    
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
        t = target_path.split('/')[-1]
        for root, _, files in os.walk(target_path):
            root = root.replace('\\', '/')
            for f in files:
                absolute_path = root  + '/' + f
                relative_path = t + '/' + absolute_path.lstrip(target_path)
                paths.append((relative_path, absolute_path))
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