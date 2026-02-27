from typing import Dict, Any, List, Literal, Optional
import logging
ENGINE_VERSION = "v1.0"

LIFECYCLE_STAGE_BASE = {
    "A": ["heat_combo", "whelping_kit", "extra_pads"],
    "B": ["wifi_monitoring", "heat_combo", "extra_pads"],
    "C": ["traction_pad", "add_on_room", "extra_pads"],
    "D": ["add_on_room_next", "feeding_station", "mess_hall", "extra_pads"],
}

WINDOW_ELIGIBLE_STAGES = {"A", "B"}

PRODUCT_CATALOG = {
    "heat_combo": {"name": "Heat Combo", "url": "https://www.ezwhelp.com/products/heating-combo-for-classic-value-box-size-3838-or-4848?_pos=1&_psq=Heat+Combo&_ss=e&_v=1.0"},
    "whelping_kit": {"name": "Whelping Kit", "url": "https://www.ezwhelp.com/products/whelping-kit?_pos=2&_psq=Whelping+Kit&_ss=e&_v=1.0"},
    "corner_seat": {"name": "Corner Seat", "url": "https://www.ezwhelp.com/products/fab-box-corner-seat?_pos=1&_sid=eec2f2382&_ss=r"},
    "acrylic_door": {"name": "Acrylic Door", "url": "https://www.ezwhelp.com/products/acrylic-glass-door-set-for-ezclassic-whelping-boxes?_pos=1&_psq=Acrylic+Door&_ss=e&_v=1.0"},
    "heat_pad": {"name": "Heat Pad", "url": "https://www.ezwhelp.com/products/heat-pad-for-whelping-boxes?_pos=1&_psq=Heat+Pad&_ss=e&_v=1.0"},
    "traction_pad": {"name": "Traction Pad", "url": "https://www.ezwhelp.com/products/ezwhelp-traction-pad?_pos=1&_psq=Traction+Pad&_ss=e&_v=1.0"},
    "extra_pads": {"name": "Extra Pads", "url": "https://www.ezwhelp.com/products/black-white-slip-resistant-paw-print-pad-mat-2-pack"},
    "wifi_monitoring": {"name": "WiFi Monitoring System", "url": "https://www.ezwhelp.com/products/ezwhelp-smart-whelping-box-wifi-camera-temperature-monitoring-system"},
    "add_on_room": {"name": "EZclassic Add-On Room", "url": "https://www.ezwhelp.com/products/ezclassic-add-on-room"},
    "add_on_room_next": {"name": "EZclassic Add-On Room (Expansion)", "url": "https://www.ezwhelp.com/products/ezclassic-add-on-room"},
    "feeding_station": {"name": "Feeding Station", "url": "https://www.ezwhelp.com/products/feeding-station"},
    "mess_hall": {"name": "EZclassic Mess Hall", "url": "https://www.ezwhelp.com/products/ezclassic-mess-hall-add-on-room-set-standard-18-height"},
}

BUNDLE_URLS = {
    "starter": "https://www.ezwhelp.com/products/bundles-ezclassic-starter-set?_pos=1&_psq=Starter&_ss=e&_v=1.0",
    "essential": "https://www.ezwhelp.com/products/bundles-ezclassic-basic-set?_pos=1&_psq=Essential&_ss=e&_v=1.0",
    "pro": "https://www.ezwhelp.com/products/copy-of-bundles-ezclassic-pro-set?_pos=1&_psq=Pro&_ss=e&_v=1.0",
    "elite": "https://www.ezwhelp.com/products/bundles-ezclassic-elite-set?_pos=1&_psq=Elite&_ss=e&_v=1.0",
    "playyard": "https://www.ezwhelp.com/products/bundles-ezclassic-play-yard-set?_pos=1&_psq=Play+Yard&_ss=e&_v=1.0",
    "condo": "https://www.ezwhelp.com/products/ezclassic-condo-bundle?_pos=1&_psq=Condo&_ss=e&_v=1.0&variant=51849455403380",
}

RULE_MATRIX = [
    {"conditions": {"space": "C", "bundle_option": "A"}, "bundle": "condo"},
    {"conditions": {"space": "C", "bundle_option": "B"}, "bundle": "playyard"},
    {"conditions": {"space": "B", "bundle_option": "A"}, "bundle": "elite"},
    {"conditions": {"space": "B", "bundle_option": "B"}, "bundle": "pro"},
    {"conditions": {"space": "A", "bundle_option": "B"}, "bundle": "essential"},
    {"conditions": {"space": "A", "bundle_option": "A"}, "bundle": "starter"},
]

SIZE_MAP = {"A": 28, "B": 38, "C": 48}

TIMELINE_MESSAGES = {
    "A": "Get fully prepared before labor begins.",
    "B": "Puppies arriving soon — prioritize readiness.",
    "C": "Monitor newborns closely during first days.",
    "D": "Support growing puppies safely.",
}

logger = logging.getLogger(__name__)


def structural_engine(data: Dict[str, Any]) -> Dict[str, Any]:
    for rule in RULE_MATRIX:
        if all(data.get(k) == v for k, v in rule["conditions"].items()):
            bundle = rule["bundle"]
            break
    else:
        bundle = "starter"

    box_size = SIZE_MAP.get(data.get("dam_size"))

    if box_size == 28:
        panel_height = '18"'
    else:
        panel_height = '28"' if data.get("panel_height") == "B" else '18"'

    return {
        "bucket": bundle,
        "bundle_url": BUNDLE_URLS[bundle],
        "box_size_inches": box_size,
        "panel_height": panel_height,
        "timeline_message": TIMELINE_MESSAGES.get(data.get("timeline")),
        "recommended_products": []
    }


def existing_owner_engine(data: Dict[str, Any]) -> Dict[str, Any]:
    stage = data.get("stage")
    has_window = data.get("has_window", "unknown")
    box_height = data.get("box_height", "unknown")

    if stage not in LIFECYCLE_STAGE_BASE:
        return {
            "bucket": "existing_owner",
            "engine_version": "v1.0-lifecycle",
            "bundle_url": None,
            "recommended_products": [],
            "additional_products": [],
            "timeline_message": "Invalid stage",
            "height_message": "Unknown configuration."
        }

    product_keys = LIFECYCLE_STAGE_BASE[stage].copy()

    if stage in WINDOW_ELIGIBLE_STAGES and has_window in ["no", "unknown"]:
        product_keys.append("acrylic_door")

    products = [PRODUCT_CATALOG[k] for k in product_keys if k in PRODUCT_CATALOG]

    primary_products = products[:3]
    additional_products = products[3:]

    if box_height == "18":
        height_message = "Standard containment configuration."
    elif box_height == "28":
        height_message = "Tall configuration reduces containment urgency."
    else:
        height_message = "Height-neutral configuration."

    return {
        "bucket": "existing_owner",
        "engine_version": "v1.0-lifecycle",
        "bundle_url": None,
        "recommended_products": primary_products,
        "additional_products": additional_products,
        "timeline_message": TIMELINE_MESSAGES.get(stage),
        "height_message": height_message,
    }


def master_engine(data: Dict[str, Any]) -> Dict[str, Any]:
    if data.get("path") == "existing":
        return existing_owner_engine(data)
    return structural_engine(data)