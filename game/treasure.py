"""
Underwater Treasure Hunt - Treasure System & Collection Depot
Defines all treasure archetypes, deceptive fake treasures, dangerous traps,
and the seafloor Treasure Chest collection depot where relics are deposited.
"""

from enum import Enum
import math
import random
import time
from typing import List, Optional, Tuple
import pygame

from config import (
    SCORE_COMMON,
    SCORE_GOLD,
    SCORE_RARE,
    SCORE_ANCIENT,
    SCORE_FAKE_PENALTY,
    FAKE_TREASURE_OXYGEN_PENALTY,
    TRAP_OXYGEN_PENALTY,
    SONAR_REVEAL_DURATION,
    DEPOSIT_ZONE_RADIUS,
    COLOR_GOLD,
    COLOR_NEON_TEAL,
    COLOR_OCEAN_CYAN,
    COLOR_CORAL_RED,
    COLOR_AMBER_WARNING,
    COLOR_PURPLE_MYSTIC,
    COLOR_EMERALD,
    COLOR_WHITE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
import os
from game.collision import point_in_circle, distance

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
_VENT_TEX: Optional[pygame.Surface] = None
_CHEST_SURF: Optional[pygame.Surface] = None

def _get_vent_texture() -> Optional[pygame.Surface]:
    global _VENT_TEX
    if _VENT_TEX is None:
        p = os.path.join(ASSETS_DIR, "seabed_oxygen_vent.png")
        if os.path.isfile(p):
            try:
                _VENT_TEX = pygame.image.load(p).convert_alpha()
            except Exception:
                pass
    return _VENT_TEX

def _get_chest_surf() -> Optional[pygame.Surface]:
    global _CHEST_SURF
    if _CHEST_SURF is None:
        p = os.path.join(ASSETS_DIR, "treasure_chest.png")
        if os.path.isfile(p):
            try:
                _CHEST_SURF = pygame.image.load(p).convert_alpha()
            except Exception:
                pass
    return _CHEST_SURF

class TreasureType(Enum):
    COMMON = "COMMON"
    GOLD = "GOLD"
    RARE = "RARE"
    ANCIENT = "ANCIENT"
    HEAVY = "HEAVY"
    KEY = "KEY"
    LOCKED_CHEST = "LOCKED_CHEST"
    FAKE = "FAKE"
    TRAP = "TRAP"

class Treasure:
    """An interactive underwater item that can be grabbed, carried, and deposited."""

    def __init__(self, x: float, y: float, treasure_type: TreasureType):
        self.x = x
        self.y = y
        self.base_y = y
        self.type = treasure_type
        self.radius = 30.0
        self.collected = False     # True once successfully deposited into the chest
        self.is_carried = False    # True while swimmer is actively carrying it
        self.revealed_timer = 0.0

        # Heavy treasure dual-hand mechanics
        self.requires_dual_hand = (self.type == TreasureType.HEAVY)
        self.is_unstable = False
        self.unstable_timer = 0.0
        self.instability: float = 0.0
        self.is_hovered_by_player = False

        # Animation state
        self.float_phase = random.uniform(0.0, math.pi * 2)
        self.float_speed = random.uniform(1.8, 2.6)
        self.float_amp = random.uniform(4.0, 8.0)
        self.shimmer_phase = random.uniform(0.0, math.pi * 2)

        # Configure score & oxygen impacts
        if self.type == TreasureType.COMMON:
            self.score_value = SCORE_COMMON
            self.oxygen_penalty = 0.0
            self.base_color = (245, 238, 220)  # Luminous Pearlescent Shell
            self.radius = 32.0
            # Natural seabed settling: rests firmly on seafloor sand shelf
            self.float_amp = random.uniform(1.2, 2.0)
            self.shell_breath_phase = random.uniform(0.0, math.pi * 2)
            self.shell_bubble_timer = random.uniform(1.2, 3.5)
            self.shell_bubbles: List[dict] = []
        elif self.type == TreasureType.GOLD:
            self.score_value = SCORE_GOLD
            self.oxygen_penalty = 0.0
            self.base_color = COLOR_GOLD
        elif self.type == TreasureType.RARE:
            self.score_value = SCORE_RARE
            self.oxygen_penalty = 0.0
            self.base_color = COLOR_OCEAN_CYAN
        elif self.type == TreasureType.ANCIENT:
            self.score_value = SCORE_ANCIENT
            self.oxygen_penalty = 0.0
            self.base_color = COLOR_PURPLE_MYSTIC
        elif self.type == TreasureType.HEAVY:
            self.score_value = 750
            self.oxygen_penalty = 0.0
            self.base_color = (185, 120, 50)  # Gilded nautical strongbox
            self.radius = 42.0
            self.requires_dual_hand = True
            self.requires_both_hands = True
            self.is_heavy = True
        elif self.type == TreasureType.KEY:
            self.score_value = 250
            self.oxygen_penalty = 0.0
            self.base_color = COLOR_GOLD
            self.radius = 28.0
        elif self.type == TreasureType.LOCKED_CHEST:
            self.score_value = 500
            self.oxygen_penalty = 0.0
            self.base_color = (185, 130, 45)
            self.radius = 36.0
        elif self.type == TreasureType.FAKE:
            self.score_value = SCORE_FAKE_PENALTY
            self.oxygen_penalty = FAKE_TREASURE_OXYGEN_PENALTY
            # Visually disguises itself as a Gold or Rare treasure
            self.base_color = COLOR_GOLD if random.random() < 0.6 else COLOR_OCEAN_CYAN
        elif self.type == TreasureType.TRAP:
            self.score_value = 0
            self.oxygen_penalty = TRAP_OXYGEN_PENALTY
            self.base_color = (70, 75, 85)  # Spiked iron naval mine
            self.radius = 34.0

    def update(self, dt: float, current_force_x: float = 0.0) -> None:
        if self.collected:
            return

        self.shimmer_phase += 3.5 * dt

        if self.type == TreasureType.COMMON:
            if not hasattr(self, "shell_breath_phase"):
                self.shell_breath_phase = 0.0
                self.shell_bubble_timer = 2.0
                self.shell_bubbles = []
            self.shell_breath_phase += 1.4 * dt
            # Siphon micro-bubbles
            self.shell_bubble_timer -= dt
            if self.shell_bubble_timer <= 0.0 and not self.is_carried:
                self.shell_bubble_timer = random.uniform(2.5, 5.0)
                for _ in range(random.randint(1, 3)):
                    self.shell_bubbles.append({
                        "ox": random.uniform(-6.0, 6.0),
                        "oy": random.uniform(-10.0, -4.0),
                        "r": random.uniform(1.5, 3.2),
                        "life": random.uniform(1.2, 2.0),
                        "speed": random.uniform(24.0, 42.0),
                    })
            surviving_bubbles = []
            for b in self.shell_bubbles:
                b["life"] -= dt
                b["oy"] -= b["speed"] * dt
                b["ox"] += math.sin(self.shell_breath_phase + b["oy"] * 0.04) * 0.3
                if b["life"] > 0:
                    surviving_bubbles.append(b)
            self.shell_bubbles = surviving_bubbles

        if not self.is_carried:
            # Gentle bobbing on seabed
            self.float_phase += self.float_speed * dt
            self.y = self.base_y + math.sin(self.float_phase) * self.float_amp
            
            # Drift slightly when water current is active
            if current_force_x != 0:
                self.x += current_force_x * 0.25 * dt
                self.x = max(60.0, min(SCREEN_WIDTH - 60.0, self.x))

        if self.revealed_timer > 0:
            self.revealed_timer -= dt

    def drop(self, drop_x: float, drop_y: float) -> None:
        """Drops treasure back into the environment if released outside the chest."""
        self.is_carried = False
        self.x = drop_x
        # Sinks back towards seafloor
        self.base_y = min(SCREEN_HEIGHT - 90.0, max(120.0, drop_y + 35.0))
        self.y = self.base_y

    def reveal(self, duration: float = SONAR_REVEAL_DURATION) -> None:
        """Reveals true identity when swept by Sonar."""
        self.revealed_timer = duration

    def is_hovered(self, cursor_x: float, cursor_y: float) -> bool:
        """Checks if player swimmer or cursor is within grabbing distance."""
        if self.collected:
            return False
        return point_in_circle(cursor_x, cursor_y, self.x, self.y, self.radius + 26.0)

    def draw(self, surface: pygame.Surface) -> None:
        """Draws the procedural representation of the treasure."""
        if self.collected:
            return

        cx, cy = int(self.x), int(self.y)
        r = int(self.radius)

        # 1. Main Object Shape by Type (Photorealistic 3D HD Relics with procedural fallback)
        rendered_with_hd = False
        relic_map = {
            TreasureType.COMMON: "pearl",
            TreasureType.GOLD: "gold_coin",
            TreasureType.RARE: "sapphire_chalice",
            TreasureType.ANCIENT: "ancient_crown",
            TreasureType.HEAVY: "heavy_chest",
        }

        if self.type in relic_map:
            relic_id = relic_map[self.type]
            try:
                from ui.relic_renderer import HDRelicRenderer
                if HDRelicRenderer.get_texture(relic_id) is not None:
                    if self.type == TreasureType.COMMON:
                        breath_p = getattr(self, "shell_breath_phase", 0.0)
                        breath_tilt = 0.05 * math.sin(breath_p)
                        sway_yaw = math.sin(self.shimmer_phase * 0.5) * (0.22 if self.is_carried else 0.08)
                        sway_pitch = (math.cos(self.float_phase * 0.8) * 0.12 if self.is_carried else -0.05) + breath_tilt
                        light_vec = (math.cos(self.shimmer_phase * 0.8) * 14.0, -20.0)
                        rad = int(self.radius * (1.04 if self.is_carried else 0.98))
                        pulse_p = breath_p
                    else:
                        sway_yaw = math.sin(self.shimmer_phase * 0.8) * 0.35
                        sway_pitch = math.cos(self.float_phase * 0.9) * 0.15
                        light_vec = (math.cos(self.shimmer_phase) * 16.0, -22.0)
                        rad = int(self.radius * 0.95)
                        pulse_p = self.shimmer_phase

                    HDRelicRenderer.draw_relic(
                        surface,
                        relic_id=relic_id,
                        cx=cx,
                        cy=cy,
                        radius=rad,
                        is_unlocked=True,
                        is_modal=False,
                        light_offset=light_vec,
                        yaw=sway_yaw,
                        pitch=sway_pitch,
                        pulse_phase=pulse_p,
                    )
                    rendered_with_hd = True
            except Exception:
                rendered_with_hd = False

        if not rendered_with_hd:
            # Fallback procedural glow for non-HD objects
            if self.type not in (TreasureType.TRAP, TreasureType.FAKE):
                glow_alpha = int(75 + 35 * math.sin(self.shimmer_phase)) if self.is_carried else int(35 + 20 * math.sin(self.shimmer_phase))
                glow_surf = pygame.Surface((r * 2 + 24, r * 2 + 24), pygame.SRCALPHA)
                glow_color = (*self.base_color[:3], glow_alpha)
                pygame.draw.circle(glow_surf, glow_color, (r + 12, r + 12), r + (10 if self.is_carried else 6))
                surface.blit(glow_surf, (cx - r - 12, cy - r - 12))

        if not rendered_with_hd:
            if self.type == TreasureType.TRAP:
                # Spiked Naval Sea Mine
                pygame.draw.circle(surface, (45, 50, 58), (cx, cy), r - 6)
                pygame.draw.circle(surface, (70, 78, 88), (cx, cy), r - 10)
                for angle_deg in range(0, 360, 45):
                    rad = math.radians(angle_deg)
                    sx = cx + math.cos(rad) * (r + 3)
                    sy = cy + math.sin(rad) * (r + 3)
                    pygame.draw.line(surface, (30, 35, 42), (cx, cy), (int(sx), int(sy)), 5)
                    pygame.draw.circle(surface, (200, 40, 40), (int(sx), int(sy)), 3)
                led_blink = (int(time.time() * 4) % 2) == 0
                led_color = (255, 30, 30) if led_blink else (90, 10, 10)
                pygame.draw.circle(surface, led_color, (cx, cy), 5)

            elif self.type == TreasureType.COMMON:
                # Photorealistic Natural Oyster Shell with Luminous Spherical Pearl
                shell_w = int(r * 2.2)
                shell_h = int(r * 1.5)
                # Seabed contact shadow
                shadow_surf = pygame.Surface((shell_w + 10, shell_h + 10), pygame.SRCALPHA)
                pygame.draw.ellipse(shadow_surf, (8, 16, 26, 120), (5, 5, shell_w, shell_h))
                surface.blit(shadow_surf, (cx - shell_w // 2 - 5, cy - shell_h // 2 + 6))
                
                # Layered natural shell fan
                for step, frac in enumerate([1.0, 0.90, 0.78, 0.65]):
                    sw_i = int(shell_w * frac)
                    sh_i = int(shell_h * frac)
                    col = (int(165 - step * 15), int(135 - step * 12), int(105 - step * 10))
                    pygame.draw.ellipse(surface, col, (cx - sw_i // 2, cy - sh_i // 2 + int(step * 2), sw_i, sh_i))
                
                # Radial fan flutes
                for ang_offset in [-0.55, -0.35, -0.15, 0.0, 0.15, 0.35, 0.55]:
                    fx = cx + math.sin(ang_offset) * (shell_w * 0.45)
                    fy = cy - math.cos(ang_offset) * (shell_h * 0.35)
                    pygame.draw.line(surface, (190, 165, 135), (cx, cy + 6), (int(fx), int(fy)), 2)
                
                # Iridescent Mother-of-pearl interior bed
                nacre_w = int(shell_w * 0.68)
                nacre_h = int(shell_h * 0.52)
                pygame.draw.ellipse(surface, (230, 225, 230), (cx - nacre_w // 2, cy - nacre_h // 2 - 1, nacre_w, nacre_h))
                pygame.draw.ellipse(surface, (210, 235, 245), (cx - nacre_w // 2 + 2, cy - nacre_h // 2 + 1, nacre_w - 4, nacre_h - 2))
                
                # Luminous Spherical Pearl
                pr = max(8, int(r * 0.55))
                p_glow = pygame.Surface((pr * 4, pr * 4), pygame.SRCALPHA)
                pygame.draw.circle(p_glow, (220, 245, 255, 60), (pr * 2, pr * 2), pr * 2)
                surface.blit(p_glow, (cx - pr * 2, cy - pr * 2 - 3))
                pygame.draw.circle(surface, (175, 195, 215), (cx, cy - 3), pr)
                pygame.draw.circle(surface, (235, 242, 252), (cx - 1, cy - 4), int(pr * 0.82))
                pygame.draw.circle(surface, (255, 255, 255), (cx - 3, cy - 6), int(pr * 0.55))
                pygame.draw.circle(surface, (255, 255, 255), (cx - pr // 3, cy - 3 - pr // 3), max(2, pr // 4))

            elif self.type == TreasureType.GOLD:
                # Realistic Antique Sunken Gold Relic Chest / Ingot Strongbox
                gw = int(r * 1.5)
                gh = int(r * 1.1)
                gx, gy = cx - gw // 2, cy - gh // 2
                s_surf = pygame.Surface((gw + 12, gh + 12), pygame.SRCALPHA)
                pygame.draw.rect(s_surf, (8, 16, 26, 120), (0, 0, gw + 12, gh + 12), border_radius=6)
                surface.blit(s_surf, (gx - 6, gy + 5))
                
                body_col = (165, 115, 28)
                lid_col = (225, 175, 45)
                crest_col = (255, 240, 150)
                
                pygame.draw.rect(surface, body_col, (gx, gy, gw, gh), border_radius=6)
                pygame.draw.rect(surface, lid_col, (gx + 2, gy + 2, gw - 4, gh // 2), border_radius=5)
                pygame.draw.line(surface, crest_col, (gx + 4, gy + 3), (gx + gw - 4, gy + 3), 2)
                pygame.draw.rect(surface, (95, 68, 22), (gx + 8, gy, 5, gh))
                pygame.draw.rect(surface, (95, 68, 22), (gx + gw - 13, gy, 5, gh))
                for ry in [gy + 4, gy + gh // 2, gy + gh - 5]:
                    pygame.draw.circle(surface, (255, 225, 95), (gx + 10, ry), 2)
                    pygame.draw.circle(surface, (255, 225, 95), (gx + gw - 11, ry), 2)
                # Ornamental Royal Sun Crest (NO keyhole, purely decorative seal)
                pygame.draw.circle(surface, (255, 215, 60), (cx, cy), 6)
                pygame.draw.circle(surface, (200, 40, 50), (cx, cy), 3)

            elif self.type == TreasureType.FAKE:
                # Cursed Mimic: Dark barnacle shell with ominous glowing fissures (NO padlock / keyhole)
                mw = int(r * 1.4)
                mh = int(r * 1.2)
                mx, my = cx - mw // 2, cy - mh // 2
                s_surf = pygame.Surface((mw + 12, mh + 12), pygame.SRCALPHA)
                pygame.draw.ellipse(s_surf, (6, 12, 20, 130), (0, 0, mw + 12, mh + 12))
                surface.blit(s_surf, (mx - 6, my + 5))

                # Weathered dark barnacle shell
                pygame.draw.ellipse(surface, (52, 58, 62), (mx, my, mw, mh))
                pygame.draw.ellipse(surface, (38, 42, 46), (mx + 3, my + 3, mw - 6, mh - 6))

                # Sinister pulsing crack vein
                pulse_crack = (math.sin(self.shimmer_phase * 2.0) + 1.0) * 0.5
                crack_col = (235, 45, 55) if self.revealed_timer > 0 else (195, 85, 30)
                crack_pts = [
                    (cx - 10, cy - 8),
                    (cx - 3, cy - 2),
                    (cx + 4, cy + 2),
                    (cx + 12, cy + 8)
                ]
                pygame.draw.lines(surface, crack_col, False, crack_pts, 3)
                pygame.draw.circle(surface, (255, 180, 50), (cx, cy), 2)

            elif self.type == TreasureType.KEY:
                # Ancient Golden Skeleton Key
                key_len = int(r * 1.7)
                bow_r = max(8, int(r * 0.48))
                stem_w = max(3, int(r * 0.16))
                
                # Soft shimmering golden halo
                glow_surf = pygame.Surface((r * 3, r * 3), pygame.SRCALPHA)
                g_alpha = int(45 + 30 * math.sin(self.shimmer_phase * 2.2))
                pygame.draw.circle(glow_surf, (255, 215, 80, g_alpha), (int(r * 1.5), int(r * 1.5)), int(r * 1.2))
                surface.blit(glow_surf, (cx - int(r * 1.5), cy - int(r * 1.5)))

                # Contact shadow
                sh_surf = pygame.Surface((key_len + 8, bow_r * 2 + 8), pygame.SRCALPHA)
                pygame.draw.ellipse(sh_surf, (6, 12, 22, 110), (2, 2, key_len + 4, bow_r * 2 + 4))
                surface.blit(sh_surf, (cx - bow_r - 2, cy - bow_r + 4))

                # Ornate Bow (Circular filigree handle)
                bow_cx = cx - bow_r
                pygame.draw.circle(surface, COLOR_GOLD, (bow_cx, cy), bow_r)
                pygame.draw.circle(surface, (255, 245, 170), (bow_cx, cy), bow_r, 2)
                pygame.draw.circle(surface, (14, 25, 42), (bow_cx, cy), max(3, bow_r - 4))
                pygame.draw.circle(surface, (255, 225, 110), (bow_cx, cy), max(1, bow_r - 7))

                # Fluted Key Stem
                shaft_x = bow_cx + bow_r - 2
                shaft_len = int(key_len * 0.72)
                pygame.draw.rect(surface, (195, 145, 35), (shaft_x, cy - stem_w // 2, shaft_len, stem_w))
                pygame.draw.line(surface, (255, 245, 180), (shaft_x, cy - stem_w // 2 + 1), (shaft_x + shaft_len, cy - stem_w // 2 + 1), 1)

                # Ward Bit (Key Teeth)
                bit_w = int(r * 0.40)
                bit_h = int(r * 0.52)
                bit_x = shaft_x + shaft_len - bit_w - 2
                pygame.draw.rect(surface, COLOR_GOLD, (bit_x, cy, bit_w, bit_h), border_radius=2)
                pygame.draw.rect(surface, (255, 245, 180), (bit_x, cy, bit_w, bit_h), width=1, border_radius=2)
                # Cutout notch
                pygame.draw.rect(surface, (14, 25, 42), (bit_x + 3, cy + 3, max(2, bit_w // 3), max(2, bit_h // 2)))

            elif self.type == TreasureType.LOCKED_CHEST:
                # 3D Photorealistic Sunken Pirate Chest with Ornate Brass Padlock
                c_surf = _get_chest_surf()
                cw, ch = 88, 88
                gx, gy = cx - cw // 2, cy - ch // 2

                # Seabed feathered contact shadow
                s_surf = pygame.Surface((cw + 24, 28), pygame.SRCALPHA)
                pygame.draw.ellipse(s_surf, (4, 10, 20, 160), (0, 0, cw + 24, 28))
                surface.blit(s_surf, (cx - (cw + 24) // 2, cy + ch // 2 - 18))

                # Soft atmospheric aura
                aura_surf = pygame.Surface((cw + 30, ch + 20), pygame.SRCALPHA)
                pulse_l = math.sin(self.shimmer_phase * 2.2)
                aura_a = int(36 + 22 * pulse_l)
                pygame.draw.ellipse(aura_surf, (255, 205, 70, aura_a), (0, 0, cw + 30, ch + 20))
                surface.blit(aura_surf, (cx - (cw + 30) // 2, cy - (ch + 20) // 2 + 6))

                if c_surf:
                    scaled_c = pygame.transform.smoothscale(c_surf, (cw, ch))
                    surface.blit(scaled_c, (gx, gy))
                else:
                    # Fallback procedural
                    pygame.draw.rect(surface, (95, 65, 35), (gx, gy, cw, ch), border_radius=6)
                    pygame.draw.rect(surface, (125, 85, 45), (gx + 2, gy + 2, cw - 4, ch // 2), border_radius=5)
                    pygame.draw.line(surface, (170, 125, 70), (gx + 4, gy + 3), (gx + cw - 4, gy + 3), 2)
                    pygame.draw.rect(surface, (45, 52, 60), (gx + 10, gy, 7, ch))
                    pygame.draw.rect(surface, (45, 52, 60), (gx + cw - 17, gy, 7, ch))

                # Heavy Ornate Brass Padlock with Metallic Shackle & Glowing Keyhole
                pl_w, pl_h = 24, 26
                pl_x = cx - pl_w // 2
                pl_y = cy - pl_h // 2 + 10

                # Shackle arc
                pygame.draw.arc(surface, (220, 230, 240), (cx - 9, pl_y - 10, 18, 18), 0, math.pi, 3)
                pygame.draw.arc(surface, (90, 100, 115), (cx - 9, pl_y - 9, 18, 18), 0, math.pi, 1)

                # Padlock Body with 3D metallic bevel
                pygame.draw.rect(surface, (245, 195, 45), (pl_x, pl_y, pl_w, pl_h), border_radius=5)
                pygame.draw.rect(surface, (255, 240, 140), (pl_x + 1, pl_y + 1, pl_w - 2, 3), border_radius=2)
                pygame.draw.rect(surface, (145, 95, 20), (pl_x, pl_y, pl_w, pl_h), width=2, border_radius=5)

                # Keyhole with soft pulsing amber beacon
                pygame.draw.circle(surface, (20, 15, 10), (cx, pl_y + 9), 4)
                pygame.draw.polygon(surface, (20, 15, 10), [(cx - 2, pl_y + 9), (cx + 2, pl_y + 9), (cx + 1, pl_y + 16), (cx - 1, pl_y + 16)])
                pygame.draw.circle(surface, (255, 220, 90), (cx, pl_y + 9), 2)

            elif self.type == TreasureType.RARE:
                # Sapphire Relic / Chalice
                poly = [
                    (cx - r // 2, cy - r // 2),
                    (cx + r // 2, cy - r // 2),
                    (cx + r // 4, cy + r // 6),
                    (cx + 4, cy + r // 3),
                    (cx + r // 3, cy + r // 2),
                    (cx - r // 3, cy + r // 2),
                    (cx - 4, cy + r // 3),
                    (cx - r // 4, cy + r // 6),
                ]
                pygame.draw.polygon(surface, COLOR_OCEAN_CYAN, poly)
                pygame.draw.polygon(surface, COLOR_WHITE, poly, 2)
                pygame.draw.circle(surface, (100, 230, 255), (cx, cy - 4), 6)

            elif self.type == TreasureType.ANCIENT:
                # Mythical Sunken Crown of Atlantis
                crown_poly = [
                    (cx - r + 4, cy + r // 3),
                    (cx - r + 4, cy - r // 4),
                    (cx - r // 2, cy - r // 2),
                    (cx, cy - r // 4),
                    (cx + r // 2, cy - r // 2),
                    (cx + r - 4, cy - r // 4),
                    (cx + r - 4, cy + r // 3),
                ]
                pygame.draw.polygon(surface, COLOR_GOLD, crown_poly)
                pygame.draw.polygon(surface, (255, 245, 180), crown_poly, 2)
                pygame.draw.circle(surface, COLOR_CORAL_RED, (cx - r // 2, cy - r // 2 + 4), 4)
                pygame.draw.circle(surface, COLOR_EMERALD, (cx, cy - r // 4 + 4), 5)
                pygame.draw.circle(surface, COLOR_CORAL_RED, (cx + r // 2, cy - r // 2 + 4), 4)

            elif self.type == TreasureType.HEAVY:
                # Massive Sunken Strongbox with Dual Iron Ring Handles
                hw, hh = int(r * 1.6), int(r * 1.2)
                h_rect = pygame.Rect(cx - hw // 2, cy - hh // 2, hw, hh)
                pygame.draw.rect(surface, (140, 85, 30), h_rect, border_radius=8)
                pygame.draw.rect(surface, COLOR_GOLD, h_rect, width=3, border_radius=8)
                # Dual Iron Grips for Left & Right Hands
                pygame.draw.circle(surface, (200, 200, 210), (cx - hw // 2 + 6, cy), 10, 3)
                pygame.draw.circle(surface, (200, 200, 210), (cx + hw // 2 - 6, cy), 10, 3)
                # Gold banding & cross braces
                pygame.draw.line(surface, COLOR_GOLD, (cx - hw // 2, cy - hh // 4), (cx + hw // 2, cy - hh // 4), 2)
                pygame.draw.line(surface, COLOR_GOLD, (cx - hw // 2, cy + hh // 4), (cx + hw // 2, cy + hh // 4), 2)
                pygame.draw.circle(surface, COLOR_GOLD, (cx, cy), 8)
                pygame.draw.circle(surface, (20, 20, 20), (cx, cy + 1), 3)

        # Dual hand UI callouts for heavy treasures (always rendered if HEAVY)
        if self.type == TreasureType.HEAVY:
            if not self.is_carried and self.is_hovered_by_player:
                tag_font = pygame.font.SysFont("segoeui", 12, bold=True)
                t1 = tag_font.render("HEAVY TREASURE", True, COLOR_GOLD)
                t2 = tag_font.render("USE BOTH HANDS 👐", True, COLOR_WHITE)
                surface.blit(t1, (cx - t1.get_width() // 2, cy - r - 32))
                surface.blit(t2, (cx - t2.get_width() // 2, cy - r - 16))
            elif self.is_carried and self.is_unstable:
                tag_font = pygame.font.SysFont("segoeui", 13, bold=True)
                t_unst = tag_font.render("⚠️ UNSTABLE! KEEP HANDS TOGETHER!", True, COLOR_CORAL_RED)
                surface.blit(t_unst, (cx - t_unst.get_width() // 2, cy - r - 22))

        # Siphon micro-bubbles rising from living clam shell in all ocean levels
        if self.type == TreasureType.COMMON and hasattr(self, "shell_bubbles"):
            for b in self.shell_bubbles:
                bx = int(cx + b["ox"])
                by = int(cy + b["oy"])
                br = max(1, int(b["r"]))
                b_alpha = int(min(220, b["life"] * 150))
                b_surf = pygame.Surface((br * 2 + 4, br * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(b_surf, (200, 240, 255, b_alpha), (br + 2, br + 2), br, 1)
                pygame.draw.circle(b_surf, (255, 255, 255, min(255, b_alpha + 50)), (br + 1, br + 1), max(1, br // 2))
                surface.blit(b_surf, (bx - br - 2, by - br - 2))

        # Context-aware hover prompt for shell, key, and locked chest
        if not self.is_carried and self.is_hovered_by_player:
            tag_font = pygame.font.SysFont("segoeui", 12, bold=True)
            if self.type == TreasureType.COMMON:
                t_shell = tag_font.render("LUMINOUS OCEAN SHELL", True, (245, 238, 220))
                surface.blit(t_shell, (cx - t_shell.get_width() // 2, cy - r - 26))
            elif self.type == TreasureType.KEY:
                t_key = tag_font.render("ANCIENT GOLDEN KEY 🗝️", True, COLOR_GOLD)
                surface.blit(t_key, (cx - t_key.get_width() // 2, cy - r - 26))
            elif self.type == TreasureType.LOCKED_CHEST:
                t_lock = tag_font.render("LOCKED CHEST 🔒 [NEEDS KEY 🗝️]", True, (255, 220, 110))
                surface.blit(t_lock, (cx - t_lock.get_width() // 2, cy - r - 26))

        # 3. Sonar Reveal Aura / Overlay
        if self.revealed_timer > 0:
            reveal_alpha = int(220 * min(1.0, self.revealed_timer / 0.8))
            halo_surf = pygame.Surface((r * 2 + 24, r * 2 + 24), pygame.SRCALPHA)
            
            if self.type == TreasureType.TRAP:
                halo_color = (*COLOR_CORAL_RED[:3], reveal_alpha)
                pygame.draw.circle(halo_surf, halo_color, (r + 12, r + 12), r + 8, 3)
                font = pygame.font.SysFont("segoeui", 14, bold=True)
                tag = font.render("TRAP!", True, COLOR_CORAL_RED)
                surface.blit(tag, (cx - tag.get_width() // 2, cy - r - 22))

            elif self.type == TreasureType.FAKE:
                halo_color = (*COLOR_AMBER_WARNING[:3], reveal_alpha)
                pygame.draw.circle(halo_surf, halo_color, (r + 12, r + 12), r + 8, 3)
                font = pygame.font.SysFont("segoeui", 14, bold=True)
                tag = font.render("FAKE!", True, COLOR_AMBER_WARNING)
                surface.blit(tag, (cx - tag.get_width() // 2, cy - r - 22))

            else:
                halo_color = (*COLOR_EMERALD[:3], reveal_alpha)
                pygame.draw.circle(halo_surf, halo_color, (r + 12, r + 12), r + 8, 3)
                font = pygame.font.SysFont("segoeui", 14, bold=True)
                tag = font.render(f"+{self.score_value}", True, COLOR_EMERALD)
                surface.blit(tag, (cx - tag.get_width() // 2, cy - r - 22))

            surface.blit(halo_surf, (cx - r - 12, cy - r - 12))


import os
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
_CHEST_SURF: Optional[pygame.Surface] = None
_CHEST_LOADED: bool = False

def _get_chest_surf() -> Optional[pygame.Surface]:
    global _CHEST_SURF, _CHEST_LOADED
    if not _CHEST_LOADED:
        _CHEST_LOADED = True
        p = os.path.join(ASSETS_DIR, "treasure_chest.png")
        if os.path.isfile(p):
            try:
                _CHEST_SURF = pygame.image.load(p).convert_alpha()
            except Exception:
                _CHEST_SURF = None
    return _CHEST_SURF

class TreasureChest:
    """The underwater collection depot where swimmers deposit gathered relics."""

    def __init__(self, x: float = 160.0, y: float = SCREEN_HEIGHT - 80.0):
        self.x = x
        self.y = y
        self.radius = DEPOSIT_ZONE_RADIUS
        self.lid_open_pct = 0.0
        self.beacon_phase = 0.0
        self.deposited_count = 0
        self.rect = pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), int(self.radius * 2), int(self.radius * 2))

    def is_in_deposit_zone(self, px: float, py: float) -> bool:
        """Checks if player swimmer is within collection range of the chest."""
        return distance(px, py, self.x, self.y) <= self.radius

    def update(self, dt: float, player_is_near: bool) -> None:
        self.beacon_phase += 3.5 * dt
        target_open = 1.0 if player_is_near else 0.0
        self.lid_open_pct += (target_open - self.lid_open_pct) * min(1.0, 10.0 * dt)

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = int(self.x), int(self.y)
        
        # 1. Volumetric Glowing Sunlit Deposit Beacon
        pulse = math.sin(self.beacon_phase)
        beam_alpha = int(24 + 12 * pulse)
        beam_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        beam_w_bot = int(90 + 15 * pulse)
        beam_w_top = int(140 + 20 * pulse)
        beam_poly = [
            (cx - beam_w_bot // 2, cy + 20),
            (cx + beam_w_bot // 2, cy + 20),
            (cx + beam_w_top // 2, 0),
            (cx - beam_w_top // 2, 0),
        ]
        pygame.draw.polygon(beam_surf, (80, 230, 200, beam_alpha), beam_poly)
        surface.blit(beam_surf, (0, 0))

        # Floating golden specks rising in the recovery beam
        t_now = time.time()
        for i in range(8):
            px = cx + math.sin(t_now * 1.2 + i * 1.1) * (35 + i * 3)
            py = (cy - (t_now * 45 + i * 40)) % cy
            pygame.draw.circle(surface, (255, 225, 120), (int(px), int(py)), 2)

        # 2. Atlantean Salvage Platform & Deposit Zone on Seabed
        ring_r = int(self.radius)
        # Deep contact shadow for stone platform
        plat_surf = pygame.Surface((ring_r * 2 + 32, ring_r * 2 + 32), pygame.SRCALPHA)
        # 3-tier feathered ambient occlusion shadow
        for step, a in [(1.0, 30), (0.75, 55), (0.50, 95)]:
            pw = int((ring_r * 2 + 16) * step)
            ph = int((ring_r * 0.70) * step)
            pygame.draw.ellipse(plat_surf, (4, 12, 22, a), ((ring_r * 2 + 32 - pw) // 2, (ring_r * 2 + 32 - ph) // 2 + 10, pw, ph))
        
        # Carved concentric rune dais on the sand
        r_alpha = int(95 + 40 * pulse)
        pygame.draw.ellipse(plat_surf, (0, 210, 200, r_alpha), (16, 16 + int(ring_r * 0.35), ring_r * 2, int(ring_r * 0.75)), 2)
        pygame.draw.ellipse(plat_surf, (255, 215, 80, int(r_alpha * 0.55)), (22, 22 + int(ring_r * 0.35), ring_r * 2 - 12, int(ring_r * 0.75) - 6), 1)
        # Ancient glowing runic tick marks along the ring perimeter
        for ang in range(0, 360, 45):
            rad = math.radians(ang + pulse * 15.0)
            rx = (ring_r + 16) + math.cos(rad) * (ring_r - 2)
            ry = (ring_r + 16 + int(ring_r * 0.35)) + math.sin(rad) * (ring_r * 0.37)
            pygame.draw.circle(plat_surf, (0, 240, 220, int(r_alpha * 0.75)), (int(rx), int(ry)), 2)
        surface.blit(plat_surf, (cx - ring_r - 16, cy - ring_r - 16))

        # 3. 3D Antique Treasure Chest
        # Seabed contact shadow (3-tier soft ambient occlusion)
        s_w = 120
        s_h = 40
        s_surf = pygame.Surface((s_w + 20, s_h + 20), pygame.SRCALPHA)
        for step, a in [(1.0, 35), (0.7, 65), (0.45, 110)]:
            sw_step = int(s_w * step)
            sh_step = max(4, int(s_h * step))
            pygame.draw.ellipse(s_surf, (4, 10, 20, a), ((s_w + 20 - sw_step) // 2, (s_h + 20 - sh_step) // 2, sw_step, sh_step))
        surface.blit(s_surf, (cx - (s_w + 20) // 2, cy - (s_h + 20) // 2 + 30))

        chest_surf = _get_chest_surf()
        if chest_surf:
            cw, ch = 96, 96
            aura_w = 120
            aura_h = 70
            aura_surf = pygame.Surface((aura_w, aura_h), pygame.SRCALPHA)
            pygame.draw.ellipse(aura_surf, (255, 210, 80, 35), (0, 0, aura_w, aura_h))
            surface.blit(aura_surf, (cx - aura_w // 2, cy - aura_h // 2 + 10))

            scaled_chest = pygame.transform.smoothscale(chest_surf, (cw, ch))
            surface.blit(scaled_chest, (cx - cw // 2, cy - ch // 2 - 4))
        else:
            chest_w = 64
            chest_h = 42
            chest_x = cx - chest_w // 2
            chest_y = cy - chest_h // 2

            # Base Chest Body
            pygame.draw.rect(surface, (120, 80, 25), (chest_x, chest_y, chest_w, chest_h), border_radius=6)
            pygame.draw.rect(surface, (60, 40, 15), (chest_x, chest_y, chest_w, chest_h), width=2, border_radius=6)
            # Gold Riveted Bands
            pygame.draw.rect(surface, COLOR_GOLD, (chest_x + 8, chest_y, 8, chest_h))
            pygame.draw.rect(surface, COLOR_GOLD, (chest_x + chest_w - 16, chest_y, 8, chest_h))

            # Animated Chest Lid (Tilts open when swimmer is near)
            lid_h = 16
            lid_offset_y = int(self.lid_open_pct * 14)
            lid_rect = pygame.Rect(chest_x - 3, chest_y - 8 - lid_offset_y, chest_w + 6, lid_h)
            pygame.draw.rect(surface, (150, 100, 35), lid_rect, border_radius=5)
            pygame.draw.rect(surface, COLOR_GOLD, lid_rect, width=2, border_radius=5)
            
            # Golden Keyhole Emblem
            pygame.draw.circle(surface, COLOR_GOLD, (cx, chest_y + 16), 5)
            pygame.draw.circle(surface, (20, 20, 20), (cx, chest_y + 17), 2)

        # Sleek Glassmorphic Plaque Badge (Replaces flat sticker)
        tag_w, tag_h = 148, 24
        tag_surf = pygame.Surface((tag_w, tag_h), pygame.SRCALPHA)
        tag_surf.fill((6, 16, 28, 190))
        pygame.draw.rect(tag_surf, (240, 200, 70, 160), (0, 0, tag_w, tag_h), width=1, border_radius=7)
        # Emerald status pip
        pygame.draw.circle(tag_surf, (0, 240, 160, 220), (12, tag_h // 2), 3)
        font = pygame.font.SysFont("segoeui", 11, bold=True)
        label_txt = font.render("SALVAGE DEPOT", True, (255, 225, 120))
        tag_surf.blit(label_txt, (22, tag_h // 2 - label_txt.get_height() // 2))
        surface.blit(tag_surf, (cx - tag_w // 2, cy + 38))


class MysteryCrate:
    """An underwater mystery crate that can be opened via pinch to reveal random contents."""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.radius = 32.0
        self.is_opened = False
        self.pulse_phase = random.uniform(0, math.pi * 2)
        self.revealed_timer = 0.0

    def update(self, dt: float, current_force_x: float = 0.0) -> None:
        self.pulse_phase += 3.0 * dt
        if current_force_x != 0:
            self.x += current_force_x * 0.15 * dt
            self.x = max(60.0, min(SCREEN_WIDTH - 60.0, self.x))

    def is_hovered(self, cx: float, cy: float) -> bool:
        if self.is_opened:
            return False
        return point_in_circle(cx, cy, self.x, self.y, self.radius + 25.0)

    def open_crate(self) -> Tuple[str, int, float, int]:
        """
        Opens crate. Returns (reward_type, score_val, oxygen_val, sonar_val).
        Possible rewards: 'OXYGEN', 'SONAR', 'TREASURE', 'BONUS', 'TRAP'
        """
        self.is_opened = True
        choices = ["OXYGEN", "SONAR", "TREASURE", "BONUS", "TRAP"]
        weights = [0.35, 0.25, 0.20, 0.12, 0.08]
        outcome = random.choices(choices, weights=weights)[0]
        if outcome == "OXYGEN":
            return ("OXYGEN", 50, 25.0, 0)
        elif outcome == "SONAR":
            return ("SONAR", 75, 0.0, 1)
        elif outcome == "TREASURE":
            return ("TREASURE", 250, 0.0, 0)
        elif outcome == "BONUS":
            return ("BONUS", 150, 0.0, 0)
        else:
            return ("TRAP", 0, -15.0, 0)

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_opened:
            return
        cx, cy = int(self.x), int(self.y)
        w, h = 54, 48
        rx, ry = cx - w // 2, cy - h // 2

        # 1. Seabed Feathered Ambient Occlusion Shadow
        sh_w, sh_h = w + 20, 22
        sh_surf = pygame.Surface((sh_w, sh_h), pygame.SRCALPHA)
        for step, a in [(1.0, 30), (0.75, 55), (0.50, 100)]:
            sw = int(sh_w * step)
            sh = max(4, int(sh_h * step))
            pygame.draw.ellipse(sh_surf, (4, 10, 20, a), ((sh_w - sw) // 2, (sh_h - sh) // 2, sw, sh))
        surface.blit(sh_surf, (cx - sh_w // 2, ry + h - 8))

        # 2. Weathered Sunken Oak Box Body (3 horizontal planks with subtle grain gradients)
        plank_h = h // 3
        plank_colors = [
            ((98, 70, 44), (74, 50, 28)),
            ((108, 78, 48), (80, 56, 32)),
            ((88, 62, 38), (66, 44, 24)),
        ]
        for pi in range(3):
            py = ry + pi * plank_h
            ph = plank_h if pi < 2 else (h - 2 * plank_h)
            top_col, bot_col = plank_colors[pi]
            # Plank base fill with bevel edge
            pygame.draw.rect(surface, top_col, (rx, py, w, ph), border_radius=2)
            pygame.draw.line(surface, bot_col, (rx + 1, py + ph - 1), (rx + w - 1, py + ph - 1), 2)
            # Subtle wood grain vein
            pygame.draw.line(surface, (top_col[0] - 12, top_col[1] - 10, top_col[2] - 8), (rx + 8, py + ph // 2), (rx + w - 8, py + ph // 2), 1)

        # 3. Forged Oxidized Iron Strapping & Perimeter Brackets
        strap_col = (42, 46, 52)
        highlight_col = (72, 78, 88)
        pygame.draw.rect(surface, strap_col, (rx, ry, w, h), width=3, border_radius=3)
        # Vertical reinforcing iron straps
        pygame.draw.line(surface, strap_col, (rx + 14, ry), (rx + 14, ry + h), 2)
        pygame.draw.line(surface, strap_col, (rx + w - 14, ry), (rx + w - 14, ry + h), 2)
        pygame.draw.line(surface, highlight_col, (rx + 15, ry), (rx + 15, ry + h), 1)

        # 4. Rusted Bronze Corner Plates & 3D Metallic Rivets
        corner_s = 10
        corner_pts = [
            (rx, ry),
            (rx + w - corner_s, ry),
            (rx, ry + h - corner_s),
            (rx + w - corner_s, ry + h - corner_s),
        ]
        for c_x, c_y in corner_pts:
            pygame.draw.rect(surface, (58, 64, 72), (c_x, c_y, corner_s, corner_s))
            pygame.draw.circle(surface, (190, 150, 75), (c_x + corner_s // 2, c_y + corner_s // 2), 2)
            pygame.draw.circle(surface, (255, 230, 160), (c_x + corner_s // 2 - 1, c_y + corner_s // 2 - 1), 1)

        # 5. Clinging Sea Barnacles & Deep Sea Emerald Algae Fronds
        # Barnacle clusters on bottom corners
        for bx, by in [(rx + 3, ry + h - 5), (rx + 8, ry + h - 3), (rx + w - 6, ry + h - 4)]:
            pygame.draw.circle(surface, (140, 145, 148), (bx, by), 3)
            pygame.draw.circle(surface, (45, 50, 55), (bx, by), 1)
        # Sea moss
        pygame.draw.circle(surface, (24, 78, 48), (rx + 2, ry + h - 2), 4)
        pygame.draw.circle(surface, (32, 92, 58), (rx + 6, ry + h - 1), 3)
        pygame.draw.circle(surface, (28, 85, 52), (rx + w - 4, ry + h - 2), 3)

        # 6. Sunken Royal Wax Seal & Glowing Atlantean Medallion
        pulse = (math.sin(self.pulse_phase) + 1.0) * 0.5
        seal_gold = (int(195 + 50 * pulse), int(155 + 40 * pulse), 55)
        # Embossed dark backing
        pygame.draw.circle(surface, (35, 24, 14), (cx, cy), 13)
        pygame.draw.circle(surface, seal_gold, (cx, cy), 11, 2)
        pygame.draw.circle(surface, (int(150 + 40 * pulse), int(115 + 30 * pulse), 35), (cx, cy), 8)
        # 5-pointed runic stars
        for ang in range(0, 360, 72):
            rad = math.radians(ang + 25.0)
            gx = cx + math.cos(rad) * 6.0
            gy = cy + math.sin(rad) * 6.0
            pygame.draw.circle(surface, (255, 235, 150), (int(gx), int(gy)), 1)


class AirBubbleStation:
    """An oxygen reef vent providing air to the diver."""
    def __init__(self, x: float, y: float = SCREEN_HEIGHT - 65.0):
        self.x = x
        self.y = y
        self.radius = 42.0
        self.cooldown = 0.0
        self.max_cooldown = 12.0
        self.pulse_phase = random.uniform(0, math.pi * 2)
        self.bubbles: List[Tuple[float, float, float, float]] = []

    def update(self, dt: float) -> None:
        self.pulse_phase += 3.5 * dt
        if self.cooldown > 0:
            self.cooldown = max(0.0, self.cooldown - dt)

        # Spawn rising oxygen bubbles
        if random.random() < 0.35:
            self.bubbles.append((
                self.x + random.uniform(-14, 14),
                self.y - 10,
                random.uniform(-50.0, -25.0),
                random.uniform(2.5, 5.0)
            ))

        new_b = []
        for bx, by, bvy, br in self.bubbles:
            by += bvy * dt
            if by > self.y - 85:
                new_b.append((bx, by, bvy, br))
        self.bubbles = new_b

    def check_restore(self, px: float, py: float) -> float:
        """Restores +25% oxygen if diver is within vent radius and station is ready."""
        if self.cooldown <= 0 and distance(px, py, self.x, self.y) <= self.radius:
            self.cooldown = self.max_cooldown
            return 25.0
        return 0.0

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = int(self.x), int(self.y)
        r = int(self.radius)
        is_ready = (self.cooldown <= 0)
        pulse = math.sin(self.pulse_phase)

        vent_tex = _get_vent_texture()
        if vent_tex:
            vw, vh = 86, 96
            # Soft seabed contact shadow
            sh_surf = pygame.Surface((vw + 20, 26), pygame.SRCALPHA)
            pygame.draw.ellipse(sh_surf, (4, 10, 20, 160), (0, 0, vw + 20, 26))
            surface.blit(sh_surf, (cx - (vw + 20) // 2, cy + 22))

            scaled_vent = pygame.transform.smoothscale(vent_tex, (vw, vh))
            surface.blit(scaled_vent, (cx - vw // 2, cy - vh // 2 + 4))

            # Chimney thermal vapor glow
            v_glow = pygame.Surface((36, 18), pygame.SRCALPHA)
            vapor_a = int(90 + 55 * pulse) if is_ready else 30
            pygame.draw.ellipse(v_glow, (*(COLOR_EMERALD if is_ready else COLOR_OCEAN_CYAN)[:3], vapor_a), (0, 0, 36, 18))
            surface.blit(v_glow, (cx - 18, cy - 28))
        else:
            # Fallback procedural vent rock
            pygame.draw.ellipse(surface, (38, 48, 56), (cx - 32, cy - 16, 64, 32))
            pygame.draw.ellipse(surface, (54, 68, 78), (cx - 28, cy - 14, 56, 26))
            pygame.draw.circle(surface, (180, 70, 110), (cx - 24, cy - 4), 5)
            pygame.draw.circle(surface, (70, 180, 160), (cx + 22, cy - 2), 6)
            pygame.draw.ellipse(surface, (14, 22, 28), (cx - 16, cy - 8, 32, 16))

        # Rising bubbles from vent aperture
        for bx, by, _, br in self.bubbles:
            ibr = max(2, int(br))
            b_surf = pygame.Surface((ibr * 2 + 4, ibr * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(b_surf, (200, 248, 255, 185), (ibr + 2, ibr + 2), ibr, 1)
            pygame.draw.circle(b_surf, (255, 255, 255), (ibr + 1, ibr + 1), max(1, ibr // 3))
            surface.blit(b_surf, (int(bx - ibr - 2), int(by - ibr - 2)))

        # Status Aura Beacon
        aura_alpha = int(70 + 35 * pulse) if is_ready else 25
        aura_col = (*COLOR_EMERALD[:3], aura_alpha) if is_ready else (70, 90, 110, 30)
        aura_surf = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, aura_col, (r + 5, r + 5), r, 2)
        surface.blit(aura_surf, (cx - r - 5, cy - r - 5))

        # Sleek Glassmorphic Dive Telemetry Badge
        font = pygame.font.SysFont("segoeui", 10, bold=True)
        lbl_text = "AIR +25% 🫧" if is_ready else f"RECHARGING {int(self.cooldown)}s"
        lbl_col = COLOR_EMERALD if is_ready else (160, 180, 195)
        txt_surf = font.render(lbl_text, True, lbl_col)
        pw = txt_surf.get_width() + 14
        ph = 20
        badge_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.rect(badge_surf, (8, 20, 32, 210), (0, 0, pw, ph), border_radius=10)
        pygame.draw.rect(badge_surf, (*lbl_col[:3], 150), (0, 0, pw, ph), width=1, border_radius=10)
        badge_surf.blit(txt_surf, (7, 2))
        surface.blit(badge_surf, (cx - pw // 2, cy - r - 22))


class TreasureManager:
    """Spawns, updates, reveals, and tracks all treasures, mystery crates, air stations, and the collection depot."""

    def __init__(self):
        self.treasures: List[Treasure] = []
        self.chest: TreasureChest = TreasureChest()
        self.mystery_crates: List[MysteryCrate] = []
        self.air_stations: List[AirBubbleStation] = []

    def clear(self) -> None:
        self.treasures.clear()
        self.mystery_crates.clear()
        self.air_stations.clear()

    def spawn_level_treasures(
        self,
        common_count: int,
        gold_count: int,
        rare_count: int,
        ancient_count: int,
        fake_count: int,
        trap_count: int,
        screen_w: int = 1280,
        screen_h: int = 720,
        key_count: int = 0,
        locked_chest_count: int = 0,
    ) -> None:
        """Spawns treasures across sea floor with neat, uncluttered spacing."""
        self.clear()
        
        # Place deposit chest on seabed with comfortable clearance from corner minimap
        chest_x = 210.0
        chest_y = screen_h - 75.0
        self.chest = TreasureChest(x=chest_x, y=chest_y)

        min_x = 320
        max_x = screen_w - 90
        min_y = 150
        max_y = screen_h - 110

        actual_keys = max(key_count, locked_chest_count) if locked_chest_count > 0 else key_count
        specs = (
            [(TreasureType.COMMON, 1) for _ in range(common_count)] +
            [(TreasureType.GOLD, 1) for _ in range(gold_count)] +
            [(TreasureType.RARE, 1) for _ in range(rare_count)] +
            [(TreasureType.ANCIENT, 1) for _ in range(ancient_count)] +
            [(TreasureType.FAKE, 1) for _ in range(fake_count)] +
            [(TreasureType.TRAP, 1) for _ in range(trap_count)] +
            [(TreasureType.KEY, 1) for _ in range(actual_keys)] +
            [(TreasureType.LOCKED_CHEST, 1) for _ in range(locked_chest_count)]
        )
        # Spawn heavy collectible treasure boxes across deeper seabed zones
        if locked_chest_count > 0 or ancient_count > 0:
            specs.append((TreasureType.HEAVY, 1))
        if locked_chest_count >= 2:
            specs.append((TreasureType.HEAVY, 1))
        random.shuffle(specs)

        for t_type, _ in specs:
            placed = False
            for attempt in range(100):
                candidate_x = random.uniform(min_x, max_x)
                candidate_y = random.uniform(min_y, max_y)
                req_spacing = 135.0 if attempt < 60 else 95.0
                # Keep distance from chest and other treasures for clean, neat placement
                if distance(candidate_x, candidate_y, chest_x, chest_y) > 140.0:
                    if all(distance(candidate_x, candidate_y, t.x, t.y) > req_spacing for t in self.treasures):
                        self.treasures.append(Treasure(candidate_x, candidate_y, t_type))
                        placed = True
                        break
            if not placed:
                self.treasures.append(Treasure(random.uniform(min_x, max_x), random.uniform(min_y, max_y), t_type))

        # Spawn Mystery Crates with clean spacing
        self.mystery_crates.append(MysteryCrate(random.uniform(400.0, 620.0), screen_h - 95.0))
        self.mystery_crates.append(MysteryCrate(random.uniform(760.0, 1060.0), screen_h - 95.0))

        # Spawn Air Bubble Stations with clean seabed spacing
        self.air_stations.append(AirBubbleStation(random.uniform(340.0, 520.0), screen_h - 55.0))
        self.air_stations.append(AirBubbleStation(random.uniform(840.0, 1140.0), screen_h - 55.0))

    def update(self, dt: float, current_active: bool = False, player_pos: Tuple[float, float] = None) -> None:
        force = 120.0 if current_active else 0.0
        for t in self.treasures:
            t.update(dt, force)

        for c in self.mystery_crates:
            c.update(dt, force)

        for a in self.air_stations:
            a.update(dt)

        player_is_near = False
        if player_pos:
            px, py = player_pos
            player_is_near = self.chest.is_in_deposit_zone(px, py)
        self.chest.update(dt, player_is_near)

    def trigger_sonar_wave(self, center_x: float, center_y: float, wave_radius: float) -> None:
        """Reveals treasures touched by expanding sonar wavefront."""
        for t in self.treasures:
            if not t.collected:
                dist = distance(center_x, center_y, t.x, t.y)
                if abs(dist - wave_radius) < 65.0 or dist < wave_radius:
                    t.reveal()

    def get_hovered_treasure(self, cursor_x: float, cursor_y: float) -> Optional[Treasure]:
        """Returns the closest uncollected, uncarried treasure within reach."""
        closest_t = None
        min_dist = float('inf')
        for t in self.treasures:
            if not t.collected and not t.is_carried:
                d = distance(cursor_x, cursor_y, t.x, t.y)
                if d <= (t.radius + 26.0) and d < min_dist:
                    min_dist = d
                    closest_t = t
        return closest_t

    def get_hovered_crate(self, cursor_x: float, cursor_y: float) -> Optional[MysteryCrate]:
        """Returns the first un-opened mystery crate within reach."""
        for c in self.mystery_crates:
            if c.is_hovered(cursor_x, cursor_y):
                return c
        return None

    def check_air_stations(self, px: float, py: float) -> float:
        """Checks if diver is in contact with any ready air station, returning restored oxygen amount."""
        total_restored = 0.0
        for a in self.air_stations:
            restored = a.check_restore(px, py)
            if restored > 0.0:
                total_restored += restored
        return total_restored

    def draw(self, surface: pygame.Surface) -> None:
        # Draw Air Bubble Stations on Seafloor
        for a in self.air_stations:
            a.draw(surface)

        # Draw Seafloor Deposit Vault Chest
        self.chest.draw(surface)

        # Draw Mystery Crates
        for c in self.mystery_crates:
            c.draw(surface)

        # Draw Uncollected Treasures
        for t in self.treasures:
            t.draw(surface)

    def remaining_real_treasures(self) -> int:
        """Returns count of remaining uncollected genuine relics."""
        return sum(1 for t in self.treasures if not t.collected and t.type not in (TreasureType.FAKE, TreasureType.TRAP))
