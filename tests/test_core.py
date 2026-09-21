from mastery import update_mastery, label


def test_mastery_stays_in_bounds():
    assert 0 <= update_mastery(0.5, True) <= 1
    assert 0 <= update_mastery(0.5, False) <= 1


def test_mastery_labels():
    assert label(0.9) == "Strong"
    assert label(0.6) == "Developing"
    assert label(0.2) == "Needs Practice"
