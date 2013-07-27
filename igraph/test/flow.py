import unittest

from igraph import *
from itertools import combinations
from random import randint

class MaxFlowTests(unittest.TestCase):
    def setUp(self):
        self.g = Graph(4, [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)])
        self.capacities = [4, 2, 10, 2, 2]
        self.g.es["capacity"] = self.capacities

    def testCapacities(self):
        self.failUnless(self.capacities == \
            self.g.es.get_attribute_values("capacity"))

    def testEdgeConnectivity(self):
        self.failUnless(self.g.edge_connectivity(0, 3) == 2)
        self.failUnless(Graph.Barabasi(50).edge_connectivity() == 1)
        self.failUnless(self.g.adhesion() == 2)
        self.failUnless(Graph.Tree(10, 3).adhesion() == 1)
        self.failUnless(Graph.Tree(10, 3, TREE_OUT).adhesion() == 0)
        self.assertRaises(ValueError, self.g.edge_connectivity, 0)

    def testVertexConnectivity(self):
        self.failUnless(self.g.vertex_connectivity(0, 3) == 2)
        self.failUnless(Graph.Barabasi(50).vertex_connectivity() == 1)
        self.failUnless(self.g.cohesion() == 2)
        self.failUnless(Graph.Tree(10, 3).cohesion() == 1)
        self.failUnless(Graph.Tree(10, 3, TREE_OUT).cohesion() == 0)
        self.assertRaises(ValueError, self.g.vertex_connectivity, 0)
        self.assertRaises(InternalError, self.g.vertex_connectivity, 0, 1)
        self.failUnless(self.g.vertex_connectivity(0, 1, neighbors="nodes") == 4)
        self.failUnless(self.g.vertex_connectivity(0, 1, neighbors="negative") == -1)

    def testMaxFlowValue(self):
        self.failUnless(self.g.maxflow_value(0, 3) == 2)
        self.failUnless(self.g.maxflow_value(0, 3, self.capacities) == 4)
        self.failUnless(self.g.maxflow_value(0, 3, "capacity") == 4)
        self.assertRaises(KeyError, self.g.maxflow_value, 0, 3, "unknown")

    def testMaxFlow(self):
        flow = self.g.maxflow(0, 3)
        self.assertEquals(flow.value, 2)
        self.assertEquals(flow.flow, [1, 1, 0, 1, 1])

        flow = self.g.maxflow(0, 3, "capacity")
        self.assertEquals(flow.value, 4)
        self.assertEquals(flow.cut, [3, 4])
        self.assertEquals([e.index for e in flow.es], [3, 4])
        self.failUnless(set(flow.partition[0]).union(flow.partition[1]) == \
          set(range(self.g.vcount())))

        self.assertRaises(KeyError, self.g.maxflow, 0, 3, "unknown")


class CutTests(unittest.TestCase):
    def constructSimpleGraph(self, directed=False):
        g = Graph(4, [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)], directed)
        g.es["capacity"] = [4, 2, 10, 2, 2]
        return g

    def constructLadderGraph(self, directed=False):
        el  = zip(range(0, 5), range(1, 6))
        el += zip(range(6, 11), range(7, 12))
        el += zip(range(0, 6), range(6, 12))
        g = Graph(el, directed=directed)
        return g

    def testMinCutValue(self):
        g = self.constructSimpleGraph()
        self.failUnless(g.mincut_value(0, 3) == 2)
        self.failUnless(g.mincut_value(0, 3, g.es["capacity"]) == 4)
        self.failUnless(g.mincut_value(0, 3, "capacity") == 4)
        self.assertRaises(KeyError, g.mincut_value, 0, 3, "unknown")
        self.failUnless(g.mincut_value() == 2)
        self.failUnless(g.mincut_value(source=0) == 2)
        self.failUnless(g.mincut_value(target=2) == 2)

    def testMinCut(self):
        g = self.constructSimpleGraph()
        mc = g.mincut()
        self.failUnless(isinstance(mc, Cut))
        self.failUnless(mc.value == 2)
        self.failUnless(set(mc.partition[0]).union(mc.partition[1]) == \
          set(range(g.vcount())))
        self.failUnless(isinstance(str(mc), str))
        self.failUnless(isinstance(repr(mc), str))
        self.failUnless(isinstance(mc.es, EdgeSeq))
        self.failUnless(len(mc.es) == 2)
        mc = g.mincut(capacity="capacity")
        self.failUnless(mc.value == 4)
        self.assertRaises(KeyError, g.mincut, capacity="unknown")

    def testMinCutWithSourceAndTarget(self):
        g = self.constructSimpleGraph()
        mc = g.mincut(0, 3, "capacity")
        self.failUnless(isinstance(mc, Cut))
        self.failUnless(mc.cut == [3, 4])
        self.failUnless(mc.value == 4)
        self.failUnless(set(mc.partition[0]).union(mc.partition[1]) == \
          set(range(g.vcount())))
        mc = g.mincut(0, 3)
        self.failUnless(isinstance(mc, Cut))
        self.failUnless(mc.cut == [3, 4])
        self.failUnless(mc.value == 2)
        mc = g.mincut(2, 0, "capacity")
        self.failUnless(isinstance(mc, Cut))
        self.failUnless(mc.cut == [0, 1])
        self.failUnless(mc.value == 6)
        self.assertRaises(ValueError, g.mincut, 2, capacity="capacity")

    def testStMinCut(self):
        g = self.constructSimpleGraph()
        mc = g.st_mincut(0, 3, "capacity")
        self.failUnless(isinstance(mc, Cut))
        self.failUnless(mc.cut == [3, 4])
        self.failUnless(mc.value == 4)
        self.failUnless(set(mc.partition[0]).union(mc.partition[1]) == \
          set(range(g.vcount())))
        mc = g.st_mincut(0, 3)
        self.failUnless(isinstance(mc, Cut))
        self.failUnless(mc.cut == [3, 4])
        self.failUnless(mc.value == 2)
        mc = g.st_mincut(2, 0, "capacity")
        self.failUnless(isinstance(mc, Cut))
        self.failUnless(mc.cut == [0, 1])
        self.failUnless(mc.value == 6)
        self.assertRaises(KeyError, g.st_mincut, 2, 0, capacity="unknown")


    def testAllSTCuts1(self):
        # Simple graph with four vertices
        g = self.constructSimpleGraph(directed=True)
        partitions = [((0, 1, 1, 1), 2), ((0, 0, 1, 1), 3),
                      ((0, 1, 0, 1), 2), ((0, 0, 0, 1), 2)]
        values = dict(partitions)
        partitions = [partition for partition, _ in partitions]
        for cut in g.all_st_cuts(0,3):
            membership = tuple(cut.membership)
            self.failUnless(membership in partitions,
                "%r not found among expected partitions" % (membership,))
            self.assertEquals(cut.value, values[membership])
            self.assertEquals(len(cut.es), values[membership])
            partitions.remove(membership)
        self.failUnless(partitions == [],
                "expected partitions not seen: %r" % (partitions, ))

    def testAllSTCuts2(self):
        # "Ladder graph"
        g = self.constructLadderGraph(directed=True)
        cuts = g.all_st_cuts(0, 11)
        self.assertEquals(len(cuts), 36)
        self.assertEquals(len(set(tuple(cut.membership) for cut in cuts)), 36)
        for cut in cuts:
            g2 = g.copy()
            g2.delete_edges(cut.es)
            self.failIf(g2.is_connected(),
                "%r is not a real cut" % (cut.membership,))
            self.failIf(cut.value < 2 or cut.value > 6)


    def testAllSTMinCuts2(self):
        # "Ladder graph"
        g = self.constructLadderGraph()
        g.to_directed("mutual")
        cuts = g.all_st_mincuts(0, 11)
        self.assertEquals(len(cuts), 7)
        self.assertEquals(len(set(tuple(cut.membership) for cut in cuts)), 7)
        for cut in cuts:
            self.assertEquals(cut.value, 2)
            g2 = g.copy()
            g2.delete_edges(cut.es)
            self.failIf(g2.is_connected(),
                "%r is not a real cut" % (cut.membership,))

        g.es["capacity"] = [2, 1, 2, 1, 2, 2, 1, 2, 1, 2, 1, 1, 1, 1, 1]
        cuts = g.all_st_mincuts(0, 11, "capacity")
        self.assertEquals(len(cuts), 2)
        self.assertEquals(cuts[0].membership, [0,0,1,1,1,1,0,0,1,1,1,1])
        self.assertEquals(cuts[1].membership, [0,0,0,0,1,1,0,0,0,0,1,1])
        self.assertEquals(cuts[0].value, 2)
        self.assertEquals(cuts[1].value, 2)


class GomoryHuTests(unittest.TestCase):
    def testEmpty(self):
        g = Graph()
        t = g.gomory_hu_tree()
        self.assertEquals(0, t.vcount())
        self.assertEquals(0, t.ecount())

    def testSimpleExample(self):
        g = Graph(6, [(0,1),(0,2),(1,2),(1,3),(1,4),(2,4),(3,4),(3,5),(4,5)], \
                directed=False)
        g.es["capacity"] = [1,7,1,3,2,4,1,6,2]
        t = g.gomory_hu_tree("capacity")
        self.validate_gomory_hu_tree(g, t)

    def testDirected(self):
        g = Graph(6, [(0,1),(0,2),(1,2),(1,3),(1,4),(2,4),(3,4),(3,5),(4,5)], \
                directed=True)
        g.es["capacity"] = [1,7,1,3,2,4,1,6,2]
        self.assertRaises(InternalError, g.gomory_hu_tree, "capacity")

    def testRandomGRG(self):
        g = Graph.GRG(100, 0.2)
        self.validate_gomory_hu_tree(g, g.gomory_hu_tree())
        g.es["capacity"] = [randint(0, 10) for _ in xrange(g.ecount())]
        self.validate_gomory_hu_tree(g, g.gomory_hu_tree("capacity"))

    def validate_gomory_hu_tree(self, g, t):
        n = g.vcount()

        self.assertEquals(n, t.vcount())
        self.assertEquals(n-1, t.ecount())
        self.assertFalse(t.is_directed())

        if "capacity" in g.edge_attributes():
            capacities = g.es["capacity"]
        else:
            capacities = None

        for i, j in combinations(range(n), 2):
            path = t.get_shortest_paths(i, j, output="epath")
            if path:
                path = path[0]
                expected_flow = min(t.es[path]["flow"])
                observed_flow = g.maxflow_value(i, j, capacities)
                self.assertEquals(observed_flow, expected_flow)

def suite():
    flow_suite = unittest.makeSuite(MaxFlowTests)
    cut_suite = unittest.makeSuite(CutTests)
    gomory_hu_suite = unittest.makeSuite(GomoryHuTests)
    return unittest.TestSuite([flow_suite, cut_suite, gomory_hu_suite])

def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
if __name__ == "__main__":
    test()

