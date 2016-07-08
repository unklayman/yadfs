import os
import sys
from xmlrpc.client import ServerProxy


class Client:
    def __init__(self, addr):
        self.ns = ServerProxy(addr)

    def start(self):
        print('send test request to ns')
        r = self.ns.list_directory('/')
        print(r)

    def splitfile(self, filename, chunksize=1024):
        if not os.path.isfile(filename):
            raise IOError('No such file as: {0}'.format(filename))

        filesize = os.stat(filename).st_size

        with open(filename, 'rb') as fr:
            n_chunks = filesize // chunksize
            chunks = []
            print('splitfile: No of chunks required: {0}'.format(str(n_chunks + 1)))
            for i in range(n_chunks + 1):
                data = fr.read(chunksize)
                chunks.append(data)
                #with open(filename + "_{0}".format(str(i)), 'xb') as fw:
                #    fw.write(data)
            return chunks

    def combinefile(self, filename, chunks):
        if os.path.isfile(filename):
            raise IOError('Such file already exists: {0}'.format(filename))

        with open(filename, 'xb') as fw:
            for chunk in chunks:
                fw.write(chunk)


# first arg - NS address - http://localhost:888
if __name__ == '__main__':
    cl = Client(sys.argv[1])
    cl.start()