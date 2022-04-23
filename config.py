# SERVER_IP = "2400:dd01:103a:2018:4521:2623:99ff:6687"
SERVER_IP = "2400:dd01:101a:5:f9bd:f57d:b56d:84d4"

SERVER_PORT = 51010

BUFFER_SIZE = 2048

DOWNLOAD_PATH = './downloads'


def get_suitable_size_unit(size):
    if size < 1024:
        return '{} B'.format(size)
    if size < 1024*1024:
        return '%.2f KB' % (size / 1024)
    if size < 1024*1024*1024:
        return '%.2f MB' % (size / 1024 / 1024)
    return '%.2f GB' % (size / 1024 / 1024 / 1024)   