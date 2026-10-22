"""
Underwater Treasure Hunt - UI Button Component
Provides glassmorphism styling, hover glow animations, sound effects,
and dual interaction support (both Mouse click and Hand Pinch).
"""

import math
import time
from typing import Callable, Optional, Tuple
import pygame

from config import (
    COLOR_NEON_TEAL,
    COLOR_OCEAN_CYAN,
    COLOR_GOLD,
    COLOR_WHITE,
    COLOR_DARK_OVERLAY,
)
from audio.sound_manager import SoundManager

class Button:
    """A polished glassmorphic interactive UI button."""

    @staticmethod
    def clean_label(text: str) -> str:
        """Removes special unicode/emoji symbols that render as hollow tofu outline boxes in Pygame SysFont."""
        replacements = {
            "▶": ">",
            "◀": "<",
            "⟳": "",
            "⚡": "",
            "🗺️": "",
            "🏛️": "",
            "🗺": "",
            "🏛": "",
            "✓": "OK",
            "✌️": "",
            "🤏": "",
            "✋": "",
            "✊": "",
            "⭐": "*",
            "🔥": "",
            "🔒": "",
            "📦": "",
            "💎": "",
            "🎁": "",
            "❤️": "",
            "🖤": "",
        }
        cleaned = text
        for k, v in replacements.items():
            cleaned = cleaned.replace(k, v)
        return " ".join(cleaned.split())

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        font_size: int = 22,
        on_click: Optional[Callable[[], None]] = None,
        sound_manager: Optional[SoundManager] = None,
        accent_color: Tuple[int, int, int] = COLOR_NEON_TEAL
    ):
        if not pygame.font.get_init():
            pygame.font.init()
        self.rect = rect
        self.raw_text = text
        self.text = self.clean_label(text)
        self.font = pygame.font.SysFont("segoeui", font_size, bold=True)
        self.on_click = on_click
        self.sound_manager = sound_manager
        self.accent_color = accent_color

        self.is_hovered: bool = False
        self.prev_hovered: bool = False
        self.hover_progress: float = 0.0
        self.click_anim_time: float = 0.0
        self.hover_dwell_time: float = 0.0
        self.dwell_threshold: float = 0.50  # 0.50s of steady pointing automatically clicks!
        self.prev_clicked: bool = False

    def update(self, cursor_x: int, cursor_y: int, is_clicked: bool, dt: float = 0.016) -> bool:
        """
        Updates button hover and click states.
        Triggers on:
        - Instant Click (Index Tap / Pinch / Left Mouse Click)
        - Hover Dwell (Holding cursor steadily over button for 0.5s)
        """
        self.is_hovered = self.rect.collidepoint(cursor_x, cursor_y)
        
        # Audio feedback on hover enter
        if self.is_hovered and not self.prev_hovered:
            if self.sound_manager:
                self.sound_manager.play('hover', volume_mult=0.4)

        # Smooth hover expansion interpolation
        target_hover = 1.0 if self.is_hovered else 0.0
        self.hover_progress += (target_hover - self.hover_progress) * min(1.0, 14.0 * dt)

        if self.click_anim_time > 0:
            self.click_anim_time -= dt

        # Dwell progress accumulation
        if self.is_hovered:
            self.hover_dwell_time += dt
        else:
            self.hover_dwell_time = max(0.0, self.hover_dwell_time - dt * 2.0)

        dwell_triggered = (self.hover_dwell_time >= self.dwell_threshold)

        # Clean click triggering:
        # 1. Pinch/click initiated while hovered on button
        # 2. Entering button while already holding pinch/click
        click_edge = (is_clicked and not self.prev_clicked and self.is_hovered) or (is_clicked and self.is_hovered and not self.prev_hovered)
        self.prev_clicked = is_clicked
        self.prev_hovered = self.is_hovered

        # Trigger action if clicked (pinch/tap/mouse) OR dwell-hovered
        if self.is_hovered and (click_edge or dwell_triggered):
            self.click_anim_time = 0.18
            self.hover_dwell_time = -0.5  # Brief pause before re-arming dwell
            if self.sound_manager:
                self.sound_manager.play('click', volume_mult=0.8)
            if self.on_click:
                self.on_click()
            return True

        return False

    def _draw_vector_icon(self, surface: pygame.Surface, icon_type: str, cx: int, cy: int, color: Tuple[int, int, int]) -> None:
        """Renders crisp glowing vector icons corresponding to button function."""
        if icon_type == "play":
            pts = [(cx - 6, cy - 7), (cx + 7, cy), (cx - 6, cy + 7)]
            pygame.draw.polygon(surface, color, pts)
            pygame.draw.polygon(surface, (255, 255, 255), pts, width=1)
        elif icon_type == "pin":
            pygame.draw.circle(surface, color, (cx, cy - 4), 6)
            pygame.draw.circle(surface, (8, 24, 45), (cx, cy - 4), 2)
            pygame.draw.polygon(surface, color, [(cx - 4, cy - 2), (cx + 4, cy - 2), (cx, cy + 7)])
        elif icon_type == "temple":
            pygame.draw.polygon(surface, color, [(cx - 8, cy - 3), (cx + 8, cy - 3), (cx, cy - 8)])
            pygame.draw.line(surface, color, (cx - 9, cy + 6), (cx + 9, cy + 6), 2)
            pygame.draw.line(surface, color, (cx - 6, cy - 2), (cx - 6, cy + 5), 2)
            pygame.draw.line(surface, color, (cx, cy - 2), (cx, cy + 5), 2)
            pygame.draw.line(surface, color, (cx + 6, cy - 2), (cx + 6, cy + 5), 2)
        elif icon_type == "fish":
            pygame.draw.ellipse(surface, color, (cx - 8, cy - 5, 12, 10))
            pygame.draw.polygon(surface, color, [(cx + 2, cy), (cx + 8, cy - 5), (cx + 8, cy + 5)])
            pygame.draw.circle(surface, (8, 24, 45), (cx - 4, cy - 2), 1)
        elif icon_type == "hand":
            pygame.draw.rect(surface, color, (cx - 5, cy - 2, 10, 8), border_radius=2)
            pygame.draw.line(surface, color, (cx - 4, cy - 2), (cx - 4, cy - 7), 2)
            pygame.draw.line(surface, color, (cx - 1, cy - 2), (cx - 1, cy - 9), 2)
            pygame.draw.line(surface, color, (cx + 2, cy - 2), (cx + 2, cy - 8), 2)
            pygame.draw.line(surface, color, (cx + 5, cy - 2), (cx + 5, cy - 6), 2)
            pygame.draw.line(surface, color, (cx - 5, cy + 1), (cx - 8, cy - 2), 2)
        elif icon_type == "camera":
            pygame.draw.rect(surface, color, (cx - 8, cy - 4, 16, 11), border_radius=2)
            pygame.draw.rect(surface, color, (cx - 4, cy - 7, 8, 3), border_radius=1)
            pygame.draw.circle(surface, (8, 24, 45), (cx, cy + 1), 4)
            pygame.draw.circle(surface, color, (cx, cy + 1), 4, width=1)
            pygame.draw.circle(surface, (255, 255, 255), (cx + 4, cy - 2), 1)
        elif icon_type == "power":
            pygame.draw.arc(surface, color, (cx - 7, cy - 7, 14, 14), 0.6, 5.68, 2)
            pygame.draw.line(surface, color, (cx, cy - 8), (cx, cy - 1), 2)

    def draw(self, surface: pygame.Surface) -> None:
        """Renders the button as a futuristic underwater holographic chamfered panel with glow and dwell meter."""
        expand = int(self.hover_progress * 4)
        draw_rect = self.rect.inflate(expand * 2, expand * 2)
        w, h = draw_rect.width, draw_rect.height
        c = 10  # Chamfer size

        # Chamfered polygon points (8-point beveled rectangle)
        points = [
            (c, 0),
            (w - c, 0),
            (w, c),
            (w, h - c),
            (w - c, h),
            (c, h),
            (0, h - c),
            (0, c),
        ]

        # 1. Semi-transparent Holographic Glass Background
        glass_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        bg_alpha = int(155 + self.hover_progress * 65)

        if self.click_anim_time > 0:
            bg_col = (18, 75, 125, 220)
        elif self.is_hovered:
            bg_col = (10, 42, 75, bg_alpha)
        else:
            bg_col = (6, 26, 50, bg_alpha)

        pygame.draw.polygon(glass_surf, bg_col, points)

        # 2. Specular Top Glass Sheen
        sheen_color = (200, 245, 255, int(80 + self.hover_progress * 60))
        pygame.draw.line(glass_surf, sheen_color, (c + 2, 2), (w - c - 2, 2), 1)

        # Subtle animated light sweep across glass
        sheen_phase = (time.time() * 0.8) % 3.0
        if sheen_phase < 1.0:
            sweep_x = int(sheen_phase * (w + 60) - 30)
            sheen_poly = [
                (sweep_x, 0),
                (sweep_x + 16, 0),
                (sweep_x - 12, h),
                (sweep_x - 28, h)
            ]
            pygame.draw.polygon(glass_surf, (220, 250, 255, int(30 + self.hover_progress * 25)), sheen_poly)

        # 3. Holographic Border & Outer Glow
        border_col = self.accent_color if self.is_hovered else (0, 195, 235)
        if self.is_hovered:
            halo_surf = pygame.Surface((w + 12, h + 12), pygame.SRCALPHA)
            halo_pts = [(p[0] + 6, p[1] + 6) for p in points]
            pygame.draw.polygon(halo_surf, (*border_col[:3], 55), halo_pts, width=4)
            surface.blit(halo_surf, (draw_rect.x - 6, draw_rect.y - 6))

        # Primary crisp border
        border_width = 2 if not self.is_hovered else 3
        pygame.draw.polygon(glass_surf, border_col, points, width=border_width)

        surface.blit(glass_surf, draw_rect.topleft)

        # 4. Determine and Render Vector Icon
        icon_type = None
        raw_upper = (self.raw_text + " " + self.text).upper()
        if "CAMERA" in raw_upper:
            icon_type = "camera"
        elif "HOW TO" in raw_upper or "GESTURE" in raw_upper:
            icon_type = "hand"
        elif "MUSEUM" in raw_upper:
            icon_type = "temple"
        elif "CHALLENGE" in raw_upper:
            icon_type = "fish"
        elif "ZONE" in raw_upper or "LEVEL" in raw_upper or "MAP" in raw_upper:
            icon_type = "pin"
        elif "START" in raw_upper or "EXPEDITION >" in raw_upper or (raw_upper.startswith("PLAY") and "HOW" not in raw_upper):
            icon_type = "play"
        elif "QUIT" in raw_upper or "EXIT" in raw_upper:
            icon_type = "power"

        icon_col = (140, 235, 255) if not self.is_hovered else (220, 255, 255)
        if icon_type:
            self._draw_vector_icon(surface, icon_type, draw_rect.left + 26, draw_rect.centery, icon_col)

        # For "START EXPEDITION", draw chevron on right
        is_start = ("START" in raw_upper)
        if is_start:
            ch_x = draw_rect.right - 26
            ch_y = draw_rect.centery
            ch_col = (160, 240, 255) if not self.is_hovered else (255, 255, 255)
            pygame.draw.lines(surface, ch_col, False, [(ch_x - 5, ch_y - 6), (ch_x + 1, ch_y), (ch_x - 5, ch_y + 6)], 2)

        # 5. Dwell Progress Meter
        if self.is_hovered and self.hover_dwell_time > 0:
            pct = min(1.0, max(0.0, self.hover_dwell_time / self.dwell_threshold))
            if pct > 0:
                bar_w = int((draw_rect.width - 24) * pct)
                bar_rect = pygame.Rect(draw_rect.left + 12, draw_rect.bottom - 4, bar_w, 3)
                pygame.draw.rect(surface, (0, 220, 255), bar_rect, border_radius=2)
                pygame.draw.circle(surface, (255, 255, 255), (bar_rect.right, bar_rect.centery), 2)

        # 6. Text Label perfectly centered inside button
        display_text = self.text
        if is_start and display_text.endswith(">"):
            display_text = display_text.rstrip(">").strip()

        text_col = COLOR_WHITE if not self.is_hovered else (225, 255, 255)
        text_surf = self.font.render(display_text, True, text_col)
        tx = draw_rect.centerx - text_surf.get_width() // 2
        ty = draw_rect.centery - text_surf.get_height() // 2

        shadow_surf = self.font.render(display_text, True, (2, 8, 18))
        surface.blit(shadow_surf, (tx + 1, ty + 1))
        surface.blit(text_surf, (tx, ty))
