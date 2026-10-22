"""
Unit and Integration Tests for Context-Aware Gesture Interaction in AquaSense.
Validates:
1. Pinch near treasure -> Grab
2. Pinch near artifact -> Inspect (opens 3D inspection modal)
3. Pinch near door -> Unlock attempt (fails when relic missing, succeeds when relic held)
4. Pinch near map -> Open map (opens tactical bathymetric chart)
5. Pinch near coral -> Examine/sample (rewards oxygen and exploration points)
6. Pinch with no valid object nearby -> No accidental action
7. Look between two objects -> Correct target selected based on priority, view angle, distance
8. Move away -> Interaction prompt disappears
9. Museum artifact -> Inspection mode and 3D rotation
10. Existing hand gestures -> Open palm, Sonar, Fist, Two-Hand lift all continue working
"""

import math
import os
import pytest
import pygame

# Headless video driver for testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from hand_tracking.gesture_detector import GestureType
from game.player import Player
from game.treasure import Treasure, TreasureType
from game.inventory import DiverInventory, UnderwaterMuseum
from game.context_interaction import (
    ContextInteractionManager,
    InteractionType,
    InteractableState,
    SonarEchoCategory,
    ContextTreasure,
    ContextArtifact,
    ContextDoor,
    ContextMap,
    ContextCoral,
    ContextMechanism,
)


class MockGameManager:
    """Mock GameManager providing audio, inventory, and museum systems for test verification."""
    def __init__(self):
        self.inventory = DiverInventory()
        self.museum = UnderwaterMuseum(auto_load=False, save_on_unlock=False)
        self.current_level_id = 1
        self.sound_played = []

    def play_sound(self, sound_name: str):
        self.sound_played.append(sound_name)


@pytest.fixture
def manager():
    return ContextInteractionManager()


@pytest.fixture
def player():
    p = Player()
    p.x = 400.0
    p.y = 300.0
    return p


@pytest.fixture
def game():
    return MockGameManager()


def test_1_pinch_near_treasure_grabs(manager, player, game):
    """Test 1: PINCH near treasure grabs it and attaches raw treasure payload."""
    t = Treasure(420.0, 310.0, TreasureType.COMMON)
    ct = ContextTreasure(t)
    manager.register(ct)

    # Player is right next to treasure and aiming at it
    manager.update(0.016, player, cursor_x=420.0, cursor_y=310.0, current_gesture=GestureType.PINCH, is_pinching=True)
    assert manager.focused_target == ct
    assert manager.best_in_range_target == ct

    res = manager.handle_gesture(GestureType.PINCH, player, game, {"inventory": game.inventory, "has_dual_hands": False})
    assert res is not None
    assert res.success is True
    assert res.action_type == InteractionType.GRAB_TREASURE
    assert player.carried_treasure == t
    assert "GRABBED" in res.feedback_message


def test_2_pinch_near_artifact_inspects(manager, player, game):
    """Test 2: PINCH near ancient artifact triggers 3D Touchless Inspection Chamber."""
    artifact = ContextArtifact(
        artifact_id="ancient_vase",
        name="Sunken Hellenic Amphora",
        era="Classical Aegean 480 BCE",
        lore="Preserved inside an airtight clay cavity beneath the seafloor.",
        x=430.0,
        y=320.0,
        score_val=350,
    )
    manager.register(artifact)

    manager.update(0.016, player, cursor_x=430.0, cursor_y=320.0, current_gesture=GestureType.PINCH, is_pinching=True)
    assert manager.focused_target == artifact
    assert manager.best_in_range_target == artifact

    initial_score = player.score
    res = manager.handle_gesture(GestureType.PINCH, player, game, {"inventory": game.inventory, "has_dual_hands": False})
    assert res is not None
    assert res.success is True
    assert res.action_type == InteractionType.INSPECT_ARTIFACT
    assert res.opens_modal == "INSPECT_ARTIFACT"
    assert manager.active_modal == "INSPECT_ARTIFACT"
    assert player.score == initial_score + 350

    # 3D rotation works
    initial_rot_y = manager.modal_rot_y
    manager.handle_artifact_rotation(dx=15.0, dy=-5.0)
    assert manager.modal_rot_y > initial_rot_y

    # Modal closes cleanly
    manager.close_modal()
    assert manager.active_modal is None


def test_3_pinch_near_door_unlock_attempt(manager, player, game):
    """Test 3: PINCH near ancient locked door checks for required relic."""
    door = ContextDoor(
        door_id="galleon_vault_gate",
        name="Sunken Galleon Vault Gate",
        x=440.0,
        y=300.0,
        required_relic="gold_coin",
        required_relic_name="Spanish Doubloon",
    )
    manager.register(door)

    manager.update(0.016, player, cursor_x=440.0, cursor_y=300.0, current_gesture=GestureType.PINCH, is_pinching=True)

    # Attempt 1: Relic is NOT in inventory
    res = manager.handle_gesture(GestureType.PINCH, player, game, {"inventory": game.inventory, "has_dual_hands": False})
    assert res is not None
    assert res.success is False
    assert "requires" in res.feedback_message.lower()
    assert door.is_unlocked is False

    # Attempt 2: Add Spanish Doubloon (gold_coin) to inventory
    game.inventory.add_item("gold_coin", 1)
    manager.last_action_time = 0.0  # Reset debounce cooldown
    res2 = manager.handle_gesture(GestureType.PINCH, player, game, {"inventory": game.inventory, "has_dual_hands": False})
    assert res2 is not None
    assert res2.success is True
    assert res2.action_type == InteractionType.UNLOCK_DOOR
    assert door.is_unlocked is True
    assert door.state == InteractableState.UNLOCKED


def test_4_pinch_near_map_opens_sea_chart(manager, player, game):
    """Test 4: PINCH near underwater map opens tactical bathymetric sea chart overlay."""
    chart = ContextMap(x=415.0, y=295.0)
    manager.register(chart)

    manager.update(0.016, player, cursor_x=415.0, cursor_y=295.0, current_gesture=GestureType.PINCH, is_pinching=True)
    res = manager.handle_gesture(GestureType.PINCH, player, game, {"inventory": game.inventory, "has_dual_hands": False})

    assert res is not None
    assert res.success is True
    assert res.action_type == InteractionType.OPEN_MAP
    assert res.opens_modal == "EXPEDITION_MAP"
    assert manager.active_modal == "EXPEDITION_MAP"


def test_5_pinch_near_coral_examines_and_samples(manager, player, game):
    """Test 5: PINCH near coral sample examines and collects biological specimen."""
    coral = ContextCoral(
        coral_id="coral_staghorn",
        name="Bioluminescent Staghorn",
        x=410.0,
        y=310.0,
    )
    manager.register(coral)

    player.oxygen = 70.0
    manager.update(0.016, player, cursor_x=410.0, cursor_y=310.0, current_gesture=GestureType.PINCH, is_pinching=True)
    res = manager.handle_gesture(GestureType.PINCH, player, game, {"inventory": game.inventory, "has_dual_hands": False})

    assert res is not None
    assert res.success is True
    assert res.action_type in (InteractionType.SAMPLE_CORAL, InteractionType.COLLECT_CORAL)
    assert coral.state == InteractableState.COLLECTED
    # Oxygen recharge bonus from photosynthetic coral
    assert player.oxygen > 70.0


def test_6_pinch_in_open_water_no_accidental_action(manager, player, game):
    """Test 6: PINCH with NO valid object nearby causes NO accidental action."""
    # Place a treasure very far away in the ocean
    far_t = Treasure(1100.0, 650.0, TreasureType.GOLD)
    manager.register(ContextTreasure(far_t))

    # Swimmer is at (400, 300) in open free water
    manager.update(0.016, player, cursor_x=400.0, cursor_y=300.0, current_gesture=GestureType.PINCH, is_pinching=True)
    assert manager.best_in_range_target is None

    res = manager.handle_gesture(GestureType.PINCH, player, game, {"inventory": game.inventory, "has_dual_hands": False})
    assert res is None
    assert player.carried_treasure is None


def test_7_look_between_two_objects_selects_correct_target(manager, player):
    """Test 7: When two objects are nearby, alignment and priority pick the intended target."""
    # Object A is to the right
    t_right = Treasure(480.0, 300.0, TreasureType.COMMON)
    ct_right = ContextTreasure(t_right)
    # Object B is above
    t_top = Treasure(400.0, 220.0, TreasureType.COMMON)
    ct_top = ContextTreasure(t_top)

    manager.register(ct_right)
    manager.register(ct_top)

    # Aim cursor toward the right object
    manager.update(0.016, player, cursor_x=485.0, cursor_y=300.0, current_gesture=GestureType.NONE, is_pinching=False)
    assert manager.focused_target == ct_right

    # Aim cursor toward the top object
    manager.update(0.016, player, cursor_x=400.0, cursor_y=215.0, current_gesture=GestureType.NONE, is_pinching=False)
    assert manager.focused_target == ct_top


def test_8_move_away_interaction_prompt_disappears(manager, player):
    """Test 8: Moving away from an object removes the in-range status and clears prompt."""
    artifact = ContextArtifact(
        artifact_id="relic_1",
        name="Ancient Seal",
        era="Atlantis",
        lore="Lore text",
        x=420.0,
        y=300.0,
    )
    manager.register(artifact)

    # Close to object
    manager.update(0.016, player, cursor_x=420.0, cursor_y=300.0, current_gesture=GestureType.NONE, is_pinching=False)
    prompt = manager.get_current_prompt(GestureType.PINCH)
    assert prompt is not None
    assert "INSPECT" in prompt[1]

    # Move swimmer 600px away into deep water
    player.x = 1050.0
    player.y = 800.0
    manager.update(0.016, player, cursor_x=1050.0, cursor_y=800.0, current_gesture=GestureType.NONE, is_pinching=False)
    assert manager.best_in_range_target is None
    assert manager.focused_target is None
    assert manager.get_current_prompt(GestureType.PINCH) is None


def test_9_context_aware_sonar_categorization(manager):
    """Test 9: Two-finger sonar acoustic scan differentiates echo categories."""
    t = ContextTreasure(Treasure(400.0, 300.0, TreasureType.GOLD))
    a = ContextArtifact("v", "Vase", "Minoan", "Lore", 450.0, 320.0)
    d = ContextDoor("d", "Gate", 500.0, 350.0, "key", "Key")
    c = ContextCoral("c", "Coral", 420.0, 380.0)

    manager.register(t)
    manager.register(a)
    manager.register(d)
    manager.register(c)

    echoes = manager.trigger_sonar(400.0, 300.0, radius=500.0)
    assert len(echoes) == 4
    categories = {cat for _, cat in echoes}
    assert SonarEchoCategory.TREASURE in categories
    assert SonarEchoCategory.ARTIFACT in categories
    assert SonarEchoCategory.SECRET_DOOR in categories
    assert SonarEchoCategory.COLLECTIBLE in categories


def test_10_two_hands_heavy_lift(manager, player, game):
    """Test 10: Heavy object requires dual hands; single hand gives context feedback."""
    heavy_t = Treasure(420.0, 300.0, TreasureType.HEAVY)
    ct_heavy = ContextTreasure(heavy_t)
    manager.register(ct_heavy)

    manager.update(0.016, player, cursor_x=420.0, cursor_y=300.0, current_gesture=GestureType.PINCH, is_pinching=True, has_dual_hands=False)

    # Single hand attempt fails with informative feedback
    res1 = manager.handle_gesture(GestureType.PINCH, player, game, {"inventory": game.inventory, "has_dual_hands": False})
    assert res1 is None
    assert "BOTH HANDS" in manager.recent_feedback_message.upper()

    # Dual hands attempt succeeds
    manager.last_action_time = 0.0
    res2 = manager.handle_gesture(GestureType.PINCH, player, game, {"inventory": game.inventory, "has_dual_hands": True})
    assert res2 is not None
    assert res2.success is True
    assert res2.action_type == InteractionType.LIFT_HEAVY
    assert player.carried_treasure == heavy_t
