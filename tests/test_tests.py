from hsm import (
    Node,
    A,
    B,
    C,
    D,
    hsm_get_lca,
    hsm_get_path_to_root,
    Event,
)


def test_tests():
    assert True


def run(node: Node, event: int) -> Node:
    if event not in node.Event:
        print(f"Unhandled event: {event}")
        print(dir(node))
    else:
        return node.run(event)


def test_init() -> None:
    # hsm_init(A, (A, B, C, D))

    print(A.run.__annotations__["event_id"].__args__)

    assert {Event.ONE, Event.TWO} == set(A.run.__annotations__["event_id"].__args__)
    assert {Event.ONE, Event.TWO} == set(A.run_events())

    pathA = hsm_get_path_to_root(A)
    assert pathA == (A,)

    pathB = hsm_get_path_to_root(B)
    assert pathB == (B, A)

    pathC = hsm_get_path_to_root(C)
    assert pathC == (C, A)

    pathD = hsm_get_path_to_root(D)
    assert pathD == (D, C, A)

    lca = hsm_get_lca(pathB, pathC)
    assert lca == A

    lca = hsm_get_lca(pathB, pathD)
    assert lca == A

    lca = hsm_get_lca(pathC, pathD)
    assert lca == C

    lca = hsm_get_lca(pathA, pathD)
    assert lca == A

    lca = hsm_get_lca(pathA, pathB)
    assert lca == A

    lca = hsm_get_lca(pathA, pathC)
    assert lca == A

    lca = hsm_get_lca(pathA, pathA)
    assert lca == A

    lca = hsm_get_lca(pathB, pathB)
    assert lca == B

    lca = hsm_get_lca(pathC, pathC)
    assert lca == C

    lca = hsm_get_lca(pathD, pathD)
    assert lca == D

    mermaid = generate_mermaid(A)
    print(mermaid)


def _test_A() -> None:
    node = B()
    print(dir(node))
    print(node.superstate)

    node.x = 1

    node = A()
    assert isinstance(node, A)

    node = run(node, A.Event.ONE)
    assert isinstance(node, B)

    node = A()
    node = run(node, 3)
    assert isinstance(node, C)

    node = node.run(0)
    assert isinstance(node, B)

    node = node.run(1)
    assert isinstance(node, C)

    node = node.run(1)
    assert isinstance(node, D)


def _test_A() -> None:
    node = A()
    assert isinstance(node, A)

    node = node.run(A.Event.ONE)
    assert isinstance(node, B)

    node = A()
    node = node.run(3)
    assert isinstance(node, C)

    node = node.run(0)
    assert isinstance(node, B)

    node = node.run(1)
    assert isinstance(node, C)

    node = node.run(1)
    assert isinstance(node, D)
