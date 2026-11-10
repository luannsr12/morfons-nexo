import unittest,sys,json,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'codigo'))
from morfon import MorphMemory,Config
from mundos import sample_world

class TestsIntegrated(unittest.TestCase):
 def test_zero_and_one_tokens_differ(self):
  m=MorphMemory(Config(),4);z=m._atom((0,0));o=m._atom((0,1))
  self.assertNotEqual(z.uid,o.uid)
 def test_one_ray_activates_without_completion(self):
  m=MorphMemory(Config(),2);n,_=m.propose(((0,1),(1,1),(2,0)))
  m.pulse([(0,1)]);self.assertEqual((n.active,n.support,n.completed),(1,1,False))
  m.pulse([(0,1),(1,1)]);self.assertEqual((n.active,n.support,n.completed),(1,2,False))
  m.pulse([(0,1),(1,1),(2,0)]);self.assertEqual((n.active,n.support,n.completed),(1,3,True))
  m.pulse([(3,1)]);self.assertEqual(n.active,0)
 def test_no_credit_on_birth(self):
  m=MorphMemory(Config(min_obs=1),9)
  m.train_one((1,1,0),1)
  node=m.nodes[m.by_lits[((0,1),(1,1))]]
  self.assertEqual(node.observations,0)
  m.train_one((1,1,0),0)
  self.assertEqual(node.observations,1)
  self.assertEqual(node.positives,0)
 def test_nested_reconstructs_parents(self):
  m=MorphMemory(Config(max_order=4,nested=True),2)
  m.propose(((0,1),(1,1)));m.propose(((2,1),(3,1)))
  n,_=m.propose(((0,1),(1,1),(2,1),(3,1)))
  self.assertEqual(n.kind,'nested'); self.assertEqual(len(n.ports),2)
  m.pulse([(0,1),(1,1),(2,1),(3,1)])
  self.assertTrue(n.completed);self.assertEqual(n.support,2)
  self.assertTrue(m.assert_integrity())
 def test_split_preserves_nested_certification(self):
  m=MorphMemory(Config(max_order=4,facet=True,facet_capacity=2),8)
  n,_=m.propose(((0,1),(1,1),(2,1),(3,1)))
  self.assertEqual(n.kind,'nested')
  m.pulse([(0,1),(1,1),(2,1),(3,1)])
  self.assertTrue(n.completed)
  self.assertTrue(m.assert_integrity())
 def test_geometry_3d_4d(self):
  for d in (3,4):
   m=MorphMemory(Config(geometry_dim=d),5)
   n,_=m.propose(((0,1),(1,1)))
   self.assertEqual(len(n.xyz),d)
   self.assertTrue(m.assert_integrity())
 def test_snapshot_restore_exact_predict(self):
  x,y,xt,yt,_=sample_world('pair_or',67,100,40)
  m=MorphMemory(Config(max_order=4,nested=True,order_controller=True,facet=True),67)
  m.fit(x,y);m.assert_integrity()
  snap=json.loads(json.dumps(m.snapshot()))
  original=[m.predict(z) for z in xt]
  n=MorphMemory.restore(snap)
  self.assertTrue(n.assert_integrity())
  self.assertEqual(original,[n.predict(z) for z in xt])
 def test_controller_only_past_evidence(self):
  m=MorphMemory(Config(order_controller=True,max_order=4),7)
  m.train_one((1,1,1,1),1)
  ctrl=m.nodes[m.controller_uid]
  self.assertEqual([f['tested'] for f in ctrl.facets],[1,1,1])
  self.assertEqual([f['correct'] for f in ctrl.facets],[0,0,0])
  self.assertEqual(m._chosen_order(),4)
 def test_local_index_ignores_distant_nodes(self):
  m=MorphMemory(Config(),5);n,_=m.propose(((0,1),(1,1)))
  m.pulse([(0,1),(1,1)]);e=m.last_info['edges']
  for i in range(1000):m._atom((i+100,1))
  m.pulse([(0,1),(1,1)])
  self.assertEqual(e,m.last_info['edges'])
 def test_completed_and_all_propagation_distinct(self):
  for mode in ('all','completed'):
   m=MorphMemory(Config(max_order=4,nested=True,propagation=mode),9)
   a,_=m.propose(((0,1),(1,1)))
   b,_=m.propose(((2,1),(3,1)))
   n,_=m.propose(((0,1),(1,1),(2,1),(3,1)))
   m.pulse([(0,1)])
   self.assertTrue(a.active)
   self.assertEqual(n.active,int(mode=='all'))
   self.assertFalse(n.completed)
 def test_negated_sensor_is_observed_zero(self):
  m=MorphMemory(Config(),12)
  n,_=m.propose(((0,1),(1,0)))
  m.pulse([(0,1),(1,0)]);self.assertTrue(n.completed)
  m.pulse([(0,1),(1,1)]);self.assertFalse(n.completed)
 def test_controller_evaluations_use_same_memory(self):
  m=MorphMemory(Config(max_order=4,order_controller=True),5)
  m.train_one((1,0,1,0),0)
  v=m.nodes[m.controller_uid].facets
  self.assertEqual(set(z['order'] for z in v),{2,3,4})
  self.assertEqual([z['tested'] for z in v],[1,1,1])

 def test_global_evidence_resides_in_ledger_morphon(self):
  m=MorphMemory(Config(),22)
  m.train_one((1,0,1),1);m.train_one((0,0,1),0)
  ledger=m.nodes[m.ledger_uid]
  self.assertEqual(ledger.kind,'ledger')
  self.assertEqual((ledger.observations,ledger.positives),(2,1))
  restored=MorphMemory.restore(json.loads(json.dumps(m.snapshot())))
  self.assertEqual((restored.n_train,restored.total_positive),(2,1))
 def test_training_resume_with_pruning_same_memory(self):
  X,Y,_,_,_=sample_world('pair_or',41,220,20)
  c=Config(max_order=4,order_controller=True,periodic_prune=True)
  a=MorphMemory(c,41);a.fit(X,Y)
  b=MorphMemory(c,41);b.fit(X[:110],Y[:110]);b=MorphMemory.restore(json.loads(json.dumps(b.snapshot())))
  b.fit(X[110:],Y[110:])
  sa=a.snapshot();sb=b.snapshot()
  self.assertEqual(sa['nodes'],sb['nodes'])
  self.assertEqual(sa['next_uid'],sb['next_uid'])
  self.assertEqual(sa['n_train'],sb['n_train'])
  self.assertEqual(sa['total_positive'],sb['total_positive'])
if __name__=='__main__':unittest.main()
