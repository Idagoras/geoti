import networkx as nx
import matplotlib.pyplot as plt


class TreeNode(object):
    def __init__(self, stop_id, pos, duration, cost):
        self.id = stop_id
        self.pos = pos
        self.next = {}
        self.duration = duration
        self.cost = cost


class Tree(object):
    def __init__(self, start_id, start, end, end_id):
        self.root = TreeNode(start_id, start, 0, 0)
        self.e_root = TreeNode(0, 0, 0, 0)
        self.end = TreeNode(end_id, end, 0, 0)
        self.fastNextStart = {}
        self.fastNextEnd = {}

    def startInsert(self, path, dict, nodes):
        for node in nodes:
            cur = self.root
            arr = path.get(node)
            i = 0
            while i < len(arr):
                a_node = None
                if arr[i] not in cur.next:
                    a_dic = dict[cur.id][arr[i]]
                    a_node = TreeNode(arr[i], a_dic['pos'], a_dic['duration'], a_dic['cost'])
                    cur.next[arr[i]] = a_node
                else:
                    a_node = cur.next[arr[i]]
                i += 1
                cur = cur.next[arr[i]]
                if i == len(arr):
                    self.fastNextStart[arr[i]] = a_node

    def endInsert(self, path, dict, nodes):
        for node in nodes:
            cur = self.e_root
            arr = path.get(node)
            i = 0
            while i < len(arr):
                a_node = None
                if arr[i] not in cur.next:
                    a_dic = dict[cur.id][arr[i]]
                    a_node = TreeNode(arr[i], a_dic['pos'], a_dic['duration'], a_dic['cost'])
                    cur.next[arr[i]] = a_node
                else:
                    a_node = cur.next[arr[i]]
                i += 1
                cur = cur.next[arr[i]]
                if i == 1:
                    self.fastNextEnd[arr[i]] = a_node

    def addEdgeBetweenStartNodesAndEndNodes(self, start_id, end_id, info):
        start_node = self.fastNextStart[start_id]
        end_node = self.fastNextEnd[end_id]
        start_node.next['end_id'] = end_node
        end_node.duration = info['duration']
        end_node.cost = info['cost']



"""
g = nx.DiGraph()
g.add_nodes_from(['a', 'b', 'c', 'd','e','f','g','h','i','j','k'])
g.add_weighted_edges_from([('a', 'c', 1), ('a', 'b', 2), ('c', 'd', 3), ('b', 'c', 2),('e','f',4),('g','h',4),('g','i',10),('i','j',5)],('k','j',2))
nx.draw(g)
path = nx.all_pairs_shortest_path(g)
for p in path:
    print(p)
print(path)
plt.savefig("youxiangtu.png")
plt.show()
"""