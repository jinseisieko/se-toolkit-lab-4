"""Unit tests for interaction filtering logic."""

from app.models.interaction import InteractionLog
from app.routers.interactions import _filter_by_item_id


def _make_log(id: int, learner_id: int, item_id: int) -> InteractionLog:
    return InteractionLog(id=id, learner_id=learner_id, item_id=item_id, kind="attempt")


def test_filter_returns_all_when_item_id_is_none() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, None)
    assert result == interactions


def test_filter_returns_empty_for_empty_input() -> None:
    result = _filter_by_item_id([], 1)
    assert result == []


def test_filter_returns_interaction_with_matching_ids() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 1
    assert result[0].id == 1


def test_filter_excludes_interaction_with_different_learner_id() -> None:
    """Test that filtering by item_id works correctly even when learner_id differs.

    This is a boundary-value case: interaction has learner_id=2, item_id=1.
    When filtering by item_id=1, this interaction should appear in results.
    The bug incorrectly filters by learner_id instead of item_id.
    """
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 1)]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 2


def test_filter_returns_multiple_interactions_with_same_item_id() -> None:
    """Test filtering returns all interactions matching the item_id."""
    interactions = [
        _make_log(1, 1, 5),
        _make_log(2, 2, 5),
        _make_log(3, 3, 5),
        _make_log(4, 4, 3),
    ]
    result = _filter_by_item_id(interactions, 5)
    assert len(result) == 3
    assert all(r.item_id == 5 for r in result)


def test_filter_returns_empty_when_no_matches() -> None:
    """Test filtering returns empty list when no interactions match item_id."""
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2), _make_log(3, 3, 3)]
    result = _filter_by_item_id(interactions, 999)
    assert result == []


def test_filter_with_zero_item_id() -> None:
    """Test boundary value: filtering with item_id=0."""
    interactions = [
        _make_log(1, 0, 0),
        _make_log(2, 1, 0),
        _make_log(3, 0, 1),
    ]
    result = _filter_by_item_id(interactions, 0)
    assert len(result) == 2
    assert all(r.item_id == 0 for r in result)


def test_filter_preserves_order() -> None:
    """Test that filtering preserves the original order of interactions."""
    interactions = [
        _make_log(1, 1, 1),
        _make_log(2, 2, 2),
        _make_log(3, 3, 1),
        _make_log(4, 4, 1),
    ]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 3
    assert result[0].id == 1
    assert result[1].id == 3
    assert result[2].id == 4
