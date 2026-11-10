from __future__ import annotations
import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from continuous import ContinuousNexo
from nexo20 import NexoDialogue

TRAIN=ROOT/'training'/'trained21.json'

class TestRegressions(unittest.TestCase):
    def make(self):return ContinuousNexo.load(TRAIN)
    def test_correction_survives_restart(self):
        n=self.make();n.answer('Meu nome é Aline.');n.answer('Meu nome é Tainá.')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'c.json';n.save(p);z=ContinuousNexo.load(p)
            self.assertEqual(z.answer('Qual é meu nome?')['answer'],'Tainá')
            self.assertEqual(z.answer('Isso permite concluir que meu nome é Aline?')['reason'],'unknown')
    def test_multiple_distinct_topics_interleaved(self):
        n=self.make()
        for i in range(20):
            n.answer(f'Gloria{i} mora em Vila{i}.')
            n.answer(f'Gloria{i} guarda mapa{i}.')
        for i in reversed(range(20)):
            self.assertEqual(n.answer(f'Onde Gloria{i} mora?')['answer'],f'Vila{i}')
            self.assertEqual(n.answer(f'O que Gloria{i} guarda?')['answer'],f'mapa{i}')
    def test_unknown_is_not_fake_response(self):
        n=self.make();n.answer('Meu nome é Paulo.')
        r=n.answer('Você entende todas as consequências ontológicas do tempo?')
        self.assertEqual(r['reason'],'self_identified_unparsed_question')
        self.assertNotEqual(r['answer'],'Paulo')
    def test_pending_survives_restart(self):
        n=self.make();n.answer('Qual é meu nome?')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'mem.json';n.save(p);n=ContinuousNexo.load(p)
            self.assertEqual(len(n.introspect()['unresolved_questions']),1)
            n.answer('Isabela');n.save(p)
            m=ContinuousNexo.load(p)
            self.assertEqual(m.answer('Qual é meu nome?')['answer'],'Isabela')
    def test_proactive_self_question_on_unparsed(self):
        n=self.make();n.answer('O universo possui uma sequência desconhecida de estados.')
        q=[x for x in n.mem.nodes.values() if x.kind=='dialogue_self_question']
        self.assertTrue(any(x.facets[0].get('source')=='unexplained_observation' for x in q))
        self.assertGreaterEqual(q[-1].support,1)
    def test_stored_evidence_not_a_cache(self):
        n=self.make();n.answer('Meu nome é Luan.')
        fact=next(x for x in n.mem.nodes.values() if x.kind=='dialogue_fact')
        self.assertIn(fact.uid,n.mem.cache[n._session_atom()])
        self.assertGreaterEqual(len(fact.ports),3)
        self.assertIn('reason_uid',fact.facets[0])
        self.assertIn(fact.facets[0]['reason_uid'],n.mem.nodes)
    def test_one_ray_activates_additional_supports(self):
        n=self.make();n.answer('Meu nome é Luan.')
        fact=next(x for x in n.mem.nodes.values() if x.kind=='dialogue_fact')
        n.mem.pulse_units([fact.ports[0]])
        self.assertEqual(fact.active,1)
        self.assertEqual(fact.support,1)
        n.mem.pulse_units([fact.ports[0],fact.ports[1]])
        self.assertEqual(fact.active,1)
        self.assertEqual(fact.support,2)
    def test_dynamic_memory_capacity(self):
        n=self.make();n.mem.cfg.max_nodes=len(n.mem.nodes)+20
        for i in range(12):n.answer(f'Meu nome é Nenio{i}.')
        self.assertGreater(n.mem.cfg.max_nodes,len(n.mem.nodes))
        self.assertEqual(n.answer('Qual é meu nome?')['answer'],'Nenio11')
    def test_failed_inference_does_not_claim_rule(self):
        n=self.make();n.answer('Se o sensor apita, então o motor aquece.')
        n.answer('Considere que o motor aquece.')
        r=n.answer('Isso permite concluir que o sensor apita?')
        self.assertEqual(r['reason'],'unknown')
    def test_different_sessions_do_not_share_facts(self):
        n=self.make();n.answer('Meu nome é César.')
        b=ContinuousNexo(n.base,'outro')
        self.assertEqual(b.answer('Qual é meu nome?')['reason'],'self_identified_missing_fact')
        self.assertEqual(b.answer('Isso permite concluir que meu nome é César?')['reason'],'unknown')
        a=ContinuousNexo(b.base,'principal')
        self.assertEqual(a.answer('Qual é meu nome?')['answer'],'César')
    def test_no_rule_without_multiple_experiences(self):
        n=self.make();count=len(n._schemas)
        n.answer('Minha fantasia é Aurora.')
        n.answer('Qual é minha fantasia?')
        n.answer('Aurora')
        self.assertEqual(count,len(n._schemas))
    def test_logic_proof_depends_on_live_fact(self):
        n=self.make()
        n.answer('Se meu nome é Luan, então a lembrança está correta.')
        n.answer('Meu nome é Luan.')
        self.assertEqual(n.answer('O que se conclui?')['reason'],'learned_inference')
        n.answer('Meu nome é Isaac.')
        self.assertNotEqual(n.answer('Isso permite concluir que a lembrança está correta?')['reason'],'yes')

if __name__=='__main__':unittest.main()

class TestParaphraseLearning(unittest.TestCase):
    def test_novel_question_paraphrase_is_learned_from_dialogue(self):
        n=ContinuousNexo.load(TRAIN)
        for person,place in [('Mara','Recife'),('Joana','Natal'),('Inês','Olinda')]:
            n.answer(f'{person} mora em {place}.')
            n.answer(f'Em qual cidade {person} reside?')
            n.answer(place)
        self.assertGreaterEqual(len(n._aliases),1)
        n.answer('Lia mora em Maceió.')
        r=n.answer('Em qual cidade Lia reside?')
        self.assertEqual(r['answer'],'Maceió')
        self.assertEqual(r['reason'],'recalled_from_live_memory')
    def test_single_paraphrase_demonstration_not_sufficient(self):
        n=ContinuousNexo.load(TRAIN)
        n.answer('Mara mora em Recife.')
        n.answer('Em qual cidade Mara reside?')
        n.answer('Recife')
        self.assertEqual(len(n._aliases),0)
        n.answer('Lia mora em Maceió.')
        self.assertEqual(n.answer('Em qual cidade Lia reside?')['reason'],'self_identified_unparsed_question')
    def test_learned_alias_survives_restart(self):
        n=ContinuousNexo.load(TRAIN)
        for person,place in [('Mara','Recife'),('Joana','Natal'),('Inês','Olinda')]:
            n.answer(f'{person} mora em {place}.')
            n.answer(f'Em qual cidade {person} reside?')
            n.answer(place)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'state.json';n.save(p)
            q=ContinuousNexo.load(p)
            q.answer('Lia mora em Maceió.')
            self.assertEqual(q.answer('Em qual cidade Lia reside?')['answer'],'Maceió')
    def test_ambiguous_evidence_does_not_create_alias(self):
        n=ContinuousNexo.load(TRAIN)
        n.answer('Lia mora em Recife.')
        n.answer('O livro verde fica em Recife.')
        n.answer('Em que município Lia reside?')
        n.answer('Recife')
        self.assertFalse(n._aliases)

class TestPendingVsObservation(unittest.TestCase):
    def test_unknown_statement_does_not_answer_unrelated_goal(self):
        n=ContinuousNexo.load(TRAIN)
        n.answer('Quem inventou o quasar de jade?')
        before=n.introspect()
        r=n.answer('Minha teoria nova afirma que corpos se relacionam.')
        self.assertEqual(r['reason'],'unparsed_observation')
        after=n.introspect()
        self.assertEqual(len(after['unresolved_questions']),len(before['unresolved_questions']))
        self.assertGreater(after['self_question_morphons'],before['self_question_morphons'])

class TestPartialObservation(unittest.TestCase):
    def test_elliptic_statement_after_question(self):
        n=ContinuousNexo.load(TRAIN)
        n.answer('Onde eu moro?')
        r=n.answer('Moro em Recife.')
        self.assertEqual(r['reason'],'learned_from_partial_observation')
        self.assertEqual(n.answer('Onde eu moro?')['answer'],'Recife')
    def test_same_operation_on_different_unseen_verb(self):
        n=ContinuousNexo.load(TRAIN)
        n.answer('Onde eu estudo?')
        r=n.answer('Estudo em Olinda.')
        self.assertEqual(r['reason'],'learned_from_partial_observation')
        self.assertEqual(n.answer('Onde eu estudo?')['answer'],'Olinda')

class TestExactReproducibility(unittest.TestCase):
    def test_uninterrupted_vs_resumed_identical_memory(self):
        sequence=['Meu nome é Iara.','Eu moro em Jaboatão.','Qual é meu nome?',
                  'Onde eu moro?','Se meu nome é Iara, então a informação está disponível.',
                  'O que se conclui?','Qual é minha hipótese?',
                  'que a memória seja contínua','Qual é minha hipótese?',
                  'Meu nome é Talita.','Qual é meu nome?','Por quê?']
        a=ContinuousNexo.load(TRAIN)
        b=ContinuousNexo.load(TRAIN)
        for item in sequence:a.answer(item)
        for item in sequence[:6]:b.answer(item)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'checkpoint.json';b.save(path)
            b=ContinuousNexo.load(path)
            for item in sequence[6:]:b.answer(item)
            self.assertEqual(json.dumps(a.mem.snapshot(),sort_keys=True),
                             json.dumps(b.mem.snapshot(),sort_keys=True))
