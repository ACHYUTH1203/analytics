import pytest
from quiz_engine import (
    structural_engine,
    existing_owner_engine,
    master_engine,
    RULE_MATRIX,
    SIZE_MAP,
    TIMELINE_MESSAGES,
)


# =========================================================
# STRUCTURAL ENGINE TESTS
# =========================================================

@pytest.mark.parametrize(
    "space,bundle_option,expected_bucket",
    [
        ("C", "A", "condo"),
        ("C", "B", "playyard"),
        ("B", "A", "elite"),
        ("B", "B", "pro"),
        ("A", "A", "starter"),
        ("A", "B", "essential"),
    ],
)
def test_structural_engine_rule_matrix(space, bundle_option, expected_bucket):
    data = {
        "space": space,
        "bundle_option": bundle_option,
        "dam_size": "B",
        "panel_height": "A",
        "timeline": "A",
    }

    result = structural_engine(data)

    assert result["bucket"] == expected_bucket
    assert result["bundle_url"] is not None
    assert result["recommended_products"] == []


def test_structural_engine_default_fallback():
    data = {
        "space": "UNKNOWN",
        "bundle_option": "UNKNOWN",
        "dam_size": "B",
        "panel_height": "A",
        "timeline": "A",
    }

    result = structural_engine(data)

    assert result["bucket"] == "starter"


@pytest.mark.parametrize(
    "dam_size,expected_inches",
    [
        ("A", 28),
        ("B", 38),
        ("C", 48),
        ("Z", None),
    ],
)
def test_structural_engine_box_size_mapping(dam_size, expected_inches):
    data = {
        "space": "A",
        "bundle_option": "A",
        "dam_size": dam_size,
        "panel_height": "A",
        "timeline": "A",
    }

    result = structural_engine(data)
    assert result["box_size_inches"] == expected_inches


def test_structural_engine_panel_height_logic():
    # dam_size A -> forced 18"
    data = {
        "space": "A",
        "bundle_option": "A",
        "dam_size": "A",
        "panel_height": "B",
        "timeline": "A",
    }
    result = structural_engine(data)
    assert result["panel_height"] == '18"'

    # dam_size B + panel_height B -> 28"
    data["dam_size"] = "B"
    result = structural_engine(data)
    assert result["panel_height"] == '28"'


def test_structural_engine_timeline_message():
    data = {
        "space": "A",
        "bundle_option": "A",
        "dam_size": "B",
        "panel_height": "A",
        "timeline": "C",
    }

    result = structural_engine(data)
    assert result["timeline_message"] == TIMELINE_MESSAGES["C"]


# =========================================================
# EXISTING OWNER ENGINE TESTS
# =========================================================

def test_existing_owner_invalid_stage():
    data = {
        "stage": "Z",
        "has_window": "yes",
        "box_height": "18",
    }

    result = existing_owner_engine(data)

    assert result["timeline_message"] == "Invalid stage"
    assert result["recommended_products"] == []
    assert result["additional_products"] == []


def test_existing_owner_stage_a_with_no_window_adds_door():
    data = {
        "stage": "A",
        "has_window": "no",
        "box_height": "18",
    }

    result = existing_owner_engine(data)

    product_names = [p["name"] for p in result["recommended_products"] + result["additional_products"]]

    assert any("Door" in name for name in product_names)


def test_existing_owner_product_split_logic():
    data = {
        "stage": "D",  # Has many products
        "has_window": "yes",
        "box_height": "18",
    }

    result = existing_owner_engine(data)

    assert len(result["recommended_products"]) <= 3
    assert len(result["additional_products"]) >= 0


@pytest.mark.parametrize(
    "box_height,expected_message",
    [
        ("18", "Standard containment configuration."),
        ("28", "Tall configuration reduces containment urgency."),
        ("unknown", "Height-neutral configuration."),
    ],
)
def test_existing_owner_height_message(box_height, expected_message):
    data = {
        "stage": "A",
        "has_window": "yes",
        "box_height": box_height,
    }

    result = existing_owner_engine(data)

    assert result["height_message"] == expected_message


# =========================================================
# MASTER ENGINE TESTS
# =========================================================

def test_master_engine_routes_existing():
    data = {
        "path": "existing",
        "stage": "A",
        "has_window": "yes",
        "box_height": "18",
    }

    result = master_engine(data)

    assert result["bucket"] == "existing_owner"


def test_master_engine_routes_structural():
    data = {
        "path": "new",
        "space": "A",
        "bundle_option": "A",
        "dam_size": "B",
        "panel_height": "A",
        "timeline": "A",
    }

    result = master_engine(data)

    assert result["bucket"] == "starter"