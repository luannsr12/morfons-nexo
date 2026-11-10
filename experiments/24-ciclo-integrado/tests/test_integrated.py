import unittest,sys
from pathlib import Path
from dataclasses import FrozenInstanceError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from integrated import InteractingMorphons, Nucleus
from evaluate import choose_inputs,world,contexts
from adversarial import contradictory_observation, physical_edge_ablation, evolving_degree
import random

class IntegrationTest(unittest.TestCase):
    def setUp(self):
        self.m=InteractingMorphons(4,2,3,2,seed=77)
    def test_nucleus_immutable(self):
        with self.assertRaises(FrozenInstanceError):self.m.K.algebra='mutable'
        self.assertEqual(self.m.K,Nucleus())
    def test_no_self_written_faces(self):
        self.m.observe((0,0,0,0),0,(1,0,0))
        self.assertTrue(self.m.validate_invariants()['no_self_edits'])
        self.assertTrue(all(m['actor']!=m['target'] for m in self.m.mutations))
    def test_no_face_split_on_conflict(self):
        self.m.observe((0,0,0,0),0,(1,0,0))
        roots=dict(self.m.roots)
        self.m.observe((0,0,0,0),0,(0,0,0))
        self.assertEqual(self.m.roots,roots)
        self.assertEqual(len(self.m._faces(roots[0,0],'experience')),2)
        self.assertIsNone(self.m.query((0,0,0,0),0)[0])
    def test_one_ray_active_support_more(self):
        rid=self.m.roots[0,0]
        self.m.mm.pulse_units([self.m.sources['action',0]])
        self.assertEqual(self.m.mm.nodes[rid].active,1)
        self.assertEqual(self.m.mm.nodes[rid].support,1)
        self.assertFalse(self.m.mm.nodes[rid].completed)
        self.m.mm.pulse_units([self.m.sources['action',0],self.m.sources['output',0]])
        self.assertEqual(self.m.mm.nodes[rid].support,2)
        self.assertTrue(self.m.mm.nodes[rid].completed)
    def test_training_and_holdout(self):
        for a in range(2):
            train,test=choose_inputs(random.Random(200+a),11,active=True)
            for x in train:self.m.observe(x,a,world(1,x,a,0))
            for x in test:self.assertEqual(self.m.query(x,a)[0],world(1,x,a,0))
    def test_no_pulses_no_prediction(self):
        self.m.observe((0,0,0,0),0,(1,0,0))
        self.assertIsNone(self.m.query((0,0,0,0),0,block_pulses=True)[0])
    def test_internal_prediction_not_training(self):
        self.m.observe((0,0,0,0),0,(1,0,0))
        before=len(self.m.events)
        self.m.query((0,0,0,0),0,record_imagination=True)
        self.assertEqual(len(self.m.events),before)
        self.assertEqual(self.m.metrics['thoughts'],1)
    def test_feedback_session_same_memory(self):
        self.m.start_session(1)
        self.assertEqual(self.m.current_history(),1)
        x=(0,0,0,1);self.m.observe(x,0,(1,0,0),live=True)
        self.assertEqual(self.m.current_history(),0)
        faces=self.m._faces(self.m.session)
        self.assertEqual(faces[-1]['origin'],'observed')
        self.assertTrue(self.m.validate_invariants()['no_self_edits'])
    def test_snapshot_recovery(self):
        self.m.observe((0,0,0,0),0,(1,0,0))
        replay=InteractingMorphons.restore(self.m.snapshot())
        self.assertEqual(replay.query((0,0,0,0),0)[0],self.m.query((0,0,0,0),0)[0])
        self.assertTrue(replay.validate_invariants()['all_nuclei_constant'])
    def test_query_compose(self):
        for a in range(2):
            train,test=choose_inputs(random.Random(200+a),11,active=True)
            for x in train:self.m.observe(x,a,world(0,x,a,0))
        s=(0,0,0);h=0
        goal=world(0,s+(h,),0,0)
        plan,trace=self.m.choose_plan(s,h,goal)
        self.assertIsNotNone(plan)
    def test_real_edge_ablation(self):
        r=physical_edge_ablation()
        self.assertTrue(r['changed']);self.assertTrue(r['restored_exactly'])
        self.assertFalse(r['irrelevant_edge_changed_result'])
    def test_contradictions_abstain(self):
        r=contradictory_observation()
        self.assertIsNone(r['after'])
        self.assertEqual(r['reason'],'inconsistent')
    def test_higher_order_update(self):
        r=evolving_degree(0)
        self.assertEqual(r['phases'][1]['wrong'],0)
        self.assertEqual(r['phases'][1]['correct'],2)

if __name__=='__main__':unittest.main()
