"""Adversarial control: duplicating a Morphon can increase rays without information."""
import json
from pathlib import Path
from morfon import MorphMemory,Morphon,Config

def run():
    m=MorphMemory(Config(max_order=4,propagation='completed'),seed=41)
    base,_=m.propose(((0,1),(1,1)))
    clone_id=m.next_uid;m.next_uid+=1
    copy=Morphon(clone_id,'replica',base.literals,base.ports,set(),base.xyz[:],base.facets[:],base.holes.copy())
    m.nodes[clone_id]=copy
    for p in copy.ports:
        m.nodes[p].children.add(clone_id);m.cache[p].add(clone_id)
    host_id=m.next_uid;m.next_uid+=1
    host=Morphon(host_id,'nested',base.literals,(base.uid,clone_id),set(),base.xyz[:],[],{base.uid:1,clone_id:1})
    m.nodes[host_id]=host
    for p in host.ports:
        m.nodes[p].children.add(host_id);m.cache[p].add(host_id)
    m.pulse(((0,1),(1,1)))
    actual=host.support
    # The physical input paths carry two rays but one repeated conjunction.
    sources={tuple(base.literals),tuple(copy.literals)}
    assert host.active==1 and host.completed and actual==2 and len(sources)==1
    return {'replicated_morphons':2,'host_physical_rays':actual,
            'unique_experiential_patterns':len(sources),'extra_independent_information':0,
            'conclusion':'Duplication raises ray weight without new evidence; replica must carry lineage to be treated appropriately.'}
if __name__=='__main__':
    r=run();(Path(__file__).resolve().parent.parent/'dados'/'controle_replicacao.json').write_text(json.dumps(r,indent=2));print(r)
