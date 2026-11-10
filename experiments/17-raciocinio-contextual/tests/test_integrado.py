import sys,unittest, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from grounded import ContextLearner,MorphGraph,tok
from laboratorio import worlds,train

class IntegratedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.learner=ContextLearner()
        train(cls.learner,world_count=3)
    def world(self):
        ep=worlds(936,test=True);g=MorphGraph()
        for text,*_ in ep['facts']:self.assertEqual(self.learner.ingest(text,g)['kind'],'observed')
        return ep,g
    def test_all_observed_questions(self):
        ep,g=self.world()
        for q,src,value,response,typ in ep['questions']:
            with self.subTest(typ=typ,q=q):self.assertEqual(tok(self.learner.ask(q,g)['answer']),tok(response))
    def test_compositions_never_taught(self):
        ep,g=self.world()
        for q,src,value,response,typ in ep['composed']:
            r=self.learner.ask(q,g,True)
            self.assertEqual(tok(r['answer']),tok(response))
            self.assertEqual(r['hops'],2 if typ=='composicao_nunca_treinada' else 3)
            self.assertEqual(len(r['reference_trace']),1 if r['hops']==2 else 2)
    def test_one_ray_activates(self):
        ep,g=self.world();q=ep['questions'][0][1]
        entity_key=(__import__('grounded').tid('entity',__import__('grounded').norm(q)),1)
        g.mem.pulse([entity_key])
        facts=[g.mem.nodes[u] for u in g.mem.last_pulsed if g.mem.nodes[u].kind=='world_fact']
        self.assertTrue(facts);self.assertTrue(all(n.active==1 and n.support==1 for n in facts))
    def test_reinforced_ray_count(self):
        ep,g=self.world();q=ep['questions'][0][0]
        r=self.learner.ask(q,g)
        self.assertTrue(r['rays']>=3)
    def test_memory_change(self):
        ep,g=self.world();old=ep['facts'][0][1]
        self.learner.ingest(f'Hoje {old} mora em LugarNovo',g)
        a=self.learner.ask(f'Onde mora {old}',g)
        self.assertEqual(tok(a['answer']),tok(f'{old} mora em LugarNovo'))
    def test_past_retained_when_now_changed(self):
        ep,g=self.world();old=ep['facts'][0][1]
        before=self.learner.ask(f'Onde morava {old}',g)['answer']
        self.learner.ingest(f'Hoje {old} mora em LugarNovo',g)
        self.assertEqual(self.learner.ask(f'Onde morava {old}',g)['answer'],before)
    def test_context_focus(self):
        ep,g=self.world();source=next(x[1] for x in ep['questions'] if x[-1]=='agora')
        self.learner.ask(f'Onde mora {source}',g)
        self.assertEqual(g.current_focus(),__import__('grounded').norm(source))
        answer=self.learner.ask('E antes',g)['answer'];self.assertIsNotNone(answer)
        self.assertEqual(tok(answer),tok(self.learner.ask(f'Onde morava {source}',g)['answer']))
    def test_unknown_lexical_format_abstains(self):
        ep,g=self.world();self.assertIsNone(self.learner.ask('Você poderia me falar de meteorologia',g)['answer'])
    def test_unknown_entity_abstains(self):
        ep,g=self.world();self.assertEqual(self.learner.ask('Onde mora Fantasma999',g)['reason'],'missing_relation')
    def test_memory_snapshot_identical(self):
        ep,g=self.world();q=ep['questions'][0][0];a=self.learner.ask(q,g)
        restored=MorphGraph.restore(g.snapshot());b=self.learner.ask(q,restored)
        self.assertEqual(a['answer'],b['answer']);restored.mem.assert_integrity()
    def test_learner_snapshot_identical(self):
        ep,g=self.world()
        with tempfile.TemporaryDirectory() as folder:
            f=Path(folder)/'model.json';self.learner.save(f);n=ContextLearner.load(f)
            for q,*_ in ep['composed']:self.assertEqual(n.ask(q,g)['answer'],self.learner.ask(q,g)['answer'])
    def test_ambiguity_does_not_guess(self):
        ep,g=self.world();who=ep['facts'][0][1]
        # criar duas superficies vigentes contraditorias p/ uma relacao: acesso nao deve escolher uma por acaso
        g.add(who,'zeta','Conflito1','fase1');g.add(who,'zeta','Conflito2','fase1')
        for n in g.mem.nodes.values():
            if n.kind=='world_fact' and n.facets[0]['src']==__import__('grounded').norm(who) and n.facets[0]['dst']=='conflito1':n.facets[0]['current']=True
        self.assertEqual(self.learner.ask(f'Onde mora {who}',g)['reason'],'multiple_consistent_answers')
    def test_no_test_names_memorized(self):
        ep,g=self.world()
        state=repr(self.learner.mem.snapshot()).lower()
        self.assertNotIn('zevira9360',state)
        self.assertNotIn('vinala9360',state)
    def test_without_reference_subphrases(self):
        ep,g=self.world();refs=[n for n in self.learner.mem.nodes.values() if n.kind=='reference_template']
        for n in refs:n.promoted=False
        try:
            q=ep['composed'][0][0]
            self.assertIsNone(self.learner.ask(q,g)['answer'])
        finally:
            for n in refs:n.promoted=True
    def test_multiword_entities_and_followup(self):
        g=MorphGraph()
        for text in ['Antes Maria Jose morava em Rio de Janeiro','Hoje Maria Jose mora em Nova Olinda',
                     'Maria Jose guarda Livro Azul','Livro Azul fica em Rio de Janeiro',
                     'Rio de Janeiro pertence a Estado Leste']:
            self.assertEqual(self.learner.ingest(text,g)['kind'],'observed')
        self.assertEqual(tok(self.learner.ask('Onde mora Maria Jose',g)['answer']),tok('Maria Jose mora em Nova Olinda'))
        self.assertEqual(tok(self.learner.ask('E antes',g)['answer']),tok('Maria Jose morava em Rio de Janeiro'))
        result=self.learner.ask('Em que região fica o lugar onde fica o objeto que Maria Jose guarda',g)
        self.assertEqual(tok(result['answer']),tok('O lugar onde fica o objeto que Maria Jose guarda fica na região Estado Leste'))
        self.assertEqual(result['hops'],3)
    def test_binary_transducer_learned_with_same_morphons(self):
        from laboratorio import train_numeric
        m=ContextLearner();train_numeric(m,300)
        for a,b in [(17,26),(255,255),(65535,987),(2**19+17,2**18+31)]:
            r=m.ask(f'Quanto é {a} mais {b}',MorphGraph())
            self.assertEqual(r['result'],a+b)
            self.assertTrue(all(step['rays']==4 for step in r['steps']))
        self.assertEqual(sum(n.kind=='bit_transition' for n in m.mem.nodes.values()),8)
    def test_bit_machine_cannot_operate_without_traces(self):
        m=ContextLearner()
        m.teach_numeric_phrase('Quanto é 13 mais 26','rotulo',13,26,39,'O resultado é 39')
        self.assertEqual(m.ask('Quanto é 17 mais 26',MorphGraph())['reason'],'unlearned_binary_transition')
    def test_real_geography_scenario(self):
        g=MorphGraph()
        for statement in ['Antes Mara morava em Olinda','Hoje Mara mora em Recife','Mara guarda Caderno',
                          'Caderno fica em Olinda','Recife pertence a Pernambuco','Olinda pertence a Pernambuco']:
            self.assertEqual(self.learner.ingest(statement,g)['kind'],'observed')
        answers={'Onde mora Mara':'Mara mora em Recife','Onde morava Mara':'Mara morava em Olinda',
                 'Onde fica o objeto que Mara guarda':'O objeto que Mara guarda fica em Olinda',
                 'Em que regiao fica o lugar onde fica o objeto que Mara guarda':
                 'O lugar onde fica o objeto que Mara guarda fica na regiao Pernambuco'}
        for q,expected in answers.items():self.assertEqual(tok(self.learner.ask(q,g)['answer']),tok(expected))

if __name__=='__main__':unittest.main()
