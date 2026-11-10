import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from spectral_faces import SpectralFaces,eliminate,uniquely_determined,solve

class SpectralTests(unittest.TestCase):
    def test_gf2_solver(self):
        rows=[(1,1),(2,0),(4,1),(3,1)]
        p=eliminate(rows)
        self.assertIsNotNone(p)
        self.assertEqual(uniquely_determined(7,p),0)
        self.assertEqual(solve(p),5)
    def test_conflict_expands_degree_and_splits_marks(self):
        L=SpectralFaces(2,1)
        for a,b in [(0,0),(1,0),(0,1),(1,1)]:
            out=a^b
            L.observe((a,b),0,(out,b))
        self.assertEqual(L.mm.nodes[L.roots[(0,0)]].facets[0]['degree'],1)
        for a,b in [(0,0),(1,0),(0,1),(1,1)]:
            self.assertEqual(L.query((a,b),0)[0],(a^b,b))
        self.assertIsNone(L.query((1,1),0,rays=False)[0])
    def test_quadratic_relation_learned(self):
        L=SpectralFaces(2,1)
        for a,b in [(0,0),(1,0),(0,1),(1,1)]:
            L.observe((a,b),0,(a&b,b))
        self.assertEqual(L.mm.nodes[L.roots[(0,0)]].facets[0]['degree'],2)
        self.assertEqual(L.query((1,1),0)[0],(1,1))
        self.assertEqual(L.query((0,1),0)[0],(0,1))
    def test_marks_causally_required(self):
        L=SpectralFaces(2,1)
        for a,b in [(0,0),(1,0),(0,1),(1,1)]:
            L.observe((a,b),0,(a&b,b))
        y,trace=L.query((1,1),0)
        mark=trace['marks'][0][0]
        altered,_=L.query((1,1),0,ablate_mark=mark)
        self.assertNotEqual(y,altered)


    def test_imagination_does_not_become_observed_evidence(self):
        L=SpectralFaces(2,1)
        for a,b in [(0,0),(1,0),(0,1),(1,1)]:L.observe((a,b),0,(a&b,b))
        before=len(L.episodes)
        expected=L.query((1,1),0)[0]
        for _ in range(20):
            out,trace=L.imagine((1,1),0)
            self.assertEqual(out,expected)
        self.assertEqual(len(L.episodes),before)
        self.assertEqual(sum(n.kind=='internal-imagination' for n in L.mm.nodes.values()),20)
        self.assertEqual(L.query((1,1),0)[0],expected)

    def test_snapshot_roundtrip_original_core(self):
        L=SpectralFaces(2,1)
        for a,b in [(0,0),(1,0),(0,1),(1,1)]:L.observe((a,b),0,(a&b,b))
        old=L.query((1,1),0)[0]
        restored=SpectralFaces.restore(L.mm.snapshot(),2,1)
        self.assertEqual(restored.query((1,1),0)[0],old)
        self.assertEqual(restored.count_live_marks(),L.count_live_marks())
        restored.observe((1,0),0,(1,0))
        self.assertIsNone(restored.query((1,0),0)[0])

    def test_provenance_from_observation_not_thought(self):
        L=SpectralFaces(2,1)
        for a,b in [(0,0),(1,0),(0,1),(1,1)]:L.observe((a,b),0,(a^b,b))
        L.imagine((1,1),0)
        assert all(L.mm.nodes[e].facets[0]['origin']=='observed' for e in L.episodes)

if __name__=='__main__':unittest.main()
