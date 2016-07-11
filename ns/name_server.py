import os
import random
import sys
from datetime import datetime
from os.path import dirname

from xmlrpc.server import SimpleXMLRPCServer
import yaml

sys.path.append(dirname(dirname(__file__)))
from enums import NodeType, Status
from ns.file_node import FileNode


class NameServer:
    def __init__(self, dump_on=True):
        self.root = FileNode('/', NodeType.directory)
        self.dump_on = dump_on
        self.dump_path = "name_server.yml"
        self.cs_timeout = 2  # chunk server timeout in seconds
        self.cs = {}  # chunk servers which should be detected by heartbeat

    # start name server
    # init heartbeat threads
    def start(self):
        self._load_dump()

    def _load_dump(self):
        # try to read file from dump
        if os.path.isfile(self.dump_path):
            print("Try to read file tree from dump file", self.dump_path)
            with open(self.dump_path) as f:
                self.root = yaml.load(f)
            print("File tree has loaded from the dump file")
        else:
            print("There is no detected dump file")

    # dump file-tree to file if self.dump_on is True
    def _dump(self):
        if self.dump_on:
            with open(self.dump_path, 'w') as outfile:
                outfile.write(yaml.dump(self.root))

    # get name where to put CS file
    # path in format like /my_dir/usr/new_file
    # returns { 'status': Status.not_found} if there are no available cs
    # if ok return { 'status': Status.ok, 'addr': cs_address }
    def get_cs(self, path):
        if self.root.find_path(path) is not None:
            return {'status': Status.already_exists}

        now = datetime.now()
        live = []
        for n, cs in self.cs.items():
            diff = (now - cs['last_hb']).total_seconds()
            if diff <= self.cs_timeout:
                live.append(cs)

        if len(live) == 0:
            return {'status': Status.not_found}

        i = random.randint(0, len(live) - 1)
        cs = live[i]

        return {'status': Status.ok, 'addr': cs['addr'], 'name': cs['name']}

    # create file in NS after its chunks were created in CS
    # data.path = full path to the file
    # data.size = file size
    # data.chunks = {'chunk_name_1': cs-1, 'chunk_name_2': cs-2} /dictionary
    # returns { 'status': Status.ok } in case of success
    # Status.error - in case of error during file creation
    # Status.already_exists - file is already created
    def create_file(self, data):
        file = self.root.find_path(data['path'])
        if file is not None:
            return {'status': Status.already_exists}

        file = self.root.create_file(data['path'])
        if file == "Error":
            return {'status': Status.error}

        file.size = data['size']
        for k, v in data['chunks'].items():
            file.chunks[k] = [v]

        self._dump()
        print("Created file " + data['path'])
        return {'status': Status.ok}

    # delete file\directory by specified path
    # r: {'status: Status.ok} if deleted
    # Status.error if you try to delete root
    # Status.not_found if path not found
    def delete(self, path):
        item = self.root.find_path(path)
        if item is None:
            return {'status': Status.not_found}

        if item.is_root:
            return {'status': Status.error}

        item.delete()
        self._dump()
        return {'status': Status.ok}

    # get file\directory info by given path
    # path format: /my_dir/index/some.file
    # response format:
    # { 'status': Status.ok
    #   'type': NodeType.type
    #   'path': '/my_dir/index/some.file' - full path for directory
    #   'size': 2014 - size in bytes
    #   'chunks': { cs - name of chunk server, path - path to the chunk
    #       'some.file_0': { 'cs': 'cs-2', 'path': '/my_dir/index/some.file_0'},
    #       'some.file_1': { 'cs': 'cs-1', 'path': '/my_dir/index/some.file_1'}
    #   }
    def get_file_info(self, path):
        file = self.root.find_path(path)
        if file is None:
            return {'status': Status.not_found}

        chunks = {}
        for c_name, val in file.chunks.items():
            chunks[c_name] = {'cs': val[0], 'path': file.get_full_dir_path() + '/' + c_name}

        return {'status': Status.ok,
                'type': file.type,
                'path': file.get_full_path(),
                'size': file.size,
                'chunks': chunks}

    # creates directory by the given path
    # response: { 'status': Status.ok }
    # Status.error - if error and directory not created
    # States.already_exists - if directory is already exists by given path
    def make_directory(self, path):
        d = self.root.find_path(path)

        if d is not None:
            return {'status': Status.already_exists}

        d = self.root.create_dir(path)
        if d == "Error":
            return {'status': Status.error}

        return {'status': Status.ok}

    # execute ls command in directory
    # response:
    # { 'status': Status.ok,
    #   'items': { - dict of items
    #       item_name: NodeType.file,
    #       item_name2: NodeType.directory }
    # }
    # if file not found: {'status': Status.not_found}
    def list_directory(self, path):
        print('request to list directory ' + path)
        directory = self.root.find_path(path)
        if directory is None:
            return {'status': Status.not_found}

        items = {}
        for f in directory.children:
            items[f.name] = f.type

        result = {'status': Status.ok, 'items': items}
        return result

    # return size of the file\directory by the given path
    # size of directory returns size of its children
    # r: { 'status': Status.ok\Status.not_found, 'size': size by path}    #
    def size_of(self, path):
        i = self.root.find_path(path)
        if i is None:
            return {'status': Status.not_found, 'size': 0}

        return {'status': Status.ok, 'size': i.size}

    # get heartbeat from chunk server
    def heartbeat(self, name, addr):
        if name not in self.cs:
            print('register CS (name:' + name + ', address:' + addr + ')')
            self.cs[name] = {'addr': addr, 'last_hb': datetime.now(), 'name': name}
        else:
            self.cs[name]['addr'] = addr
            self.cs[name]['last_hb'] = datetime.now()

        return {'status': Status.ok}

# args: host and port: localhost 888
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("You have to specify host and port!")

    host = sys.argv[1]
    port = int(sys.argv[2])

    ns = NameServer(dump_on=True)
    ns.start()

    server = SimpleXMLRPCServer((host, port), logRequests=False)
    server.register_introspection_functions()
    server.register_instance(ns)
    server.serve_forever()