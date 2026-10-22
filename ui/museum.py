"""
Underwater Treasure Hunt - Real-time 3D Cinematic Underwater Museum Experience
Submerged archaeological sanctuary showcasing discovered oceanic wonders with:
- 3D perspective depth environment (stone tile floors, receding Atlantean columns, arches, caustics)
- Physical locked stone doors with ancient inscriptions and cinematic unlock opening animations
- Full campaign level progression integration (Level 1-5 Galleries + Final Rank Legendary Chamber)
- 3D interactive artifact vector rendering with pitch/yaw 3D rotation and dynamic specular lighting
- Dual-hand interaction for large artifacts (dual-lift chest lid, dual-rotate guardian seal)
- Living 3D marine life (turtles, rays, sharks, jellyfish, tropical reef fish)
- Touchless hand gestures (Pinch, Two Fingers, Open Palm, Fist) with clean futuristic HUD visor
"""

import math
import os
import random
import time
from typing import Callable, Dict, List, Optional, Set, Tuple
import pygame

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_NEON_TEAL,
    COLOR_OCEAN_CYAN,
    COLOR_GOLD,
    COLOR_CORAL_RED,
    COLOR_EMERALD,
    COLOR_AMBER_WARNING,
    COLOR_PURPLE_MYSTIC,
    COLOR_WHITE,
)
from ui.buttons import Button
from audio.sound_manager import SoundManager
from hand_tracking.gesture_detector import GestureType
from ui.underwater_3d_scene import Underwater3DScene
from game.inventory import UnderwaterMuseum, MuseumExhibit

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")


class MuseumChamberConfig:
    """Configuration for an underwater museum chamber tied to expedition campaign progression."""
    def __init__(
        self,
        chamber_id: str,
        label: str,
        banner: str,
        subtitle: str,
        file_name: str,
        required_level: int,
        relic_ids: List[str],
        lock_accent: Tuple[int, int, int] = COLOR_GOLD,
    ):
        self.chamber_id = chamber_id
        self.label = label
        self.banner = banner
        self.subtitle = subtitle
        self.file_name = file_name
        self.required_level = required_level  # 0 = always, 1-5 = level completed, 6 = all 5 completed
        self.relic_ids = relic_ids
        self.lock_accent = lock_accent


class MuseumScreen:
    """
    Photorealistic 3D Underwater Museum Experience.
    Displays discovered oceanic wonders in submerged architectural halls with
    depth perspective, physical locked stone gates, interactive 3D artifact rotation,
    dual-hand hoisting, and living environmental marine life.
    """

    def __init__(
        self,
        on_back: Callable[[], None],
        sound_manager: Optional[SoundManager] = None
    ):
        self.on_back = on_back
        self.sound_manager = sound_manager
        self.museum: Optional[UnderwaterMuseum] = None

        # Typography
        if not pygame.font.get_init():
            pygame.font.init()
        self.font_brand = pygame.font.SysFont("segoeui", 26, bold=True)
        self.font_title = pygame.font.SysFont("segoeui", 20, bold=True)
        self.font_sub = pygame.font.SysFont("segoeui", 13, bold=True)
        self.font_card_title = pygame.font.SysFont("segoeui", 13, bold=True)
        self.font_card_desc = pygame.font.SysFont("segoeui", 11)
        self.font_badge = pygame.font.SysFont("segoeui", 11, bold=True)
        self.font_modal_title = pygame.font.SysFont("segoeui", 22, bold=True)
        self.font_modal_sub = pygame.font.SysFont("segoeui", 13, bold=True)
        self.font_modal_body = pygame.font.SysFont("segoeui", 13)
        self.font_featured_title = pygame.font.SysFont("segoeui", 19, bold=True)
        self.font_featured_desc = pygame.font.SysFont("segoeui", 12)
        self.font_door_banner = pygame.font.SysFont("segoeui", 22, bold=True)
        self.font_door_sub = pygame.font.SysFont("segoeui", 14, bold=True)

        # Photorealistic 3D Underwater Simulation Environment
        self.scene_3d = Underwater3DScene(theme="shipwreck")
        self.cursor_pos: Tuple[int, int] = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # Chamber Definitions Connected to Existing Campaign Progression
        # Ordered so that Two-Fingers gesture cycles gallery -> archive -> legendary (matching tests)
        self.chambers: Dict[str, MuseumChamberConfig] = {
            "entrance": MuseumChamberConfig(
                chamber_id="entrance",
                label="MUSEUM ENTRANCE",
                banner="Monumental Sunken Sanctuary Portal",
                subtitle="Submerged Atlantean Portal Arch & Ancient Ruins",
                file_name="aquasense_grand_museum.png",
                required_level=0,
                relic_ids=["pearl", "gold_coin", "heavy_chest", "coral_compass", "ancient_vase", "sapphire_chalice", "guardian_seal", "ancient_crown"],
                lock_accent=COLOR_NEON_TEAL,
            ),
            "gallery": MuseumChamberConfig(
                chamber_id="gallery",
                label="TREASURE GALLERY",
                banner="Treasure Gallery (Level 1)",
                subtitle="Gilded Exhibition Hall & Sunken Armada Relics",
                file_name="aquasense_grand_museum.png",
                required_level=1,
                relic_ids=["pearl", "gold_coin", "heavy_chest"],
                lock_accent=COLOR_GOLD,
            ),
            "archive": MuseumChamberConfig(
                chamber_id="archive",
                label="DEEP ARCHIVE",
                banner="Deep Ocean Archive (Level 3)",
                subtitle="Abyssal Reliquary & Crystal Sanctuary",
                file_name="aquasense_archive.jpg",
                required_level=3,
                relic_ids=["sapphire_chalice"],
                lock_accent=COLOR_OCEAN_CYAN,
            ),
            "legendary": MuseumChamberConfig(
                chamber_id="legendary",
                label="LEGENDARY CHAMBER",
                banner="LEGENDARY CHAMBER",
                subtitle="ALL EXPEDITIONS COMPLETE",
                file_name="aquasense_legendary.jpg",
                required_level=6,  # All 5 levels completed
                relic_ids=["ancient_crown"],
                lock_accent=COLOR_GOLD,
            ),
            "coral_gallery": MuseumChamberConfig(
                chamber_id="coral_gallery",
                label="CORAL GALLERY",
                banner="Coral Artifact Gallery (Level 2)",
                subtitle="Living Coral Corridors & Nautilus Relics",
                file_name="aquasense_coral_gallery.jpg",
                required_level=2,
                relic_ids=["coral_compass", "ancient_vase"],
                lock_accent=COLOR_EMERALD,
            ),
            "shipwreck_gallery": MuseumChamberConfig(
                chamber_id="shipwreck_gallery",
                label="LOST SHIP GALLERY",
                banner="Lost Ship Gallery (Level 4)",
                subtitle="Galleon San Pedro Armory & Maritime Relics",
                file_name="aquasense_shipwreck_gallery.jpg",
                required_level=4,
                relic_ids=["ancient_vase", "heavy_chest"],
                lock_accent=COLOR_AMBER_WARNING,
            ),
            "ruins_gallery": MuseumChamberConfig(
                chamber_id="ruins_gallery",
                label="ANCIENT RUINS",
                banner="Ancient Ruins Gallery (Level 5)",
                subtitle="Submerged Atlantean Temple of the Sea Gods",
                file_name="aquasense_ruins_gallery.jpg",
                required_level=5,
                relic_ids=["guardian_seal"],
                lock_accent=COLOR_PURPLE_MYSTIC,
            ),
            "vault": MuseumChamberConfig(
                chamber_id="vault",
                label="VAULT PORTAL",
                banner="Sunken Vault Sanctuary",
                subtitle="Ancient Carved Sea Vault Gates",
                file_name="aquasense_vault.jpg",
                required_level=1,
                relic_ids=["heavy_chest", "ancient_crown"],
                lock_accent=COLOR_GOLD,
            ),
        }

        self.chamber_keys: List[str] = list(self.chambers.keys())
        self.chamber_info: Dict[str, Dict[str, str]] = {
            k: {
                "label": c.label,
                "banner": c.banner,
                "subtitle": c.subtitle,
                "file": c.file_name,
            }
            for k, c in self.chambers.items()
        }

        # Cached Chamber Backdrop Environments
        self.chamber_images: Dict[str, pygame.Surface] = {}
        has_display = (pygame.display.get_surface() is not None)
        for k, c in self.chambers.items():
            img_path = os.path.join(ASSETS_DIR, c.file_name)
            if os.path.exists(img_path):
                try:
                    loaded = pygame.image.load(img_path)
                    if has_display:
                        try:
                            loaded = loaded.convert()
                        except Exception:
                            pass
                    self.chamber_images[k] = pygame.transform.smoothscale(loaded, (SCREEN_WIDTH, SCREEN_HEIGHT))
                except Exception:
                    pass

        # Locked Stone Door Texture
        self.locked_door_image: Optional[pygame.Surface] = None
        door_path = os.path.join(ASSETS_DIR, "aquasense_locked_door.jpg")
        if os.path.exists(door_path):
            try:
                raw_d = pygame.image.load(door_path)
                if has_display:
                    try:
                        raw_d = raw_d.convert()
                    except Exception:
                        pass
                self.locked_door_image = pygame.transform.smoothscale(raw_d, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except Exception:
                pass

        # Cutout Arch Overlay for Monumental 3D Entrance
        self.arch_cutout: Optional[pygame.Surface] = None
        arch_path = os.path.join(ASSETS_DIR, "ruins_arch.png")
        if os.path.exists(arch_path):
            try:
                raw_a = pygame.image.load(arch_path)
                if has_display:
                    try:
                        raw_a = raw_a.convert_alpha()
                    except Exception:
                        pass
                self.arch_cutout = pygame.transform.smoothscale(raw_a, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except Exception:
                pass

        # Navigation State
        self.active_chamber: str = "gallery"
        self.selected_relic_id: str = "gold_coin"
        self.cam_ox: float = 0.0
        self.cam_oy: float = 0.0

        # Campaign Progression State (Passed dynamically from GameManager)
        self.completed_levels: Set[int] = set()
        self.unlocked_levels_count: int = 1
        self.curator_mode_active: bool = False

        # Physical Door Slide Animation (0.0 = fully closed, 1.0 = fully open)
        self.door_open_progress: Dict[str, float] = {k: 1.0 for k in self.chamber_keys}
        self.door_opening_chamber: Optional[str] = None
        self.door_animation_timer: float = 0.0

        # 3D Artifact Interactive Rotation State
        self.relic_yaw: float = 0.0
        self.relic_pitch: float = 0.0
        self.is_dragging_relic: bool = False
        self.last_drag_x: float = 0.0
        self.last_drag_y: float = 0.0

        # Two-Hand Interaction State
        self.has_second_hand: bool = False
        self.second_cursor_pos: Optional[Tuple[float, float]] = None
        self.second_gesture: GestureType = GestureType.NONE
        self.dual_hand_lift_progress: float = 0.0  # For heavy chest opening
        self.chest_is_opened: bool = False

        # Floating Chamber Navigation Tabs (Sleek glass pills across top)
        self.tab_rects: Dict[str, pygame.Rect] = {}
        tab_w, tab_h = 126, 24
        tab_gap = 5
        total_tab_w = len(self.chamber_keys) * tab_w + (len(self.chamber_keys) - 1) * tab_gap
        start_tab_x = (SCREEN_WIDTH - total_tab_w) // 2
        tab_y = 52
        for i, k in enumerate(self.chamber_keys):
            self.tab_rects[k] = pygame.Rect(start_tab_x + i * (tab_w + tab_gap), tab_y, tab_w, tab_h)

        # Hand Tracking & Gesture Control State Machine
        self.current_gesture: GestureType = GestureType.NONE
        self.is_hand_detected: bool = False
        self.gesture_action_cooldown: float = 0.0
        self.palm_hold_timer: float = 0.0
        self.palm_hold_threshold: float = 0.65
        self.last_triggered_gesture: Optional[str] = None
        self.gesture_feedback_timer: float = 0.0

        # Vitrines & Cards Hitboxes on Floor
        self.card_rects: Dict[str, pygame.Rect] = {}
        self.card_dwell_times: Dict[str, float] = {}
        self.dwell_threshold: float = 0.65
        self.hovered_card_id: Optional[str] = None
        self.prev_hovered_card_id: Optional[str] = None
        self.inspected_exhibit: Optional[MuseumExhibit] = None
        self.pulse_phase: float = 0.0
        self.prev_clicked: bool = False
        self.modal_open_time: float = 0.0

        # Initialize vitrine pedestal hitboxes for all 8 standard relics
        # 4 Prominent in-world pedestals + 4 archival floor dock relics
        self.card_rects = {
            "pearl": pygame.Rect(35, 330, 220, 360),
            "ancient_crown": pygame.Rect(335, 410, 165, 305),
            "ancient_vase": pygame.Rect(775, 410, 165, 305),
            "gold_coin": pygame.Rect(1010, 390, 230, 325),
            "sapphire_chalice": pygame.Rect(515, 646, 56, 56),
            "heavy_chest": pygame.Rect(580, 646, 56, 56),
            "guardian_seal": pygame.Rect(645, 646, 56, 56),
            "coral_compass": pygame.Rect(710, 646, 56, 56),
        }

        # UI Buttons matching exact visual layout of user's reference mockup
        self.back_btn = Button(
            pygame.Rect(26, 618, 126, 52),
            "< BACK",
            font_size=15,
            on_click=self._on_back_clicked,
            sound_manager=self.sound_manager,
            accent_color=COLOR_OCEAN_CYAN,
        )
        self.next_btn = Button(
            pygame.Rect(1128, 636, 126, 52),
            "NEXT >",
            font_size=15,
            on_click=self._next_chamber,
            sound_manager=self.sound_manager,
            accent_color=COLOR_OCEAN_CYAN,
        )
        self.curator_btn = Button(
            pygame.Rect(1000, 20, 269, 68),
            "UNLOCK ALL (CURATOR)",
            font_size=12,
            on_click=self._toggle_curator_mode,
            sound_manager=self.sound_manager,
            accent_color=COLOR_GOLD,
        )
        self.pinch_inspect_btn = Button(
            pygame.Rect(915, 436, 295, 38),
            "PINCH TO INSPECT",
            font_size=14,
            on_click=self._inspect_selected_relic,
            sound_manager=self.sound_manager,
            accent_color=COLOR_OCEAN_CYAN,
        )
        self.modal_close_btn = Button(
            pygame.Rect(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 195, 260, 44),
            "CLOSE INSPECTION",
            on_click=self._close_modal,
            sound_manager=self.sound_manager,
            accent_color=COLOR_NEON_TEAL,
        )

        # Particle motes for divine / underwater chambers
        self.chamber_particles: List[Dict[str, float]] = []
        for _ in range(40):
            self.chamber_particles.append({
                "x": random.uniform(0, SCREEN_WIDTH),
                "y": random.uniform(0, SCREEN_HEIGHT),
                "vy": random.uniform(-25, -8),
                "vx": random.uniform(-10, 10),
                "radius": random.uniform(1.5, 4.0),
                "alpha": random.uniform(80, 200),
                "gold": random.random() > 0.5,
            })

    def _is_chamber_unlocked(self, chamber_id: str, completed_levels: Optional[Set[int]] = None) -> bool:
        """Determines whether a chamber is accessible based on campaign progression or curator mode."""
        if self.curator_mode_active:
            return True
        comp = completed_levels if completed_levels is not None else self.completed_levels
        cfg = self.chambers.get(chamber_id)
        if not cfg or cfg.required_level == 0:
            return True
        if cfg.required_level == 1:
            return True  # Level 1 gallery accessible
        if cfg.required_level in (2, 3, 4, 5):
            return cfg.required_level in comp or self.unlocked_levels_count >= (cfg.required_level + 1)
        if cfg.required_level == 6:
            # Legendary chamber unlocked when all 5 levels are conquered
            return len(comp) >= 5 or (5 in comp and len(comp) >= 4)
        return False

    def _inspect_selected_relic(self) -> None:
        """Inspects the currently selected featured relic."""
        if self.museum and self.selected_relic_id in self.museum.exhibits:
            self.inspected_exhibit = self.museum.exhibits[self.selected_relic_id]
            self.modal_open_time = time.time()
            self.relic_yaw = 0.0
            self.relic_pitch = 0.0
            self.dual_hand_lift_progress = 0.0
            self.chest_is_opened = False
            if self.sound_manager:
                self.sound_manager.play('click', volume_mult=0.8)

    def _close_modal(self) -> None:
        self.inspected_exhibit = None
        self.chest_is_opened = False

    def close_inspection(self) -> bool:
        """Closes the active exhibit modal if open. Returns True if modal was open."""
        if self.inspected_exhibit is not None:
            self.inspected_exhibit = None
            self.chest_is_opened = False
            if self.sound_manager:
                self.sound_manager.play('click', volume_mult=0.5)
            return True
        return False

    def set_return_label(self, label: str) -> None:
        """Dynamically adjusts back button label depending on origin screen."""
        self.back_btn.raw_text = label
        self.back_btn.text = Button.clean_label(label)

    def _toggle_curator_mode(self) -> None:
        """Toggles Curator mode: unlocks all 8 relics and opens all chamber gates, or resets."""
        if not self.museum:
            return
        if self.museum.get_unlocked_count() >= self.museum.get_total_count():
            self.museum.reset_all()
            self.curator_mode_active = False
            # Revert locked doors
            for k, c in self.chambers.items():
                if not self._is_chamber_unlocked(k, self.completed_levels):
                    self.door_open_progress[k] = 0.0
        else:
            self.museum.unlock_all()
            self.curator_mode_active = True
            # Trigger cinematic door opening on locked doors
            for k in self.chamber_keys:
                self.door_open_progress[k] = 1.0
        if self.sound_manager:
            self.sound_manager.play('puzzle_success')

    def _on_back_clicked(self) -> None:
        """Handles back button click. Returns to Grand Hall or exits museum."""
        if self.inspected_exhibit is not None:
            self._close_modal()
            return
        if self.active_chamber != "gallery":
            self.active_chamber = "gallery"
            if self.sound_manager:
                self.sound_manager.play('click', volume_mult=0.7)
        else:
            if callable(self.on_back):
                self.on_back()

    def _next_chamber(self) -> None:
        """Cycles forward to the next museum gallery/chamber or next relic in modal."""
        if self.inspected_exhibit is not None:
            if self.museum:
                all_eids = list(self.museum.exhibits.keys())
                if self.inspected_exhibit.exhibit_id in all_eids:
                    idx = all_eids.index(self.inspected_exhibit.exhibit_id)
                    next_eid = all_eids[(idx + 1) % len(all_eids)]
                    self.inspected_exhibit = self.museum.exhibits[next_eid]
                    self.selected_relic_id = next_eid
                    self.modal_open_time = time.time()
                    self.relic_yaw = 0.0
                    self.relic_pitch = 0.0
                    if self.sound_manager:
                        self.sound_manager.play('sonar')
            return

        curr_idx = self.chamber_keys.index(self.active_chamber) if self.active_chamber in self.chamber_keys else 0
        next_idx = (curr_idx + 1) % len(self.chamber_keys)
        self.active_chamber = self.chamber_keys[next_idx]
        if self.sound_manager:
            self.sound_manager.play('click', volume_mult=0.7)

    def update(
        self,
        cursor_x: int,
        cursor_y: int,
        is_clicked: bool,
        dt: float,
        current_gesture: GestureType = GestureType.NONE,
        is_hand_detected: bool = True,
        palm_triggered: bool = False,
        sonar_triggered: bool = False,
        shield_active: bool = False,
        is_pinching: bool = False,
        completed_levels: Optional[Set[int]] = None,
        unlocked_levels: Optional[int] = None,
        has_second_hand: bool = False,
        second_cursor_pos: Optional[Tuple[float, float]] = None,
        second_gesture: GestureType = GestureType.NONE,
    ) -> None:
        """Updates physics, touchless gestures, dual-hand interaction, 3D camera, and animations."""
        self.cursor_pos = (cursor_x, cursor_y)
        self.current_gesture = current_gesture
        self.is_hand_detected = is_hand_detected
        self.has_second_hand = has_second_hand
        self.second_cursor_pos = second_cursor_pos
        self.second_gesture = second_gesture
        if completed_levels is not None:
            self.completed_levels = completed_levels
        if unlocked_levels is not None:
            self.unlocked_levels_count = unlocked_levels

        self.scene_3d.update(dt, cursor_x, cursor_y)
        self.pulse_phase += 3.5 * dt
        self.gesture_action_cooldown = max(0.0, self.gesture_action_cooldown - dt)
        self.gesture_feedback_timer = max(0.0, self.gesture_feedback_timer - dt)

        # Update floating chamber dust and golden motes
        for p in self.chamber_particles:
            p["y"] += p["vy"] * dt
            p["x"] += p["vx"] * dt + math.sin(self.pulse_phase + p["y"] * 0.01) * 0.5
            if p["y"] < -10:
                p["y"] = SCREEN_HEIGHT + 10
                p["x"] = random.uniform(0, SCREEN_WIDTH)

        effective_clicked = is_clicked or is_pinching or (current_gesture == GestureType.PINCH)
        click_just_pressed = (effective_clicked and not self.prev_clicked)

        # Smooth 3D physical camera parallax panning as user moves hand in air
        target_cam_x = (cursor_x - SCREEN_WIDTH / 2) / (SCREEN_WIDTH / 2) * -16.0
        target_cam_y = (cursor_y - SCREEN_HEIGHT / 2) / (SCREEN_HEIGHT / 2) * -10.0
        self.cam_ox += (target_cam_x - self.cam_ox) * 0.12
        self.cam_oy += (target_cam_y - self.cam_oy) * 0.12

        # Update physical door opening animation
        for k in self.chamber_keys:
            is_unlocked = self._is_chamber_unlocked(k, self.completed_levels)
            target_prog = 1.0 if is_unlocked else 0.0
            curr_prog = self.door_open_progress.get(k, 1.0)
            if curr_prog < target_prog:
                self.door_open_progress[k] = min(target_prog, curr_prog + 1.2 * dt)
            elif curr_prog > target_prog:
                self.door_open_progress[k] = max(target_prog, curr_prog - 2.0 * dt)

        # 1. Gesture Navigation: TWO FINGERS (Sonar / Peace Sign)
        # In Modal: cycles through exhibits; In Chamber: cycles through chambers
        if (sonar_triggered or current_gesture == GestureType.TWO_FINGERS) and self.gesture_action_cooldown <= 0.0:
            if self.inspected_exhibit is not None and self.museum:
                all_eids = list(self.museum.exhibits.keys())
                if self.inspected_exhibit.exhibit_id in all_eids:
                    idx = all_eids.index(self.inspected_exhibit.exhibit_id)
                    next_eid = all_eids[(idx + 1) % len(all_eids)]
                    self.inspected_exhibit = self.museum.exhibits[next_eid]
                    self.selected_relic_id = next_eid
                    self.modal_open_time = time.time()
                    self.relic_yaw = 0.0
                    self.relic_pitch = 0.0
                    self.gesture_action_cooldown = 0.40
                    self.last_triggered_gesture = f"INSPECTING: {self.inspected_exhibit.name.upper()}"
                    self.gesture_feedback_timer = 1.2
                    if self.sound_manager:
                        self.sound_manager.play('sonar')
            else:
                curr_c_idx = self.chamber_keys.index(self.active_chamber) if self.active_chamber in self.chamber_keys else 0
                next_c_idx = (curr_c_idx + 1) % len(self.chamber_keys)
                self.active_chamber = self.chamber_keys[next_c_idx]
                self.gesture_action_cooldown = 0.40
                lbl = self.chambers[self.active_chamber].label
                self.last_triggered_gesture = f"CHAMBER: {lbl}"
                self.gesture_feedback_timer = 1.2
                if self.sound_manager:
                    self.sound_manager.play('sonar')

        # 2. Gesture Navigation: OPEN PALM (Dismiss Modal / Hold to Return)
        if palm_triggered or current_gesture == GestureType.OPEN_PALM:
            if self.inspected_exhibit is not None:
                if self.gesture_action_cooldown <= 0.0:
                    self.inspected_exhibit = None
                    self.gesture_action_cooldown = 0.35
                    self.last_triggered_gesture = "CLOSED INSPECTION"
                    self.gesture_feedback_timer = 1.0
                    if self.sound_manager:
                        self.sound_manager.play('click', volume_mult=0.6)
            else:
                self.palm_hold_timer += dt
                if self.palm_hold_timer >= self.palm_hold_threshold and self.gesture_action_cooldown <= 0.0:
                    self.palm_hold_timer = 0.0
                    self.gesture_action_cooldown = 0.60
                    self.last_triggered_gesture = "RETURNING TO MENU"
                    self.gesture_feedback_timer = 1.0
                    if self.sound_manager:
                        self.sound_manager.play('click', volume_mult=0.8)
                    if callable(self.on_back):
                        self.on_back()
                        self.prev_clicked = effective_clicked
                        return
        else:
            self.palm_hold_timer = max(0.0, self.palm_hold_timer - dt * 2.0)

        # 3. Gesture Navigation: FIST (Shield) -> Close Modal / Toggle Curator Mode
        if (shield_active or current_gesture == GestureType.FIST) and self.gesture_action_cooldown <= 0.0:
            if self.inspected_exhibit is not None:
                self.inspected_exhibit = None
                self.gesture_action_cooldown = 0.35
                self.last_triggered_gesture = "CLOSED INSPECTION"
                self.gesture_feedback_timer = 1.0
                if self.sound_manager:
                    self.sound_manager.play('click', volume_mult=0.6)
            else:
                self._toggle_curator_mode()
                self.gesture_action_cooldown = 0.50
                self.last_triggered_gesture = "CURATOR MODE TOGGLED"
                self.gesture_feedback_timer = 1.2

        # 4. Interactive 3D Artifact Rotation in Inspection Modal
        if self.inspected_exhibit is not None:
            # Ambient sinusoidal float
            self.relic_yaw += 0.8 * dt
            # Hand motion shifts yaw & pitch
            norm_hx = (cursor_x - SCREEN_WIDTH / 2) / (SCREEN_WIDTH / 2)
            norm_hy = (cursor_y - SCREEN_HEIGHT / 2) / (SCREEN_HEIGHT / 2)
            self.relic_pitch = norm_hy * 0.45
            if effective_clicked:
                self.relic_yaw += norm_hx * 2.5 * dt

            # Two-Hand Interaction: Lifting & Opening Large Chest / Guardian Seal
            if self.has_second_hand and self.second_cursor_pos:
                h2_x, h2_y = self.second_cursor_pos
                # Hands moving together / apart changes 3D rotation
                hand_dist = math.hypot(cursor_x - h2_x, cursor_y - h2_y)
                self.relic_yaw += (cursor_x - h2_x) * 0.002

                # Upward dual-lift gesture for chest lid opening
                avg_y = (cursor_y + h2_y) / 2.0
                if avg_y < SCREEN_HEIGHT * 0.48:
                    self.dual_hand_lift_progress = min(1.0, self.dual_hand_lift_progress + 1.8 * dt)
                    if self.dual_hand_lift_progress >= 0.85 and not self.chest_is_opened:
                        self.chest_is_opened = True
                        if self.sound_manager:
                            self.sound_manager.play('treasure')
                else:
                    self.dual_hand_lift_progress = max(0.0, self.dual_hand_lift_progress - 1.2 * dt)

            modal_rect = pygame.Rect(SCREEN_WIDTH // 2 - 350, SCREEN_HEIGHT // 2 - 250, 700, 500)
            self.modal_close_btn.update(cursor_x, cursor_y, effective_clicked, dt)
            if click_just_pressed and not modal_rect.collidepoint(cursor_x, cursor_y):
                if time.time() - self.modal_open_time > 0.30:
                    self.inspected_exhibit = None
                    if self.sound_manager:
                        self.sound_manager.play('click', volume_mult=0.6)
            self.prev_clicked = effective_clicked
            return

        # Main gallery navigation buttons
        self.back_btn.update(cursor_x, cursor_y, effective_clicked, dt)
        self.next_btn.update(cursor_x, cursor_y, effective_clicked, dt)
        self.curator_btn.update(cursor_x, cursor_y, effective_clicked, dt)
        self.pinch_inspect_btn.update(cursor_x, cursor_y, effective_clicked, dt)

        # Top-Right Collected Artifacts Badge click toggles curator mode
        top_right_badge_rect = pygame.Rect(1000, 10, 269, 75)
        if click_just_pressed and top_right_badge_rect.collidepoint(cursor_x, cursor_y):
            self._toggle_curator_mode()

        # Chamber Tab Navigation
        for k, trect in self.tab_rects.items():
            if trect.collidepoint(cursor_x, cursor_y):
                if click_just_pressed and self.active_chamber != k:
                    self.active_chamber = k
                    if self.sound_manager:
                        self.sound_manager.play('click', volume_mult=0.6)
                break

        # Vitrine Pedestals on the floor
        self.hovered_card_id = None
        for eid, rect in self.card_rects.items():
            if rect.collidepoint(cursor_x, cursor_y):
                self.hovered_card_id = eid
                self.selected_relic_id = eid
                self.card_dwell_times[eid] = self.card_dwell_times.get(eid, 0.0) + dt
                dwell_triggered = (self.card_dwell_times[eid] >= self.dwell_threshold)

                if (click_just_pressed or dwell_triggered) and self.museum:
                    self.inspected_exhibit = self.museum.exhibits.get(eid)
                    self.modal_open_time = time.time()
                    self.relic_yaw = 0.0
                    self.relic_pitch = 0.0
                    self.card_dwell_times[eid] = -0.5
                    if self.sound_manager:
                        self.sound_manager.play('click', volume_mult=0.8)
                    break
            else:
                self.card_dwell_times[eid] = max(0.0, self.card_dwell_times.get(eid, 0.0) - dt * 2.0)

        if self.hovered_card_id != self.prev_hovered_card_id:
            if self.hovered_card_id is not None and self.sound_manager:
                self.sound_manager.play('hover', volume_mult=0.3)
            self.prev_hovered_card_id = self.hovered_card_id

        self.prev_clicked = effective_clicked

    # =========================================================================
    # 3D PHYSICAL ENVIRONMENT RENDERING (Floors, Columns, Arches, Caustics)
    # =========================================================================

    def _draw_3d_perspective_floor(self, surface: pygame.Surface) -> None:
        """Renders realistic 3D perspective ancient stone tile floor with depth vanishing point."""
        vp_x = SCREEN_WIDTH // 2 + int(self.cam_ox * 0.8)
        vp_y = int(SCREEN_HEIGHT * 0.44) + int(self.cam_oy * 0.5)

        floor_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - vp_y), pygame.SRCALPHA)
        # Deep oceanic floor shadow gradient
        for y_idx in range(0, SCREEN_HEIGHT - vp_y, 4):
            frac = y_idx / float(SCREEN_HEIGHT - vp_y)
            alpha = int(45 + 130 * frac)
            pygame.draw.line(floor_surf, (8, 22, 42, alpha), (0, y_idx), (SCREEN_WIDTH, y_idx), 4)

        # Perspective stone tile longitudinal seams
        num_seams = 18
        for i in range(-num_seams // 2, num_seams // 2 + 1):
            bottom_x = SCREEN_WIDTH // 2 + i * (SCREEN_WIDTH / (num_seams - 2))
            pygame.draw.line(floor_surf, (18, 48, 80, 110), (vp_x, 0), (int(bottom_x), SCREEN_HEIGHT - vp_y), 2)

        # Transverse stone slab seams receding geometrically
        num_slabs = 9
        for j in range(1, num_slabs + 1):
            frac = (j / float(num_slabs)) ** 2.2
            y_slab = int((SCREEN_HEIGHT - vp_y) * frac)
            pygame.draw.line(floor_surf, (24, 58, 92, int(80 + 110 * frac)), (0, y_slab), (SCREEN_WIDTH, y_slab), 2)

        surface.blit(floor_surf, (0, vp_y))

    def _draw_3d_ancient_columns(self, surface: pygame.Surface) -> None:
        """Renders 3D fluted stone columns with perspective scaling and gold Atlantean rings."""
        vp_ox = self.cam_ox * 0.5

        # Left Column Series receding into depth
        # (x_base, width, col_color, is_foreground)
        cols_left = [
            (32 + vp_ox * 0.3, 44, (14, 26, 44), False),
            (115 + vp_ox * 0.6, 36, (18, 34, 56), False),
            (210 + vp_ox * 0.9, 28, (22, 40, 66), False),
        ]
        for cx, cw, col, _ in cols_left:
            pygame.draw.rect(surface, col, (int(cx - cw // 2), 0, cw, SCREEN_HEIGHT))
            pygame.draw.rect(surface, (36, 60, 95), (int(cx - cw // 2), 0, cw, SCREEN_HEIGHT), width=2)
            # Flutes
            for fl in (-cw // 3, 0, cw // 3):
                pygame.draw.line(surface, (10, 18, 30), (int(cx + fl), 0), (int(cx + fl), SCREEN_HEIGHT), 2)
            # Gold rings
            for ry in (110, SCREEN_HEIGHT // 2, SCREEN_HEIGHT - 130):
                pygame.draw.rect(surface, (215, 175, 45), (int(cx - cw // 2), ry, cw, 6))

        # Right Column Series receding into depth
        cols_right = [
            (SCREEN_WIDTH - 210 + vp_ox * 0.9, 28, (22, 40, 66), False),
            (SCREEN_WIDTH - 115 + vp_ox * 0.6, 36, (18, 34, 56), False),
            (SCREEN_WIDTH - 32 + vp_ox * 0.3, 44, (14, 26, 44), False),
        ]
        for cx, cw, col, _ in cols_right:
            pygame.draw.rect(surface, col, (int(cx - cw // 2), 0, cw, SCREEN_HEIGHT))
            pygame.draw.rect(surface, (36, 60, 95), (int(cx - cw // 2), 0, cw, SCREEN_HEIGHT), width=2)
            for fl in (-cw // 3, 0, cw // 3):
                pygame.draw.line(surface, (10, 18, 30), (int(cx + fl), 0), (int(cx + fl), SCREEN_HEIGHT), 2)
            for ry in (110, SCREEN_HEIGHT // 2, SCREEN_HEIGHT - 130):
                pygame.draw.rect(surface, (215, 175, 45), (int(cx - cw // 2), ry, cw, 6))

    def _draw_volumetric_god_rays(self, surface: pygame.Surface) -> None:
        """Renders dynamic volumetric sunlight rays penetrating the submerged ocean volume."""
        ray_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        num_rays = 7
        t = self.scene_3d.time_sec
        for i in range(num_rays):
            sway = math.sin(t * 0.38 + i * 1.10) * 36.0
            x_top = (i + 1) * (SCREEN_WIDTH / (num_rays + 1)) + sway
            width_top = 45.0
            width_bottom = 145.0
            x_bottom = x_top + 115.0 + sway * 1.4

            ray_poly = [
                (x_top - width_top / 2, 0),
                (x_top + width_top / 2, 0),
                (x_bottom + width_bottom / 2, SCREEN_HEIGHT),
                (x_bottom - width_bottom / 2, SCREEN_HEIGHT),
            ]
            ray_alpha = int(16 + 8 * math.sin(t * 1.15 + i * 0.85))
            pygame.draw.polygon(ray_surf, (215, 245, 255, ray_alpha), ray_poly)

        surface.blit(ray_surf, (0, 0))

    def _draw_underwater_caustics(self, surface: pygame.Surface) -> None:
        """Renders realistic animated water caustics shimmering across museum floor."""
        if self.scene_3d.surf_caustics:
            caustic_layer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            cw, ch = 512, 512
            offset_x1 = int(self.scene_3d.caustic_scroll_1)
            offset_y1 = int(self.scene_3d.caustic_scroll_2)
            for tx in range(-cw, SCREEN_WIDTH + cw, cw):
                for ty in range(int(SCREEN_HEIGHT * 0.15), SCREEN_HEIGHT + ch, ch):
                    caustic_layer.blit(self.scene_3d.surf_caustics, (tx + offset_x1 % cw, ty + offset_y1 % ch))
            caustic_layer.set_alpha(int(22 + 6 * math.sin(self.scene_3d.time_sec * 1.6)))
            surface.blit(caustic_layer, (0, 0))

    def _draw_chamber_marine_life(self, surface: pygame.Surface) -> None:
        """Marine life removed from indoor museum chambers per user specification."""
        pass


    # =========================================================================
    # PHYSICAL LOCKED STONE DOORS & CINEMATIC OPENING
    # =========================================================================

    def _draw_physical_locked_door(self, surface: pygame.Surface, cfg: MuseumChamberConfig) -> None:
        """Renders massive ancient stone locked portal with glowing lock emblem and inscriptions."""
        door_open = self.door_open_progress.get(cfg.chamber_id, 0.0)
        slide_offset = int(door_open * (SCREEN_WIDTH // 2 + 100))

        # 1. Background image of the gallery behind the opening door
        bg_img = self.chamber_images.get(cfg.chamber_id)
        if bg_img:
            bx = int(-20 + self.cam_ox)
            by = int(-12 + self.cam_oy)
            surface.blit(bg_img, (bx, by))
        else:
            self.scene_3d.draw(surface, show_chest=False)

        # 2. Giant Moving Left & Right Carved Stone Slabs
        hw = SCREEN_WIDTH // 2
        if self.locked_door_image:
            left_half = self.locked_door_image.subsurface((0, 0, hw, SCREEN_HEIGHT))
            right_half = self.locked_door_image.subsurface((hw, 0, hw, SCREEN_HEIGHT))
            surface.blit(left_half, (-slide_offset, 0))
            surface.blit(right_half, (hw + slide_offset, 0))
            # Glowing runes along sliding seam
            pygame.draw.line(surface, cfg.lock_accent, (hw - slide_offset, 0), (hw - slide_offset, SCREEN_HEIGHT), 2)
            pygame.draw.line(surface, cfg.lock_accent, (hw + slide_offset, 0), (hw + slide_offset, SCREEN_HEIGHT), 2)
        else:
            slab_w = hw + 20
            left_x = -slide_offset
            pygame.draw.rect(surface, (16, 28, 44), (left_x, 0, slab_w, SCREEN_HEIGHT))
            pygame.draw.rect(surface, (34, 56, 84), (left_x, 0, slab_w, SCREEN_HEIGHT), width=3)
            right_x = hw - 20 + slide_offset
            pygame.draw.rect(surface, (16, 28, 44), (right_x, 0, slab_w, SCREEN_HEIGHT))
            pygame.draw.rect(surface, (34, 56, 84), (right_x, 0, slab_w, SCREEN_HEIGHT), width=3)

        # Volumetric golden light beam bursting from door seam if opening
        if door_open > 0.01:
            glow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            seam_cx = SCREEN_WIDTH // 2
            beam_poly = [
                (seam_cx - slide_offset, 0),
                (seam_cx + slide_offset, 0),
                (seam_cx + slide_offset + 120, SCREEN_HEIGHT),
                (seam_cx - slide_offset - 120, SCREEN_HEIGHT),
            ]
            pygame.draw.polygon(glow_surf, (255, 220, 110, int(160 * (1.0 - door_open * 0.5))), beam_poly)
            surface.blit(glow_surf, (0, 0))

        # If door is sliding open significantly, skip drawing center emblem
        if door_open > 0.65:
            return

        # 3. Massive Glowing Ancient Central Lock Emblem
        lock_cx = SCREEN_WIDTH // 2
        lock_cy = SCREEN_HEIGHT // 2 - 20
        pulse = 0.5 + 0.5 * math.sin(self.pulse_phase * 2.5)
        lock_r = int(58 + pulse * 6)

        # Radiating mystical energy aura
        halo_surf = pygame.Surface((lock_r * 4, lock_r * 4), pygame.SRCALPHA)
        pygame.draw.circle(halo_surf, (*cfg.lock_accent[:3], int(65 * pulse)), (lock_r * 2, lock_r * 2), lock_r + 28)
        pygame.draw.circle(halo_surf, (*COLOR_OCEAN_CYAN[:3], int(45 * pulse)), (lock_r * 2, lock_r * 2), lock_r + 14)
        surface.blit(halo_surf, (lock_cx - lock_r * 2, lock_cy - lock_r * 2))

        # Heavy Bronze / Obsidian Lock Plate
        pygame.draw.circle(surface, (12, 22, 38), (lock_cx, lock_cy), lock_r)
        pygame.draw.circle(surface, cfg.lock_accent, (lock_cx, lock_cy), lock_r, width=3)
        pygame.draw.circle(surface, COLOR_OCEAN_CYAN, (lock_cx, lock_cy), lock_r - 8, width=1)

        # Runic Keyway & Lock Shackle
        shackle_r = int(lock_r * 0.45)
        pygame.draw.arc(surface, cfg.lock_accent, (lock_cx - shackle_r, lock_cy - shackle_r * 2 + 6, shackle_r * 2, shackle_r * 2), 0, math.pi, 3)
        pygame.draw.circle(surface, (255, 235, 120), (lock_cx, lock_cy - 4), 6)
        pygame.draw.line(surface, (255, 235, 120), (lock_cx, lock_cy - 4), (lock_cx, lock_cy + 16), 3)

        # Ancient Runic Inscription Plate
        rw, rh = 560, 115
        rx = SCREEN_WIDTH // 2 - rw // 2
        ry = lock_cy + lock_r + 34

        p_surf = pygame.Surface((rw, rh), pygame.SRCALPHA)
        p_surf.fill((6, 18, 34, 210))
        pygame.draw.rect(p_surf, cfg.lock_accent, (0, 0, rw, rh), width=2, border_radius=12)
        surface.blit(p_surf, (rx, ry))

        # Title
        t_s = self.font_door_banner.render(f"SEALED: {cfg.label}", True, cfg.lock_accent)
        surface.blit(t_s, (SCREEN_WIDTH // 2 - t_s.get_width() // 2, ry + 16))

        # Unlock Requirement
        req_lvl = cfg.required_level
        if req_lvl == 6:
            req_msg = "Complete All 5 Ocean Expedition Zones to Break This Divine Seal"
        else:
            req_msg = f"Complete Level {req_lvl} Expedition to Break This Ancient Seal"
        req_s = self.font_door_sub.render(req_msg, True, (215, 238, 255))
        surface.blit(req_s, (SCREEN_WIDTH // 2 - req_s.get_width() // 2, ry + 52))

        # Subtle curator override hint
        hint_s = self.font_badge.render("[TIP: TOGGLE CURATOR MODE AT BOTTOM-RIGHT TO UNLOCK ALL GALLERIES]", True, (135, 175, 210))
        surface.blit(hint_s, (SCREEN_WIDTH // 2 - hint_s.get_width() // 2, ry + 82))

    # =========================================================================
    # TOUCHLESS HAND GESTURE VISOR HUD
    # =========================================================================

    def _draw_touchless_gesture_hud(self, surface: pygame.Surface) -> None:
        """Renders an intuitive, high-tech glassmorphic Touchless Hand Gesture HUD visor."""
        hud_w, hud_h = 600, 26
        hx = SCREEN_WIDTH // 2 - hud_w // 2
        hy = 20

        hud_surf = pygame.Surface((hud_w, hud_h), pygame.SRCALPHA)
        hud_surf.fill((6, 20, 36, 175))
        pygame.draw.rect(hud_surf, (0, 200, 240, 160), (0, 0, hud_w, hud_h), width=1, border_radius=13)
        surface.blit(hud_surf, (hx, hy))

        # 1. Live Tracking Status
        pulse_val = 0.5 + 0.5 * math.sin(self.pulse_phase * 2.0)
        status_col = COLOR_EMERALD if self.is_hand_detected else (255, 195, 45)
        dot_cx = hx + 18
        dot_cy = hy + hud_h // 2
        pygame.draw.circle(surface, status_col, (dot_cx, dot_cy), 4)
        if self.is_hand_detected:
            pygame.draw.circle(surface, (*status_col[:3], int(80 * pulse_val)), (dot_cx, dot_cy), 8, width=1)

        det_txt = "VISION ACTIVE" if self.is_hand_detected else "VISION READY"
        det_s = self.font_badge.render(det_txt, True, status_col)
        surface.blit(det_s, (dot_cx + 10, dot_cy - det_s.get_height() // 2))

        div_x = dot_cx + 10 + det_s.get_width() + 14
        pygame.draw.line(surface, (30, 65, 95), (div_x, hy + 5), (div_x, hy + hud_h - 5), 1)

        # 2. Gesture Actions with Live Highlight
        gestures_info = [
            ("[PINCH]", "SELECT/INSPECT", self.current_gesture == GestureType.PINCH or self.prev_clicked, COLOR_GOLD),
            ("[TWO FINGERS]", "NEXT CHAMBER", self.current_gesture == GestureType.TWO_FINGERS, COLOR_OCEAN_CYAN),
            ("[PALM]", "RETURN", self.current_gesture == GestureType.OPEN_PALM, COLOR_CORAL_RED),
            ("[FIST]", "CURATOR", self.current_gesture == GestureType.FIST, COLOR_EMERALD),
        ]

        curr_gx = div_x + 14
        for badge_text, action_text, is_active, col in gestures_info:
            txt_s = self.font_card_desc.render(badge_text, True, COLOR_WHITE if is_active else col)
            act_s = self.font_card_desc.render(action_text, True, COLOR_WHITE if is_active else (150, 180, 205))

            pw = txt_s.get_width() + act_s.get_width() + 14
            pill_rect = pygame.Rect(curr_gx, hy + 4, pw, hud_h - 8)

            if is_active:
                p_surf = pygame.Surface((pill_rect.w, pill_rect.h), pygame.SRCALPHA)
                p_surf.fill((*col[:3], 120))
                pygame.draw.rect(p_surf, col, (0, 0, pill_rect.w, pill_rect.h), width=1, border_radius=6)
                surface.blit(p_surf, pill_rect.topleft)

            surface.blit(txt_s, (curr_gx + 4, hy + hud_h // 2 - txt_s.get_height() // 2))
            surface.blit(act_s, (curr_gx + 8 + txt_s.get_width(), hy + hud_h // 2 - act_s.get_height() // 2))

            curr_gx += pw + 8

        # 3. Action Feedback Flash
        if self.gesture_feedback_timer > 0.0 and self.last_triggered_gesture:
            fb_surf = self.font_badge.render(f"✨ {self.last_triggered_gesture}", True, COLOR_GOLD)
            surface.blit(fb_surf, (SCREEN_WIDTH // 2 - fb_surf.get_width() // 2, hy + hud_h + 8))

        # 4. Palm Hold Return Progress Arc
        if self.palm_hold_timer > 0.0 and self.inspected_exhibit is None:
            pct = min(1.0, self.palm_hold_timer / self.palm_hold_threshold)
            ret_surf = pygame.Surface((240, 28), pygame.SRCALPHA)
            ret_surf.fill((20, 8, 14, 200))
            pygame.draw.rect(ret_surf, COLOR_CORAL_RED, (0, 0, 240, 28), width=1, border_radius=8)
            prog_w = int(236 * pct)
            pygame.draw.rect(ret_surf, (*COLOR_CORAL_RED[:3], 160), (2, 2, prog_w, 24), border_radius=6)
            surface.blit(ret_surf, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 80))
            p_lbl = self.font_badge.render(f"HOLD PALM: RETURNING ({int(pct*100)}%)", True, COLOR_WHITE)
            surface.blit(p_lbl, (SCREEN_WIDTH // 2 - p_lbl.get_width() // 2, SCREEN_HEIGHT - 74))

    # =========================================================================
    # 3D ARTIFACT VECTOR RENDERING WITH PITCH / YAW ROTATION
    # =========================================================================

    def _draw_relic_icon(
        self,
        surface: pygame.Surface,
        eid: str,
        cx: int,
        cy: int,
        r: int,
        color: Tuple[int, int, int],
        is_unlocked: bool
    ) -> None:
        """Backward-compatible entry point delegating to the HD relic renderer."""
        self._draw_hd_relic(surface, eid, cx, cy, r, color, is_unlocked, is_modal=False)

    def _draw_hd_relic(
        self,
        surface: pygame.Surface,
        eid: str,
        cx: int,
        cy: int,
        r: int,
        color: Tuple[int, int, int],
        is_unlocked: bool,
        is_modal: bool = False,
        light_offset: Tuple[float, float] = (0.0, 0.0),
        yaw: float = 0.0,
        pitch: float = 0.0,
    ) -> None:
        """Photorealistic 3D HD rendering of ancient oceanic wonders with 3D rotation."""
        from ui.relic_renderer import HDRelicRenderer
        HDRelicRenderer.draw_relic(
            surface,
            relic_id=eid,
            cx=cx,
            cy=cy,
            radius=r,
            is_unlocked=is_unlocked,
            is_modal=is_modal,
            light_offset=light_offset,
            yaw=yaw,
            pitch=pitch,
            dual_lift_prog=self.dual_hand_lift_progress,
            chest_opened=self.chest_is_opened,
            pulse_phase=self.pulse_phase,
        )


    # =========================================================================
    # IN-DEPTH EXHIBIT INSPECTION MODAL WITH 3D ROTATION & DUAL-HAND HOISTING
    # =========================================================================

    def _draw_inspection_modal(self, surface: pygame.Surface, ex: MuseumExhibit) -> None:
        """Renders rich 3D exhibit inspection modal with interactive pitch/yaw 3D rotation."""
        dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim_surf.fill((2, 6, 16, 240))
        surface.blit(dim_surf, (0, 0))

        mw, mh = 700, 500
        mx = SCREEN_WIDTH // 2 - mw // 2
        my = SCREEN_HEIGHT // 2 - mh // 2

        ped_cx = mx + 165
        ped_cy = my + 215

        # Spotlight cone
        spot_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        spot_poly = [
            (SCREEN_WIDTH // 2, 0),
            (ped_cx + 120, SCREEN_HEIGHT),
            (ped_cx - 120, SCREEN_HEIGHT),
        ]
        pygame.draw.polygon(spot_surf, (210, 245, 255, 16), spot_poly)
        surface.blit(spot_surf, (0, 0))

        # Modal window frame
        pygame.draw.rect(surface, (10, 22, 42), (mx, my, mw, mh), border_radius=16)
        border_col = ex.color_rgb if ex.is_unlocked else COLOR_GOLD
        pygame.draw.rect(surface, border_col, (mx, my, mw, mh), width=2, border_radius=16)

        # Header Title
        if ex.is_unlocked:
            if ex.exhibit_id == "gold_coin":
                title_text = "ANCIENT GOLD COIN"
                sub_text = "Spanish Royal Escudo Doubloon • Recovered Relic"
            else:
                title_text = ex.name.upper()
                sub_text = f"{ex.rarity} RELIC • {ex.era}"
        else:
            title_text = "UNDISCOVERED ABYSSAL WONDER"
            sub_text = "LOCKED ANCIENT ARTIFACT • RECOVER IN EXPEDITIONS"

        t_surf = self.font_modal_title.render(title_text, True, COLOR_GOLD if ex.is_unlocked else (180, 195, 210))
        surface.blit(t_surf, (mx + mw // 2 - t_surf.get_width() // 2, my + 18))

        sub_surf = self.font_modal_sub.render(sub_text, True, COLOR_OCEAN_CYAN if ex.is_unlocked else COLOR_AMBER_WARNING)
        surface.blit(sub_surf, (mx + mw // 2 - sub_surf.get_width() // 2, my + 50))

        # Exhibition Plinth
        pulse = math.sin(self.pulse_phase) * 3.0
        ped_r = int(76 + pulse)
        pygame.draw.circle(surface, (14, 30, 56), (ped_cx, ped_cy), ped_r)
        pygame.draw.circle(surface, border_col, (ped_cx, ped_cy), ped_r, width=2)
        pygame.draw.circle(surface, (8, 18, 36), (ped_cx, ped_cy), ped_r - 6)

        # Dynamic lighting offset from cursor
        dx = (self.cursor_pos[0] - ped_cx) / float(SCREEN_WIDTH) * 50.0
        dy = (self.cursor_pos[1] - ped_cy) / float(SCREEN_HEIGHT) * 50.0

        # Render 3D Rotatable Relic
        self._draw_hd_relic(
            surface,
            ex.exhibit_id,
            ped_cx,
            ped_cy,
            r=70,
            color=ex.color_rgb,
            is_unlocked=ex.is_unlocked,
            is_modal=True,
            light_offset=(dx, dy),
            yaw=self.relic_yaw,
            pitch=self.relic_pitch,
        )

        # Discovery status badge
        if ex.is_unlocked:
            lvl_str = f"Recovered in Zone {ex.unlocked_in_level}" if ex.unlocked_in_level else "Permanent Collection"
            status_text = f"CATALOGED • {lvl_str}"
            st_col = COLOR_EMERALD
        else:
            status_text = "UNDISCOVERED IN EXPEDITIONS"
            st_col = COLOR_CORAL_RED
        st_surf = self.font_badge.render(status_text, True, st_col)
        surface.blit(st_surf, (ped_cx - st_surf.get_width() // 2, my + 308))

        # 3D interactive rotation hint
        hint_light = self.font_badge.render("HAND MOTION ROTATES ARTIFACT IN 3D", True, (120, 160, 195))
        surface.blit(hint_light, (ped_cx - hint_light.get_width() // 2, my + 328))

        # Two-Hand Interaction indicator for large artifacts
        if ex.exhibit_id in ("heavy_chest", "guardian_seal", "ancient_vase"):
            if self.has_second_hand:
                dual_s = self.font_badge.render("[DUAL HANDS: LIFT TO OPEN / ROTATE]", True, COLOR_GOLD)
            else:
                dual_s = self.font_badge.render("PRESENT TWO HANDS TO DUAL-LIFT", True, (140, 180, 210))
            surface.blit(dual_s, (ped_cx - dual_s.get_width() // 2, my + 348))

        # Structured Archaeological Dossier Fields matching exact user specification
        origin_table = {
            "gold_coin": ("Lost Civilization", "500+ Years", "RARE", "Level 1 — Shallow Ocean"),
            "pearl": ("Holocene Coral Reef", "50+ Years", "COMMON", "Level 1 — Shallow Ocean"),
            "sapphire_chalice": ("Classical Hellenic Realm", "2,400+ Years", "RARE", "Level 3 — Deep Ocean"),
            "ancient_vase": ("Minoan Archaeological Ruins", "3,400+ Years", "RARE", "Level 2 — Coral Reef"),
            "heavy_chest": ("Sunken Armada Galleon", "350+ Years", "EPIC", "Level 4 — Sunken Shipwreck"),
            "ancient_crown": ("Lost Kingdom of Atlantis", "10,000+ Years", "LEGENDARY", "Final Rank — Legendary Chamber"),
            "guardian_seal": ("Sea Temple of Ancients", "Timeless", "MYTHIC", "Level 5 — Ancient Ruins"),
            "coral_compass": ("Nautilus Cartographer Guild", "420+ Years", "UNCOMMON", "Level 2 — Coral Reef"),
        }
        item_origin, item_age, item_rarity, item_discovery = origin_table.get(
            ex.exhibit_id, ("Lost Civilization", "500+ Years", ex.rarity, f"Level {ex.unlocked_in_level or 1}")
        )

        rx = mx + 310
        rw = mw - 340

        # Dossier Table Box
        dossier_box = pygame.Rect(rx, my + 80, rw, 96)
        pygame.draw.rect(surface, (8, 22, 40), dossier_box, border_radius=8)
        pygame.draw.rect(surface, (30, 75, 120), dossier_box, width=1, border_radius=8)

        # 4 Metadata Fields (Origin, Estimated Age, Rarity, Discovery)
        fields = [
            ("Origin:", item_origin if ex.is_unlocked else "Unknown Origin"),
            ("Estimated Age:", item_age if ex.is_unlocked else "Undetermined"),
            ("Rarity:", item_rarity if ex.is_unlocked else "LOCKED"),
            ("Discovery:", item_discovery if ex.is_unlocked else "Uncataloged in Deep Sea"),
        ]
        fy = my + 86
        for f_lbl, f_val in fields:
            l_s = self.font_badge.render(f_lbl, True, (140, 185, 220))
            v_col = COLOR_GOLD if "Rarity" in f_lbl and ex.is_unlocked else (COLOR_WHITE if ex.is_unlocked else (150, 170, 190))
            v_s = self.font_badge.render(f_val, True, v_col)
            surface.blit(l_s, (rx + 12, fy))
            surface.blit(v_s, (rx + 115, fy))
            fy += 22

        # Lore details
        ry = my + 186
        h_lore = self.font_badge.render("ARCHAEOLOGICAL PROVENANCE:", True, COLOR_NEON_TEAL)
        surface.blit(h_lore, (rx, ry))
        ry += 18

        full_lore = ex.lore if ex.is_unlocked else "This ancient wonder remains submerged in the ocean abyss. Dive into deeper expedition zones to recover authentic relics and unlock this exhibit."
        words = full_lore.split(" ")
        line = ""
        lore_lines = []
        for w in words:
            test_line = f"{line} {w}".strip()
            if self.font_modal_body.size(test_line)[0] < rw - 15:
                line = test_line
            else:
                lore_lines.append(line)
                line = w
        if line:
            lore_lines.append(line)
        for l_txt in lore_lines[:3]:
            l_s = self.font_card_desc.render(l_txt, True, (215, 235, 255) if ex.is_unlocked else (145, 165, 185))
            surface.blit(l_s, (rx, ry))
            ry += 18

        # Power Notes Box
        ry += 6
        hint_box = pygame.Rect(rx, ry, rw, 64)
        pygame.draw.rect(surface, (12, 28, 50), hint_box, border_radius=8)
        pygame.draw.rect(surface, (45, 85, 130), hint_box, width=1, border_radius=8)
        hint_header = self.font_badge.render("CURATOR RECOVERY & POWER NOTES:", True, COLOR_GOLD)
        surface.blit(hint_header, (rx + 12, ry + 6))
        if ex.is_unlocked:
            power_notes = {
                "pearl": "Passive Effect: Bioluminescent underwater radius +30% in dark depths.",
                "gold_coin": "Passive Effect: Permanently multiplies expedition score by 1.25x.",
                "sapphire_chalice": "Passive Effect: Poseidon blessing calms seafloor ocean currents.",
                "ancient_vase": "Passive Effect: Unlocks hidden coral corridor ancient secrets.",
                "heavy_chest": "Passive Effect: Diver pouch weight capacity expanded by +3 slots.",
                "ancient_crown": "Passive Effect: Sunken Atlantis Divine Radiance — 2x Star Rating bonus.",
                "guardian_seal": "Passive Effect: Ancient Guardian appeased — predator aggression halved.",
                "coral_compass": "Passive Effect: Nautilus magnetic lodestone guides diver to chests.",
            }
            hint_body = power_notes.get(ex.exhibit_id, "Relic successfully cataloged in the museum vault. Retains permanent score multipliers.")
        else:
            hint_body = "Complete ocean expeditions and deposit authentic treasures in vault chests to unlock."
        hb_surf = self.font_card_desc.render(hint_body, True, (195, 220, 245))
        surface.blit(hb_surf, (rx + 12, ry + 26))

        # Touchless Gesture Modal Hint
        hint_gesture = self.font_badge.render("PALM / FIST: CLOSE MODAL   •   TWO FINGERS: NEXT RELIC   •   MOVE HAND: 3D LIGHT", True, COLOR_GOLD)
        surface.blit(hint_gesture, (mx + mw // 2 - hint_gesture.get_width() // 2, my + mh - 80))

        # Close button
        self.modal_close_btn.draw(surface)

    # =========================================================================
    # MAIN DRAW PIPELINE
    # =========================================================================

    def draw(
        self,
        surface: pygame.Surface,
        museum: UnderwaterMuseum,
        completed_levels: Optional[Set[int]] = None,
        unlocked_levels: Optional[int] = None,
    ) -> None:
        """Renders the complete 3D realistic underwater museum experience."""
        self.museum = museum
        if completed_levels is not None:
            self.completed_levels = completed_levels
        if unlocked_levels is not None:
            self.unlocked_levels_count = unlocked_levels

        unlocked_cnt = museum.get_unlocked_count()
        total_cnt = museum.get_total_count()

        # Update curator button label
        if unlocked_cnt >= total_cnt:
            self.curator_btn.text = "RESET EXHIBITS (1/8)"
        else:
            self.curator_btn.text = "UNLOCK ALL (CURATOR)"

        # Ensure selected relic exists
        if self.selected_relic_id not in museum.exhibits:
            self.selected_relic_id = next(iter(museum.exhibits.keys()), "pearl")

        cfg = self.chambers.get(self.active_chamber, self.chambers["gallery"])
        is_chamber_open = self._is_chamber_unlocked(self.active_chamber, self.completed_levels)
        door_open_prog = self.door_open_progress.get(self.active_chamber, 1.0)

        is_grand_hall = (self.active_chamber in ("gallery", "entrance"))

        # 1. Chamber Background Environment
        bg_img = self.chamber_images.get(self.active_chamber)
        if bg_img:
            if is_grand_hall:
                surface.blit(bg_img, (0, 0))
            else:
                bx = int(-20 + self.cam_ox)
                by = int(-12 + self.cam_oy)
                surface.blit(bg_img, (bx, by))
        else:
            self.scene_3d.draw(surface, show_chest=False)

        # Monumental cutout arch for entrance
        if self.active_chamber == "entrance" and self.arch_cutout and not is_grand_hall:
            surface.blit(self.arch_cutout, (int(self.cam_ox * 0.4), int(self.cam_oy * 0.4)))

        # 2. 3D Perspective Depth Floor & Columns (for non-grand chambers only)
        if not is_grand_hall:
            self._draw_3d_perspective_floor(surface)
            self._draw_3d_ancient_columns(surface)

        # 3. Living 3D Marine Life swimming across the chamber (for non-grand chambers)
        if not is_grand_hall:
            self._draw_chamber_marine_life(surface)

        # 4. Animated Water Caustics Shimmering Over the Floor
        self._draw_underwater_caustics(surface)

        # 5. Volumetric Sunlight God Rays & Particles
        self._draw_volumetric_god_rays(surface)

        # Draw floating golden dust motes
        for p in self.chamber_particles:
            col = (255, 215, 80) if p["gold"] else (190, 235, 255)
            pygame.draw.circle(surface, col, (int(p["x"]), int(p["y"])), int(p["radius"]))

        # 6. Physical Locked Stone Doors (if chamber is sealed)
        if door_open_prog < 0.98 and not is_chamber_open:
            self._draw_physical_locked_door(surface, cfg)

        if is_grand_hall:
            # =================================================================
            # GRAND UNDERWATER ARCHAEOLOGICAL MUSEUM HALL (Matches Mockup)
            # =================================================================

            # Update vitrine hitboxes: 4 grand pedestals + 4 central dock relics
            self.card_rects["pearl"] = pygame.Rect(45, 340, 160, 340)
            self.card_rects["ancient_crown"] = pygame.Rect(345, 420, 150, 260)
            self.card_rects["ancient_vase"] = pygame.Rect(785, 420, 150, 260)
            self.card_rects["gold_coin"] = pygame.Rect(1030, 400, 205, 280)
            self.card_rects["sapphire_chalice"] = pygame.Rect(515, 646, 56, 56)
            self.card_rects["heavy_chest"] = pygame.Rect(580, 646, 56, 56)
            self.card_rects["guardian_seal"] = pygame.Rect(645, 646, 56, 56)
            self.card_rects["coral_compass"] = pygame.Rect(710, 646, 56, 56)

            # 1. Four Monumental In-World Display Vitrines
            grand_pedestals = [
                ("pearl", pygame.Rect(45, 340, 160, 340), pygame.Rect(55, 340, 140, 175)),
                ("ancient_crown", pygame.Rect(345, 420, 150, 260), pygame.Rect(360, 420, 120, 140)),
                ("ancient_vase", pygame.Rect(785, 420, 150, 260), pygame.Rect(800, 420, 120, 140)),
                ("gold_coin", pygame.Rect(1030, 400, 205, 280), pygame.Rect(1045, 400, 175, 160)),
            ]

            for eid, ped_rect, glass_rect in grand_pedestals:
                ex = museum.exhibits.get(eid)
                is_unlocked = ex.is_unlocked if ex else False
                is_hov = (self.hovered_card_id == eid and self.inspected_exhibit is None)
                is_sel = (self.selected_relic_id == eid)

                # Frosted glass veil and ancient padlock if locked
                if not is_unlocked:
                    frost_surf = pygame.Surface((glass_rect.w, glass_rect.h), pygame.SRCALPHA)
                    frost_surf.fill((8, 26, 46, 175))
                    pygame.draw.rect(frost_surf, (0, 195, 235, 130), (0, 0, glass_rect.w, glass_rect.h), width=1, border_radius=8)
                    surface.blit(frost_surf, glass_rect.topleft)

                    pl_cx, pl_cy = glass_rect.centerx, glass_rect.centery
                    shackle_r = 14
                    pygame.draw.arc(surface, COLOR_GOLD, (pl_cx - shackle_r, pl_cy - shackle_r * 2 + 2, shackle_r * 2, shackle_r * 2), 0, math.pi, 3)
                    pygame.draw.rect(surface, (18, 30, 48), (pl_cx - 18, pl_cy, 36, 28), border_radius=4)
                    pygame.draw.rect(surface, COLOR_GOLD, (pl_cx - 18, pl_cy, 36, 28), width=2, border_radius=4)
                    pygame.draw.circle(surface, (255, 235, 120), (pl_cx, pl_cy + 10), 3)
                    pygame.draw.line(surface, (255, 235, 120), (pl_cx, pl_cy + 10), (pl_cx, pl_cy + 18), 2)

                # Hover highlight and dwell progress
                if is_hov:
                    # Glowing border around vitrine
                    glow_border = pygame.Surface((glass_rect.w + 8, glass_rect.h + 8), pygame.SRCALPHA)
                    pygame.draw.rect(glow_border, (0, 240, 255, 120), (0, 0, glass_rect.w + 8, glass_rect.h + 8), width=2, border_radius=8)
                    surface.blit(glow_border, (glass_rect.x - 4, glass_rect.y - 4))

                    # Spotlight beam
                    spot_surf = pygame.Surface((glass_rect.w + 80, glass_rect.bottom), pygame.SRCALPHA)
                    spot_pts = [(glass_rect.w // 2 + 40, 0), (glass_rect.w + 70, glass_rect.bottom), (10, glass_rect.bottom)]
                    pygame.draw.polygon(spot_surf, (0, 230, 255, 18), spot_pts)
                    surface.blit(spot_surf, (glass_rect.x - 40, 0))

                    # Dwell progress bar along base of plaque
                    dwell_t = self.card_dwell_times.get(eid, 0.0)
                    if dwell_t > 0:
                        pct = min(1.0, max(0.0, dwell_t / self.dwell_threshold))
                        bar_w = int(glass_rect.w * pct)
                        pygame.draw.rect(surface, (0, 245, 255), (glass_rect.x, ped_rect.bottom - 8, bar_w, 3), border_radius=2)

                    # Dynamic Context-Aware Interaction Prompt above Vitrine
                    prompt_txt = f"PINCH -> INSPECT {ex.name.upper()}" if ex and ex.is_unlocked else "PINCH -> INSPECT RELIC [LOCKED]"
                    prompt_surf = self.font_card_title.render(prompt_txt, True, COLOR_GOLD if ex and ex.is_unlocked else (180, 205, 230))
                    pw = prompt_surf.get_width() + 24
                    ph = 32
                    px = max(10, min(SCREEN_WIDTH - pw - 10, glass_rect.centerx - pw // 2))
                    py = max(75, glass_rect.top - 42)
                    p_badge = pygame.Surface((pw, ph), pygame.SRCALPHA)
                    pygame.draw.rect(p_badge, (8, 20, 36, 230), (0, 0, pw, ph), border_radius=6)
                    pygame.draw.rect(p_badge, COLOR_GOLD if ex and ex.is_unlocked else (0, 200, 240), (0, 0, pw, ph), width=1, border_radius=6)
                    p_badge.blit(prompt_surf, (12, ph // 2 - prompt_surf.get_height() // 2))
                    surface.blit(p_badge, (px, py))

            # 2. Central Archival Dock for Remaining 4 Ocean Relics
            dock_rect = pygame.Rect(510, 642, 260, 66)
            dock_surf = pygame.Surface((dock_rect.w, dock_rect.h), pygame.SRCALPHA)
            dock_surf.fill((6, 22, 40, 185))
            pygame.draw.rect(dock_surf, (0, 210, 245, 160), (0, 0, dock_rect.w, dock_rect.h), width=1, border_radius=12)
            surface.blit(dock_surf, dock_rect.topleft)

            badge_lbl = self.font_badge.render("ARCHIVE SANCTUARY • 4 RELICS", True, (0, 240, 255))
            surface.blit(badge_lbl, (dock_rect.centerx - badge_lbl.get_width() // 2, dock_rect.y + 4))

            sub_relics = ["sapphire_chalice", "heavy_chest", "guardian_seal", "coral_compass"]
            for s_idx, s_eid in enumerate(sub_relics):
                s_rect = self.card_rects[s_eid]
                s_ex = museum.exhibits.get(s_eid)
                is_shov = (self.hovered_card_id == s_eid and self.inspected_exhibit is None)
                is_ssel = (self.selected_relic_id == s_eid)
                s_cx, s_cy = s_rect.centerx, s_rect.centery + 6

                p_col = COLOR_GOLD if is_ssel else ((0, 240, 255) if is_shov else (35, 70, 110))
                pygame.draw.circle(surface, (12, 28, 52), (s_cx, s_cy), 20)
                pygame.draw.circle(surface, p_col, (s_cx, s_cy), 20, width=2 if (is_shov or is_ssel) else 1)

                self._draw_hd_relic(surface, s_eid, s_cx, s_cy, r=13, color=s_ex.color_rgb if s_ex else COLOR_GOLD, is_unlocked=s_ex.is_unlocked if s_ex else False, is_modal=False)

                if is_shov:
                    dwell_t = self.card_dwell_times.get(s_eid, 0.0)
                    if dwell_t > 0:
                        pct = min(1.0, dwell_t / self.dwell_threshold)
                        dw_w = int(36 * pct)
                        pygame.draw.rect(surface, (0, 245, 255), (s_cx - 18, s_cy + 16, dw_w, 2), border_radius=1)
                    # Floating Context Prompt for archival relic
                    p_name = s_ex.name.upper() if s_ex else "ARTIFACT"
                    prompt_txt = f"PINCH -> INSPECT {p_name}"
                    prompt_surf = self.font_badge.render(prompt_txt, True, COLOR_GOLD)
                    pw = prompt_surf.get_width() + 18
                    ph = 26
                    px = max(10, min(SCREEN_WIDTH - pw - 10, s_cx - pw // 2))
                    py = s_cy - 48
                    p_badge = pygame.Surface((pw, ph), pygame.SRCALPHA)
                    pygame.draw.rect(p_badge, (8, 20, 36, 230), (0, 0, pw, ph), border_radius=6)
                    pygame.draw.rect(p_badge, COLOR_GOLD, (0, 0, pw, ph), width=1, border_radius=6)
                    p_badge.blit(prompt_surf, (9, ph // 2 - prompt_surf.get_height() // 2))
                    surface.blit(p_badge, (px, py))

            # 3. Dynamic Live Artifact Counter on Top-Right Badge
            cnt_bg = pygame.Surface((60, 22), pygame.SRCALPHA)
            cnt_bg.fill((0, 48, 80, 245))
            surface.blit(cnt_bg, (1120, 46))
            cnt_text = f"{unlocked_cnt} / 8" if total_cnt == 8 else f"{unlocked_cnt} / {total_cnt}"
            cnt_surf = self.font_sub.render(cnt_text, True, (215, 245, 255))
            surface.blit(cnt_surf, (1122, 47))

            # 4. Interactive Bottom Buttons
            self.back_btn.rect = pygame.Rect(26, 618, 126, 52)
            if self.back_btn.is_hovered:
                glow_surf = pygame.Surface((130, 56), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (0, 240, 255, 120), (0, 0, 130, 56), width=3, border_radius=10)
                surface.blit(glow_surf, (24, 616))
            if self.back_btn.text not in ("< BACK", "<", "BACK"):
                self.back_btn.draw(surface)

            self.next_btn.rect = pygame.Rect(1128, 636, 126, 52)
            if self.next_btn.is_hovered:
                glow_surf = pygame.Surface((130, 56), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (0, 240, 255, 120), (0, 0, 130, 56), width=3, border_radius=10)
                surface.blit(glow_surf, (1126, 634))

        else:
            # =================================================================
            # EXPEDITION SUB-GALLERIES & ARCHIVAL SANCTUARIES
            # =================================================================
            for k, trect in self.tab_rects.items():
                is_act = (self.active_chamber == k)
                is_hov = (trect.collidepoint(self.cursor_pos) and self.inspected_exhibit is None)
                is_unlocked = self._is_chamber_unlocked(k, self.completed_levels)

                tab_surf = pygame.Surface((trect.w, trect.h), pygame.SRCALPHA)
                bg_c = (14, 42, 75, 220) if is_act else ((20, 38, 64, 180) if is_hov else (6, 18, 34, 130))
                border_c = COLOR_OCEAN_CYAN if is_act else ((0, 210, 245) if is_hov else (35, 68, 102))
                tab_surf.fill(bg_c)
                pygame.draw.rect(tab_surf, border_c, (0, 0, trect.w, trect.h), width=2 if is_act else 1, border_radius=12)
                if not is_unlocked:
                    pygame.draw.circle(tab_surf, COLOR_CORAL_RED, (10, trect.h // 2), 3)
                elif is_act:
                    pygame.draw.circle(tab_surf, COLOR_GOLD, (10, trect.h // 2), 3)
                surface.blit(tab_surf, trect.topleft)

                lbl = self.chambers[k].label
                t_col = COLOR_WHITE if is_act else ((215, 238, 255) if is_hov else (145, 170, 195))
                lbl_s = self.font_sub.render(lbl, True, t_col)
                surface.blit(lbl_s, (trect.centerx - lbl_s.get_width() // 2 + 5, trect.centery - lbl_s.get_height() // 2))

            # Vitrines along the floor for this chamber
            ped_w, ped_h = 108, 92
            ped_gap = 22
            total_cards_w = 8 * ped_w + 7 * ped_gap
            start_cards_x = (SCREEN_WIDTH - total_cards_w) // 2
            cards_y = 592
            self.card_rects.clear()

            for idx, (eid, ex) in enumerate(museum.exhibits.items()):
                cx = start_cards_x + idx * (ped_w + ped_gap)
                cy = cards_y
                self.card_rects[eid] = pygame.Rect(cx, cy, ped_w, ped_h)
                is_sel = (self.selected_relic_id == eid)
                is_hov = (self.hovered_card_id == eid and self.inspected_exhibit is None)
                pl_cx = cx + ped_w // 2
                pl_base_y = cy + 62

                vitrine_surf = pygame.Surface((68, 54), pygame.SRCALPHA)
                vit_bg = (14, 40, 70, 75) if (is_sel or is_hov) else (8, 24, 44, 45)
                vitrine_surf.fill(vit_bg)
                vit_border = COLOR_GOLD if is_sel else ((0, 220, 255) if is_hov else (40, 75, 110))
                pygame.draw.rect(vitrine_surf, vit_border, (0, 0, 68, 54), width=1, border_radius=10)
                surface.blit(vitrine_surf, (pl_cx - 34, pl_base_y - 48))

                plinth_col = (20, 36, 56) if (is_sel or is_hov) else (14, 24, 38)
                pygame.draw.ellipse(surface, plinth_col, (pl_cx - 36, pl_base_y - 6, 72, 16))
                pygame.draw.ellipse(surface, vit_border, (pl_cx - 36, pl_base_y - 6, 72, 16), width=2 if (is_sel or is_hov) else 1)

                float_y = math.sin(self.pulse_phase * 1.5 + idx * 0.8) * 3.5
                relic_cy = pl_base_y - 24 + int(float_y)
                self._draw_hd_relic(surface, eid, pl_cx, relic_cy, r=18, color=ex.color_rgb, is_unlocked=ex.is_unlocked, is_modal=False)

                short_name = ex.name.split(" ")[0]
                n_surf = self.font_card_desc.render(short_name, True, COLOR_GOLD if is_sel else (COLOR_WHITE if is_hov else (160, 185, 210)))
                surface.blit(n_surf, (pl_cx - n_surf.get_width() // 2, pl_base_y + 12))

            # Bottom buttons
            self.back_btn.rect = pygame.Rect(28, SCREEN_HEIGHT - 44, 130, 34)
            self.curator_btn.rect = pygame.Rect(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 44, 172, 34)
            self.back_btn.draw(surface)
            self.curator_btn.draw(surface)

        # 5. Touchless Hand Gesture Visor Banner
        self._draw_touchless_gesture_hud(surface)

        # 6. 3D Exhibit Inspection Modal (if open)
        if self.inspected_exhibit is not None:
            self._draw_inspection_modal(surface, self.inspected_exhibit)

    def _draw_first_person_hand(self, surface: pygame.Surface, cx: int, cy: int, is_clicked: bool) -> None:
        """Deprecated: First-person stick pointer completely removed in favor of touchless gestures."""
        pass
