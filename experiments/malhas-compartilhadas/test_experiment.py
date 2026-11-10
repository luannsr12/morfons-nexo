import unittest
from experiment import (MeshMemory,antiunify,match_pattern,instantiate,build_world,
                        evaluate_cases,CORE_LAW,random_oracle_tests,motif_test,test_ray_and_provenance,chain_pattern_test,proof_factorization_test)

class MeshMathematicalTests(unittest.TestCase):
    def test_immutable_nucleus_mutable_faces(self):
        m=MeshMemory();m.genesis_create('a',config={'old':'v'})
        self.assertEqual(m.nodes['a'].core,CORE_LAW)
        m.genesis_edit_face('a','new','value')
        self.assertEqual(m.nodes['a'].faces['new'],'value')
        with self.assertRaises(AttributeError):m.nodes['a'].core=('reprogrammed',)
        self.assertEqual(m.nodes['a'].core,CORE_LAW)

    def test_genesis_transient_persistent(self):
        m=MeshMemory();m.genesis_create('a');m.genesis_create('b')
        m.genesis_promote('a')
        with self.assertRaises(ValueError):m.genesis_remove('a')
        m.genesis_remove('b')
        self.assertNotIn('b',m.nodes)

    def test_join_requires_same_identity(self):
        m=MeshMemory()
        for uid,display in [('s','s'),('b1','B'),('b2','B'),('t','t')]:m.genesis_create(uid,display)
        m.add_fact('s','a','b1',0,{0},'e1')
        m.add_fact('b2','b','t',1,{0},'e2')
        ans,_,_=m.query('s',('a','b'),context=0)
        self.assertNotIn('t',ans)
        ans_bad,_,_=m.query('s',('a','b'),context=0,match_display=True)
        self.assertIn('t',ans_bad)

    def test_intersection_of_contexts(self):
        m=MeshMemory()
        for uid in ('s','b','c','t'):m.genesis_create(uid)
        for a,r,b,ly,scope,ev in [('s','a','b',0,{0,1},'e1'),
                                  ('b','b','c',1,{1,2},'e2'),
                                  ('c','c','t',2,{1},'e3')]:
            m.add_fact(a,r,b,ly,scope,ev)
        ans,_,_=m.query('s',('a','b','c'))
        self.assertEqual(ans['t'][0]['scope'],[1])
        ans0,_,_=m.query('s',('a','b','c'),context=0)
        self.assertNotIn('t',ans0)

    def test_provenance_and_physical_rays(self):
        v=test_ray_and_provenance()
        self.assertEqual(v['initial_independent_paths'],2)
        self.assertEqual(v['initial_terminal_distinct_rays'],2)
        self.assertEqual(v['remaining_proofs_after_retraction'],1)

    def test_conservative_generalization(self):
        m=motif_test()
        self.assertEqual(m['exact_reconstructions'],6)
        self.assertEqual(m['identity_savings_n3'],2)
        self.assertLess(m['unrelated_savings_n3'],0)
        p=antiunify(('a','a'),('b','b'))
        self.assertIsNone(match_pattern(p,('a','b')))
        self.assertEqual(instantiate(p,match_pattern(p,('z','z'))),('z','z'))

    def test_cross_mesh_motif_generalization(self):
        r=chain_pattern_test()
        self.assertEqual(r['generalized_variables'],5)
        self.assertTrue(r['new_unseen_path_matches'])
        self.assertTrue(r['broken_identity_rejected'])
        self.assertTrue(r['broken_context_rejected'])

    def test_cost_accounting(self):
        m,cases=build_world(n=20,seed=3)
        r=m.structural_counts(64,8,16)
        self.assertEqual(r['minimal_copy_bridges'],r['layer_occurrences']-r['distinct_used_units'])
        self.assertEqual(r['copied_cost']-r['shared_cost'],r['saving'])

    def test_multiple_randomized_worlds(self):
        for seed in range(20):
            m,cases=build_world(n=120,seed=seed)
            r,_=evaluate_cases(m,cases,'shared_context')
            self.assertEqual((r['fp'],r['fn']),(0,0),seed)
            self.assertEqual(r['tp']+r['tn'],len(cases),seed)

    def test_proof_factorization_against_exhaustive_paths(self):
        rows=proof_factorization_test()
        self.assertEqual(rows[-1]['explicit_proof_paths'],4096)
        self.assertLess(rows[-1]['factorized_dag_nodes'],200)
        self.assertEqual(rows[-1]['target_physical_rays'],2)

    def test_independent_join_oracle(self):
        self.assertEqual(random_oracle_tests(iterations=250),250)

if __name__=='__main__':unittest.main(verbosity=2)
