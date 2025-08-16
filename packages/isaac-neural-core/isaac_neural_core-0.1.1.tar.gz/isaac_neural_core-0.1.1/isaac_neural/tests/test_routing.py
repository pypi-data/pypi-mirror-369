from isaac_neural.controller.routing import route_for, DEFAULT_CONFIG


def test_route_doc_quick_lane():
    d = route_for("doc", DEFAULT_CONFIG)
    assert d.lane == "quick"
    assert d.model == "oss_fast"


def test_route_refactor_deep_lane():
    d = route_for("refactor", DEFAULT_CONFIG)
    assert d.lane == "deep"
    assert d.model == "llama_strong"
