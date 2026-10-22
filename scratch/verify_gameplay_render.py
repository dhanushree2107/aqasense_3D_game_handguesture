"""
Visual Verification Script for Context-Aware Gesture Interaction in AquaSense.
Renders real frames with:
1. Dynamic In-Game Reticle & HUD Context Prompt ([CONTEXT] PINCH -> INSPECT)
2. Interactive 3D Artifact Inspection Chamber
3. Tactical Bathymetric Sea Chart Overlay
Saves images to artifact directory for verification.
"""

import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pygame

# Run in headless mode to capture surfaces
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

from game.game_manager import GameManager, GameState
from hand_tracking.gesture_detector import GestureType
from game.treasure import TreasureType
from config import SCREEN_WIDTH, SCREEN_HEIGHT

OUT_DIR = r"C:\Users\VINU\.gemini\antigravity-ide\brain\c4f442f1-2477-4917-8514-fc8478138646"

def capture_snapshots():
    gm = GameManager()
    gm.start_new_expedition()
    gm.hand_detector.stop()  # Stop webcam background thread for deterministic snapshot

    # 1. Approach ancient artifact in Level 1
    art = None
    for item in gm.context_manager.interactables:
        if getattr(item, "object_id", "") == "ancient_vase":
            art = item
            break

    if art:
        gm.player.carried_treasure = None
        gm.player.x = art.x - 45
        gm.player.y = art.y - 15
        cursor_x = int(art.x)
        cursor_y = int(art.y)
    else:
        gm.player.x = 360
        gm.player.y = 500
        cursor_x = 360
        cursor_y = 515

    # Run one frame update & render with NO pinch -> Shows Reticle & Floating Context Badge
    gm._update_gameplay(
        dt=0.016,
        target_x=cursor_x,
        target_y=cursor_y,
        pinch_triggered=False,
        palm_triggered=False,
        sonar_triggered=False,
        shield_active=False
    )
    gm._render()

    shot1_path = os.path.join(OUT_DIR, "context_hud_reticle_gameplay.png")
    pygame.image.save(gm.screen, shot1_path)
    print(f"Captured: {shot1_path}")

    # 2. Trigger PINCH on the ancient artifact -> Opens 3D Inspection Chamber
    gm.context_manager.last_action_time = 0.0
    gm.player.carried_treasure = None
    if art:
        gm.context_manager.focused_target = art
        gm.context_manager.best_in_range_target = art
        gm.context_manager.handle_gesture(
            GestureType.PINCH,
            gm.player,
            gm,
            {"inventory": gm.inventory, "has_dual_hands": False}
        )
    # Rotate 3D artifact
    gm.context_manager.handle_artifact_rotation(dx=35.0, dy=-15.0)
    gm._render()

    shot2_path = os.path.join(OUT_DIR, "context_3d_inspection_chamber.png")
    pygame.image.save(gm.screen, shot2_path)
    print(f"Captured: {shot2_path}")

    # 3. Close inspection modal, approach map station, and open sea chart
    gm.context_manager.close_modal()
    gm.context_manager.last_action_time = 0.0
    gm.player.carried_treasure = None

    map_item = None
    for item in gm.context_manager.interactables:
        if item.interaction_type.value == "OPEN_MAP":
            map_item = item
            break

    if map_item:
        gm.player.x = map_item.x - 30
        gm.player.y = map_item.y - 10
        mx = int(map_item.x)
        my = int(map_item.y)
    else:
        gm.player.x = 640
        gm.player.y = 620
        mx = 640
        my = 630

    gm._update_gameplay(
        dt=0.016,
        target_x=mx,
        target_y=my,
        pinch_triggered=True,
        palm_triggered=False,
        sonar_triggered=False,
        shield_active=False
    )
    gm._render()

    shot3_path = os.path.join(OUT_DIR, "context_sea_chart_modal.png")
    pygame.image.save(gm.screen, shot3_path)
    print(f"Captured: {shot3_path}")

if __name__ == "__main__":
    capture_snapshots()
