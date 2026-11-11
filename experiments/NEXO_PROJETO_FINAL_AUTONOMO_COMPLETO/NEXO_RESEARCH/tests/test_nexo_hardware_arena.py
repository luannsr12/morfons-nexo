import os, sys, ctypes
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from nexo_autonomous_engine import MorphonNode, PortEdge, SurfaceFaceMark, AutonomousMorphMemory

def test_binary_arena_integrity():
    assert ctypes.sizeof(MorphonNode) == 64
    assert ctypes.sizeof(PortEdge) == 32
    assert ctypes.sizeof(SurfaceFaceMark) == 32
    mem = AutonomousMorphMemory(max_nodes=256, max_edges=512, max_marks=512)
    assert mem.node_count == 8
    mem.close()
    return True

if __name__ == "__main__":
    assert test_binary_arena_integrity()
    print("INTEGRIDADE BINÁRIA (64B / 32B / 32B) E 8 GÊNESIS VERIFICADA COM SUCESSO.")
