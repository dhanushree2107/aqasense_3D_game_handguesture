"""
Comprehensive test suite for the Underwater Museum, exhibit discovery,
curator controls, persistence, and interactive inspection modals.
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import tempfile
import pygame
import pytest

from game.inventory import UnderwaterMuseum, MuseumExhibit
from game.treasure import Treasure, TreasureType
from ui.screens import MuseumScreen
from game.game_manager import GameManager, GameState
from hand_tracking.gesture_detector import GestureType


def test_museum_initial_state():
    """Museum begins with 8 historical exhibits and Pearl unlocked."""
    museum = UnderwaterMuseum(auto_load=False)
    assert museum.get_total_count() == 8
    assert museum.get_unlocked_count() == 1
    assert museum.exhibits["pearl"].is_unlocked is True
    assert museum.exhibits["gold_coin"].is_unlocked is False
    assert museum.exhibits["sapphire_chalice"].is_unlocked is False


def test_museum_campaign_zone_deposits():
    """Zone-specific treasure deposits unlock the corresponding museum wonders."""
    museum = UnderwaterMuseum(auto_load=False)

    # Level 3: Minoan Octopod Amphora
    rare_t = Treasure(100, 100, TreasureType.RARE)
    ex3 = museum.register_treasure_deposit(rare_t, level_id=3)
    assert ex3 is not None
    assert ex3.exhibit_id == "ancient_vase"
    assert museum.exhibits["ancient_vase"].is_unlocked is True

    # Level 4: Nautilus Treasure Compass
    common_t = Treasure(100, 100, TreasureType.COMMON)
    ex4 = museum.register_treasure_deposit(common_t, level_id=4)
    assert ex4 is not None
    assert ex4.exhibit_id == "coral_compass"
    assert museum.exhibits["coral_compass"].is_unlocked is True

    # Level 5: Talisman of the Ancient Guardian
    ancient_t = Treasure(100, 100, TreasureType.ANCIENT)
    ex5 = museum.register_treasure_deposit(ancient_t, level_id=5)
    assert ex5 is not None
    assert ex5.exhibit_id == "guardian_seal"
    assert museum.exhibits["guardian_seal"].is_unlocked is True

    # Heavy Chest
    heavy_t = Treasure(100, 100, TreasureType.HEAVY)
    ex_h = museum.register_treasure_deposit(heavy_t, level_id=1)
    assert ex_h is not None
    assert ex_h.exhibit_id == "heavy_chest"
    assert museum.exhibits["heavy_chest"].is_unlocked is True


def test_museum_curator_mode_toggle():
    """Curator mode unlocks all 8 relics and can reset back to 1."""
    museum = UnderwaterMuseum(auto_load=False)
    assert museum.get_unlocked_count() == 1

    museum.unlock_all()
    assert museum.get_unlocked_count() == 8
    for ex in museum.exhibits.values():
        assert ex.is_unlocked is True

    museum.reset_all()
    assert museum.get_unlocked_count() == 1
    assert museum.exhibits["pearl"].is_unlocked is True
    assert museum.exhibits["gold_coin"].is_unlocked is False


def test_museum_disk_persistence():
    """Ensures save_to_disk and load_from_disk cleanly persist unlocked progress."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        temp_path = tf.name

    try:
        museum = UnderwaterMuseum(auto_load=False, save_on_unlock=True)
        museum.unlock_exhibit("gold_coin", 2)
        museum.unlock_exhibit("coral_compass", 4)
        museum.save_to_disk(filepath=temp_path, force=True)

        # Load into fresh instance
        loaded_museum = UnderwaterMuseum(auto_load=False)
        loaded_museum.load_from_disk(filepath=temp_path)
        assert loaded_museum.exhibits["pearl"].is_unlocked is True
        assert loaded_museum.exhibits["gold_coin"].is_unlocked is True
        assert loaded_museum.exhibits["coral_compass"].is_unlocked is True
        assert loaded_museum.exhibits["ancient_crown"].is_unlocked is False
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_museum_screen_card_interaction_and_dwell():
    """Tests card hovering, dwell-to-inspect, click-to-inspect, and modal dismissal."""
    pygame.init()
    surface = pygame.Surface((1280, 720))
    museum = UnderwaterMuseum(auto_load=False)

    back_called = False
    def on_back():
        nonlocal back_called
        back_called = True

    screen = MuseumScreen(on_back=on_back)
    # Render once to lay out card rects
    screen.draw(surface, museum)
    assert len(screen.card_rects) == 8

    # Card rect for pearl
    pearl_rect = screen.card_rects["pearl"]
    cx, cy = pearl_rect.center

    # 1. Hover without click
    screen.update(cursor_x=cx, cursor_y=cy, is_clicked=False, dt=0.016)
    assert screen.hovered_card_id == "pearl"
    assert screen.inspected_exhibit is None

    # 2. Dwell-to-inspect (accumulate past 0.65s threshold)
    for _ in range(50):
        screen.update(cursor_x=cx, cursor_y=cy, is_clicked=False, dt=0.016)

    assert screen.inspected_exhibit is not None
    assert screen.inspected_exhibit.exhibit_id == "pearl"

    # 3. Close modal via close_inspection
    assert screen.close_inspection() is True
    assert screen.inspected_exhibit is None
    assert screen.close_inspection() is False

    # 4. Instant click with pinch
    screen.update(cursor_x=cx, cursor_y=cy, is_clicked=True, dt=0.016)
    assert screen.inspected_exhibit is not None
    assert screen.inspected_exhibit.exhibit_id == "pearl"

    # Close modal
    screen.close_inspection()

    # 5. Return label update
    screen.set_return_label("RETURN TO EXPEDITION")
    assert "RETURN" in screen.back_btn.text


def test_game_manager_museum_navigation_and_esc():
    """Verifies GameManager transitions into museum, returns correctly, and handles ESC."""
    gm = GameManager()
    assert gm.current_state == GameState.MAIN_MENU

    # Enter museum from main menu
    gm._enter_museum(GameState.MAIN_MENU)
    assert gm.current_state == GameState.MUSEUM
    assert gm.previous_state == GameState.MAIN_MENU

    # Open inspection modal
    gm.museum_screen.inspected_exhibit = gm.museum.exhibits["pearl"]
    assert gm.museum_screen.inspected_exhibit is not None

    # ESC should close modal first
    gm._exit_museum()
    assert gm.museum_screen.inspected_exhibit is None
    assert gm.current_state == GameState.MUSEUM

    # Next ESC should return to MAIN_MENU
    gm._exit_museum()
    assert gm.current_state == GameState.MAIN_MENU

    # Enter museum from LEVEL_COMPLETE
    gm._enter_museum(GameState.LEVEL_COMPLETE)
    assert gm.current_state == GameState.MUSEUM
    assert "RETURN" in gm.museum_screen.back_btn.text

    # Back button returns to LEVEL_COMPLETE
    gm._exit_museum()
    assert gm.current_state == GameState.LEVEL_COMPLETE

    gm.hand_detector.stop()


def test_museum_gesture_navigation_and_controls():
    """Validates Two-Fingers chamber cycling, Palm modal dismissal, Palm return, and Fist curator mode."""
    back_count = 0
    def on_back():
        nonlocal back_count
        back_count += 1

    screen = MuseumScreen(on_back=on_back)
    museum = UnderwaterMuseum(auto_load=False)
    screen.museum = museum

    assert screen.active_chamber == "gallery"

    # 1. TWO_FINGERS cycles to the next chamber (gallery -> archive)
    screen.update(cursor_x=640, cursor_y=360, is_clicked=False, dt=0.016, current_gesture=GestureType.TWO_FINGERS)
    assert screen.active_chamber == "archive"

    # Next frame with cooldown active doesn't double-cycle
    screen.update(cursor_x=640, cursor_y=360, is_clicked=False, dt=0.016, current_gesture=GestureType.TWO_FINGERS)
    assert screen.active_chamber == "archive"

    # Advance cooldown
    screen.gesture_action_cooldown = 0.0

    # Next cycle (archive -> legendary)
    screen.update(cursor_x=640, cursor_y=360, is_clicked=False, dt=0.016, current_gesture=GestureType.TWO_FINGERS)
    assert screen.active_chamber == "legendary"

    # 2. Inspecting relic and using TWO_FINGERS cycles inspected exhibit
    screen.inspected_exhibit = museum.exhibits["pearl"]
    screen.gesture_action_cooldown = 0.0
    screen.update(cursor_x=640, cursor_y=360, is_clicked=False, dt=0.016, current_gesture=GestureType.TWO_FINGERS)
    assert screen.inspected_exhibit.exhibit_id == "gold_coin"

    # 3. OPEN_PALM closes inspection modal
    screen.gesture_action_cooldown = 0.0
    screen.update(cursor_x=640, cursor_y=360, is_clicked=False, dt=0.016, current_gesture=GestureType.OPEN_PALM)
    assert screen.inspected_exhibit is None

    # 4. FIST toggles curator mode
    screen.gesture_action_cooldown = 0.0
    assert museum.get_unlocked_count() == 1
    screen.update(cursor_x=640, cursor_y=360, is_clicked=False, dt=0.016, current_gesture=GestureType.FIST)
    assert museum.get_unlocked_count() == 8

    # 5. Holding OPEN_PALM triggers on_back
    screen.gesture_action_cooldown = 0.0
    assert back_count == 0
    # Hold palm past 0.65s threshold
    for _ in range(45):
        screen.update(cursor_x=640, cursor_y=360, is_clicked=False, dt=0.016, current_gesture=GestureType.OPEN_PALM)
    assert back_count == 1


def test_museum_no_stick_rendered():
    """Ensures no stick pointer is rendered and _draw_first_person_hand is a clean no-op."""
    screen = MuseumScreen(on_back=lambda: None)
    surf1 = pygame.Surface((1280, 720))
    surf2 = surf1.copy()

    # Calling _draw_first_person_hand produces no changes to pixel buffer
    screen._draw_first_person_hand(surf1, 640, 360, is_clicked=False)
    assert pygame.image.tostring(surf1, "RGB") == pygame.image.tostring(surf2, "RGB")

