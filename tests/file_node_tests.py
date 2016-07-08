import unittest
from name_server import FileNode, NodeType


class FileNodeTests(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.root = FileNode("root", NodeType.directory)

    def test_find_node(self):
        file = FileNode("test.txt", NodeType.file)
        self.root.add_child(file)
        self.assertEqual(file, self.root.find_path("/test.txt"))

    def test_among_several_files(self):
        file = FileNode("test1.txt", NodeType.file)
        self.root.add_child(file)

        file = FileNode("test2.txt", NodeType.file)
        self.root.add_child(file)

        file = FileNode("another_file", NodeType.file)
        self.root.add_child(file)

        self.assertEqual(file, self.root.find_path("/another_file"))

    def test_find_in_sub_folders(self):
        parent = self.root
        folder = FileNode("usr", NodeType.directory)
        parent.add_child(folder)

        parent = folder
        folder = FileNode("bin", NodeType.directory)
        parent.add_child(folder)

        parent = folder
        folder = FileNode("local", NodeType.directory)
        parent.add_child(folder)

        self.assertEqual(folder, self.root.find_path("/usr/bin/local"))

    def test_if_not_found_return_none(self):
        parent = self.root
        folder = FileNode("usr", NodeType.directory)
        parent.add_child(folder)

        parent = folder
        folder = FileNode("bin", NodeType.directory)
        parent.add_child(folder)

        parent = folder
        folder = FileNode("local", NodeType.directory)
        parent.add_child(folder)

        self.assertEqual(None, self.root.find_path("/usr/ans"))


if __name__ == '__main__':
    unittest.main()
