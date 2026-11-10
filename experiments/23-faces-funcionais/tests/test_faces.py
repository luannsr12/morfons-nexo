import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from facets import FaceWorldLearner

class FaceTests(unittest.TestCase):
    def test_original_core_identity_and_rays(self):
        L=FaceWorldLearner(3,1)
        L.observe((0,0,0),0,(0,0,0))
        result,proof=L.query((0,0,0),0)
        self.assertEqual(result,(0,0,0))
        self.assertEqual(proof['reason'],'ok')
        self.assertTrue(all(v>=1 for v in proof['support']))
        self.assertIsNone(L.query((0,0,0),0,rays=False)[0])
    def test_context_forces_morphological_split(self):
        L=FaceWorldLearner(3,1)
        L.observe((1,0,0),0,(1,1,0))
        L.observe((1,0,1),0,(1,0,1))
        self.assertGreater(L.stats['subdivisions'],0)
        self.assertEqual(L.query((1,0,0),0)[0],(1,1,0))
        self.assertEqual(L.query((1,0,1),0)[0],(1,0,1))
    def test_ablate_face_blocks_inference(self):
        L=FaceWorldLearner(2,1)
        L.observe((1,0),0,(1,1))
        _,pr=L.query((1,0),0)
        self.assertEqual(L.query((1,0),0,ablation_face=pr['faces'][0])[0],None)
    def test_no_split_cannot_separate_conflict(self):
        L=FaceWorldLearner(3,1,morph=False)
        L.observe((1,0,0),0,(1,1,0))
        L.observe((1,0,1),0,(1,0,1))
        self.assertEqual(L.query((1,0,0),0)[0],L.query((1,0,1),0)[0])
    def test_snapshot_roundtrip(self):
        from morfon_exp21_original import MorphMemory
        L=FaceWorldLearner(3,1)
        L.observe((1,0,0),0,(1,1,0))
        L.observe((1,0,1),0,(1,0,1))
        restored=MorphMemory.restore(L.snapshot())
        self.assertEqual(len(restored.nodes),len(L.mm.nodes))
        self.assertEqual(restored.nodes[L.roots[(0,1)]].facets[0],L.mm.nodes[L.roots[(0,1)]].facets[0])
    def test_no_teacher_during_inference(self):
        L=FaceWorldLearner(2,1)
        L.observe((0,0),0,(1,0))
        L.observe((1,0),0,(1,0))
        self.assertEqual(L.query((0,0),0)[0],(1,0))
        self.assertEqual(L.query((1,0),0)[0],(1,0))

if __name__=='__main__':unittest.main()
