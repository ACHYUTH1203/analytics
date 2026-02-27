import pytest
from quiz_engine import existing_owner_engine


STAGES = ["A", "B", "C", "D"]
WINDOW_STATES = ["yes", "no", "unknown"]


@pytest.mark.parametrize("stage", STAGES)
@pytest.mark.parametrize("has_window", WINDOW_STATES)
def test_all_stage_window_combinations(stage, has_window):

    payload = {
        "stage": stage,
        "has_window": has_window,
        "box_height": "18",
        "due_date": None,
    }

    result = existing_owner_engine(payload)

    # 1️⃣ Engine version exists
    assert "engine_version" in result

    # 2️⃣ Bucket is correct
    assert result["bucket"] == "existing_owner"

    # 3️⃣ Must always return at least 1 product
    assert len(result["recommended_products"]) >= 1
    # 4️⃣ Acrylic logic validation
    if stage in ["A", "B"]:
        if has_window == "yes":
            product_names = [p["name"] for p in result["recommended_products"]]
            assert "Acrylic Door" not in product_names
        else:
            all_products = result["recommended_products"] + result.get("additional_products", [])
            product_names = [p["name"] for p in all_products]
            assert "Acrylic Door" in product_names

    # 5️⃣ Stage C & D must NOT include acrylic
    if stage in ["C", "D"]:
        all_products = result["recommended_products"] + result.get("additional_products", [])
        product_names = [p["name"] for p in all_products]
        assert "Acrylic Door" not in product_names

    # 6️⃣ Cap rule validation
    assert len(result["recommended_products"]) <= 3