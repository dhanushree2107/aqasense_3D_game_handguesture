"""
Underwater Treasure Hunt - Photorealistic 3D HD Relic & Artifact Rendering Engine
Renders the 8 historical oceanic wonders with:
- 1024x1024 Ultra-HD photorealistic textures with smooth alpha channels
- Real-time 3D yaw, pitch, and depth perspective deformation linked to hand tracking
- Dynamic 3D directional specular gleam responding to hand cursor lighting vector
- Dynamic pedestal contact shadow that shifts and scales with 3D orientation
- Ethereal underwater aura and bioluminescent core pulsing
- Seamless scaling from mini vitrines (r=14) to monumental inspection modal (r=75)
"""

import math
import os
import time
from typing import Dict, List, Optional, Tuple
import pygame

from config import (
    COLOR_GOLD,
    COLOR_OCEAN_CYAN,
    COLOR_NEON_TEAL,
    COLOR_WHITE,
    COLOR_CORAL_RED,
    COLOR_EMERALD,
    COLOR_PURPLE_MYSTIC,
    COLOR_AMBER_WARNING,
)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")


class HDRelicRenderer:
    """
    Ultra-high-definition 3D rendering pipeline for the 8 historical ocean relics.
    Combines 1024x1024 museum-grade photorealistic asset textures with real-time
    3D perspective rotation, dynamic directional specular lighting, and volumetric auras.
    """

    _cached_textures: Dict[str, pygame.Surface] = {}
    _scaled_cache: Dict[Tuple[str, int, int], pygame.Surface] = {}

    @classmethod
    def get_texture(cls, relic_id: str) -> Optional[pygame.Surface]:
        """Loads and caches the 1024x1024 HD relic texture."""
        if relic_id in cls._cached_textures:
            return cls._cached_textures[relic_id]

        path = os.path.join(ASSETS_DIR, f"relic_{relic_id}.png")
        if not os.path.exists(path):
            # Fallback for heavy chest
            if relic_id == "heavy_chest":
                alt_path = os.path.join(ASSETS_DIR, "treasure_chest.png")
                if os.path.exists(alt_path):
                    path = alt_path

        if os.path.exists(path):
            try:
                loaded = pygame.image.load(path)
                has_display = (pygame.display.get_surface() is not None)
                if has_display:
                    try:
                        loaded = loaded.convert_alpha()
                    except Exception:
                        pass
                cls._cached_textures[relic_id] = loaded
                return loaded
            except Exception:
                pass

        return None

    @classmethod
    def draw_relic(
        cls,
        surface: pygame.Surface,
        relic_id: str,
        cx: int,
        cy: int,
        radius: int,
        is_unlocked: bool = True,
        is_modal: bool = False,
        light_offset: Tuple[float, float] = (0.0, 0.0),
        yaw: float = 0.0,
        pitch: float = 0.0,
        dual_lift_prog: float = 0.0,
        chest_opened: bool = False,
        pulse_phase: float = 0.0,
    ) -> None:
        """
        Renders a photorealistic 3D relic at (cx, cy) with given radius.
        Supports continuous 3D yaw and pitch rotation and dynamic lighting.
        """
        if not is_unlocked:
            cls._draw_locked_vault_icon(surface, cx, cy, radius, is_modal)
            return

        tex = cls.get_texture(relic_id)
        if tex is None:
            # Fallback procedural lock icon if file missing
            cls._draw_locked_vault_icon(surface, cx, cy, radius, is_modal)
            return

        # 1. 3D Orientation & Perspective Deformation
        cos_y = math.cos(yaw)
        sin_y = math.sin(yaw)
        cos_p = math.cos(pitch)
        sin_p = math.sin(pitch)

        # 3D Foreshortening
        scale_x = max(0.24, abs(cos_y))
        scale_y = max(0.85, 1.0 - 0.12 * abs(sin_p))

        # Destination dimensions
        target_diam = radius * 2
        dw = max(10, int(target_diam * scale_x))
        dh = max(10, int(target_diam * scale_y))

        # Vertical depth offset from pitch
        tilt_oy = int(sin_p * (radius * 0.22))
        relic_center_y = cy + tilt_oy

        # 2. Dynamic Pedestal Contact Shadow (Realistic Feathered Ambient Occlusion)
        sh_w = int(radius * 1.7 * (0.85 + 0.15 * scale_x))
        sh_h = max(6, int(radius * 0.40 * scale_y))
        sh_ox = int(-sin_y * 8)
        sh_oy = int(radius * 0.80) + tilt_oy // 2

        sh_surf = pygame.Surface((sh_w + 24, sh_h + 16), pygame.SRCALPHA)
        # 3-tier feathered falloff
        for step, a in [(1.0, 35), (0.75, 55), (0.50, 95)]:
            sw_step = int(sh_w * step)
            sh_step = max(3, int(sh_h * step))
            pygame.draw.ellipse(sh_surf, (8, 20, 36, a), ((sh_w + 24 - sw_step) // 2, (sh_h + 16 - sh_step) // 2, sw_step, sh_step))
        surface.blit(sh_surf, (cx - (sh_w + 24) // 2 + sh_ox, relic_center_y + sh_oy - (sh_h + 16) // 2))

        # 3. Ethereal Subsurface Ambient Ocean Radiance (Modal inspection or legendary relics)
        if is_modal or relic_id in ("ancient_crown", "sapphire_chalice"):
            aura_r = int(radius * (1.35 if is_modal else 1.15))
            aura_surf = pygame.Surface((aura_r * 2 + 16, aura_r * 2 + 16), pygame.SRCALPHA)
            pulse_a = int(35 + 20 * math.sin(pulse_phase * 2.2))
            if relic_id in ("ancient_crown", "gold_coin", "heavy_chest"):
                aura_col = (255, 215, 60)
            elif relic_id == "guardian_seal":
                aura_col = (185, 110, 255)
            else:
                aura_col = (0, 220, 255)
            for step, a_mult in [(1.0, 0.3), (0.75, 0.6), (0.50, 1.0)]:
                cur_r = int(aura_r * step)
                pygame.draw.circle(aura_surf, (*aura_col[:3], int(pulse_a * a_mult)), (aura_r + 8, aura_r + 8), cur_r)
            surface.blit(aura_surf, (cx - aura_r - 8, relic_center_y - aura_r - 8))

        # 4. Bilinear Smoothscale Render of Photorealistic Asset
        scaled = pygame.transform.smoothscale(tex, (dw, dh))

        # If yaw is negative, flip horizontally for natural 3D turnover
        if cos_y < 0 and relic_id not in ("gold_coin", "guardian_seal", "coral_compass", "pearl"):
            scaled = pygame.transform.flip(scaled, True, False)

        dest_x = cx - dw // 2
        dest_y = relic_center_y - dh // 2
        surface.blit(scaled, (dest_x, dest_y))

        # 5. Dual-Hand Lift Effect for Heavy Chest
        effective_lift = max(dual_lift_prog, 1.0 if chest_opened else 0.0)
        if relic_id == "heavy_chest" and effective_lift > 0.05:
            lift_h = int(effective_lift * (dh * 0.45))
            burst_surf = pygame.Surface((dw + 40, lift_h + 30), pygame.SRCALPHA)
            burst_poly = [
                (20, lift_h + 15),
                (dw + 20, lift_h + 15),
                (dw + 35, 0),
                (5, 0),
            ]
            burst_a = int(120 + 70 * math.sin(pulse_phase * 3.5))
            pygame.draw.polygon(burst_surf, (255, 225, 90, burst_a), burst_poly)
            surface.blit(burst_surf, (dest_x - 20, dest_y - lift_h - 10))

        # 6. Dynamic Directional 3D Specular Sheen (Moves with Hand Cursor)
        lx, ly = light_offset
        ldist = math.hypot(lx, ly)
        if ldist > 0.01:
            lnx, lny = lx / ldist, ly / ldist
        else:
            lnx, lny = -0.55, -0.65

        # Glint highlight shifts on the 3D surface
        glint_cx = cx + int(lnx * (dw * 0.28) + sin_y * 8)
        glint_cy = relic_center_y + int(lny * (dh * 0.28) + sin_p * 8)
        glint_r = max(2, int(radius * (0.16 if is_modal else 0.10)))

        # Specular glint star
        glint_surf = pygame.Surface((glint_r * 6 + 4, glint_r * 6 + 4), pygame.SRCALPHA)
        g_center = glint_r * 3 + 2
        pygame.draw.circle(glint_surf, (255, 255, 255, 180), (g_center, g_center), glint_r)
        pygame.draw.line(glint_surf, (255, 255, 255, 220), (g_center - glint_r * 2, g_center), (g_center + glint_r * 2, g_center), 2)
        pygame.draw.line(glint_surf, (255, 255, 255, 220), (g_center, g_center - glint_r * 2), (g_center, g_center + glint_r * 2), 2)
        surface.blit(glint_surf, (glint_cx - g_center, glint_cy - g_center))

    # =========================================================================
    # LOCKED VAULT EMBLEM
    # =========================================================================

    @classmethod
    def _draw_locked_vault_icon(cls, surface: pygame.Surface, cx: int, cy: int, r: int, is_modal: bool) -> None:
        """Renders an ancient heavy locked iron-and-gold shackle for uncataloged wonders."""
        body_w = int(r * 1.35)
        body_h = int(r * 1.05)
        bx = cx - body_w // 2
        by = cy - body_h // 2 + int(r * 0.22)
        shackle_r = int(r * 0.44)

        # Ambient drop shadow
        sh_surf = pygame.Surface((body_w + 14, body_h + 14), pygame.SRCALPHA)
        pygame.draw.rect(sh_surf, (4, 10, 20, 130), (0, 0, body_w + 14, body_h + 14), border_radius=7)
        surface.blit(sh_surf, (bx - 7, by - 4))

        # Heavy forged shackle
        pygame.draw.arc(surface, (255, 215, 60), (cx - shackle_r, by - shackle_r * 2 + 4, shackle_r * 2, shackle_r * 2), 0, math.pi, max(2, int(r * 0.12)))
        pygame.draw.arc(surface, (140, 100, 20), (cx - shackle_r, by - shackle_r * 2 + 4, shackle_r * 2, shackle_r * 2), 0, math.pi, 1)

        # Obsidian lock body with beveled gold trim
        pygame.draw.rect(surface, (12, 22, 38), (bx, by, body_w, body_h), border_radius=6)
        pygame.draw.rect(surface, (255, 215, 60), (bx, by, body_w, body_h), width=2, border_radius=6)
        pygame.draw.rect(surface, (30, 60, 95), (bx + 3, by + 3, body_w - 6, body_h - 6), width=1, border_radius=4)

        # Mystical runic keyhole
        pygame.draw.circle(surface, (255, 215, 60), (cx, by + body_h // 2 - 2), max(2, int(r * 0.10)))
        pygame.draw.polygon(surface, (255, 215, 60), [
            (cx - int(r * 0.08), by + body_h // 2 - 2),
            (cx + int(r * 0.08), by + body_h // 2 - 2),
            (cx + int(r * 0.05), by + body_h // 2 + int(r * 0.22)),
            (cx - int(r * 0.05), by + body_h // 2 + int(r * 0.22)),
        ])
