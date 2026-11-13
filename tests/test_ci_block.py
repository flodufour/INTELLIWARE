"""Temporary: check that a failing test blocks merging. Do not merge."""


def test_ci_blocks_merge():
    assert False, "intentional failure"
