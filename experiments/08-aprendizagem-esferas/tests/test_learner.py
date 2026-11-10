"""Regressões e invariantes do protótipo. Testes repetíveis com Python puro."""
import unittest
from learner import NexoSphereLearner
from worlds import generate_world

class NexoStructuralTests(unittest.TestCase):
    def test_one_ray_activates_and_extra_ray_raises_support(self):
        m=NexoSphereLearner(max_order=2)
        m.create(((0,1),(1,1)))
        k=tuple(sorted(((0,1),(1,1))))
        m.activate(m.tokens_from_vector((1,0)))
        self.assertEqual(m.spheres[k].state,1)
        self.assertEqual(m.spheres[k].rays,1)
        m.activate(m.tokens_from_vector((1,1)))
        self.assertEqual(m.spheres[k].state,1)
        self.assertEqual(m.spheres[k].rays,2)
        m.activate(frozenset())
        self.assertEqual(m.spheres[k].state,0)
        self.assertEqual(m.spheres[k].rays,0)

    def test_zero_observed_is_not_missing(self):
        m=NexoSphereLearner()
        self.assertEqual(m.tokens_from_vector((0,1)),frozenset({(0,0),(1,1)}))
        m.create(((0,0),))
        m.activate(m.tokens_from_vector((0,1)))
        self.assertEqual(m.spheres[((0,0),)].rays,1)

    def test_candidate_does_not_get_credit_for_birth_example(self):
        m=NexoSphereLearner()
        m.step((1,1,0),1)
        k=((0,1),(1,1))
        self.assertIn(k,m.spheres)
        self.assertEqual(m.spheres[k].hits,0)
        self.assertEqual(m.spheres[k].positives,0)
        m.step((1,1,0),0)
        self.assertEqual(m.spheres[k].hits,1)
        self.assertEqual(m.spheres[k].positives,0)

    def test_partial_activation_does_not_fake_complete_rule(self):
        m=NexoSphereLearner(min_evidence=1,min_confidence=.7,min_gain=0)
        k=((0,1),(1,1))
        m.create(k)
        m.spheres[k].useful=True
        predicted,focus=m.predict(m.tokens_from_vector((1,0)))
        self.assertEqual(m.spheres[k].state,1)
        self.assertEqual(m.spheres[k].rays,1)
        self.assertEqual(predicted,0)
        self.assertIsNone(focus)
        predicted,focus=m.predict(m.tokens_from_vector((1,1)))
        self.assertEqual(predicted,1)

    def test_remote_memories_are_not_scanned_on_activation(self):
        m=NexoSphereLearner(max_candidates=1000)
        k=((0,1),(1,1))
        m.create(k)
        m.spheres[k].useful=True
        m.activate(m.tokens_from_vector((1,1)))
        initial=m.rays_visited
        initial_result=m.predict(m.tokens_from_vector((1,1)))
        delta_before=m.rays_visited-initial
        for i in range(100,400,2):
            m.create(((i,1),(i+1,1)))
        before=m.rays_visited
        self.assertEqual(m.predict(m.tokens_from_vector((1,1))),initial_result)
        delta_after=m.rays_visited-before
        self.assertEqual(delta_before,delta_after)
        self.assertEqual(delta_before,2)

    def test_learns_pair_without_embedding_world_rule(self):
        m=NexoSphereLearner()
        train=list(generate_world('pares',1100,215))
        for x,y in train:m.step(x,y)
        useful=[set(s.parts) for s in m.spheres.values() if s.useful and len(s.parts)==2]
        self.assertIn({(0,1),(4,1)},useful)
        self.assertIn({(2,1),(9,1)},useful)

    def test_negative_control_no_rule(self):
        m=NexoSphereLearner()
        for x,y in generate_world('sem_relacao',1100,215):m.step(x,y)
        self.assertEqual(m.audit()['n_useful'],0)

if __name__=='__main__':unittest.main()

class PersistenceTests(unittest.TestCase):
    def test_save_restore_inference_without_training_events(self):
        import tempfile
        from pathlib import Path
        m=NexoSphereLearner()
        for x,y in generate_world('pares',1100,215):m.step(x,y)
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/'aprendido.json'
            n=m.save_learned_memory(f)
            self.assertGreaterEqual(n,2)
            restored=NexoSphereLearner.from_learned_memory(f)
            for x,y in list(generate_world('pares',100,286)):
                tok=m.tokens_from_vector(x)
                self.assertEqual(m.predict(tok)[0],restored.predict(tok)[0])
