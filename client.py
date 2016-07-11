import os
from xmlrpc.client import ServerProxy
from enums import NodeType, Status


class Client:
    def __init__(self):
        self.chunk_servers = []
        if not os.getenv('YAD_NS'):
            os.environ["YAD_NS"] = "http://localhost:8889"
        self.ns = ServerProxy(os.environ["YAD_NS"])

    def start(self):
        print('send test request to ns')
        r = self.ns.list_directory('/')
        print(r)

    def list_dir(self, dir_path):
        ls = self.ns.list_directory(dir_path)
        return ls

    def create_dir(self, path):
        res = self.ns.make_directory(path)
        return res

    def delete_dir(self, path):
        res = self.ns.delete_dir(path)
        return res

    def create_file(self, path, content):
        cs_addr = self._get_cs_addr(path)
        cs = ServerProxy(cs_addr)
        chunks = self.split_file(path)
        for count, chunk in enumerate(chunks):
            cs.upload_chunk(path + '_{0}'.format(str(count)), chunk)

        res = self.ns.create_file(path, content)
        return res

    def delete_file(self, path):
        res = self.ns.delete_file(path)
        return res

    def download_file(self, path):
        pass

    def path_status(self, path):
        return "neither"

    def _get_cs_addr(self, path):
        res = self.ns.get_cs(path)
        return res['addr']

    @staticmethod
    def split_file(filename, chunksize=1024):
        if not os.path.isfile(filename):
            return Status.not_found

        with open(filename, 'r') as fr:
            data = fr.read()
        chunks = []
        while len(data) >= chunksize:
            i = chunksize+1
            while not data[i].isspace():
                if i == 0:
                    i = chunksize+1
                    break
                else:
                    i -= 1
            chunks.append(data[:i])
            data = data[i:]
        chunks.append(data)
        return chunks

    @staticmethod
    def write_combined_file(filename, chunks):
        if os.path.isfile(filename):
            return Status.already_exists

        with open(filename, 'x') as fw:
            for chunk in chunks:
                fw.write(chunk)

    # for testing purposes
    def add_chunk_server(self, cs_addr):
        cs = ServerProxy(cs_addr)
        self.chunk_servers.append(cs)

    def write(self):
        for cs in self.chunk_servers:
            cs.upload_chunk("/folder/chunk1", "123")

    def read(self):
        for cs in self.chunk_servers:
            f = cs.get_chunk("/folder/chunk1")
            print(f)

    def delete(self):
        for cs in self.chunk_servers:
            cs.delete_chunk("/folder/chunk1")


# # first arg - NS address - http://localhost:888
# if __name__ == '__main__':
#     cl = Client(sys.argv[1])
#
    # cl.start()
    # cl.add_chunk_server("http://localhost:9999")
    # cl.write()
    # cl.read()
    # cl.delete()
