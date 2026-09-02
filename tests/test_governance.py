from src.governance import driver_tree, intervention

def test_driver_tree_is_structured():
    tree = driver_tree("Public Transport")
    assert "root" in tree
    assert len(tree["branches"]) >= 3

def test_intervention_has_validation():
    action = intervention("Public Transport")
    assert action["validation_data"]
    assert action["success_metric"]
