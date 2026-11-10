from __future__ import annotations
import json, os, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from continuous import ContinuousNexo, answer_mask, induce
from nexo20 import NexoDialogue

TRAIN=ROOT/'training'/'trained21.json'
BASE=ROOT/'training'/'base20_trained.json'

class TestContinuousNexo(unittest.TestCase):
    def agent(self, session='principal'):return ContinuousNexo.from_state(TRAIN,session)
    def test_predecessor_cannot_understand_name(self):
        old=NexoDialogue.load(BASE)
        self.assertEqual(old.answer('Meu nome é Zefira.')['reason'],'no_learned_interpretation')
    def test_learn_name_in_first_dialogue(self):
        n=self.agent();n.answer('Meu nome é Luan.')
        self.assertEqual(n.answer('Qual é meu nome?')['answer'],'Luan')
    def test_ask_then_learn_bare_answer(self):
        n=self.agent();r=n.answer('Qual é meu nome?')
        self.assertEqual(r['reason'],'self_identified_missing_fact')
        self.assertGreater(n.introspect()['self_question_morphons'],0)
        n.answer('Luan')
        self.assertEqual(n.answer('Qual é meu nome?')['answer'],'Luan')
        self.assertEqual(n.introspect()['unresolved_questions'],[])
    def test_pending_does_not_swallow_known_statement(self):
        n=self.agent();n.answer('Qual é meu nome?')
        n.answer('Meu nome é Marcio.')
        self.assertEqual(n.answer('Qual é meu nome?')['answer'],'Marcio')
    def test_revision_not_old_current(self):
        n=self.agent();n.answer('Meu nome é Luan.')
        n.answer('Meu nome é Lucas.')
        self.assertEqual(n.answer('Qual é meu nome?')['answer'],'Lucas')
        self.assertEqual(n.answer('Isso permite concluir que meu nome é Lucas?')['reason'],'yes')
        self.assertEqual(n.answer('Isso permite concluir que meu nome é Luan?')['reason'],'unknown')
        self.assertEqual(sum(x.kind=='dialogue_fact' for x in n.mem.nodes.values()),2)
    def test_multiword_new_value_and_key(self):
        n=self.agent();n.answer('Rosa Maria mora em Belo Horizonte.')
        self.assertEqual(n.answer('Onde Rosa Maria mora?')['answer'],'Belo Horizonte')
    def test_shared_verb_induction(self):
        n=self.agent();n.answer('Eu resido em Belém.')
        self.assertEqual(n.answer('Onde eu resido?')['answer'],'Belém')
    def test_frozen_memory_has_no_evaluation_answers(self):
        n=self.agent();r=n.answer('Qual é meu nome?')
        self.assertEqual(r['reason'],'self_identified_missing_fact')
    def test_session_isolation(self):
        n=self.agent('sessao1');n.answer('Meu nome é Geovana.')
        n2=ContinuousNexo(n.base,'sessao2')
        self.assertEqual(n2.answer('Qual é meu nome?')['reason'],'self_identified_missing_fact')
        n1=ContinuousNexo(n2.base,'sessao1')
        self.assertEqual(n1.answer('Qual é meu nome?')['answer'],'Geovana')
    def test_persist_and_resume(self):
        n=self.agent();n.answer('Meu nome é Cecilia.')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'memoria.json';n.save(p)
            n2=ContinuousNexo.load(p)
            self.assertEqual(n2.answer('Qual é meu nome?')['answer'],'Cecilia')
            n2.answer('Meu nome é Renata.')
            n2.save(p)
            n3=ContinuousNexo.load(p)
            self.assertEqual(n3.answer('Qual é meu nome?')['answer'],'Renata')
    def test_unparsed_question_episodic_memory(self):
        n=self.agent()
        n.answer('O dodecaedro chama-se Dreno.')
        self.assertEqual(n.answer('Quem é Dreno?')['reason'],'self_identified_unparsed_question')
        n.answer('um sólido')
        r=n.answer('Quem é Dreno?')
        self.assertEqual(r['answer'],'um sólido')
        self.assertEqual(r['reason'],'recalled_specific_episode')
    def test_3_live_examples_create_new_schema(self):
        n=self.agent();base=len(n._schemas)
        for val in ['Coral','Lótus','Fóssil']:
            n.answer(f'Minha música favorita é {val}.')
            n.answer('Qual é minha música favorita?')
            n.answer(val)
        self.assertGreater(len(n._schemas),base)
        n.answer('Minha música favorita é Ametista.')
        self.assertEqual(n.answer('Qual é minha música favorita?')['answer'],'Ametista')
    def test_only_one_example_no_overgeneralization(self):
        n=self.agent()
        n.answer('Meu ritual se chama Estalo.')
        n.answer('Qual o nome do meu ritual?')
        n.answer('Estalo')
        self.assertEqual(n.answer('Meu ritual se chama Trovão.')['reason'],'unparsed_observation')
    def test_live_fact_proves_logical_premise(self):
        n=self.agent();n.answer('Meu nome é Davi.')
        n.answer('Se meu nome é Davi, então minha identificação é conhecida.')
        r=n.answer('O que se conclui?')
        self.assertIn('minha identificação é conhecida',r['answer'])
        self.assertEqual(r['reason'],'learned_inference')
    def test_philosophical_proof_persists_restart(self):
        n=self.agent();n.answer('Se o farol acende, então a entrada é visível.')
        n.answer('Considere que o farol acende.')
        self.assertEqual(n.answer('O que se conclui?')['reason'],'learned_inference')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'mem.json';n.save(p)
            m=ContinuousNexo.load(p)
            self.assertEqual(m.answer('Por quê?')['reason'],'learned_proof_trace')
    def test_reasoning_binary_retained(self):
        n=self.agent();r=n.answer('Quanto é 17 mais 26?')
        self.assertIn('43',str(r['answer']))
    def test_self_question_is_real_morphon(self):
        n=self.agent();r=n.answer('Qual é meu nome?');g=n.mem.nodes[r['goal_uid']]
        q=[x for x in n.mem.nodes.values() if x.kind=='dialogue_self_question']
        self.assertTrue(q)
        self.assertIn(g.uid,q[-1].ports)
        self.assertGreaterEqual(q[-1].support,1)
    def test_negative_ambiguity_safe(self):
        self.assertIsNone(answer_mask('O brilho do metal é azul','azul e vermelho'))
        self.assertIsNone(induce([{'statement':'Zé corre','question':'Quem corre?','answer':'João'}]*3))

if __name__=='__main__':unittest.main()
