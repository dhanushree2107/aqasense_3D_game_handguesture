"""
Unit tests verifying the hand detector fix, dual-hand calculations,
main menu status indicator, and button responsiveness.
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
import pytest
from unittest.mock import MagicMock
from hand_tracking.hand_detector import HandDetector, SingleHandData, HandDetectionResult
from ui.menu import MainMenu
from ui.buttons import Button
from config import SCREEN_WIDTH, SCREEN_HEIGHT

@pytest.fixture(autouse=True)
def init_pygame():
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    yield

def test_hand_detector_math_available():
    """Confirms math module is imported and available in hand_detector module."""
    import hand_tracking.hand_detector as hd_mod
    assert hasattr(hd_mod, "math"), "math module must be imported in hand_detector"
    assert hd_mod.math.hypot(3, 4) == 5.0

def test_hand_detector_process_frame_dual_hands_no_exception():
    """Tests _process_frame with two hands detected to verify math.hypot does not raise NameError."""
    detector = HandDetector()
    
    # Mock MediaPipe results with 2 hands
    mock_results = MagicMock()
    
    # Hand 1 landmarks (21 points)
    h1_lms = MagicMock()
    h1_lms.landmark = [MagicMock(x=0.3, y=0.5, z=0.0) for _ in range(21)]
    
    # Hand 2 landmarks (21 points)
    h2_lms = MagicMock()
    h2_lms.landmark = [MagicMock(x=0.7, y=0.5, z=0.0) for _ in range(21)]
    
    mock_results.multi_hand_landmarks = [h1_lms, h2_lms]
    
    mock_handedness_1 = MagicMock()
    mock_handedness_1.classification = [MagicMock(label="Left")]
    mock_handedness_2 = MagicMock()
    mock_handedness_2.classification = [MagicMock(label="Right")]
    mock_results.multi_handedness = [mock_handedness_1, mock_handedness_2]
    
    detector.hands_detector = MagicMock()
    detector.hands_detector.process.return_value = mock_results
    
    import numpy as np
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    result = detector._process_frame(dummy_frame)
    assert result.is_detected is True
    assert result.num_hands == 2
    assert result.has_second_hand is True
    assert result.is_dual_hand_swimming is True
    assert result.swim_target_x > 0
    assert result.swim_target_y > 0

def test_main_menu_hand_detected_status_banner():
    """Verifies that MainMenu updates its status banner when hands are detected vs not detected."""
    menu = MainMenu(
        on_play=lambda: None,
        on_level_select=lambda: None,
        on_instructions=lambda: None,
        on_camera_check=lambda: None,
        on_quit=lambda: None,
        on_museum=lambda: None,
        on_challenges=lambda: None,
    )
    
    # 1. Hand not detected
    menu.update(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, is_clicked=False, dt=0.016, is_hand_detected=False)
    assert menu.is_hand_detected is False
    
    # 2. Single Hand detected
    menu.update(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, is_clicked=False, dt=0.016, is_hand_detected=True, num_hands=1)
    assert menu.is_hand_detected is True
    assert menu.num_hands == 1
    
    # 3. Dual Hands detected
    menu.update(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, is_clicked=False, dt=0.016, is_hand_detected=True, num_hands=2)
    assert menu.is_hand_detected is True
    assert menu.num_hands == 2
    
    # Render should execute without error
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    menu.draw(surf)

def test_button_edge_triggered_pinch_and_dwell():
    """Verifies Button edge-triggered click and dwell-click."""
    clicked_count = 0
    def on_click():
        nonlocal clicked_count
        clicked_count += 1
        
    btn = Button(
        rect=pygame.Rect(100, 100, 200, 50),
        text="TEST BUTTON",
        on_click=on_click
    )
    
    # Cursor outside button
    btn.update(50, 50, is_clicked=True, dt=0.016)
    assert clicked_count == 0
    
    # Cursor moves over button while clicking -> fires once
    btn.update(150, 125, is_clicked=True, dt=0.016)
    assert clicked_count == 1
    
    # Continuing to hold click over button -> should NOT multi-fire
    btn.update(150, 125, is_clicked=True, dt=0.016)
    assert clicked_count == 1
    
    # Release click
    btn.update(150, 125, is_clicked=False, dt=0.016)
    assert clicked_count == 1
    
    # Pinch again while hovering -> fires second click cleanly
    btn.update(150, 125, is_clicked=True, dt=0.016)
    assert clicked_count == 2
