"""
Underwater Treasure Hunt - Level Environment & Progression System
Handles all 5 thematic levels, procedural parallax seabeds, swaying corals,
ancient ruins, shipwrecks, depth fog, and victory/defeat evaluation.
"""

import math
import os
import random
import time
from typing import Dict, List, Tuple, Optional
import numpy as np
import pygame

from config import (
    LEVELS,
    LevelConfig,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_DEEP_BLUE,
    COLOR_OCEAN_CYAN,
    COLOR_NEON_TEAL,
    COLOR_GOLD,
    COLOR_WHITE,
)
from hand_tracking.gesture_detector import GestureType
from game.treasure import TreasureManager
from game.enemy import MarineLifeManager
from game.particles import ParticleSystem
from game.player import Player
from game.collision import distance

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")

_PEDESTAL_TEX: Optional[pygame.Surface] = None
_KELP_TEX: Optional[pygame.Surface] = None
_SEAGRASS_TEX: Optional[pygame.Surface] = None

def _get_pedestal_texture() -> Optional[pygame.Surface]:
    global _PEDESTAL_TEX
    if _PEDESTAL_TEX is None:
        p = os.path.join(ASSETS_DIR, "ancient_stone_pedestal.png")
        if os.path.isfile(p):
            try:
                _PEDESTAL_TEX = pygame.image.load(p).convert_alpha()
            except Exception:
                pass
    return _PEDESTAL_TEX

def _get_kelp_texture() -> Optional[pygame.Surface]:
    global _KELP_TEX
    if _KELP_TEX is None:
        p = os.path.join(ASSETS_DIR, "ocean_kelp_frond.png")
        if os.path.isfile(p):
            try:
                _KELP_TEX = pygame.image.load(p).convert_alpha()
            except Exception:
                pass
    return _KELP_TEX

def _get_seagrass_texture() -> Optional[pygame.Surface]:
    global _SEAGRASS_TEX
    if _SEAGRASS_TEX is None:
        p = os.path.join(ASSETS_DIR, "ocean_seagrass.png")
        if os.path.isfile(p):
            try:
                _SEAGRASS_TEX = pygame.image.load(p).convert_alpha()
            except Exception:
                pass
    return _SEAGRASS_TEX

class AncientGesturePuzzle:
    """An ancient Atlantean stone pedestal in Level 5 requiring a gesture sequence to unlock."""
    def __init__(self, x: float = SCREEN_WIDTH - 240.0, y: float = SCREEN_HEIGHT - 130.0):
        self.x = x
        self.y = y
        self.radius = 70.0
        self.solved = False
        self.sequence = [GestureType.TWO_FINGERS, GestureType.OPEN_PALM, GestureType.PINCH]
        self.labels = ["SONAR ✌️", "CURRENT ✋", "PINCH 🤏"]
        self.current_step = 0
        self.pulse_phase = 0.0

    def check_gesture(self, gesture: GestureType, px: float, py: float) -> Tuple[bool, bool]:
        """
        Checks if player performed the next gesture in the sequence near the pedestal.
        Returns (solved_just_now, step_advanced).
        """
        if self.solved:
            return False, False
        if distance(px, py, self.x, self.y) <= (self.radius + 60.0):
            if gesture == self.sequence[self.current_step]:
                self.current_step += 1
                if self.current_step >= len(self.sequence):
                    self.solved = True
                    return True, True
                return False, True
        return False, False

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = int(self.x), int(self.y)
        self.pulse_phase += 0.05
        pulse = math.sin(self.pulse_phase)

        ped_tex = _get_pedestal_texture()
        if ped_tex:
            pw, ph = 96, 122
            # Seabed contact shadow
            sh_surf = pygame.Surface((pw + 20, 28), pygame.SRCALPHA)
            pygame.draw.ellipse(sh_surf, (5, 12, 22, 160), (0, 0, pw + 20, 28))
            surface.blit(sh_surf, (cx - (pw + 20) // 2, cy + 32))

            scaled_ped = pygame.transform.smoothscale(ped_tex, (pw, ph))
            # Runic glow shimmer
            if self.solved:
                glow_overlay = pygame.Surface(scaled_ped.get_size(), pygame.SRCALPHA)
                glow_overlay.fill((*COLOR_GOLD[:3], int(35 + 25 * pulse)))
                scaled_ped.blit(glow_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            surface.blit(scaled_ped, (cx - pw // 2, cy - ph // 2 + 10))

            # Glowing basin beacon
            b_alpha = int(140 + 70 * pulse) if not self.solved else int(200 + 55 * pulse)
            b_col = COLOR_GOLD if self.solved else COLOR_NEON_TEAL
            basin_surf = pygame.Surface((44, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(basin_surf, (*b_col[:3], b_alpha), (0, 0, 44, 20))
            surface.blit(basin_surf, (cx - 22, cy - ph // 2 + 12))
        else:
            # Fallback procedural base
            pygame.draw.rect(surface, (40, 55, 75), (cx - 45, cy - 25, 90, 50), border_radius=6)
            pygame.draw.rect(surface, (20, 35, 50), (cx - 45, cy - 25, 90, 50), width=2, border_radius=6)
            col = COLOR_GOLD if self.solved else COLOR_NEON_TEAL
            pygame.draw.circle(surface, col, (cx, cy - 15), 18, 2)

        # Draw glyph tablets
        font = pygame.font.SysFont("segoeui", 11, bold=True)
        for i, lbl in enumerate(self.labels):
            gx = cx - 75 + i * 52
            gy = cy - 75
            is_done = (i < self.current_step)
            is_active = (i == self.current_step and not self.solved)
            
            box_col = COLOR_GOLD if is_done else (COLOR_NEON_TEAL if is_active else (50, 70, 90))
            pygame.draw.rect(surface, (15, 25, 40, 220), (gx, gy, 48, 24), border_radius=5)
            pygame.draw.rect(surface, box_col, (gx, gy, 48, 24), width=1, border_radius=5)
            
            txt_surf = font.render(lbl, True, box_col)
            surface.blit(txt_surf, (gx + 24 - txt_surf.get_width() // 2, gy + 4))

        title_font = pygame.font.SysFont("segoeui", 12, bold=True)
        t_str = "VAULT UNLOCKED! 🏆" if self.solved else "ANCIENT PUZZLE"
        t_surf = title_font.render(t_str, True, COLOR_GOLD if self.solved else COLOR_WHITE)
        surface.blit(t_surf, (cx - t_surf.get_width() // 2, cy + 46))


class Seaweed:
    """Animated swaying photorealistic botanical underwater plant anchored to seabed."""
    def __init__(
        self,
        x: float,
        height: float,
        color: Tuple[int, int, int] = (25, 95, 60),
        plant_type: str = "kelp",
        flip_x: bool = False,
        base_y_offset: float = 0.0,
    ):
        self.x = x
        self.height = height
        self.color = color
        self.plant_type = plant_type
        self.flip_x = flip_x
        self.base_y_offset = base_y_offset
        self.sway_phase = random.uniform(0.0, math.pi * 2)
        self.sway_speed = random.uniform(0.9, 1.5)
        self.sway_amp = random.uniform(3.5, 6.5)

    def draw(self, surface: pygame.Surface, current_active: bool = False) -> None:
        t = time.time()
        extra_sway = 6.0 if current_active else 0.0
        
        raw_tex = _get_seagrass_texture() if self.plant_type == "seagrass" else _get_kelp_texture()
        if not raw_tex:
            raw_tex = _get_kelp_texture() or _get_seagrass_texture()

        if raw_tex:
            orig_w, orig_h = raw_tex.get_size()
            kh = int(self.height)
            kw = int(kh * (orig_w / orig_h))
            
            scaled = pygame.transform.smoothscale(raw_tex, (max(16, kw), max(24, kh)))
            if self.flip_x:
                scaled = pygame.transform.flip(scaled, True, False)
                
            # Realistic gentle sway angle (degrees)
            sway_deg = math.sin(t * self.sway_speed + self.sway_phase) * (self.sway_amp + extra_sway)
            
            # Rotate around root anchor (bottom center of plant)
            rotated = pygame.transform.rotate(scaled, sway_deg)
            rot_w, rot_h = rotated.get_size()
            
            # Anchor offset from center: (0, kh / 2 - 6)
            rad = math.radians(-sway_deg)
            ay = kh * 0.5 - 6.0
            rot_anchor_x = -ay * math.sin(rad)
            rot_anchor_y = ay * math.cos(rad)
            
            # Anchor position in rotated surface
            anchor_x = rot_w * 0.5 + rot_anchor_x
            anchor_y = rot_h * 0.5 + rot_anchor_y
            
            dest_x = int(self.x - anchor_x)
            dest_y = int(SCREEN_HEIGHT - self.base_y_offset - anchor_y)
            surface.blit(rotated, (dest_x, dest_y))
            return

        # Fallback procedural waving blade
        points = []
        segments = 7
        base_y = SCREEN_HEIGHT - self.base_y_offset
        for i in range(segments + 1):
            ratio = i / segments
            y = base_y - self.height * ratio
            offset = math.sin(t * self.sway_speed + self.sway_phase + ratio * 2.0) * (self.sway_amp * ratio) + (extra_sway * ratio)
            points.append((self.x + offset, y))
        
        if len(points) >= 2:
            pygame.draw.lines(surface, (18, 48, 28), False, points, 6)
            pygame.draw.lines(surface, self.color, False, points, 4)


class Level:
    """Represents an active game stage with custom environment, challenges, and goals."""

    def __init__(self, level_id: int):
        self.config: LevelConfig = LEVELS.get(level_id, LEVELS[1])
        self.level_id = level_id
        self.time_remaining: float = self.config.time_limit
        
        self.deposited_count: int = 0
        self.required_deposits: int = self.config.required_deposits

        # Exploration Grid (32 cols x 18 rows = 40x40px tiles)
        self.explored_grid: List[List[bool]] = [[False for _ in range(32)] for _ in range(18)]

        # Ancient Puzzle (Level 5)
        self.puzzle: Optional[AncientGesturePuzzle] = AncientGesturePuzzle() if level_id == 5 else None

        # Managers
        self.treasure_manager = TreasureManager()
        self.marine_manager = MarineLifeManager(fish_count=8 if level_id == 3 else (12 + level_id * 2))
        
        # Scenery & Photorealistic Textures
        self.backdrop_tex: Optional[pygame.Surface] = None
        self.coral_fg_tex: Optional[pygame.Surface] = None
        self.caustics_tex: Optional[pygame.Surface] = None
        self.caustic_offset = 0.0
        self._load_textures()

        self.seaweeds: List[Seaweed] = []
        self._init_scenery()

        # Spawn Level Interactive Items with clean neat spacing and keys
        self.treasure_manager.spawn_level_treasures(
            common_count=self.config.common_treasures,
            gold_count=self.config.gold_treasures,
            rare_count=self.config.rare_treasures,
            ancient_count=self.config.ancient_treasures,
            fake_count=self.config.fake_treasures,
            trap_count=self.config.traps,
            screen_w=SCREEN_WIDTH,
            screen_h=SCREEN_HEIGHT,
            key_count=getattr(self.config, "key_count", 0),
            locked_chest_count=getattr(self.config, "locked_chests", 0),
        )

        # Spawn bioluminescent electric jellyfish in deeper zones
        if level_id == 3:
            self.marine_manager.spawn_jellyfish(2)
        elif level_id == 5:
            self.marine_manager.spawn_jellyfish(3)

    def _load_textures(self) -> None:
        """Lazily loads high-definition environmental backdrop textures."""
        def load_img(fname: str, alpha: bool = False) -> Optional[pygame.Surface]:
            p = os.path.join(ASSETS_DIR, fname)
            if not os.path.isfile(p):
                return None
            try:
                s = pygame.image.load(p)
                return s.convert_alpha() if alpha else s.convert()
            except Exception:
                return None

        if self.level_id == 1:
            self.backdrop_tex = load_img("level1_shallow_ocean.jpg")
            self.coral_fg_tex = None
        elif self.level_id == 2:
            self.backdrop_tex = load_img("coral_reef.jpg")
            self.coral_fg_tex = None
        elif self.level_id == 3:
            self.backdrop_tex = load_img("level3_atlantis_temple.png") or load_img("shipwreck_ruins_cinematic.jpg")
            self.coral_fg_tex = None
        elif self.level_id == 4:
            self.backdrop_tex = load_img("shipwreck.jpg")
            self.coral_fg_tex = None
        elif self.level_id == 5:
            self.backdrop_tex = load_img("ruins.jpg")
            self.coral_fg_tex = None

        if self.backdrop_tex:
            self.backdrop_tex = pygame.transform.smoothscale(self.backdrop_tex, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Caustics: use clean transparent caustics texture with delicate subtle alpha
        caust_path = os.path.join(ASSETS_DIR, "caustics_clean.png")
        if os.path.isfile(caust_path):
            try:
                self.caustics_tex = pygame.image.load(caust_path).convert_alpha()
                self.caustics_tex = pygame.transform.smoothscale(self.caustics_tex, (640, 640))
                # Soften alpha so caustics shimmer naturally without harsh spiderweb lines
                alpha_arr = pygame.surfarray.pixels_alpha(self.caustics_tex)
                # Deep ocean levels (3, 4, 5) have very faint, atmospheric caustics (0.04) to avoid harsh chicken-wire net appearance,
                # while shallow sunlit levels (1, 2) have gentle shimmering caustics (0.10).
                caustic_mult = 0.04 if self.level_id in (3, 4, 5) else 0.10
                alpha_arr[:] = (alpha_arr * caustic_mult).astype(np.uint8)
                del alpha_arr
            except Exception:
                self.caustics_tex = None
        else:
            self.caustics_tex = load_img("caustics.jpg")
            if self.caustics_tex:
                self.caustics_tex = pygame.transform.smoothscale(self.caustics_tex, (640, 640))

    def _init_scenery(self) -> None:
        """
        Keeps all levels clean and cinematic with zero foreground plant clutter.
        Preserves the pristine photorealistic backdrops and ensures all relics,
        chests, oxygen vents, and marine life are completely unobstructed.
        """
        self.seaweeds = []

    def get_exploration_ratio(self) -> float:
        """Returns the percentage of the seabed map that has been explored."""
        tot = 32 * 18
        vis = sum(sum(1 for cell in row if cell) for row in self.explored_grid)
        return vis / tot

    def update(self, dt: float, current_active: bool, cursor_pos: Tuple[int, int], shield_active: bool) -> Tuple[bool, bool, bool, bool, bool, bool]:
        """
        Updates level timers, marine life, exploration fog, and hazards.
        Returns:
            (is_level_complete, is_game_over, shark_hit, shark_deflected, jelly_hit, jelly_deflected)
        """
        self.time_remaining = max(0.0, self.time_remaining - dt)
        cx, cy = cursor_pos

        # Update Exploration Fog Grid
        c_tile = int(cx // 40)
        r_tile = int(cy // 40)
        for dr in range(-3, 4):
            for dc in range(-3, 4):
                rr = r_tile + dr
                cc = c_tile + dc
                if 0 <= rr < 18 and 0 <= cc < 32:
                    self.explored_grid[rr][cc] = True
        
        # Update Treasures & Collection Chest Depot
        self.treasure_manager.update(dt, current_active, player_pos=cursor_pos)

        # Update Marine Life & Sharks
        self.marine_manager.update(
            dt,
            current_active,
            cursor_pos,
            shark_allowed=self.config.shark_enabled,
            shark_interval=self.config.shark_interval
        )

        # Check Shark & Jellyfish Collision
        shark_hit, shark_deflected = self.marine_manager.check_shark_interaction(cx, cy, shield_active)
        jelly_hit, jelly_deflected = self.marine_manager.check_jellyfish_interaction(cx, cy, shield_active)

        # Check Win/Loss conditions based on deposited relics objective
        is_level_complete = (self.deposited_count >= self.required_deposits)
        is_game_over = (self.time_remaining <= 0)

        return is_level_complete, is_game_over, shark_hit, shark_deflected, jelly_hit, jelly_deflected

    def draw_background(self, surface: pygame.Surface, current_active: bool = False) -> None:
        """Renders realistic multi-depth underwater gradient, parallax seabed, and scenery."""
        # 1. Depth Gradient or Thematic 3D Backdrop
        top_col = self.config.ambient_color
        bot_col = self.config.deep_color

        if self.backdrop_tex:
            surface.blit(self.backdrop_tex, (0, 0))
            # Oceanic depth tinting layer (clear for shallow waters, atmospheric for deep abyss)
            tint_alpha = int(75 * (1.0 - self.config.visibility))
            if tint_alpha > 0:
                tint_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                tint_surf.fill((*self.config.deep_color[:3], tint_alpha))
                surface.blit(tint_surf, (0, 0))
        else:
            grad_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, 4):
                t = y / SCREEN_HEIGHT
                r = int(top_col[0] + (bot_col[0] - top_col[0]) * t)
                g = int(top_col[1] + (bot_col[1] - top_col[1]) * t)
                b = int(top_col[2] + (bot_col[2] - top_col[2]) * t)
                pygame.draw.rect(grad_surf, (r, g, b), (0, y, SCREEN_WIDTH, 4))
            surface.blit(grad_surf, (0, 0))

        # 2. Dynamic Water Caustics projection (sunlight rippling across water column)
        if self.caustics_tex:
            self.caustic_offset = (self.caustic_offset + 0.35) % 640
            cw, ch = 640, 640
            ox = int(self.caustic_offset)
            t_now = time.time()
            oy = int(t_now * 8) % ch
            for tx in range(-cw, SCREEN_WIDTH + cw, cw):
                for ty in range(-ch, SCREEN_HEIGHT + ch, ch):
                    surface.blit(self.caustics_tex, (tx + ox, ty + oy))

        # 3. Ancient Puzzle Pedestal (Level 5)
        if self.level_id == 5 and self.puzzle:
            self.puzzle.draw(surface)

        # 4. Level-Specific Scenery Backdrop (Fallback or Accent)
        if not self.backdrop_tex:
            if self.level_id == 4:
                # Sunken Shipwreck Silhouette
                ship_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                hull_col = (12, 22, 34, 180)
                hull_poly = [
                    (140, SCREEN_HEIGHT),
                    (160, SCREEN_HEIGHT - 180),
                    (360, SCREEN_HEIGHT - 150),
                    (540, SCREEN_HEIGHT - 170),
                    (620, SCREEN_HEIGHT),
                ]
                pygame.draw.polygon(ship_surf, hull_col, hull_poly)
                pygame.draw.line(ship_surf, hull_col, (340, SCREEN_HEIGHT - 150), (320, SCREEN_HEIGHT - 380), 12)
                pygame.draw.line(ship_surf, hull_col, (260, SCREEN_HEIGHT - 310), (380, SCREEN_HEIGHT - 325), 6)
                surface.blit(ship_surf, (0, 0))

            elif self.level_id == 5:
                # Sunken Ancient Temple of Atlantis
                temple_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pillar_col = (20, 32, 50, 190)
                for px in (120, 240, SCREEN_WIDTH - 240, SCREEN_WIDTH - 120):
                    pygame.draw.rect(temple_surf, pillar_col, (px, SCREEN_HEIGHT - 260, 48, 260))
                    pygame.draw.rect(temple_surf, pillar_col, (px - 10, SCREEN_HEIGHT - 275, 68, 16))
                    pygame.draw.rect(temple_surf, pillar_col, (px - 6, SCREEN_HEIGHT - 20, 60, 20))
                pygame.draw.polygon(temple_surf, pillar_col, [
                    (90, SCREEN_HEIGHT - 275),
                    (280, SCREEN_HEIGHT - 275),
                    (260, SCREEN_HEIGHT - 310),
                    (110, SCREEN_HEIGHT - 310),
                ])
                surface.blit(temple_surf, (0, 0))

        # 5. Foreground Coral Reef Formations (Level 1 & 2)
        if self.coral_fg_tex:
            surface.blit(self.coral_fg_tex, (0, SCREEN_HEIGHT - self.coral_fg_tex.get_height()))

        # 6. Parallax Sandy Sea Floor (only when no photographic backdrop is active)
        if not self.backdrop_tex:
            seafloor_col = (int(bot_col[0] * 1.5 + 8), int(bot_col[1] * 1.5 + 14), int(bot_col[2] * 1.5 + 20))
            floor_points = [(0, SCREEN_HEIGHT)]
            for x in range(0, SCREEN_WIDTH + 50, 40):
                fy = SCREEN_HEIGHT - 55 + math.sin(x * 0.015) * 14.0
                floor_points.append((x, fy))
            floor_points.append((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.polygon(surface, seafloor_col, floor_points)

        # 7. Swaying Seaweed
        for sw in self.seaweeds:
            sw.draw(surface, current_active)

    def draw_fog(self, surface: pygame.Surface, player_pos: Tuple[float, float] = (640, 360), sonar_active: bool = False) -> None:
        """Draws dynamic depth fog with a circular diver flashlight beam in dark abyss levels."""
        if self.config.visibility < 0.95:
            fog_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fog_alpha = 40 if sonar_active else int(240 * (1.0 - self.config.visibility))
            fog_surf.fill((*self.config.deep_color[:3], max(0, min(235, fog_alpha))))

            # Flashlight illumination cutout around the player
            if not sonar_active and player_pos:
                px, py = int(player_pos[0]), int(player_pos[1])
                light_radius = 230
                pygame.draw.circle(fog_surf, (0, 0, 0, 0), (px, py), light_radius)
                # Soft luminous light falloff ring
                pygame.draw.circle(fog_surf, (*COLOR_OCEAN_CYAN[:3], 35), (px, py), light_radius + 15, 8)

            surface.blit(fog_surf, (0, 0))

