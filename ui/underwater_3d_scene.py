"""
Underwater Treasure Hunt - Real-time 3D Cinematic Underwater Environment
Provides a photorealistic, dynamic, multi-layered 3D underwater simulation with:
- Volumetric ocean atmosphere and depth fog attenuation
- Distant sunken Spanish galleon shipwreck and ancient Atlantean ruins
- Fully animated 3D sea creatures with realistic physics, body deformation, and locomotion:
  * Great White Shark (carangiform tail and body undulation, silver-gray skin, white belly, depth fog, sunbeam illumination)
  * Green Sea Turtle (chelonian flipper stroke propulsion, dynamic surging, pitch/yaw banking, sunlight gleam)
  * Multiple Fish Schools at distinct 3D depths (Foreground tropical reef fish, Midground boid school, Distant deep ocean shoal)
  * Giant Manta Ray with undulating wingtip flexion
  * Bioluminescent Jellyfish with rhythmic bell contraction and natural glow
- Lush coral reef floor, swaying multi-joint kelp fronds, and dynamic dual-layer water caustics
- Glistening 3D antique treasure chest with glowing aura and floating gold motes
- Multi-plane cinematic camera with subtle sway, drift, and parallax
"""

import math
import os
import random
import time
from typing import List, Optional, Tuple
import pygame

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_NEON_TEAL,
    COLOR_OCEAN_CYAN,
    COLOR_GOLD,
    COLOR_WHITE,
    COLOR_EMERALD,
    COLOR_CORAL_RED,
)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")


class CinematicCamera:
    """Simulates a floating underwater cinematic camera with natural sway and parallax."""

    def __init__(self):
        self.time = 0.0
        self.sway_x = 0.0
        self.sway_y = 0.0
        self.target_parallax_x = 0.0
        self.target_parallax_y = 0.0
        self.current_parallax_x = 0.0
        self.current_parallax_y = 0.0

    def update(self, dt: float, cursor_x: float = SCREEN_WIDTH / 2, cursor_y: float = SCREEN_HEIGHT / 2) -> None:
        self.time += dt
        # Gentle natural oceanic surge and sway (smooth multi-frequency sines)
        self.sway_x = math.sin(self.time * 0.35) * 14.0 + math.sin(self.time * 0.75) * 5.0
        self.sway_y = math.cos(self.time * 0.28) * 9.0 + math.sin(self.time * 0.55) * 3.5

        # Subtle responsive parallax relative to center (max 20px offset)
        norm_cx = (cursor_x - SCREEN_WIDTH / 2) / (SCREEN_WIDTH / 2)
        norm_cy = (cursor_y - SCREEN_HEIGHT / 2) / (SCREEN_HEIGHT / 2)
        self.target_parallax_x = norm_cx * 20.0
        self.target_parallax_y = norm_cy * 12.0

        # Smooth damping
        self.current_parallax_x += (self.target_parallax_x - self.current_parallax_x) * min(1.0, 3.5 * dt)
        self.current_parallax_y += (self.target_parallax_y - self.current_parallax_y) * min(1.0, 3.5 * dt)

    def get_offset(self, depth_factor: float = 1.0) -> Tuple[float, float]:
        """Returns (ox, oy) for a layer given its depth factor (0.0 = infinite distance, 1.0 = near foreground)."""
        ox = (self.sway_x + self.current_parallax_x) * depth_factor
        oy = (self.sway_y + self.current_parallax_y) * depth_factor
        return ox, oy


# =========================================================================
# 1. GREAT WHITE SHARK — REALISTIC 3D ANIMATION & NATURAL LIGHTING
# =========================================================================

class RealisticShark3D:
    """
    Apex predator Great White Shark swimming realistically through the mid-to-deep background:
    - Sleek steel-gray dorsal and pure white underbelly with photorealistic skin countershading
    - Realistic carangiform swimming wave: snout and gills steady, trunk and caudal fin flex smoothly
    - Smooth 3D turning with yaw foreshortening and banking pitch
    - Clean masked caustic sunbeam illumination preserving 100% solid opacity with zero box artifacts
    - Swims gracefully across the upper sunlit open ocean corridor
    """

    def __init__(self, surface: Optional[pygame.Surface]):
        self.base_surface = surface
        # Start in mid-upper open water column, swimming left-to-right
        self.x = SCREEN_WIDTH * 0.18
        self.y = SCREEN_HEIGHT * 0.14
        self.z = 0.45
        self.base_speed = 46.0
        self.speed = self.base_speed
        self.direction = 1  # Swimming right across sunlit open corridor
        self.target_direction = 1

        self.swim_phase = random.uniform(0, math.pi * 2)
        self.tail_frequency = 3.6
        self.tail_amplitude = 11.0

        # 3D Turning dynamics
        self.is_turning = False
        self.turn_timer = 0.0
        self.turn_duration = 2.4
        self.turn_scale_x = 1.0

        # Vertical wandering path
        self.wander_phase = random.uniform(0, math.pi * 2)
        self.pitch = 0.0
        self.target_w = 400

    def update(self, dt: float) -> None:
        self.swim_phase += self.tail_frequency * dt
        self.wander_phase += 0.40 * dt

        surge = (math.sin(self.swim_phase * 2.0) + 1.0) * 0.5
        current_speed = self.base_speed * (0.88 + surge * 0.24)

        if self.is_turning:
            self.turn_timer += dt
            prog = min(1.0, self.turn_timer / self.turn_duration)
            self.turn_scale_x = math.cos(prog * math.pi)
            self.pitch = math.sin(prog * math.pi) * (4.5 * -self.direction)

            if prog >= 1.0:
                self.is_turning = False
                self.direction = self.target_direction
                self.turn_scale_x = 1.0
                self.pitch = 0.0
        else:
            vy = math.sin(self.wander_phase) * 7.0
            self.y += vy * dt
            self.pitch = math.sin(self.wander_phase) * 2.0
            self.x += current_speed * self.direction * dt

            # Patrol boundaries triggering smooth 3D turn
            if self.direction == 1 and self.x > SCREEN_WIDTH + 240:
                self.start_turn(-1)
            elif self.direction == -1 and self.x < -240:
                self.start_turn(1)

        # Depth wandering between 0.42 and 0.48
        self.z = 0.45 + math.sin(self.wander_phase * 0.5) * 0.03

    def start_turn(self, new_dir: int) -> None:
        if not self.is_turning:
            self.is_turning = True
            self.turn_timer = 0.0
            self.target_direction = new_dir
            self.y = random.uniform(SCREEN_HEIGHT * 0.12, SCREEN_HEIGHT * 0.16)

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float], time_sec: float) -> None:
        if not self.base_surface:
            return

        ox, oy = cam_offset
        eff_scale = (self.z / 0.40)
        w = max(24, int(self.target_w * eff_scale * abs(self.turn_scale_x)))
        aspect = self.base_surface.get_height() / self.base_surface.get_width()
        h = max(12, int(self.target_w * aspect * eff_scale))

        scaled = pygame.transform.smoothscale(self.base_surface, (w, h))

        current_sign = self.direction * (1 if self.turn_scale_x >= 0 else -1)
        facing_left = (current_sign == -1)
        if not facing_left:
            scaled = pygame.transform.flip(scaled, True, False)

        # Realistic Carangiform Swimming Deformation (32 Slices for fluid curvature)
        num_slices = 32
        slice_step = w / num_slices
        slice_w = int(math.ceil(slice_step)) + 1
        max_pad_y = 35
        bent_surf = pygame.Surface((w + 30, h + max_pad_y * 2), pygame.SRCALPHA)

        for i in range(num_slices):
            # Ratio: 0 is head/snout, 1 is caudal tail
            ratio = i / (num_slices - 1) if facing_left else (1.0 - i / (num_slices - 1))
            # True Carangiform kinematics: head (ratio < 0.25) stays firm, body & tail propel
            amp = (ratio ** 2.4) * self.tail_amplitude

            phase_offset = ratio * 3.6
            offset_y = math.sin(self.swim_phase - phase_offset) * amp

            sx = int(i * slice_step)
            cur_sw = slice_w if sx + slice_w <= w else (w - sx)

            if cur_sw > 0:
                rect = pygame.Rect(sx, 0, cur_sw, h)
                bent_surf.blit(scaled, (sx + 15, max_pad_y + offset_y), rect)

        # Crisp Photorealistic Ocean Lighting (Preserving dark dorsal & white belly contrast)
        sun_center = SCREEN_WIDTH * 0.50
        sun_spread = SCREEN_WIDTH * 0.35
        dist_to_sun = abs(self.x - sun_center)
        sun_factor = max(0.0, 1.0 - dist_to_sun / sun_spread) if dist_to_sun < sun_spread else 0.0

        r = int(215 + 40 * sun_factor)
        g = int(230 + 25 * sun_factor)
        b = int(248 + 7 * sun_factor)

        tint_surf = pygame.Surface(bent_surf.get_size(), pygame.SRCALPHA)
        tint_surf.fill((min(255, r), min(255, g), min(255, b), 255))
        bent_surf.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        # Realistic sunlight caustic gleam along dorsal spine (CLEANLY MASKED with shark alpha)
        caustic_wave = math.sin(time_sec * 2.8 + self.x * 0.012) * 0.5 + 0.5
        caustic_val = int(24 * caustic_wave + 14 * sun_factor)
        if caustic_val > 0:
            spec_surf = pygame.Surface(bent_surf.get_size(), pygame.SRCALPHA)
            spec_surf.fill((int(caustic_val * 0.75), int(caustic_val * 0.9), int(caustic_val * 1.1), 255))
            spec_surf.blit(bent_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            bent_surf.blit(spec_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        final_surf = pygame.transform.rotate(bent_surf, self.pitch)

        rx = int(self.x + ox * self.z - final_surf.get_width() / 2)
        ry = int(self.y + oy * self.z - final_surf.get_height() / 2)
        target.blit(final_surf, (rx, ry))


# =========================================================================
# 2. GREEN SEA TURTLE — CHELONIAN FLIPPER STROKE PROPULSION
# =========================================================================

def generate_turtle_stroke_surfaces(base_surface: Optional[pygame.Surface], num_frames: int = 16) -> List[pygame.Surface]:
    """Pre-renders 16 articulated flipper hydrodynamic deflection frames preserving 100% rigid shell & head."""
    if not base_surface:
        return []
    try:
        import cv2
        import numpy as np

        w, h = base_surface.get_size()
        raw_bytes = pygame.image.tostring(base_surface, "RGBA")
        arr = np.frombuffer(raw_bytes, dtype=np.uint8).reshape((h, w, 4))

        shoulder_x, shoulder_y = w * 0.355, h * 0.650
        map_x_base = np.tile(np.arange(w, dtype=np.float32), (h, 1))
        map_y_base = np.tile(np.arange(h, dtype=np.float32)[:, np.newaxis], (1, w))

        dx = (map_x_base - shoulder_x) / max(1.0, w - shoulder_x)
        dy = (map_y_base - shoulder_y) / max(1.0, h - shoulder_y)
        flipper_mask = np.clip(dx * 1.4, 0, 1) * np.clip(dy * 2.2, 0, 1)
        far_mask = np.clip((w * 0.17 - map_x_base) / max(1.0, w * 0.17), 0, 1) * np.clip((map_y_base - h * 0.68) / max(1.0, h * 0.31), 0, 1)

        frames: List[pygame.Surface] = []
        for i in range(num_frames):
            t = i / float(num_frames)
            if t < 0.28:
                p = t / 0.28
                flex = math.sin(p * math.pi) * 1.0
            elif t < 0.48:
                p = (t - 0.28) / 0.20
                flex = -math.sin(p * math.pi) * 0.35
            else:
                p = (t - 0.48) / 0.52
                flex = math.sin(p * math.pi * 2.0) * 0.05

            disp_y = (flipper_mask * (flex * 38.0 * (h / 555.0)) + far_mask * (flex * 20.0 * (h / 555.0))).astype(np.float32)
            disp_x = (flipper_mask * (flex * 10.0 * (w / 1072.0))).astype(np.float32)

            remapped = cv2.remap(arr, map_x_base - disp_x, map_y_base - disp_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))
            surf = pygame.image.frombuffer(remapped.tobytes(), (w, h), "RGBA")
            frames.append(surf)
        return frames
    except Exception:
        return [base_surface]


class RealisticTurtle3D:
    """
    Photorealistic Green Sea Turtle gliding through the midground:
    - 16-frame articulated pectoral flipper wing-strokes (sweeping downstroke, recovery, horizontal glide)
    - 100% rigid bone carapace & cranium (zero artificial sprite stretching/squashing)
    - Burst-and-coast propulsion: power downstroke surges forward (+38 px/s), extended majestic glide coasting on momentum
    - Smooth 3D elliptical banking arc turnaround (dips leading flipper, banks 18 deg, perspective foreshortening)
    - Generous 570px wide open oceanic swimming path from ancient ruins (-140px) to clear water corridor (435px)
    - Fully separated vertical lanes (Turtle: y=200-280, Shark: y=90-120, Jellyfish: y=540)
    - Subtle sunlight caustic specular highlights dancing across the amber shell scutes
    """

    def __init__(self, surface: Optional[pygame.Surface], patrol_left: bool = False):
        self.base_surface = surface
        self.patrol_left = patrol_left
        self.stroke_surfaces = generate_turtle_stroke_surfaces(self.base_surface, num_frames=16)

        # Start in the left open water column near ancient ruins
        self.x = SCREEN_WIDTH * 0.12
        self.y = SCREEN_HEIGHT * 0.33
        self.z = 0.70
        self.base_speed = 30.0
        self.speed = self.base_speed
        self.direction = 1  # Swimming towards archway
        self.target_direction = 1

        self.cycle_duration = 3.6  # 3.6s natural stroke + glide cycle
        self.cycle_timer = random.uniform(0.0, 3.6)

        # 3D Turning dynamics
        self.is_turning = False
        self.turn_timer = 0.0
        self.turn_duration = 3.2
        self.turn_scale_x = 1.0
        self.bank_angle = 0.0

        self.wander_phase = random.uniform(0, math.pi * 2)
        self.pitch = 0.0
        self.heave = 0.0
        self.target_w = 235

        # Generous horizontal swimming corridor
        self.turn_left_bound = -140.0
        self.turn_right_bound = SCREEN_WIDTH * 0.34  # 435px, well clear of center menu buttons at 475px

    def update(self, dt: float) -> None:
        self.cycle_timer = (self.cycle_timer + dt) % self.cycle_duration
        p_cycle = self.cycle_timer / self.cycle_duration

        # 1. Chelonian Hydrofoil Locomotion Phasing
        if p_cycle < 0.26:
            # Power downstroke (~0.94s): flippers sweep down and back, generating strong forward surge
            sub_p = p_cycle / 0.26
            surge = (math.sin(sub_p * math.pi) ** 1.4) * 36.0
            self.speed = self.base_speed + surge
            stroke_pitch = -math.sin(sub_p * math.pi) * 3.6
            self.heave = -math.sin(sub_p * math.pi) * 4.0
        elif p_cycle < 0.44:
            # Recovery upstroke (~0.65s): flippers feather back to level gliding orientation
            sub_p = (p_cycle - 0.26) / 0.18
            self.speed = self.base_speed + 16.0 * (1.0 - sub_p)
            stroke_pitch = -3.6 * (1.0 - sub_p)
            self.heave = -4.0 * (1.0 - sub_p)
        else:
            # Extended hydrodynamic coast & glide (~2.01s): flippers hold steady like glider wings
            sub_p = (p_cycle - 0.44) / 0.56
            decay = math.exp(-1.4 * (p_cycle - 0.44) * self.cycle_duration)
            self.speed = self.base_speed + 10.0 * decay
            stroke_pitch = math.sin(sub_p * math.pi * 2.0) * 0.8 + 0.6
            self.heave = math.sin(sub_p * math.pi * 2.0) * 1.5

        # 2. Turning vs. Straight Cruising
        if self.is_turning:
            self.turn_timer += dt
            turn_prog = min(1.0, self.turn_timer / self.turn_duration)
            self.bank_angle = math.sin(turn_prog * math.pi) * 16.0 * (-self.direction)
            self.turn_scale_x = math.cos(turn_prog * math.pi)

            # Smooth curved elliptical arc
            arc_vx = (self.base_speed * 0.40) * self.direction * math.cos(turn_prog * math.pi)
            arc_vy = math.sin(turn_prog * math.pi) * 14.0
            self.x += arc_vx * dt
            self.y += arc_vy * dt
            self.pitch = stroke_pitch * 0.5

            if turn_prog >= 1.0:
                self.is_turning = False
                self.direction = self.target_direction
                self.turn_scale_x = 1.0
                self.bank_angle = 0.0
                self.pitch = 0.0
        else:
            self.wander_phase += 0.35 * dt
            vy = math.sin(self.wander_phase) * 8.0
            self.y += vy * dt
            self.pitch = stroke_pitch
            self.bank_angle = 0.0
            self.x += self.speed * self.direction * dt

            # Keep turtle smoothly roaming within its safe vertical ocean band
            min_y = SCREEN_HEIGHT * 0.28
            max_y = SCREEN_HEIGHT * 0.38
            if self.y < min_y:
                self.y += (min_y - self.y) * 2.0 * dt
            elif self.y > max_y:
                self.y -= (self.y - max_y) * 2.0 * dt

            if self.direction == 1 and self.x > self.turn_right_bound:
                self.start_turn(-1)
            elif self.direction == -1 and self.x < self.turn_left_bound:
                self.start_turn(1)

        self.z = 0.70 + math.sin(self.wander_phase * 0.4) * 0.03

    def start_turn(self, new_dir: int) -> None:
        if not self.is_turning:
            self.is_turning = True
            self.turn_timer = 0.0
            self.target_direction = new_dir

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float], time_sec: float) -> None:
        if not self.base_surface:
            return

        ox, oy = cam_offset
        eff_scale = (self.z / 0.72)

        # Select stroke surface frame
        p_cycle = self.cycle_timer / self.cycle_duration
        if self.stroke_surfaces:
            frame_idx = int(p_cycle * len(self.stroke_surfaces)) % len(self.stroke_surfaces)
            active_surf = self.stroke_surfaces[frame_idx]
        else:
            active_surf = self.base_surface

        aspect = active_surf.get_height() / max(1, active_surf.get_width())

        # Perspective width during turn (never flatten into 0px needle)
        persp_scale = max(0.24, abs(self.turn_scale_x))
        w = max(24, int(self.target_w * eff_scale * persp_scale))
        h = max(16, int(self.target_w * aspect * eff_scale))

        scaled = pygame.transform.smoothscale(active_surf, (w, h))

        current_sign = self.direction * (1 if self.turn_scale_x >= 0 else -1)
        if current_sign == 1:
            scaled = pygame.transform.flip(scaled, True, False)

        # Realistic warm sunlight sheen
        sun_center = SCREEN_WIDTH * 0.50
        sun_spread = SCREEN_WIDTH * 0.35
        dist_to_sun = abs(self.x - sun_center)
        sun_factor = max(0.0, 1.0 - dist_to_sun / sun_spread) if dist_to_sun < sun_spread else 0.0

        r = int(220 + 35 * sun_factor)
        g = int(230 + 25 * sun_factor)
        b = int(245 + 10 * sun_factor)

        tint_surf = pygame.Surface(scaled.get_size(), pygame.SRCALPHA)
        tint_surf.fill((min(255, r), min(255, g), min(255, b), 255))
        scaled.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        # Subtle realistic underwater caustic specular highlight on turtle shell (CLEANLY MASKED)
        caustic_phase = time_sec * 2.4 + self.x * 0.014
        caustic_glow = max(0, int(math.sin(caustic_phase) * 22 + 18))
        if caustic_glow > 0:
            spec_layer = pygame.Surface(scaled.get_size(), pygame.SRCALPHA)
            spec_layer.fill((int(caustic_glow * 0.8), int(caustic_glow * 0.95), int(caustic_glow * 1.1), 255))
            spec_layer.blit(scaled, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            scaled.blit(spec_layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # Dynamic pitch and banking rotation
        total_rot = self.pitch + self.bank_angle
        rotated = pygame.transform.rotate(scaled, total_rot)

        rx = int(self.x + ox * self.z - rotated.get_width() / 2)
        ry = int(self.y + oy * self.z + self.heave - rotated.get_height() / 2)
        target.blit(rotated, (rx, ry))


# =========================================================================
# 3. FISH SCHOOL SYSTEM — SUBCARANGIFORM DEFORMATION & BOID SCHOOLING
# =========================================================================

def deform_subcarangiform_swimming(
    surface: Optional[pygame.Surface],
    target_w: int,
    target_h: int,
    swim_phase: float,
    tail_amp: float,
    facing_left: bool,
    turn_scale_x: float,
    pitch: float,
    depth_haze: float = 0.0,
    caustic_val: int = 0
) -> Optional[pygame.Surface]:
    """
    Renders photorealistic subcarangiform swimming deformation:
    - Cranium / snout stays steady (first 25% of body) for natural forward gaze.
    - Sinuous traveling wave articulates mid-body, peduncle, and caudal tail fin.
    - 3D turn foreshortening with cosine compression and pitch banking.
    - Subtle specular sunbeam caustic gleam dancing across dorsal scales.
    - Atmospheric oceanic depth haze matching water column depth.
    """
    if not surface:
        return None

    eff_w = max(10, int(target_w * abs(turn_scale_x)))
    eff_h = max(8, target_h)

    scaled = pygame.transform.smoothscale(surface, (eff_w, eff_h))
    current_facing_left = facing_left if turn_scale_x >= 0 else not facing_left
    if not current_facing_left:
        scaled = pygame.transform.flip(scaled, True, False)

    num_slices = 18
    slice_step = eff_w / num_slices
    slice_w = int(math.ceil(slice_step)) + 1
    max_pad_y = int(tail_amp * 1.5) + 8

    bent_surf = pygame.Surface((eff_w + 10, eff_h + max_pad_y * 2), pygame.SRCALPHA)

    for i in range(num_slices):
        ratio = (i / (num_slices - 1)) if current_facing_left else (1.0 - i / (num_slices - 1))

        # Subcarangiform wave: head (ratio < 0.25) is firm, trunk & caudal fin flex
        if ratio < 0.25:
            amp = 0.0
        else:
            amp = (((ratio - 0.25) / 0.75) ** 2.2) * tail_amp

        phase_lag = ratio * 3.4
        offset_y = math.sin(swim_phase - phase_lag) * amp

        sx = int(i * slice_step)
        cur_sw = slice_w if sx + slice_w <= eff_w else (eff_w - sx)

        if cur_sw > 0:
            rect = pygame.Rect(sx, 0, cur_sw, eff_h)
            bent_surf.blit(scaled, (sx + 5, max_pad_y + offset_y), rect)

    # Clean specular caustic highlight on scales
    if caustic_val > 0:
        spec_surf = pygame.Surface(bent_surf.get_size(), pygame.SRCALPHA)
        spec_surf.fill((int(caustic_val * 0.75), int(caustic_val * 0.9), int(caustic_val * 1.1), 255))
        spec_surf.blit(bent_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        bent_surf.blit(spec_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Atmospheric oceanic depth haze
    if depth_haze > 0.05:
        haze_surf = pygame.Surface(bent_surf.get_size(), pygame.SRCALPHA)
        haze_alpha = int(depth_haze * 120)
        haze_surf.fill((16, 75, 120, haze_alpha))
        haze_surf.blit(bent_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        bent_surf.blit(haze_surf, (0, 0))

    if abs(pitch) > 0.5:
        return pygame.transform.rotate(bent_surf, pitch)
    return bent_surf


def apply_fish_separation(fish_list: List["RealisticFish3D"], min_dist: float = 65.0) -> None:
    """Applies inverse-distance repulsion force between fish to guarantee zero clumping."""
    n = len(fish_list)
    for i in range(n):
        f1 = fish_list[i]
        for j in range(i + 1, n):
            f2 = fish_list[j]
            dx = f1.x - f2.x
            dy = f1.y - f2.y
            dist = math.hypot(dx, dy)
            if 0.1 < dist < min_dist:
                overlap = min_dist - dist
                nx = dx / dist
                ny = dy / dist
                push = overlap * 48.0
                f1.repel_x += nx * push
                f1.repel_y += ny * push * 0.4
                f2.repel_x -= nx * push
                f2.repel_y -= ny * push * 0.4


class RealisticFish3D:
    """
    Individual autonomous tropical marine fish with genuine living biomechanics:
    - Burst-and-Coast swimming propulsion (burst acceleration, hydrodynamic glide coast, coral hover/graze)
    - 3D yaw turnaround with cosine foreshortening and pitch banking
    - Traveling wave caudal fin undulation
    - Soft translucent contact shadow cast on sandy seabed mosaic floor
    - Strict Boid separation preventing any clumping
    """
    def __init__(
        self,
        surface: Optional[pygame.Surface],
        species: str,
        x: float,
        y: float,
        z: float,
        patrol_min_x: float,
        patrol_max_x: float,
        base_y: float,
        y_wander_amp: float = 24.0,
        base_w: int = 70,
        depth_haze: float = 0.0
    ):
        self.surface = surface
        self.species = species
        self.x = x
        self.y = y
        self.z = z
        self.patrol_min_x = patrol_min_x
        self.patrol_max_x = patrol_max_x
        self.base_y = base_y
        self.y_wander_amp = y_wander_amp
        self.base_w = base_w
        self.depth_haze = depth_haze

        self.direction = random.choice([-1, 1])
        self.target_direction = self.direction
        self.is_turning = False
        self.turn_progress = 0.0
        self.turn_duration = random.uniform(0.7, 1.0)
        self.turn_scale_x = 1.0

        # Locomotion state machine: 'burst', 'coast', 'hover'
        self.state = random.choice(["burst", "coast", "hover"])
        self.state_timer = random.uniform(0.6, 2.0)
        self.swim_speed = 45.0
        self.vx = self.swim_speed * self.direction
        self.vy = 0.0
        self.pitch = 0.0

        self.swim_phase = random.uniform(0, math.pi * 2)
        self.tail_frequency = 10.0
        self.tail_amplitude = 6.0
        self.wander_phase = random.uniform(0, math.pi * 2)
        self.repel_x = 0.0
        self.repel_y = 0.0

    def update(self, dt: float) -> None:
        self.swim_phase += self.tail_frequency * dt
        self.wander_phase += 0.9 * dt
        self.state_timer -= dt

        # State transition
        if self.state_timer <= 0:
            if self.state == "burst":
                self.state = "coast"
                self.state_timer = random.uniform(1.0, 2.2)
            elif self.state == "coast":
                if random.random() < 0.45 and self.y > SCREEN_HEIGHT * 0.65:
                    self.state = "hover"
                    self.state_timer = random.uniform(1.2, 2.8)
                else:
                    self.state = "burst"
                    self.state_timer = random.uniform(0.35, 0.65)
            else:  # hover
                self.state = "burst"
                self.state_timer = random.uniform(0.40, 0.70)
                if random.random() < 0.35:
                    self.start_turn(-self.direction)

        # Kinematics by state
        if self.state == "burst":
            self.tail_frequency = random.uniform(14.0, 17.0)
            self.tail_amplitude = 7.5
            target_speed = random.uniform(75.0, 110.0)
            self.swim_speed += (target_speed - self.swim_speed) * min(1.0, 5.0 * dt)
        elif self.state == "coast":
            self.tail_frequency = 3.2
            self.tail_amplitude = 3.0
            # Drag deceleration
            self.swim_speed *= max(0.0, 1.0 - 1.6 * dt)
            self.swim_speed = max(24.0, self.swim_speed)
        else:  # hover
            self.tail_frequency = 12.0  # gentle pectoral flutter
            self.tail_amplitude = 1.8
            self.swim_speed *= max(0.0, 1.0 - 3.5 * dt)

        # 3D Turn dynamics
        if self.is_turning:
            self.turn_progress += dt / self.turn_duration
            prog = min(1.0, self.turn_progress)
            self.turn_scale_x = math.cos(prog * math.pi)
            self.pitch = math.sin(prog * math.pi) * (9.0 * -self.direction)
            if prog >= 1.0:
                self.is_turning = False
                self.direction = self.target_direction
                self.turn_scale_x = 1.0
                self.pitch = 0.0
        else:
            self.turn_scale_x = 1.0
            # Pitch reflects vertical movement
            target_pitch = math.sin(self.wander_phase) * 6.0
            if self.state == "hover":
                target_pitch += 8.0  # slight downward grazing tilt
            self.pitch += (target_pitch - self.pitch) * min(1.0, 6.0 * dt)

            # Move along velocity
            self.vx = self.swim_speed * self.direction + self.repel_x
            self.vy = math.sin(self.wander_phase) * (self.y_wander_amp * 0.45) + self.repel_y
            self.x += self.vx * dt
            self.y += self.vy * dt

            # Damp repulsion impulses
            self.repel_x *= max(0.0, 1.0 - 5.0 * dt)
            self.repel_y *= max(0.0, 1.0 - 5.0 * dt)

            # Patrol boundaries triggering smooth 3D turnaround
            if self.direction == 1 and self.x > self.patrol_max_x:
                self.start_turn(-1)
            elif self.direction == -1 and self.x < self.patrol_min_x:
                self.start_turn(1)

            # Vertical range clamp
            self.y = max(self.base_y - self.y_wander_amp, min(self.base_y + self.y_wander_amp, self.y))

    def start_turn(self, new_dir: int) -> None:
        if not self.is_turning:
            self.is_turning = True
            self.turn_progress = 0.0
            self.target_direction = new_dir

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float], time_sec: float = 0.0) -> None:
        if not self.surface:
            return

        ox, oy = cam_offset
        fx = self.x + ox * self.z
        fy = self.y + oy * self.z

        aspect = self.surface.get_height() / max(1, self.surface.get_width())
        w = int(self.base_w * (self.z / 0.85))
        h = max(8, int(w * aspect))

        # Soft translucent seabed floor contact shadow
        if fy > 530 and self.z >= 0.75:
            dist_to_floor = max(0.0, min(1.0, (fy - 530) / 100.0))
            shadow_alpha = int(55 * dist_to_floor)
            if shadow_alpha > 0:
                shadow_w = max(12, int(w * 0.85 * abs(self.turn_scale_x)))
                shadow_h = max(4, int(shadow_w * 0.28))
                shadow_surf = pygame.Surface((shadow_w + 4, shadow_h + 4), pygame.SRCALPHA)
                pygame.draw.ellipse(shadow_surf, (8, 24, 42, shadow_alpha), (2, 2, shadow_w, shadow_h))
                shadow_y = min(SCREEN_HEIGHT - 35, int(fy + h * 0.46))
                target.blit(shadow_surf, (int(fx - shadow_w / 2), shadow_y))

        # Caustic gleam on scales
        caustic_wave = math.sin(time_sec * 2.6 + fx * 0.015) * 0.5 + 0.5
        caustic_val = int(22 * caustic_wave)

        facing_left = (self.direction == -1)
        fish_surf = deform_subcarangiform_swimming(
            surface=self.surface,
            target_w=w,
            target_h=h,
            swim_phase=self.swim_phase,
            tail_amp=self.tail_amplitude,
            facing_left=facing_left,
            turn_scale_x=self.turn_scale_x,
            pitch=self.pitch,
            depth_haze=self.depth_haze,
            caustic_val=caustic_val
        )

        if fish_surf:
            target.blit(fish_surf, (int(fx - fish_surf.get_width() / 2), int(fy - fish_surf.get_height() / 2)))


# Backward compatibility alias
IndividualReefFish = RealisticFish3D


class ForegroundReefSchool:
    """School of tropical reef fish browsing the seabed and lower mosaic floor (Z: 0.82 - 0.90)."""

    def __init__(self, clown_surf: Optional[pygame.Surface], tang_surf: Optional[pygame.Surface], yellow_surf: Optional[pygame.Surface]):
        self.fish: List[RealisticFish3D] = []
        # 4 well-spaced grazers across the temple mosaic floor:
        # 1. Yellow Tang on left mosaic tiles
        self.fish.append(RealisticFish3D(
            yellow_surf, "yellow_tang",
            x=SCREEN_WIDTH * 0.22, y=SCREEN_HEIGHT * 0.82, z=0.88,
            patrol_min_x=SCREEN_WIDTH * 0.12, patrol_max_x=SCREEN_WIDTH * 0.34,
            base_y=SCREEN_HEIGHT * 0.82, y_wander_amp=18.0, base_w=68
        ))
        # 2. Blue Tang browsing center-left mosaic
        self.fish.append(RealisticFish3D(
            tang_surf, "blue_tang",
            x=SCREEN_WIDTH * 0.42, y=SCREEN_HEIGHT * 0.85, z=0.86,
            patrol_min_x=SCREEN_WIDTH * 0.32, patrol_max_x=SCREEN_WIDTH * 0.54,
            base_y=SCREEN_HEIGHT * 0.85, y_wander_amp=18.0, base_w=66
        ))
        # 3. Yellow Tang on center-right sand
        self.fish.append(RealisticFish3D(
            yellow_surf, "yellow_tang",
            x=SCREEN_WIDTH * 0.64, y=SCREEN_HEIGHT * 0.83, z=0.89,
            patrol_min_x=SCREEN_WIDTH * 0.54, patrol_max_x=SCREEN_WIDTH * 0.74,
            base_y=SCREEN_HEIGHT * 0.83, y_wander_amp=20.0, base_w=68
        ))
        # 4. Yellow Tang grazing near right coral base
        self.fish.append(RealisticFish3D(
            yellow_surf, "yellow_tang",
            x=SCREEN_WIDTH * 0.84, y=SCREEN_HEIGHT * 0.86, z=0.85,
            patrol_min_x=SCREEN_WIDTH * 0.74, patrol_max_x=SCREEN_WIDTH * 0.92,
            base_y=SCREEN_HEIGHT * 0.86, y_wander_amp=16.0, base_w=64
        ))

    def update(self, dt: float) -> None:
        for f in self.fish:
            f.update(dt)
        apply_fish_separation(self.fish, min_dist=75.0)

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float], time_sec: float = 0.0) -> None:
        for f in self.fish:
            f.draw(target, cam_offset, time_sec)


class MidgroundOceanSchool:
    """Coordinated oceanic ribbon school of Blue Tangs swimming across the upper sunlit open ocean corridor (Z: 0.58)."""

    def __init__(self, tang_surf: Optional[pygame.Surface], count: int = 8):
        self.tang_surf = tang_surf
        self.center_x = SCREEN_WIDTH * 0.85
        self.center_y = SCREEN_HEIGHT * 0.20  # In sunlit water column ABOVE menu buttons!
        self.speed = 44.0
        self.direction = -1
        self.target_direction = -1
        self.wander_phase = random.uniform(0, math.pi * 2)
        self.swim_phase = random.uniform(0, math.pi * 2)

        # 3D Turning dynamics
        self.is_turning = False
        self.turn_timer = 0.0
        self.turn_duration = 2.0
        self.turn_scale_x = 1.0

        # Ribbon wave offsets: distributed along a flowing serpentine stream
        self.offsets = []
        for i in range(count):
            rel_x = i * 36.0 - (count * 18.0)
            rel_y = math.sin(i * 0.9) * 16.0
            z = random.uniform(0.55, 0.62)
            phase_off = i * 0.65
            sz = 52 if i % 2 == 0 else 46
            self.offsets.append((rel_x, rel_y, z, phase_off, sz))

    def update(self, dt: float) -> None:
        self.wander_phase += 0.65 * dt
        self.swim_phase += 9.5 * dt

        if self.is_turning:
            self.turn_timer += dt
            prog = min(1.0, self.turn_timer / self.turn_duration)
            self.turn_scale_x = math.cos(prog * math.pi)
            if prog >= 1.0:
                self.is_turning = False
                self.direction = self.target_direction
                self.turn_scale_x = 1.0
        else:
            self.center_x += self.speed * self.direction * dt
            self.center_y += math.sin(self.wander_phase) * (8.0 * dt)

            if self.direction == -1 and self.center_x < -220:
                self.start_turn(1)
            elif self.direction == 1 and self.center_x > SCREEN_WIDTH + 220:
                self.start_turn(-1)

    def start_turn(self, new_dir: int) -> None:
        if not self.is_turning:
            self.is_turning = True
            self.turn_timer = 0.0
            self.target_direction = new_dir
            self.center_y = random.uniform(SCREEN_HEIGHT * 0.17, SCREEN_HEIGHT * 0.23)

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float], time_sec: float = 0.0) -> None:
        if not self.tang_surf:
            return

        ox, oy = cam_offset
        facing_left = (self.direction == -1)

        for rel_x, rel_y, z, phase_off, sz in self.offsets:
            fx = self.center_x + rel_x + math.sin(time_sec * 2.4 + phase_off) * 10.0 + ox * z
            fy = self.center_y + rel_y + math.cos(time_sec * 1.8 + phase_off) * 6.0 + oy * z

            aspect = self.tang_surf.get_height() / max(1, self.tang_surf.get_width())
            w = int(sz * (z / 0.58))
            h = max(6, int(w * aspect))

            vy = math.cos(time_sec * 1.8 + phase_off)
            pitch = -vy * 5.0 * self.direction

            fish_surf = deform_subcarangiform_swimming(
                surface=self.tang_surf,
                target_w=w,
                target_h=h,
                swim_phase=self.swim_phase + phase_off,
                tail_amp=4.5,
                facing_left=facing_left,
                turn_scale_x=self.turn_scale_x,
                pitch=pitch,
                depth_haze=0.18,
                caustic_val=int(14 * (math.sin(time_sec * 2.5 + fx * 0.02) * 0.5 + 0.5))
            )
            if fish_surf:
                target.blit(fish_surf, (int(fx - fish_surf.get_width() / 2), int(fy - fish_surf.get_height() / 2)))


class CoralAnemoneClownfish:
    """
    Resident pair of Clownfish living strictly near the sea anemones on the right coral reef.
    They hover, dart playfully, and waddle with rapid caudal fin flutter, never wandering away from their anemone home.
    """

    def __init__(self, clown_surf: Optional[pygame.Surface], home_x: float, home_y: float, is_female: bool = True):
        self.surface = clown_surf
        self.home_x = home_x
        self.home_y = home_y
        self.x = home_x
        self.y = home_y
        self.z = 0.88 if is_female else 0.84
        self.base_w = 68 if is_female else 54
        self.swim_phase = random.uniform(0, math.pi * 2)
        self.waddle_phase = random.uniform(0, math.pi * 2)
        self.direction = 1
        self.turn_scale_x = 1.0
        self.is_turning = False
        self.turn_timer = 0.0
        self.pitch = 0.0
        self.dart_target_x = 0.0
        self.dart_target_y = 0.0
        self.timer = random.uniform(1.2, 2.5)

    def update(self, dt: float) -> None:
        self.swim_phase += 14.0 * dt
        self.waddle_phase += 3.5 * dt
        self.timer -= dt

        if self.timer <= 0:
            self.timer = random.uniform(2.0, 4.5)
            self.dart_target_x = random.uniform(-42.0, 42.0)
            self.dart_target_y = random.uniform(-28.0, 22.0)
            new_dir = 1 if self.dart_target_x > (self.x - self.home_x) else -1
            if new_dir != self.direction:
                self.is_turning = True
                self.turn_timer = 0.0
                self.direction = new_dir

        if self.is_turning:
            self.turn_timer += dt
            prog = min(1.0, self.turn_timer / 0.75)
            self.turn_scale_x = math.cos(prog * math.pi)
            self.pitch = math.sin(prog * math.pi) * (7.0 * -self.direction)
            if prog >= 1.0:
                self.is_turning = False
                self.turn_scale_x = 1.0
                self.pitch = 0.0
        else:
            self.turn_scale_x = 1.0
            self.pitch = math.sin(self.waddle_phase) * 5.0

        tx = self.home_x + self.dart_target_x + math.sin(self.waddle_phase) * 8.0
        ty = self.home_y + self.dart_target_y + math.cos(self.waddle_phase * 0.8) * 6.0
        self.x += (tx - self.x) * min(1.0, 3.2 * dt)
        self.y += (ty - self.y) * min(1.0, 3.2 * dt)

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float], time_sec: float = 0.0) -> None:
        if not self.surface:
            return
        ox, oy = cam_offset
        fx = self.x + ox * self.z
        fy = self.y + oy * self.z

        aspect = self.surface.get_height() / max(1, self.surface.get_width())
        w = int(self.base_w * (self.z / 0.85))
        h = max(8, int(w * aspect))

        facing_left = (self.direction == -1)
        fish_surf = deform_subcarangiform_swimming(
            surface=self.surface,
            target_w=w,
            target_h=h,
            swim_phase=self.swim_phase,
            tail_amp=6.5,
            facing_left=facing_left,
            turn_scale_x=self.turn_scale_x,
            pitch=self.pitch,
            depth_haze=0.0,
            caustic_val=int(18 * (math.sin(time_sec * 2.8 + fx * 0.02) * 0.5 + 0.5))
        )
        if fish_surf:
            target.blit(fish_surf, (int(fx - fish_surf.get_width() / 2), int(fy - fish_surf.get_height() / 2)))


class RuinsReefSchool:
    """Curious reef fish exploring the ancient Grecian pillars on the left (Z: 0.74 - 0.82)."""

    def __init__(self, tang_surf: Optional[pygame.Surface], yellow_surf: Optional[pygame.Surface]):
        self.fish: List[RealisticFish3D] = []
        # 1. Blue Tang around outer pillar
        self.fish.append(RealisticFish3D(
            tang_surf, "blue_tang",
            x=SCREEN_WIDTH * 0.14, y=SCREEN_HEIGHT * 0.58, z=0.76,
            patrol_min_x=SCREEN_WIDTH * 0.06, patrol_max_x=SCREEN_WIDTH * 0.24,
            base_y=SCREEN_HEIGHT * 0.58, y_wander_amp=26.0, base_w=64, depth_haze=0.10
        ))
        # 2. Yellow Tang pecking at mossy pillar base
        self.fish.append(RealisticFish3D(
            yellow_surf, "yellow_tang",
            x=SCREEN_WIDTH * 0.22, y=SCREEN_HEIGHT * 0.66, z=0.80,
            patrol_min_x=SCREEN_WIDTH * 0.12, patrol_max_x=SCREEN_WIDTH * 0.28,
            base_y=SCREEN_HEIGHT * 0.66, y_wander_amp=20.0, base_w=62, depth_haze=0.08
        ))
        # 3. Blue Tang near stone mosaic border
        self.fish.append(RealisticFish3D(
            tang_surf, "blue_tang",
            x=SCREEN_WIDTH * 0.18, y=SCREEN_HEIGHT * 0.74, z=0.82,
            patrol_min_x=SCREEN_WIDTH * 0.08, patrol_max_x=SCREEN_WIDTH * 0.26,
            base_y=SCREEN_HEIGHT * 0.74, y_wander_amp=18.0, base_w=60, depth_haze=0.06
        ))

    def update(self, dt: float) -> None:
        for f in self.fish:
            f.update(dt)
        apply_fish_separation(self.fish, min_dist=68.0)

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float], time_sec: float = 0.0) -> None:
        for f in self.fish:
            f.draw(target, cam_offset, time_sec)


class DistantFishShoal:
    """Large shoal of 35 shimmering silvery fish in the distant oceanic background (Z: 0.22 - 0.30)."""

    def __init__(self, count: int = 35):
        self.center_x = SCREEN_WIDTH * 0.35
        self.center_y = SCREEN_HEIGHT * 0.32
        self.speed = 38.0
        self.direction = 1
        self.wander_phase = random.uniform(0, math.pi * 2)

        self.members = [
            (random.uniform(-150, 150), random.uniform(-35, 35), random.uniform(0.22, 0.30), random.uniform(0, math.pi * 2))
            for _ in range(count)
        ]

    def update(self, dt: float) -> None:
        self.wander_phase += 0.5 * dt
        self.center_x += self.speed * self.direction * dt
        self.center_y += math.sin(self.wander_phase) * (9.0 * dt)

        if self.direction == 1 and self.center_x > SCREEN_WIDTH + 220:
            self.center_x = -220
            self.center_y = random.uniform(SCREEN_HEIGHT * 0.22, SCREEN_HEIGHT * 0.42)

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float], time_sec: float) -> None:
        ox, oy = cam_offset
        for mx, my, z, ph in self.members:
            fx = self.center_x + mx + math.sin(time_sec * 2.2 + ph) * 12.0 + ox * z
            fy = self.center_y + my + math.cos(time_sec * 1.8 + ph) * 5.0 + oy * z

            fish_len = int(8.0 * (z / 0.25))
            fish_h = max(2, int(3.0 * (z / 0.25)))
            shimmer = math.sin(time_sec * 7.0 + ph) * 0.3 + 0.7
            alpha = int(140 * shimmer * (z / 0.30))

            f_surf = pygame.Surface((fish_len + 4, fish_h + 4), pygame.SRCALPHA)
            pygame.draw.ellipse(f_surf, (170, 225, 250, alpha), (2, 2, fish_len, fish_h))

            target.blit(f_surf, (int(fx - fish_len / 2), int(fy - fish_h / 2)))


# =========================================================================
# 3b. BOTTLENOSE DOLPHINS — CETACEAN DORSOVENTRAL UNDULATION
# =========================================================================

def generate_dolphin_stroke_surfaces(base_surface: Optional[pygame.Surface], num_frames: int = 16) -> List[pygame.Surface]:
    """Pre-renders 16 articulated dorsoventral caudal fluke strokes preserving rigid dolphin skull/melon with traveling wave hydrodynamics."""
    if not base_surface:
        return []
    try:
        import cv2
        import numpy as np

        w, h = base_surface.get_size()
        raw_bytes = pygame.image.tostring(base_surface, "RGBA")
        arr = np.frombuffer(raw_bytes, dtype=np.uint8).reshape((h, w, 4))

        map_x_base = np.tile(np.arange(w, dtype=np.float32), (h, 1))
        map_y_base = np.tile(np.arange(h, dtype=np.float32)[:, np.newaxis], (1, w))

        # Snout on right (x=w), tail fluke on left (x=0)
        # Rigid rostrum/melon from x = 0.62*w to w
        # Articulated peduncle & fluke from x = 0 to 0.62*w
        fluke_ratio = np.clip((w * 0.62 - map_x_base) / max(1.0, w * 0.62), 0.0, 1.0)
        fluke_curve = fluke_ratio ** 1.75

        frames: List[pygame.Surface] = []
        for i in range(num_frames):
            t = i / float(num_frames)
            # Propagating kinematic wave from posterior spine to caudal fluke tip
            wave_phase = t * 2.0 * math.pi - fluke_ratio * 1.15
            stroke = np.sin(wave_phase)
            disp_y = (fluke_curve * stroke * (38.0 * (h / 606.0))).astype(np.float32)

            remapped = cv2.remap(arr, map_x_base, map_y_base - disp_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))
            surf = pygame.image.frombuffer(remapped.tobytes(), (w, h), "RGBA")
            frames.append(surf)
        return frames
    except Exception:
        return [base_surface]


class OceanWaterFlow:
    """Simulates real dynamic 2D ocean currents, water flow, and tidal swells."""

    def __init__(self):
        self.time = 0.0
        self.flow_vx = 14.0
        self.flow_vy = 0.0

    def update(self, dt: float) -> Tuple[float, float]:
        self.time += dt
        # Eastward ocean current with harmonic ebb and surge
        self.flow_vx = 14.0 + math.sin(self.time * 0.45) * 8.0 + math.sin(self.time * 1.1) * 3.5
        # Gentle vertical tidal swell
        self.flow_vy = math.cos(self.time * 0.35) * 4.5
        return (self.flow_vx, self.flow_vy)


class LivingOceanWater3D:
    """
    Simulates real 3D moving ocean water across the underwater environment:
    - Moving surface swells with animated crests and sunlight refraction (y: 0 to 140)
    - Volumetric 3D sunbeams (god rays) sweeping dynamically with surface wave angles
    - Fluid optical refraction wave shimmer across the water column
    - Current streamlines & drifting bioluminescent ocean wisps carried by (flow_vx, flow_vy)
    """

    def __init__(self):
        self.time = 0.0
        # 16 ocean current streamline drifters
        self.streamlines = []
        for _ in range(16):
            self.streamlines.append({
                "x": random.uniform(-100, SCREEN_WIDTH + 100),
                "y": random.uniform(50, SCREEN_HEIGHT - 50),
                "length": random.uniform(50, 130),
                "speed_mult": random.uniform(0.7, 1.3),
                "alpha": random.randint(35, 75),
                "width": random.choice([1, 2]),
            })

    def update(self, dt: float, flow_vx: float, flow_vy: float) -> None:
        self.time += dt
        for st in self.streamlines:
            st["x"] += (flow_vx * st["speed_mult"] + 20.0) * dt
            st["y"] += (flow_vy * 0.35 + math.sin(self.time * 0.9 + st["x"] * 0.01) * 3.5) * dt
            if st["x"] > SCREEN_WIDTH + 140:
                st["x"] = -140
                st["y"] = random.uniform(50, SCREEN_HEIGHT - 50)

    def draw_current_streamlines(self, target: pygame.Surface) -> None:
        """Renders visible fluid current streamlines that drift across the 3D space."""
        for st in self.streamlines:
            pts = []
            cur_x = st["x"]
            cur_y = st["y"]
            length = st["length"]
            num_pts = 6
            step_len = length / num_pts
            for j in range(num_pts):
                px = cur_x - j * step_len
                py = cur_y + math.sin(self.time * 2.2 + j * 0.45 + cur_x * 0.01) * 4.5
                pts.append((int(px), int(py)))
            if len(pts) >= 2:
                alpha = st["alpha"]
                col = (160, 235, 255, alpha)
                surf_line = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.lines(surf_line, col, False, pts, st["width"])
                target.blit(surf_line, (0, 0))

    def draw_surface_and_rays(self, target: pygame.Surface, flow_vx: float, time_sec: float) -> None:
        """Renders undulating surface waves and sweeping volumetric 3D sunbeams."""
        # 1. Volumetric Sweeping Sunbeams (God Rays)
        ray_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        num_rays = 8
        for i in range(num_rays):
            sway = math.sin(time_sec * 0.42 + i * 1.15) * 42.0 + (flow_vx * 0.75)
            x_top = (i + 1) * (SCREEN_WIDTH / (num_rays + 1)) + sway
            width_top = 45.0
            width_bottom = 150.0
            x_bottom = x_top + 110.0 + sway * 1.4

            ray_poly = [
                (x_top - width_top / 2, 0),
                (x_top + width_top / 2, 0),
                (x_bottom + width_bottom / 2, SCREEN_HEIGHT),
                (x_bottom - width_bottom / 2, SCREEN_HEIGHT),
            ]
            ray_alpha = int(24 + 10 * math.sin(time_sec * 1.3 + i * 0.95))
            pygame.draw.polygon(ray_surf, (215, 248, 255, ray_alpha), ray_poly)

        target.blit(ray_surf, (0, 0))

        # 2. Moving 3D Ocean Surface Swells & Sunlight Caustic Sky (y: 0 to 110)
        surf_layer = pygame.Surface((SCREEN_WIDTH, 120), pygame.SRCALPHA)
        wave_pts = [(0, 0)]
        step_x = 24
        for px in range(0, SCREEN_WIDTH + step_x, step_x):
            wy = 28.0 + math.sin(px * 0.012 + time_sec * 1.6) * 9.0 + math.cos(px * 0.025 - time_sec * 2.2) * 5.0 + (flow_vx * 0.15)
            wave_pts.append((px, wy))
        wave_pts.append((SCREEN_WIDTH, 0))

        if len(wave_pts) >= 4:
            # Translucent sunlit cyan surface gradient
            pygame.draw.polygon(surf_layer, (35, 155, 215, 55), wave_pts)
            # Bright sunlight glare along crest
            pygame.draw.lines(surf_layer, (230, 250, 255, 110), False, wave_pts[1:-1], 2)

        target.blit(surf_layer, (0, 0))


class DolphinBubbleRing:
    """Toroidal bubble ring blown from a dolphin's blowhole expanding as it ascends with the water flow."""

    def __init__(self, x: float, y: float, z: float, dir_x: float):
        self.x = x
        self.y = y
        self.z = z
        self.dir_x = dir_x
        self.radius = 4.0
        self.max_radius = random.uniform(18.0, 26.0)
        self.life = random.uniform(2.4, 3.6)
        self.age = 0.0
        self.speed_y = random.uniform(34.0, 52.0)
        self.spin = random.uniform(0, math.pi * 2)

    def update(self, dt: float, flow_vx: float = 0.0, flow_vy: float = 0.0) -> bool:
        self.age += dt
        prog = min(1.0, self.age / self.life)
        self.radius = 4.0 + (self.max_radius - 4.0) * (prog ** 0.6)
        self.y -= (self.speed_y - flow_vy * 0.3) * dt
        self.x += (self.dir_x * 12.0 * (1.0 - prog) + flow_vx * 0.65) * dt
        self.spin += 2.0 * dt
        return self.age < self.life

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float]) -> None:
        ox, oy = cam_offset
        px = int(self.x + ox * self.z)
        py = int(self.y + oy * self.z)
        prog = self.age / self.life
        alpha = int(220 * (1.0 - prog) * (self.z / 0.60))
        if alpha <= 0:
            return

        rx = int(self.radius)
        ry = max(2, int(self.radius * 0.45))
        surf_w = rx * 2 + 10
        surf_h = ry * 2 + 10
        ring_surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        rcx, rcy = surf_w // 2, surf_h // 2

        # Glowing toroidal bubble ring
        pygame.draw.ellipse(ring_surf, (200, 245, 255, alpha), (rcx - rx, rcy - ry, rx * 2, ry * 2), 2)
        pygame.draw.ellipse(ring_surf, (255, 255, 255, int(alpha * 0.8)), (rcx - rx + 1, rcy - ry + 1, max(1, rx * 2 - 2), max(1, ry * 2 - 2)), 1)
        # Specular glint on upper crest
        glint_x = rcx + int(math.cos(self.spin) * rx * 0.7)
        glint_y = rcy + int(math.sin(self.spin) * ry * 0.7)
        pygame.draw.circle(ring_surf, (255, 255, 255, int(alpha * 0.9)), (glint_x, glint_y), max(1, int(rx * 0.18)))

        target.blit(ring_surf, (px - rcx, py - rcy))


class DolphinSplashDrop:
    """Water droplet arcing into the air and falling during a dolphin breach leap."""

    def __init__(self, x: float, y: float, z: float, vx: float, vy: float):
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.life = random.uniform(0.45, 0.85)
        self.age = 0.0
        self.radius = random.uniform(2.0, 4.5)

    def update(self, dt: float) -> bool:
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 220.0 * dt  # Gravity pulls spray back to ocean
        return self.age < self.life

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float]) -> None:
        ox, oy = cam_offset
        px = int(self.x + ox * self.z)
        py = int(self.y + oy * self.z)
        prog = self.age / self.life
        alpha = int(220 * (1.0 - prog))
        if alpha > 0 and 0 <= px < SCREEN_WIDTH and 0 <= py < SCREEN_HEIGHT:
            r = max(1, int(self.radius * (1.0 - prog * 0.4)))
            pygame.draw.circle(target, (215, 245, 255), (px, py), r)


class RealisticDolphin3D:
    """
    Photorealistic Bottlenose Dolphin (Tursiops truncatus) featuring true Cetacean hydrodynamics:
    - 16-frame articulated dorsoventral fluke undulation with traveling wave hydrodynamics
    - Authentic Oceanic porpoising leaps: dynamic breach arc, surface water spray, parabolic trajectory
    - Deep sea cruising, dive-and-climb undulation, and social echelon swimming
    - 3D banking turnaround with perspective foreshortening and roll angles
    - Masked sunbeam caustics dancing on smooth skin
    - Blowhole bubble ring emission and leaping splash droplets
    """

    def __init__(
        self,
        surface: Optional[pygame.Surface],
        x: float = 200.0,
        y: float = 220.0,
        z: float = 0.60,
        base_speed: float = 58.0,
        direction: int = 1,
        scale: int = 265,
        phase_offset: float = 0.0,
        wave_phase: float = 0.0,
        wave_amplitude: float = 22.0,
        wave_freq: float = 0.55,
        leap_interval: float = 5.0,
    ):
        self.base_surface = surface
        self.stroke_surfaces = generate_dolphin_stroke_surfaces(self.base_surface, num_frames=16)

        self.x = x
        self.base_y = y
        self.cruise_y = y
        self.y = y
        self.z = z
        self.base_speed = base_speed
        self.speed = self.base_speed
        self.direction = direction
        self.target_direction = direction
        self.target_w = scale

        # Fluke beat timing
        self.fluke_phase = phase_offset
        self.fluke_frequency = 2.4  # Fluke beats per second

        # Undulating dive-and-climb trajectory
        self.wave_phase = wave_phase
        self.wave_freq = wave_freq
        self.wave_amplitude = wave_amplitude

        # Oceanic Breach Leap & Porpoising
        self.is_leaping = False
        self.leap_progress = 0.0
        self.leap_duration = 2.2
        self.leap_timer = leap_interval
        self.leap_interval_base = leap_interval
        self.splashes: List[DolphinSplashDrop] = []

        # 3D Banking Turns
        self.is_turning = False
        self.turn_timer = 0.0
        self.turn_duration = 2.6
        self.turn_scale_x = 1.0
        self.bank_angle = 0.0
        self.pitch = 0.0

        # Boundaries
        self.turn_left_bound = -260.0
        self.turn_right_bound = SCREEN_WIDTH + 260.0

        # Real dolphin blowhole bubble rings
        self.bubble_rings: List[DolphinBubbleRing] = []
        self.blowhole_timer = random.uniform(2.0, 4.5)

    def update(self, dt: float, flow_vx: float = 0.0, flow_vy: float = 0.0) -> None:
        self.splashes = [sp for sp in self.splashes if sp.update(dt)]

        if self.is_turning:
            self.turn_timer += dt
            turn_prog = min(1.0, self.turn_timer / self.turn_duration)
            self.bank_angle = math.sin(turn_prog * math.pi) * 22.0 * (-self.direction)
            self.turn_scale_x = math.cos(turn_prog * math.pi)

            # Curved arc turn
            arc_vx = (self.base_speed * 0.45) * self.direction * math.cos(turn_prog * math.pi)
            arc_vy = math.sin(turn_prog * math.pi) * 12.0
            self.x += arc_vx * dt
            self.base_y += arc_vy * dt
            self.y = self.base_y
            self.pitch = math.sin(turn_prog * math.pi) * 6.0 * (-self.direction)

            if turn_prog >= 1.0:
                self.is_turning = False
                self.direction = self.target_direction
                self.turn_scale_x = 1.0
                self.bank_angle = 0.0
                self.pitch = 0.0
        elif self.is_leaping:
            self.leap_progress += dt / self.leap_duration
            prog = min(1.0, self.leap_progress)

            # Powerful fast fluke stroke during leap surge
            self.fluke_phase += 4.5 * dt * (2.0 * math.pi)

            # Parabolic leap arc over surface:
            # Starts at cruising depth (~200), arcs up to apex near surface (~35), and dives back in!
            apex_y = SCREEN_HEIGHT * 0.05
            arc_h = self.cruise_y - apex_y
            self.y = apex_y + 4.0 * ((prog - 0.5) ** 2) * arc_h

            leap_speed = self.base_speed * 1.65
            self.x += (leap_speed * self.direction + flow_vx * 0.15) * dt

            # Dynamic pitch through parabolic arc:
            # Ascent: ~ -32° upward; Apex: 0°; Descent: ~ +32° dive
            self.pitch = (prog - 0.5) * 62.0 * self.direction

            # Emit surface splash when breaching or plunging
            if self.y < SCREEN_HEIGHT * 0.12 and 0.15 < prog < 0.85:
                for _ in range(2):
                    self.splashes.append(
                        DolphinSplashDrop(
                            self.x - self.direction * 15.0,
                            self.y + 25.0,
                            self.z,
                            random.uniform(-35, 35) - self.direction * 25.0,
                            random.uniform(-110, -40),
                        )
                    )

            if prog >= 1.0:
                self.is_leaping = False
                self.leap_timer = random.uniform(self.leap_interval_base * 0.8, self.leap_interval_base * 1.3)
                self.pitch = 0.0
                self.base_y = self.cruise_y
                # Emit bubble ring on re-entry dive
                self.bubble_rings.append(DolphinBubbleRing(self.x, self.y, self.z, self.direction))
        else:
            # Swimming normally in the open sea
            self.fluke_phase += self.fluke_frequency * dt * (2.0 * math.pi)
            self.wave_phase += self.wave_freq * dt * (2.0 * math.pi)

            thrust = abs(math.sin(self.fluke_phase)) * 14.0
            current_speed = self.base_speed + thrust

            wave_dy = math.sin(self.wave_phase) * self.wave_amplitude
            self.y = self.base_y + wave_dy + (flow_vy * 0.2)
            self.x += (current_speed * self.direction + flow_vx * 0.15) * dt

            vy = math.cos(self.wave_phase) * self.wave_amplitude * (self.wave_freq * 2.0 * math.pi)
            raw_slope = math.degrees(math.atan2(vy, max(20.0, current_speed)))
            traj_pitch = -raw_slope * 0.28 * self.direction
            fluke_pitch = math.sin(self.fluke_phase - 0.4) * 1.8
            trim_pitch = 6.0 * self.direction
            self.pitch = traj_pitch + fluke_pitch + trim_pitch
            self.bank_angle = 0.0

            # Countdown to next leap
            self.leap_timer -= dt
            if self.leap_timer <= 0.0 and 120.0 < self.x < SCREEN_WIDTH - 120.0:
                self.is_leaping = True
                self.leap_progress = 0.0

            # Turn at boundaries
            if self.direction == 1 and self.x > self.turn_right_bound:
                self.start_turn(-1)
            elif self.direction == -1 and self.x < self.turn_left_bound:
                self.start_turn(1)

        self.z = max(0.40, min(0.75, self.z + math.sin(self.wave_phase * 0.5) * 0.015 * dt))

        # Real dolphin blowhole bubble ring emission
        self.blowhole_timer -= dt
        if self.blowhole_timer <= 0.0:
            self.blowhole_timer = random.uniform(3.5, 6.0)
            facing_sign = self.direction * (1 if self.turn_scale_x >= 0 else -1)
            eff_w = self.target_w * (self.z / 0.60)
            eff_h = eff_w * 0.46
            bx = self.x + 0.22 * eff_w * facing_sign
            by = self.y - 0.20 * eff_h
            self.bubble_rings.append(DolphinBubbleRing(bx, by, self.z, facing_sign))

        # Update active bubble rings
        self.bubble_rings = [br for br in self.bubble_rings if br.update(dt, flow_vx, flow_vy)]

    def start_turn(self, new_dir: int) -> None:
        if not self.is_turning:
            self.is_turning = True
            self.turn_timer = 0.0
            self.target_direction = new_dir

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float], time_sec: float) -> None:
        # Draw leaping splash droplets
        for sp in self.splashes:
            sp.draw(target, cam_offset)

        # Draw dolphin blowhole bubble rings
        for br in self.bubble_rings:
            br.draw(target, cam_offset)

        if not self.base_surface:
            return

        ox, oy = cam_offset
        eff_scale = (self.z / 0.60)

        # Select fluke frame
        norm_fluke = (self.fluke_phase / (2.0 * math.pi)) % 1.0
        if self.stroke_surfaces:
            frame_idx = int(norm_fluke * len(self.stroke_surfaces)) % len(self.stroke_surfaces)
            active_surf = self.stroke_surfaces[frame_idx]
        else:
            active_surf = self.base_surface

        aspect = active_surf.get_height() / max(1, active_surf.get_width())

        # Perspective width during turn (never flatten into 0px)
        persp_scale = max(0.22, abs(self.turn_scale_x))
        w = max(24, int(self.target_w * eff_scale * persp_scale))
        h = max(16, int(self.target_w * aspect * eff_scale))

        scaled = pygame.transform.smoothscale(active_surf, (w, h))

        # Snout is on right in raw image:
        # direction == 1 (swim right): no flip
        # direction == -1 (swim left): flip
        facing_sign = self.direction * (1 if self.turn_scale_x >= 0 else -1)
        if facing_sign == -1:
            scaled = pygame.transform.flip(scaled, True, False)

        # Realistic sunlit oceanic lighting sheen (neutral high-key ambient so pink and blue remain vivid)
        sun_center = SCREEN_WIDTH * 0.50
        sun_spread = SCREEN_WIDTH * 0.40
        dist_to_sun = abs(self.x - sun_center)
        sun_factor = max(0.0, 1.0 - dist_to_sun / sun_spread) if dist_to_sun < sun_spread else 0.0

        r = int(235 + 20 * sun_factor)
        g = int(240 + 15 * sun_factor)
        b = int(245 + 10 * sun_factor)

        tint_surf = pygame.Surface(scaled.get_size(), pygame.SRCALPHA)
        tint_surf.fill((min(255, r), min(255, g), min(255, b), 255))
        scaled.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        # Masked sunbeam caustics highlight on dolphin melon and dorsal fin
        caustic_phase = time_sec * 2.8 + self.x * 0.012
        caustic_glow = max(0, int(math.sin(caustic_phase) * 26 + 20))
        if caustic_glow > 0:
            spec_layer = pygame.Surface(scaled.get_size(), pygame.SRCALPHA)
            spec_layer.fill((int(caustic_glow * 0.85), int(caustic_glow * 0.95), int(caustic_glow * 1.15), 255))
            spec_layer.blit(scaled, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            scaled.blit(spec_layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # Dynamic pitch and banking rotation
        total_rot = self.pitch + self.bank_angle
        rotated = pygame.transform.rotate(scaled, total_rot)

        rx = int(self.x + ox * self.z - rotated.get_width() / 2)
        ry = int(self.y + oy * self.z - rotated.get_height() / 2)
        target.blit(rotated, (rx, ry))


class RealisticGoldenSeahorse:
    """
    Photorealistic Golden Seahorse (Hippocampus) with authentic syngnathid kinematics:
    - Vertical upright posture with gentle buoyancy bobbing in the water column
    - Current-coupled tilt angle leaning into the ocean water flow
    - Rapid 32 Hz transparent dorsal fin flutter with refraction highlights
    - Prehensile tail curl and uncurl respiration micro-movement
    - Submerged hovering near the ancient ruins columns and kelp
    """

    def __init__(self, surface: Optional[pygame.Surface], x: float = 175.0, y: float = 430.0, z: float = 0.72):
        self.surface = surface
        self.base_x = x
        self.base_y = y
        self.x = x
        self.y = y
        self.z = z
        self.target_h = 106
        self.bob_phase = random.uniform(0, math.pi * 2)
        self.fin_phase = 0.0
        self.tail_phase = random.uniform(0, math.pi * 2)
        self.drift_phase = random.uniform(0, math.pi * 2)
        self.current_tilt = 0.0

    def update(self, dt: float, flow_vx: float = 0.0, flow_vy: float = 0.0) -> None:
        self.bob_phase += 1.6 * dt
        self.fin_phase += 32.0 * (2.0 * math.pi) * dt  # Rapid dorsal fin flutter
        self.tail_phase += 1.2 * dt
        self.drift_phase += 0.8 * dt

        # Natural vertical buoyancy bobbing
        bob_y = math.sin(self.bob_phase) * 9.0 + math.cos(self.bob_phase * 0.5) * 3.0
        bob_x = math.sin(self.drift_phase) * 5.0 + (flow_vx * 0.15)
        self.y = self.base_y + bob_y
        self.x = self.base_x + bob_x

        # Tilt gently into water flow current (hydrodynamic drag)
        target_tilt = -(flow_vx * 0.35) + math.sin(self.bob_phase * 0.8) * 3.0
        self.current_tilt += (target_tilt - self.current_tilt) * 3.0 * dt

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float], time_sec: float) -> None:
        if not self.surface:
            return
        ox, oy = cam_offset
        eff_scale = self.z / 0.72
        aspect = self.surface.get_width() / max(1, self.surface.get_height())
        h = max(24, int(self.target_h * eff_scale))
        w = max(16, int(h * aspect))

        scaled = pygame.transform.smoothscale(self.surface, (w, h))

        # Rapidly fluttering tiny transparent dorsal fin on the seahorse back
        fin_flutter = math.sin(self.fin_phase)
        fin_w = max(4, int(w * 0.28))
        fin_h = max(6, int(h * 0.32))
        fin_surf = pygame.Surface((fin_w + 4, fin_h + 4), pygame.SRCALPHA)
        fin_cx = fin_w // 2 + 2
        fin_pts = [
            (fin_cx, 2),
            (fin_cx - int(fin_flutter * fin_w * 0.4), fin_h // 2),
            (fin_cx, fin_h),
            (fin_cx + 2, fin_h // 2),
        ]
        pygame.draw.polygon(fin_surf, (200, 240, 255, 140), fin_pts)
        pygame.draw.polygon(fin_surf, (255, 255, 255, 190), fin_pts, 1)

        # Ambient underwater lighting and sunbeam caustics
        caustic_glow = max(0, int(math.sin(time_sec * 2.5 + self.x * 0.02) * 20 + 15))
        if caustic_glow > 0:
            spec_layer = pygame.Surface((w, h), pygame.SRCALPHA)
            spec_layer.fill((caustic_glow, caustic_glow, int(caustic_glow * 0.6), 255))
            spec_layer.blit(scaled, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            scaled.blit(spec_layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # Rotate by current tilt
        rotated = pygame.transform.rotate(scaled, self.current_tilt)
        rx = int(self.x + ox * self.z - rotated.get_width() / 2)
        ry = int(self.y + oy * self.z - rotated.get_height() / 2)

        # Blit dorsal fin behind seahorse back
        fin_rot = pygame.transform.rotate(fin_surf, self.current_tilt)
        fin_x = rx + int(rotated.get_width() * 0.22)
        fin_y = ry + int(rotated.get_height() * 0.32)
        target.blit(fin_rot, (fin_x, fin_y))

        # Blit seahorse body
        target.blit(rotated, (rx, ry))


class RealisticNudibranch:
    """
    Photorealistic Leaf Sheep / Sea Angel Nudibranch (Costasiella kuroshimae):
    - Realistic benthic crawling locomotion along the ancient seabed mosaic tiles
    - Smooth patrol between ruins columns and reef sand with lifelike pauses
    - Peristaltic crawling expansion/contraction along muscular ventral foot
    - Organic leaf cerata undulating in response to ocean water flow
    - Twitching sensory bunny-ear rhinophores (chemoreceptors)
    - Pristine natural coloration without artificial blinking overlays
    """

    def __init__(self, surface: Optional[pygame.Surface], x: float = 380.0, y: float = 612.0, z: float = 0.88):
        self.surface = surface
        self.x = x
        self.base_y = y
        self.y = y
        self.z = z
        self.target_w = 98
        self.crawl_phase = 0.0
        self.cerata_phase = 0.0
        self.rhinophore_twitch_timer = 3.5
        self.twitch_angle = 0.0
        self.direction = 1  # 1 = crawl right, -1 = crawl left
        self.crawl_speed = 9.5  # Authentic sea slug slow crawl
        self.pause_timer = 0.0
        self.min_x = SCREEN_WIDTH * 0.22
        self.max_x = SCREEN_WIDTH * 0.44

    def update(self, dt: float, flow_vx: float = 0.0, flow_vy: float = 0.0) -> None:
        self.cerata_phase += 1.8 * dt

        if self.pause_timer > 0.0:
            self.pause_timer -= dt
            # Inquisitive antenna twitch during pause
            self.twitch_angle = math.sin(self.cerata_phase * 2.2) * 2.0
            return

        self.crawl_phase += 1.2 * dt
        # Smooth crawling along seabed floor
        self.x += self.crawl_speed * self.direction * dt
        self.y = self.base_y + math.sin(self.crawl_phase * 2.0) * 1.5

        # Patrol boundary turnaround with natural grazing pauses
        if self.direction == 1 and self.x > self.max_x:
            self.direction = -1
            self.pause_timer = random.uniform(1.8, 3.2)
        elif self.direction == -1 and self.x < self.min_x:
            self.direction = 1
            self.pause_timer = random.uniform(1.8, 3.2)

        # Rhinophore (bunny ears) twitch behavior every 3-5 seconds
        self.rhinophore_twitch_timer -= dt
        if self.rhinophore_twitch_timer <= 0.0:
            self.twitch_angle = math.sin(self.rhinophore_twitch_timer * -24.0) * 4.0
            if self.rhinophore_twitch_timer < -0.35:
                self.rhinophore_twitch_timer = random.uniform(3.5, 6.0)
                self.twitch_angle = 0.0

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float], time_sec: float, flow_vx: float = 0.0) -> None:
        if not self.surface:
            return
        ox, oy = cam_offset
        eff_scale = self.z / 0.88
        aspect = self.surface.get_height() / max(1, self.surface.get_width())

        # Peristaltic breathing expansion
        stretch = math.sin(self.crawl_phase * 2.0) * 0.04
        w = max(20, int(self.target_w * eff_scale * (1.0 + stretch)))
        h = max(20, int(self.target_w * aspect * eff_scale * (1.0 - stretch)))

        scaled = pygame.transform.smoothscale(self.surface, (w, h))
        # Facing direction: In raw asset, cute bunny face is on right.
        # When crawling left (direction == -1), flip so head leads!
        if self.direction == -1:
            scaled = pygame.transform.flip(scaled, True, False)

        # Cerata undulating wave: leaf cerata sway naturally with the ocean current flow
        num_slices = 10
        slice_h = max(1, h // num_slices)
        bent_surf = pygame.Surface((w + 16, h + 4), pygame.SRCALPHA)
        for i in range(num_slices):
            norm_y = (num_slices - 1 - i) / float(num_slices)  # 1.0 at top cerata, 0.0 at base foot
            cerata_sway = math.sin(self.cerata_phase + i * 0.4) * (norm_y ** 1.5) * 4.5 + (flow_vx * 0.12 * norm_y)
            sy = i * slice_h
            sh = slice_h if sy + slice_h <= h else (h - sy)
            if sh > 0:
                rect = pygame.Rect(0, sy, w, sh)
                bent_surf.blit(scaled, (8 + int(cerata_sway), sy), rect)

        # Ambient sunlight caustics reflection (soft, organic, no crude blinking blotches)
        sun_gleam = max(0, int(math.sin(time_sec * 1.8 + self.x * 0.02) * 16 + 10))
        if sun_gleam > 0:
            gleam_layer = pygame.Surface(bent_surf.get_size(), pygame.SRCALPHA)
            gleam_layer.fill((sun_gleam, int(sun_gleam * 1.1), int(sun_gleam * 0.8), 255))
            gleam_layer.blit(bent_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            bent_surf.blit(gleam_layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # Rotate by twitch angle
        rotated = pygame.transform.rotate(bent_surf, self.twitch_angle)
        rx = int(self.x + ox * self.z - rotated.get_width() / 2)
        ry = int(self.y + oy * self.z - rotated.get_height() / 2)
        target.blit(rotated, (rx, ry))


class RealisticTieredBetta:
    """
    Photorealistic Tiered Silk Gown Betta Fish (Betta splendens):
    - Cascading multi-tiered ruffled fins billowing with fluid cloth physics
    - Authentic Siamese Betta burst-and-glide locomotion (thrust burst, regal glide, hovering flare)
    - Correct facing orientation (head leads forward in swimming direction)
    - Ambient prismatic shimmer across vibrant magenta and cyan scales
    """

    def __init__(self, surface: Optional[pygame.Surface], x: float = 840.0, y: float = 330.0, z: float = 0.56, direction: int = -1):
        self.surface = surface
        self.x = x
        self.base_y = y
        self.y = y
        self.z = z
        self.base_speed = 28.0
        self.speed = self.base_speed
        self.direction = direction  # -1 = cruises left, 1 = cruises right
        self.target_w = 130
        self.fin_phase = random.uniform(0, math.pi * 2)
        self.swim_cycle = random.uniform(0.0, 2.8)
        self.pitch = 0.0

    def update(self, dt: float, flow_vx: float = 0.0, flow_vy: float = 0.0) -> None:
        self.fin_phase += 2.4 * dt
        self.swim_cycle = (self.swim_cycle + dt) % 2.8

        # Authentic Siamese Betta Burst-and-Glide Kinematics:
        # 0.0 - 0.55s: Burst propulsion stroke
        # 0.55 - 1.9s: Smooth glide with fluid resistance deceleration
        # 1.9 - 2.8s: Hovering flare & gentle settling in water current
        if self.swim_cycle < 0.55:
            stroke_prog = self.swim_cycle / 0.55
            thrust = math.sin(stroke_prog * math.pi) * 44.0
            self.speed = self.base_speed + thrust
            self.pitch = -4.0 * self.direction  # Pitches slightly up during stroke
        elif self.swim_cycle < 1.9:
            glide_prog = (self.swim_cycle - 0.55) / 1.35
            self.speed = max(9.0, (self.base_speed + 14.0) * (1.0 - glide_prog * 0.68))
            self.pitch = math.sin(glide_prog * math.pi) * 2.2 * self.direction
        else:
            self.speed = 6.0
            self.pitch = math.sin(self.swim_cycle * 2.0) * 1.5

        # Horizontal translation & vertical tidal undulation
        self.x += (self.speed * self.direction + flow_vx * 0.22) * dt
        self.y = self.base_y + math.sin(self.swim_cycle * 1.4) * 12.0 + (flow_vy * 0.3)

        # Screen boundaries wrap
        if self.direction == -1 and self.x < -180:
            self.x = SCREEN_WIDTH + 180
            self.base_y = random.uniform(SCREEN_HEIGHT * 0.30, SCREEN_HEIGHT * 0.46)
        elif self.direction == 1 and self.x > SCREEN_WIDTH + 180:
            self.x = -180
            self.base_y = random.uniform(SCREEN_HEIGHT * 0.30, SCREEN_HEIGHT * 0.46)

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float], time_sec: float, flow_vx: float = 0.0) -> None:
        if not self.surface:
            return
        ox, oy = cam_offset
        eff_scale = self.z / 0.56
        aspect = self.surface.get_height() / max(1, self.surface.get_width())

        w = max(18, int(self.target_w * eff_scale))
        h = max(24, int(self.target_w * aspect * eff_scale))

        scaled = pygame.transform.smoothscale(self.surface, (w, h))
        # Facing direction: In raw asset, head is on RIGHT.
        # When moving left (direction == -1), MUST flip horizontally so head points left!
        # When moving right (direction == 1), do NOT flip (head already points right)!
        if self.direction == -1:
            scaled = pygame.transform.flip(scaled, True, False)

        # Sinuous multi-tiered peacock gown feather billow:
        # 24 vertical slices undulate with phase lag down the tiers
        num_slices = 24
        slice_step = h / num_slices
        slice_h = int(math.ceil(slice_step)) + 1
        max_pad = 28
        bent_surf = pygame.Surface((w + max_pad * 2, h + 4), pygame.SRCALPHA)

        for i in range(num_slices):
            ratio_y = i / float(num_slices)  # 0 at head, 1 at bottom tier skirt
            # Primary feather sway + secondary high-frequency ripple
            primary_amp = (ratio_y ** 1.5) * 15.0
            ripple_amp = (ratio_y ** 1.1) * 3.5
            wave_offset = (
                math.sin(self.fin_phase - ratio_y * 3.2) * primary_amp
                + math.sin(self.fin_phase * 2.2 - ratio_y * 5.0) * ripple_amp
                + (flow_vx * 0.16 * ratio_y) * self.direction
            )

            sy = int(i * slice_step)
            cur_sh = slice_h if sy + slice_h <= h else (h - sy)
            if cur_sh > 0:
                rect = pygame.Rect(0, sy, w, cur_sh)
                bent_surf.blit(scaled, (max_pad + int(wave_offset), sy), rect)

        # Specular light gleam on silk fin edges
        gleam_alpha = max(0, int(math.sin(time_sec * 3.0 + self.x * 0.02) * 22 + 14))
        if gleam_alpha > 0:
            spec = pygame.Surface(bent_surf.get_size(), pygame.SRCALPHA)
            spec.fill((int(gleam_alpha * 1.2), int(gleam_alpha * 0.9), int(gleam_alpha * 1.3), 255))
            spec.blit(bent_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            bent_surf.blit(spec, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        rotated = pygame.transform.rotate(bent_surf, self.pitch)
        rx = int(self.x + ox * self.z - rotated.get_width() / 2)
        ry = int(self.y + oy * self.z - rotated.get_height() / 2)
        target.blit(rotated, (rx, ry))


class RealisticWhiteBetta:
    """
    Photorealistic Angelic White Halfmoon Betta Fish:
    - 180-degree spread gossamer caudal veil fin billowing in current
    - Authentic Siamese Betta burst-and-glide locomotion
    - Horizontal trailing-edge fin flexion with delicate cloth ripples
    - Ethereal translucent pearlescent sheen with soft caustic refraction
    """

    def __init__(self, surface: Optional[pygame.Surface], x: float = 380.0, y: float = 270.0, z: float = 0.65, direction: int = 1):
        self.surface = surface
        self.x = x
        self.base_y = y
        self.y = y
        self.z = z
        self.base_speed = 32.0
        self.speed = self.base_speed
        self.direction = direction  # Cruises across water column
        self.target_w = 160
        self.fin_phase = random.uniform(0, math.pi * 2)
        self.swim_cycle = random.uniform(0.0, 2.8)
        self.pitch = 0.0

    def update(self, dt: float, flow_vx: float = 0.0, flow_vy: float = 0.0) -> None:
        self.fin_phase += 2.2 * dt
        self.swim_cycle = (self.swim_cycle + dt) % 2.8

        # Authentic Siamese Betta Burst-and-Glide Kinematics:
        if self.swim_cycle < 0.55:
            stroke_prog = self.swim_cycle / 0.55
            thrust = math.sin(stroke_prog * math.pi) * 46.0
            self.speed = self.base_speed + thrust
            self.pitch = -4.5 * self.direction
        elif self.swim_cycle < 1.9:
            glide_prog = (self.swim_cycle - 0.55) / 1.35
            self.speed = max(10.0, (self.base_speed + 16.0) * (1.0 - glide_prog * 0.68))
            self.pitch = math.sin(glide_prog * math.pi) * 2.5 * self.direction
        else:
            self.speed = 7.0
            self.pitch = math.sin(self.swim_cycle * 2.0) * 1.6

        self.x += (self.speed * self.direction + flow_vx * 0.26) * dt
        self.y = self.base_y + math.sin(self.swim_cycle * 1.3) * 14.0 + (flow_vy * 0.35)

        if self.direction == 1 and self.x > SCREEN_WIDTH + 200:
            self.x = -200
            self.base_y = random.uniform(SCREEN_HEIGHT * 0.22, SCREEN_HEIGHT * 0.38)
        elif self.direction == -1 and self.x < -200:
            self.x = SCREEN_WIDTH + 200
            self.base_y = random.uniform(SCREEN_HEIGHT * 0.22, SCREEN_HEIGHT * 0.38)

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float], time_sec: float, flow_vx: float = 0.0) -> None:
        if not self.surface:
            return
        ox, oy = cam_offset
        eff_scale = self.z / 0.65
        aspect = self.surface.get_height() / max(1, self.surface.get_width())

        w = max(20, int(self.target_w * eff_scale))
        h = max(20, int(self.target_w * aspect * eff_scale))

        scaled = pygame.transform.smoothscale(self.surface, (w, h))
        # Facing direction: In raw asset, head is on RIGHT, tail is on LEFT.
        # direction == 1 (swims right): head points right (no flip)
        # direction == -1 (swims left): flipped horizontally so head points left
        if self.direction == -1:
            scaled = pygame.transform.flip(scaled, True, False)

        # Gossamer halfmoon veil fin trailing wave:
        num_slices = 16
        slice_step = w / num_slices
        slice_w = int(math.ceil(slice_step)) + 1
        max_pad = 20
        bent_surf = pygame.Surface((w + 8, h + max_pad * 2), pygame.SRCALPHA)

        for i in range(num_slices):
            norm_tail = (num_slices - 1 - i) / float(num_slices) if self.direction == 1 else (i / float(num_slices))
            amp = (norm_tail ** 1.8) * 13.0
            offset_y = math.sin(self.fin_phase - norm_tail * 2.8) * amp + math.sin(time_sec * 1.5) * (flow_vx * 0.08 * norm_tail)

            sx = int(i * slice_step)
            cur_sw = slice_w if sx + slice_w <= w else (w - sx)
            if cur_sw > 0:
                rect = pygame.Rect(sx, 0, cur_sw, h)
                bent_surf.blit(scaled, (sx + 4, max_pad + int(offset_y)), rect)

        # Translucent gossamer pearlescent sheen
        caustic_glow = max(0, int(math.sin(time_sec * 2.8 + self.x * 0.015) * 25 + 18))
        if caustic_glow > 0:
            spec = pygame.Surface(bent_surf.get_size(), pygame.SRCALPHA)
            spec.fill((caustic_glow, int(caustic_glow * 1.1), int(caustic_glow * 1.2), 255))
            spec.blit(bent_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            bent_surf.blit(spec, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        rotated = pygame.transform.rotate(bent_surf, self.pitch)
        rx = int(self.x + ox * self.z - rotated.get_width() / 2)
        ry = int(self.y + oy * self.z - rotated.get_height() / 2)
        target.blit(rotated, (rx, ry))


class RealisticMermaid:
    """
    Photorealistic Luminescent Mermaid:
    - Biological dolphin-kick undulation: 28-slice traveling wave from hips to caudal flukes
    - Authentic propulsion physics: acceleration surge on downstroke, graceful hydrodynamic glide on upstroke
    - Smooth 3D yaw and banking turnaround (no abrupt snapping or card flipping)
    - Natural body pitch dynamically following the 3D velocity vector
    - Ethereal floating turquoise hair responding to ocean water flow
    - Trailing bioluminescent starlight sparkles and micro-bubbles emitted from gemstone bracelet & caudal fluke
    """

    def __init__(self, surface: Optional[pygame.Surface], x: float = 210.0, y: float = 340.0, z: float = 0.62, direction: int = 1):
        self.surface = surface
        self.x = x
        self.base_y = y
        self.y = y
        self.z = z
        self.direction = direction  # 1 = swimming right, -1 = swimming left
        self.target_direction = direction
        self.target_w = 400  # Majestic life-size photorealistic mermaid scale
        self.base_speed = 32.0
        self.speed = self.base_speed
        
        # Kinematics
        self.swim_phase = random.uniform(0, math.pi * 2)
        self.wave_phase = random.uniform(0, math.pi * 2)
        self.pitch = 0.0
        self.bank_angle = 0.0
        
        # 3D Turnaround physics
        self.is_turning = False
        self.turn_timer = 0.0
        self.turn_duration = 2.4
        self.turn_scale_x = 1.0

        # Corridor bounds (keeps her within scenic Atlantis lagoon, completely clear of central UI buttons)
        self.min_x = 75.0
        self.max_x = 285.0
        
        # Sparkles and wake bubbles
        self.sparkles: List[GoldSparkleMote] = []
        self.sparkle_timer = 0.0

    def start_turn(self, new_dir: int) -> None:
        if not self.is_turning:
            self.is_turning = True
            self.turn_timer = 0.0
            self.target_direction = new_dir

    def update(self, dt: float, flow_vx: float = 0.0, flow_vy: float = 0.0) -> None:
        # Biological dolphin-kick cycle: ~1.2 cycles per second
        self.swim_phase += 3.4 * dt
        self.wave_phase += 0.85 * dt

        # Downstroke thrust surge (power stroke produces burst, followed by elegant buoyant glide)
        stroke_val = math.sin(self.swim_phase)
        downstroke_thrust = max(0.0, stroke_val) ** 1.6 * 26.0
        glide_thrust = max(0.0, -stroke_val) * 6.0
        current_speed = self.base_speed + downstroke_thrust + glide_thrust

        if self.is_turning:
            self.turn_timer += dt
            prog = min(1.0, self.turn_timer / self.turn_duration)
            # Smooth 3D yaw foreshortening: cosine scale transition
            self.turn_scale_x = math.cos(prog * math.pi)
            self.bank_angle = math.sin(prog * math.pi) * 18.0 * (-self.direction)
            
            # Graceful curved loop during turnaround
            arc_vx = (self.base_speed * 0.35) * self.direction * math.cos(prog * math.pi)
            arc_vy = math.sin(prog * math.pi) * 9.0
            self.x += arc_vx * dt
            self.y += arc_vy * dt
            self.pitch = math.sin(prog * math.pi) * 8.0 * (-self.direction)

            if prog >= 1.0:
                self.is_turning = False
                self.direction = self.target_direction
                self.turn_scale_x = 1.0
                self.bank_angle = 0.0
                self.pitch = 0.0
        else:
            self.turn_scale_x = 1.0
            self.bank_angle = 0.0
            # Sinuous 3D depth-lagoon cruise
            dy = math.sin(self.wave_phase) * 18.0 + math.cos(self.swim_phase * 0.5) * 6.0
            self.y = self.base_y + dy + (flow_vy * 0.20)
            self.x += (current_speed * self.direction + flow_vx * 0.18) * dt

            # Body pitch dynamically aligns with dolphin kick and swimming velocity
            kick_pitch = -math.cos(self.swim_phase) * 6.5 * self.direction
            climb_pitch = math.cos(self.wave_phase) * 3.5 * self.direction
            self.pitch = kick_pitch + climb_pitch

            # Check boundary turnaround
            if self.direction == 1 and self.x > self.max_x:
                self.start_turn(-1)
            elif self.direction == -1 and self.x < self.min_x:
                self.start_turn(1)

        # Emit magical gemstone sparkles from reaching hand & bioluminescent tail flukes
        self.sparkle_timer += dt
        if self.sparkle_timer >= 0.14:
            self.sparkle_timer = 0.0
            eff_w = self.target_w * (self.z / 0.62)
            facing_sign = self.direction * (1 if self.turn_scale_x >= 0 else -1)
            # Hand sparkle
            hand_x = self.x + (0.32 * eff_w) * facing_sign
            hand_y = self.y + 0.04 * eff_w
            self.sparkles.append(GoldSparkleMote(hand_x, hand_y))
            # Tail tip luminescence
            tail_x = self.x - (0.36 * eff_w) * facing_sign
            tail_y = self.y + math.sin(self.swim_phase) * 12.0
            self.sparkles.append(GoldSparkleMote(tail_x, tail_y))

        self.sparkles = [sp for sp in self.sparkles if sp.update(dt)]

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float], time_sec: float, flow_vx: float = 0.0) -> None:
        if not self.surface:
            return
        ox, oy = cam_offset
        eff_scale = self.z / 0.62
        aspect = self.surface.get_height() / max(1, self.surface.get_width())

        # Perspective 3D yaw width (never collapse into a thin slit during turnaround)
        persp_scale = max(0.65, abs(self.turn_scale_x))
        w = max(40, int(self.target_w * eff_scale * persp_scale))
        h = max(25, int(self.target_w * aspect * eff_scale))

        scaled = pygame.transform.smoothscale(self.surface, (w, h))

        # Facing direction: In raw asset, head is on RIGHT, tail is on LEFT
        facing_sign = self.direction * (1 if self.turn_scale_x >= 0 else -1)
        if facing_sign == -1:
            scaled = pygame.transform.flip(scaled, True, False)

        # Sinuous 28-slice traveling wave undulation from hips to caudal fin
        num_slices = 28
        slice_step = w / num_slices
        slice_w = int(math.ceil(slice_step)) + 1
        max_pad = 28
        bent_surf = pygame.Surface((w + 10, h + max_pad * 2), pygame.SRCALPHA)

        for i in range(num_slices):
            # Tail is at left when facing_sign == 1, at right when facing_sign == -1
            if facing_sign == 1:
                norm_pos = (num_slices - 1 - i) / float(num_slices)  # 1.0 at tail (left), 0.0 at head (right)
            else:
                norm_pos = i / float(num_slices)  # 1.0 at tail (right), 0.0 at head (left)

            # Torso (0.0 to 0.35) remains firm with gentle breathing motion
            # Tail flukes (0.35 to 1.0) undulate with full hydrodynamic traveling wave
            if norm_pos < 0.35:
                # Gentle chest breathing and shoulder tilt
                amp = (norm_pos / 0.35) * 2.5
                wave_offset = math.sin(self.swim_phase) * amp
            else:
                tail_t = (norm_pos - 0.35) / 0.65
                # Progressive amplitude with whip at fluke tips
                amp = 2.5 + (tail_t ** 1.65) * 16.5
                # True traveling wave: phase delay increases towards the tail tips
                wave_phase = self.swim_phase - tail_t * 2.85
                wave_offset = math.sin(wave_phase) * amp + (flow_vx * 0.06 * tail_t)

            sx = int(i * slice_step)
            cur_sw = slice_w if sx + slice_w <= w else (w - sx)
            if cur_sw > 0:
                rect = pygame.Rect(sx, 0, cur_sw, h)
                bent_surf.blit(scaled, (sx + 4, max_pad + int(wave_offset)), rect)

        # Bioluminescent iridescence sheen across scales & floating turquoise hair
        caustic_glow = max(0, int(math.sin(time_sec * 2.4 + self.x * 0.015) * 24 + 18))
        if caustic_glow > 0:
            spec = pygame.Surface(bent_surf.get_size(), pygame.SRCALPHA)
            spec.fill((int(caustic_glow * 0.6), int(caustic_glow * 1.15), int(caustic_glow * 1.35), 255))
            spec.blit(bent_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            bent_surf.blit(spec, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # Total 3D rotation: pitch + banking roll angle
        total_rot = self.pitch + self.bank_angle
        rotated = pygame.transform.rotate(bent_surf, total_rot)
        rx = int(self.x + ox * self.z - rotated.get_width() / 2)
        ry = int(self.y + oy * self.z - rotated.get_height() / 2)
        target.blit(rotated, (rx, ry))

        # Draw magical sparkle motes
        for sp in self.sparkles:
            sp.draw(target, cam_offset)


# =========================================================================
# 4. MANTA RAY & BIOLUMINESCENT JELLYFISH
# =========================================================================

class RealisticManta:
    """Giant manta ray soaring gracefully through the high pelagic open ocean (Z: 0.30)."""

    def __init__(self, surface: Optional[pygame.Surface]):
        self.base_surface = surface
        self.x = SCREEN_WIDTH * 0.72
        self.y = SCREEN_HEIGHT * 0.08  # High in pelagic surface layer, above shark and title
        self.z = 0.30  # Distant background
        self.speed = 34.0
        self.direction = -1
        self.wing_phase = random.uniform(0, math.pi * 2)
        self.target_w = 300
        self.pitch = 0.0

    def update(self, dt: float) -> None:
        self.wing_phase += 1.35 * dt
        self.x += self.speed * self.direction * dt
        self.y += math.sin(self.wing_phase * 0.5) * (6.0 * dt)
        self.pitch = math.sin(self.wing_phase) * 2.8

        if self.x < -360:
            self.x = SCREEN_WIDTH + 360
            self.y = random.uniform(SCREEN_HEIGHT * 0.06, SCREEN_HEIGHT * 0.10)

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float]) -> None:
        if not self.base_surface:
            return
        ox, oy = cam_offset
        aspect = self.base_surface.get_height() / max(1, self.base_surface.get_width())

        w = int(self.target_w * (self.z / 0.30))
        h = int(self.target_w * aspect)
        if w <= 0 or h <= 0:
            return

        scaled = pygame.transform.smoothscale(self.base_surface, (w, h))
        if self.direction == 1:
            scaled = pygame.transform.flip(scaled, True, False)

        # Sinuous wingtip flexion wave: outer wingtips flex vertically
        num_slices = 16
        slice_step = w / num_slices
        slice_w = int(math.ceil(slice_step)) + 1
        max_pad = 20
        bent_surf = pygame.Surface((w + 10, h + max_pad * 2), pygame.SRCALPHA)

        for i in range(num_slices):
            norm_center = abs(i - (num_slices / 2)) / (num_slices / 2)  # 0 at center, 1 at wingtips
            wing_amp = (norm_center ** 1.8) * 9.0
            offset_y = math.sin(self.wing_phase - norm_center * 1.5) * wing_amp

            sx = int(i * slice_step)
            cur_sw = slice_w if sx + slice_w <= w else (w - sx)
            if cur_sw > 0:
                rect = pygame.Rect(sx, 0, cur_sw, h)
                bent_surf.blit(scaled, (sx + 5, max_pad + offset_y), rect)

        # Ambient deep ocean cyan tint
        tint = pygame.Surface(bent_surf.get_size(), pygame.SRCALPHA)
        tint.fill((190, 220, 245, 255))
        bent_surf.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        rotated = pygame.transform.rotate(bent_surf, self.pitch)

        rx = int(self.x + ox * self.z - rotated.get_width() / 2)
        ry = int(self.y + oy * self.z - rotated.get_height() / 2)
        target.blit(rotated, (rx, ry))


class RealisticJellyfish:
    """Bioluminescent underwater jellyfish pulsing rhythmically upwards with trailing tentacles."""

    def __init__(self, surface: Optional[pygame.Surface], x: float = 220, y: float = 460, z: float = 0.74):
        self.surface = surface
        self.x = x
        self.y = y
        self.z = z
        self.target_w = 125
        self.pulse_phase = random.uniform(0, math.pi * 2)
        self.pulse_speed = 1.6
        self.speed_y = 18.0
        self.drift_phase = random.uniform(0, math.pi * 2)

    def update(self, dt: float) -> None:
        self.pulse_phase += self.pulse_speed * dt
        self.drift_phase += 0.7 * dt

        pulse = math.sin(self.pulse_phase)
        thrust = max(0.0, pulse)
        self.y -= (self.speed_y + thrust * 22.0) * dt
        self.x += math.sin(self.drift_phase) * (10.0 * dt)

        if self.y < -140:
            self.y = SCREEN_HEIGHT + random.uniform(40, 110)
            self.x = random.uniform(120, SCREEN_WIDTH - 120)

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float]) -> None:
        if not self.surface:
            return
        ox, oy = cam_offset
        pulse = math.sin(self.pulse_phase)
        thrust = max(0.0, pulse)
        scale_x = (1.0 - thrust * 0.12)
        scale_y = (1.0 + thrust * 0.18)

        aspect = self.surface.get_height() / self.surface.get_width()
        sw = max(12, int(self.target_w * scale_x))
        sh = max(12, int(self.target_w * aspect * scale_y))

        scaled = pygame.transform.smoothscale(self.surface, (sw, sh))

        # Rhythmic inner bioluminescent core glow (CLEANLY MASKED with jellyfish alpha)
        glow_alpha = int(45 + 35 * thrust)
        if glow_alpha > 0:
            glow_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            glow_cx, glow_cy = sw // 2, int(sh * 0.35)
            glow_r = max(6, int(sw * 0.40))
            pygame.draw.circle(glow_surf, (80, 220, 255, glow_alpha), (glow_cx, glow_cy), glow_r)
            glow_surf.blit(scaled, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            scaled.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        target.blit(scaled, (int(self.x + ox * self.z - sw / 2), int(self.y + oy * self.z - sh / 2)))


# =========================================================================
# 5. PARTICLES, BUBBLES, KELP & TREASURE CHEST SPARKLES
# =========================================================================

class MarineSnowMote:
    """Microscopic organic drift particle creating underwater volumetric atmosphere."""

    def __init__(self):
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = random.uniform(0, SCREEN_HEIGHT)
        self.z = random.uniform(0.2, 1.0)
        self.speed_y = random.uniform(6.0, 16.0) * self.z
        self.drift_phase = random.uniform(0, math.pi * 2)
        self.drift_speed = random.uniform(0.8, 1.8)
        self.radius = max(1.0, 2.0 * self.z)
        self.alpha = int(120 * self.z)

    def update(self, dt: float, flow_vx: float = 0.0, flow_vy: float = 0.0) -> None:
        self.drift_phase += self.drift_speed * dt
        self.y += (self.speed_y + flow_vy * 0.3) * dt
        self.x += (math.sin(self.drift_phase) * 10.0 + flow_vx * 0.45 * self.z) * dt

        if self.y > SCREEN_HEIGHT + 10:
            self.y = -10
            self.x = random.uniform(0, SCREEN_WIDTH)
        elif self.x < -10:
            self.x = SCREEN_WIDTH + 10
        elif self.x > SCREEN_WIDTH + 10:
            self.x = -10

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float]) -> None:
        ox, oy = cam_offset
        px = int(self.x + ox * self.z)
        py = int(self.y + oy * self.z)
        if 0 <= px < SCREEN_WIDTH and 0 <= py < SCREEN_HEIGHT:
            r = int(self.radius)
            if r <= 1:
                target.set_at((px, py), (200, 240, 255))
            else:
                dot_surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(dot_surf, (200, 240, 255, self.alpha), (r + 1, r + 1), r)
                target.blit(dot_surf, (px - r - 1, py - r - 1))


class Realistic3DBubble:
    """Rising ambient bubble with physical refraction glint and wobble."""

    def __init__(self, x: float = None, y: float = None):
        self.x = x if x is not None else random.uniform(0, SCREEN_WIDTH)
        self.y = y if y is not None else random.uniform(0, SCREEN_HEIGHT)
        self.z = random.uniform(0.35, 1.0)
        self.radius = random.uniform(3.0, 8.5) * self.z
        self.speed = random.uniform(38.0, 95.0) * (0.8 + self.z * 0.4)
        self.wobble_phase = random.uniform(0, math.pi * 2)
        self.wobble_speed = random.uniform(3.0, 6.0)
        self.wobble_amp = random.uniform(1.0, 2.8)

    def update(self, dt: float, flow_vx: float = 0.0, flow_vy: float = 0.0) -> None:
        self.y -= (self.speed - flow_vy * 0.4) * dt
        self.wobble_phase += self.wobble_speed * dt
        self.x += (math.sin(self.wobble_phase) * self.wobble_amp + flow_vx * 0.45 * self.z) * dt

        if self.y < -30:
            self.y = SCREEN_HEIGHT + random.uniform(10, 60)
            self.x = random.uniform(0, SCREEN_WIDTH)
            self.z = random.uniform(0.35, 1.0)
            self.radius = random.uniform(3.0, 8.5) * self.z
        elif self.x > SCREEN_WIDTH + 40:
            self.x = -40

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float]) -> None:
        ox, oy = cam_offset
        px = int(self.x + ox * self.z)
        py = int(self.y + oy * self.z)
        r = int(self.radius)
        if r < 1:
            return

        size = r * 2 + 6
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        alpha = int(175 * self.z)

        pygame.draw.circle(surf, (180, 240, 255, alpha), (center, center), r, max(1, int(r * 0.18)))
        pygame.draw.circle(surf, (0, 180, 220, int(alpha * 0.20)), (center, center), int(r * 0.8))
        glint_off = max(1, int(r * 0.35))
        glint_r = max(1, int(r * 0.28))
        pygame.draw.circle(surf, (255, 255, 255, int(alpha * 0.95)), (center - glint_off, center - glint_off), glint_r)

        target.blit(surf, (px - center, py - center))


class GoldSparkleMote:
    """Sparkling golden motes drifting from the treasure chest."""

    def __init__(self, chest_x: float, chest_y: float):
        self.cx = chest_x
        self.cy = chest_y
        self.x = chest_x + random.uniform(-60, 60)
        self.y = chest_y + random.uniform(-35, 15)
        self.life = random.uniform(1.2, 2.4)
        self.age = 0.0
        self.vy = -random.uniform(16.0, 42.0)
        self.vx = random.uniform(-10.0, 10.0)
        self.size = random.uniform(1.8, 3.8)
        self.twinkle_phase = random.uniform(0, math.pi * 2)

    def update(self, dt: float) -> bool:
        self.age += dt
        self.twinkle_phase += 8.0 * dt
        self.y += self.vy * dt
        self.x += (self.vx + math.sin(self.twinkle_phase) * 8.0) * dt
        return self.age < self.life

    def draw(self, target: pygame.Surface, cam_offset: Tuple[float, float]) -> None:
        ox, oy = cam_offset
        fade = 1.0 - (self.age / self.life)
        alpha = int(240 * fade * (0.6 + 0.4 * math.sin(self.twinkle_phase)))
        r = max(1, int(self.size))
        surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 220, 50, alpha), (r + 2, r + 2), r)
        pygame.draw.circle(surf, (255, 255, 255, int(alpha * 0.8)), (r + 2, r + 2), max(1, r // 2))
        target.blit(surf, (int(self.x + ox - r - 2), int(self.y + oy - r - 2)))


class RealisticKelpFrond:
    """Organic multi-jointed kelp frond swaying with physics-based water currents."""

    def __init__(self, x: float, height: float, color: Tuple[int, int, int]):
        self.x = x
        self.height = height
        self.color = color
        self.num_segments = 7
        self.sway_phase = random.uniform(0, math.pi * 2)
        self.sway_speed = random.uniform(1.1, 1.8)
        self.amplitude = random.uniform(18.0, 32.0)

    def draw(self, target: pygame.Surface, time_sec: float, cam_offset: Tuple[float, float], flow_vx: float = 0.0) -> None:
        ox, oy = cam_offset
        base_x = self.x + ox * 0.95
        base_y = SCREEN_HEIGHT + oy * 0.95

        points = [(base_x, base_y)]
        for i in range(1, self.num_segments + 1):
            ratio = i / self.num_segments
            seg_y = base_y - self.height * ratio
            sway = math.sin(time_sec * self.sway_speed + self.sway_phase + ratio * 2.8) * (self.amplitude * ratio * ratio) + (flow_vx * 1.4 * ratio * ratio)
            points.append((base_x + sway, seg_y))

        if len(points) >= 2:
            pygame.draw.lines(target, self.color, False, points, 4)
            highlight_col = (min(255, self.color[0] + 25), min(255, self.color[1] + 35), min(255, self.color[2] + 20))
            pygame.draw.lines(target, highlight_col, False, points, 2)


# =========================================================================
# CENTRAL 3D CINEMATIC UNDERWATER SCENE MANAGER
# =========================================================================

class Underwater3DScene:
    """
    Central 3D Cinematic Underwater Environment Manager.
    Renders realistic volumetric ocean lighting, multi-depth parallax layers,
    marine life, animated caustics, and foreground coral reef.
    """

    def __init__(self, theme: str = "shipwreck"):
        self.theme = theme
        self.camera = CinematicCamera()
        self.time_sec = 0.0

        # Layer Surfaces (loaded safely)
        self.surf_reference_bg: Optional[pygame.Surface] = None
        self.surf_master_bg: Optional[pygame.Surface] = None
        self.surf_shipwreck: Optional[pygame.Surface] = None
        self.surf_ruins: Optional[pygame.Surface] = None
        self.surf_coral_reef: Optional[pygame.Surface] = None
        self.surf_chest: Optional[pygame.Surface] = None
        self.surf_turtle: Optional[pygame.Surface] = None
        self.surf_manta: Optional[pygame.Surface] = None
        self.surf_shark: Optional[pygame.Surface] = None
        self.surf_jellyfish: Optional[pygame.Surface] = None
        self.surf_clownfish: Optional[pygame.Surface] = None
        self.surf_blue_tang: Optional[pygame.Surface] = None
        self.surf_yellow_tang: Optional[pygame.Surface] = None
        self.surf_caustics: Optional[pygame.Surface] = None
        self.surf_dolphin: Optional[pygame.Surface] = None
        self.surf_dolphin_blue: Optional[pygame.Surface] = None
        self.surf_dolphin_pink: Optional[pygame.Surface] = None
        self.surf_seahorse: Optional[pygame.Surface] = None
        self.surf_nudibranch: Optional[pygame.Surface] = None
        self.surf_tiered_betta: Optional[pygame.Surface] = None
        self.surf_white_betta: Optional[pygame.Surface] = None
        self.surf_mermaid: Optional[pygame.Surface] = None

        self._load_textures()

        # Dynamic Ocean Water Flow Current & 3D Living Water Simulation
        self.water_flow = OceanWaterFlow()
        self.living_water = LivingOceanWater3D()

        # Autonomous Sea Creatures
        self.shark: Optional[RealisticShark3D] = None
        self.turtle: Optional[RealisticTurtle3D] = None
        self.manta: Optional[RealisticManta] = None
        self.jellyfish_list: List[RealisticJellyfish] = []
        self.foreground_school: Optional[ForegroundReefSchool] = None
        self.midground_school: Optional[MidgroundOceanSchool] = None
        self.ruins_school: Optional[RuinsReefSchool] = None
        self.anemone_clownfish: List[CoralAnemoneClownfish] = []
        self.distant_shoal: Optional[DistantFishShoal] = None
        self.dolphins: List[RealisticDolphin3D] = []

        # Authentic Living Marine Species
        self.seahorse: Optional[RealisticGoldenSeahorse] = None
        self.nudibranch: Optional[RealisticNudibranch] = None
        self.tiered_betta: Optional[RealisticTieredBetta] = None
        self.white_betta: Optional[RealisticWhiteBetta] = None
        self.mermaid: Optional[RealisticMermaid] = None

        # Pod of Photorealistic Bottlenose Dolphins: 1 Sapphire Blue, 1 Rosy Pink!
        self.dolphins = []
        blue_surf = self.surf_dolphin_blue or self.surf_dolphin
        pink_surf = self.surf_dolphin_pink or self.surf_dolphin

        if blue_surf:
            # 1. Sapphire Blue Dolphin (Alpha) — majestic swimmer soaring & leaping across the ocean surface
            self.dolphins.append(
                RealisticDolphin3D(
                    blue_surf,
                    x=SCREEN_WIDTH * 0.65,
                    y=SCREEN_HEIGHT * 0.18,
                    z=0.60,
                    base_speed=58.0,
                    direction=1,
                    scale=310,
                    phase_offset=0.0,
                    wave_phase=0.0,
                    wave_amplitude=24.0,
                    wave_freq=0.48,
                    leap_interval=4.6,
                )
            )
        if pink_surf:
            # 2. Rosy Pink Dolphin (Companion) — swimming alongside in harmonic echelon leaping formation
            self.dolphins.append(
                RealisticDolphin3D(
                    pink_surf,
                    x=SCREEN_WIDTH * 0.15,
                    y=SCREEN_HEIGHT * 0.22,
                    z=0.52,
                    base_speed=54.0,
                    direction=1,
                    scale=260,
                    phase_offset=1.2,
                    wave_phase=0.85,
                    wave_amplitude=20.0,
                    wave_freq=0.48,
                    leap_interval=6.8,
                )
            )

        # Photorealistic Luminescent Mermaid — majestic life-sized scale (target_w = 400)
        if self.surf_mermaid:
            self.mermaid = RealisticMermaid(
                self.surf_mermaid,
                x=SCREEN_WIDTH * 0.17,
                y=SCREEN_HEIGHT * 0.44,
                z=0.68,
                direction=1,
            )
            self.mermaid.target_w = 400

        # Peacock Tiered Betta Fish with corrected lush feathered tiers
        if self.surf_tiered_betta:
            self.tiered_betta = RealisticTieredBetta(
                self.surf_tiered_betta,
                x=SCREEN_WIDTH * 0.86,
                y=SCREEN_HEIGHT * 0.40,
                z=0.58,
                direction=-1,
            )
            self.tiered_betta.target_w = 160

        # Removed sea angel (nudibranch), white betta, and seahorse as requested
        self.seahorse = None
        self.nudibranch = None
        self.white_betta = None

        # Marine Snow & Rising Bubbles
        self.marine_snow = [MarineSnowMote() for _ in range(65)]
        self.bubbles = [Realistic3DBubble() for _ in range(30)]

        # Kelp Forest
        self.kelp_forest: List[RealisticKelpFrond] = []
        kelp_colors = [
            (24, 76, 52),
            (18, 65, 42),
            (32, 95, 62),
            (16, 55, 36),
            (28, 88, 58),
        ]
        for kx in [35, 80, 130, SCREEN_WIDTH - 190, SCREEN_WIDTH - 130, SCREEN_WIDTH - 40]:
            kh = random.uniform(180, 290)
            col = random.choice(kelp_colors)
            self.kelp_forest.append(RealisticKelpFrond(kx, kh, col))

        # Antique Treasure Chest
        self.chest_x = SCREEN_WIDTH - 150.0
        self.chest_y = SCREEN_HEIGHT - 95.0
        self.chest_scale = 0.26
        self.gold_sparkles: List[GoldSparkleMote] = []
        self.sparkle_emit_timer = 0.0

        # Caustic Scrolling Coordinates
        self.caustic_scroll_1 = 0.0
        self.caustic_scroll_2 = 0.0

    def _load_textures(self) -> None:
        """Loads and pre-processes high-resolution visual textures with LOD optimization."""
        def load_img(fname: str, alpha: bool = False) -> Optional[pygame.Surface]:
            path = os.path.join(ASSETS_DIR, fname)
            if not os.path.isfile(path):
                return None
            try:
                surf = pygame.image.load(path)
                if pygame.display.get_surface():
                    return surf.convert_alpha() if alpha else surf.convert()
                return surf
            except Exception:
                return None

        # Master clean composite backdrop
        self.surf_front_page = load_img("aquasense_front_page.png", alpha=False)
        self.surf_reference_bg = load_img("reference_clean_backdrop.jpg", alpha=False)
        self.surf_master_bg = self.surf_front_page or self.surf_reference_bg or load_img("shipwreck_ruins_cinematic.jpg", alpha=False)
        self.surf_shipwreck = load_img("shipwreck.jpg", alpha=False)
        self.surf_ruins = load_img("ruins.jpg", alpha=False)
        self.surf_coral_reef = load_img("coral_reef.jpg", alpha=False)
        self.surf_chest = load_img("treasure_chest.png", alpha=True)
        self.surf_caustics = load_img("caustics_clean.png", alpha=True)

        # High-quality creature textures
        raw_shark = load_img("shark.png", alpha=True)
        raw_turtle = load_img("sea_turtle.png", alpha=True)
        raw_manta = load_img("manta_ray.png", alpha=True)
        raw_jelly = load_img("jellyfish.png", alpha=True)
        raw_clown = load_img("clownfish.png", alpha=True)
        raw_tang = load_img("blue_tang.png", alpha=True)
        raw_yellow = load_img("yellow_tang.png", alpha=True)

        target_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        if self.surf_front_page:
            self.surf_front_page = pygame.transform.smoothscale(self.surf_front_page, target_size)
        if self.surf_reference_bg:
            self.surf_reference_bg = pygame.transform.smoothscale(self.surf_reference_bg, target_size)
        if self.surf_master_bg:
            self.surf_master_bg = pygame.transform.smoothscale(self.surf_master_bg, target_size)
        if self.surf_shipwreck:
            self.surf_shipwreck = pygame.transform.smoothscale(self.surf_shipwreck, target_size)
        if self.surf_ruins:
            self.surf_ruins = pygame.transform.smoothscale(self.surf_ruins, target_size)
        if self.surf_coral_reef:
            self.surf_coral_reef = pygame.transform.smoothscale(self.surf_coral_reef, target_size)
        if self.surf_caustics:
            self.surf_caustics = pygame.transform.smoothscale(self.surf_caustics, (512, 512))

        # Ultra HD Creature Textures — High working resolution for razor-sharp photographic clarity
        if raw_shark:
            sw, sh = 960, int(960 * raw_shark.get_height() / raw_shark.get_width())
            self.surf_shark = pygame.transform.smoothscale(raw_shark, (sw, sh))
        if raw_turtle:
            tw, th = 800, int(800 * raw_turtle.get_height() / raw_turtle.get_width())
            self.surf_turtle = pygame.transform.smoothscale(raw_turtle, (tw, th))
        if raw_manta:
            mw, mh = 640, int(640 * raw_manta.get_height() / raw_manta.get_width())
            self.surf_manta = pygame.transform.smoothscale(raw_manta, (mw, mh))
        if raw_jelly:
            jw, jh = 360, int(360 * raw_jelly.get_height() / raw_jelly.get_width())
            self.surf_jellyfish = pygame.transform.smoothscale(raw_jelly, (jw, jh))
        if raw_clown:
            cw, ch = 360, int(360 * raw_clown.get_height() / raw_clown.get_width())
            self.surf_clownfish = pygame.transform.smoothscale(raw_clown, (cw, ch))
        if raw_tang:
            bw, bh = 360, int(360 * raw_tang.get_height() / raw_tang.get_width())
            self.surf_blue_tang = pygame.transform.smoothscale(raw_tang, (bw, bh))
        if raw_yellow:
            yw, yh = 360, int(360 * raw_yellow.get_height() / raw_yellow.get_width())
            self.surf_yellow_tang = pygame.transform.smoothscale(raw_yellow, (yw, yh))
        raw_dolphin = load_img("dolphin.png", alpha=True)
        raw_dolphin_blue = load_img("dolphin_blue.png", alpha=True) or raw_dolphin
        raw_dolphin_pink = load_img("dolphin_pink.png", alpha=True) or raw_dolphin

        if raw_dolphin:
            dw, dh = 800, int(800 * raw_dolphin.get_height() / raw_dolphin.get_width())
            self.surf_dolphin = pygame.transform.smoothscale(raw_dolphin, (dw, dh))
        if raw_dolphin_blue:
            dw, dh = 800, int(800 * raw_dolphin_blue.get_height() / raw_dolphin_blue.get_width())
            self.surf_dolphin_blue = pygame.transform.smoothscale(raw_dolphin_blue, (dw, dh))
        else:
            self.surf_dolphin_blue = self.surf_dolphin
        if raw_dolphin_pink:
            dw, dh = 800, int(800 * raw_dolphin_pink.get_height() / raw_dolphin_pink.get_width())
            self.surf_dolphin_pink = pygame.transform.smoothscale(raw_dolphin_pink, (dw, dh))
        else:
            self.surf_dolphin_pink = self.surf_dolphin

        # Load newly requested marine species textures
        raw_seahorse = load_img("golden_seahorse.png", alpha=True) or load_img("seahorse.png", alpha=True)
        if raw_seahorse:
            sh_w, sh_h = 240, int(240 * raw_seahorse.get_height() / raw_seahorse.get_width())
            self.surf_seahorse = pygame.transform.smoothscale(raw_seahorse, (sh_w, sh_h))

        raw_nudi = load_img("sea_angel_nudibranch.png", alpha=True) or load_img("nudibranch.png", alpha=True)
        if raw_nudi:
            nw, nh = 250, int(250 * raw_nudi.get_height() / raw_nudi.get_width())
            self.surf_nudibranch = pygame.transform.smoothscale(raw_nudi, (nw, nh))

        raw_tiered = load_img("tiered_silk_betta.png", alpha=True) or load_img("betta_tiered.png", alpha=True)
        if raw_tiered:
            tw, th = 300, int(300 * raw_tiered.get_height() / raw_tiered.get_width())
            self.surf_tiered_betta = pygame.transform.smoothscale(raw_tiered, (tw, th))

        raw_white = load_img("white_halfmoon_betta.png", alpha=True) or load_img("betta_white.png", alpha=True)
        if raw_white:
            ww, wh = 340, int(340 * raw_white.get_height() / raw_white.get_width())
            self.surf_white_betta = pygame.transform.smoothscale(raw_white, (ww, wh))

        raw_mermaid = load_img("mermaid.png", alpha=True)
        if raw_mermaid:
            mw, mh = 680, int(680 * raw_mermaid.get_height() / raw_mermaid.get_width())
            self.surf_mermaid = pygame.transform.smoothscale(raw_mermaid, (mw, mh))

    def update(self, dt: float, cursor_x: float = SCREEN_WIDTH / 2, cursor_y: float = SCREEN_HEIGHT / 2) -> None:
        """Updates camera kinematics, creatures, particles, and caustics."""
        self.time_sec += dt
        self.camera.update(dt, cursor_x, cursor_y)

        # Dynamic ocean water flow vector
        flow_vx, flow_vy = self.water_flow.update(dt)

        # Real 3D dynamic moving ocean water current simulation
        self.living_water.update(dt, flow_vx, flow_vy)

        # Caustic drift speeds coupled to ocean current
        self.caustic_scroll_1 = (self.caustic_scroll_1 + (13.0 + flow_vx * 0.25) * dt) % 512
        self.caustic_scroll_2 = (self.caustic_scroll_2 - (10.0 - flow_vx * 0.2) * dt) % 512

        # 1. Pod of Realistic Bottlenose Dolphins with blowhole bubble rings
        for d in self.dolphins:
            d.update(dt, flow_vx, flow_vy)

        # 2. Photorealistic Luminescent Mermaid
        if self.mermaid:
            self.mermaid.update(dt, flow_vx, flow_vy)

        # 3. Authentic living marine species
        if self.seahorse:
            self.seahorse.update(dt, flow_vx, flow_vy)
        if self.nudibranch:
            self.nudibranch.update(dt, flow_vx, flow_vy)
        if self.tiered_betta:
            self.tiered_betta.update(dt, flow_vx, flow_vy)
        if self.white_betta:
            self.white_betta.update(dt, flow_vx, flow_vy)

        # Legacy optional components preserved if instantiated
        if self.distant_shoal:
            self.distant_shoal.update(dt)
        if self.shark:
            self.shark.update(dt)
        if self.turtle:
            self.turtle.update(dt)
        if self.midground_school:
            self.midground_school.update(dt)
        for j in self.jellyfish_list:
            j.update(dt)
        if self.foreground_school:
            self.foreground_school.update(dt)
        if self.ruins_school:
            self.ruins_school.update(dt)
        for c in self.anemone_clownfish:
            c.update(dt)

        # Floating Particles & Bubbles carried by dynamic ocean water flow
        for s in self.marine_snow:
            s.update(dt, flow_vx, flow_vy)
        for b in self.bubbles:
            b.update(dt, flow_vx, flow_vy)

        # Chest Golden Sparkles
        self.sparkle_emit_timer += dt
        if self.sparkle_emit_timer >= 0.08:
            self.sparkle_emit_timer = 0.0
            if len(self.gold_sparkles) < 26:
                self.gold_sparkles.append(GoldSparkleMote(self.chest_x, self.chest_y))

        self.gold_sparkles = [sp for sp in self.gold_sparkles if sp.update(dt)]

    def draw(self, surface: pygame.Surface, show_chest: bool = True) -> None:
        """
        Renders the realistic cinematic 3D underwater world with layered depth:
        Layer 1: Background plate (ancient ruins, shipwreck, coral floor) with subtle camera parallax
        Layer 2: Distant deep ocean fish shoal (Z ~ 0.25)
        Layer 3: Great White Shark (Z ~ 0.38)
        Layer 4: Giant Manta Ray (Z ~ 0.52)
        Layer 5: Midground ocean fish school (Z ~ 0.60)
        Layer 6: Green Sea Turtle (Z ~ 0.72)
        Layer 7: Bioluminescent Jellyfish (Z ~ 0.74)
        Layer 8: Dynamic dual-layer caustics network
        Layer 9: Foreground tropical reef school (Z ~ 0.88)
        Layer 10: Swaying 3D kelp forest fronds (Z ~ 0.94)
        Layer 11: 3D antique treasure chest with golden radiance aura and sparkling motes (Z ~ 1.0)
        Layer 12: Volumetric sunlight rays cascading from ocean surface
        Layer 13: Marine snow plankton motes & rising 3D glint bubbles!
        """
        # =====================================================================
        # Layer 1: Volumetric Ocean Atmosphere & Clean 3D Stage Plate (Z ~ 0.12)
        # =====================================================================
        ox_bg, oy_bg = self.camera.get_offset(0.12)
        backdrop_to_use = self.surf_master_bg or (
            self.surf_shipwreck if self.theme == "shipwreck" else (
                self.surf_ruins if self.theme == "ruins" else self.surf_coral_reef
            )
        )

        is_front_page = (
            self.theme == "front_page"
            or (self.surf_front_page is not None and (
                backdrop_to_use is self.surf_front_page
                or backdrop_to_use is self.surf_master_bg
                or self.theme == "shipwreck"
            ))
        )

        if backdrop_to_use:
            # Subtle gentle parallax for backdrop
            bg_pos = (0, 0) if is_front_page else (int(ox_bg), int(oy_bg))
            surface.blit(backdrop_to_use, bg_pos)
        else:
            for y in range(0, SCREEN_HEIGHT, 4):
                t = y / SCREEN_HEIGHT
                r = int(4 + (2 - 4) * t)
                g = int(24 + (8 - 24) * t)
                b = int(58 + (20 - 58) * t)
                pygame.draw.rect(surface, (r, g, b), (0, y, SCREEN_WIDTH, 4))

        # Soft atmospheric oceanic depth fog (only on standard backgrounds)
        if not is_front_page:
            fog_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fog_surf.fill((4, 18, 38, 22))
            surface.blit(fog_surf, (0, 0))

        # =====================================================================
        # Real 3D Ocean Water Current Streamlines (Living Water Flow)
        # =====================================================================
        self.living_water.draw_current_streamlines(surface)

        # =====================================================================
        # Pod of Photorealistic Bottlenose Dolphins (Z ~ 0.48 - 0.60)
        # =====================================================================
        for d in self.dolphins:
            ox_d, oy_d = self.camera.get_offset(d.z)
            d.draw(surface, (ox_d, oy_d), self.time_sec)

        # =====================================================================
        # Photorealistic Luminescent Mermaid (Z ~ 0.62)
        # =====================================================================
        if self.mermaid:
            ox_mm, oy_mm = self.camera.get_offset(self.mermaid.z)
            self.mermaid.draw(surface, (ox_mm, oy_mm), self.time_sec, self.water_flow.flow_vx)

        # =====================================================================
        # Tiered Silk Gown Betta Fish (Z ~ 0.56)
        # =====================================================================
        if self.tiered_betta:
            ox_tb, oy_tb = self.camera.get_offset(self.tiered_betta.z)
            self.tiered_betta.draw(surface, (ox_tb, oy_tb), self.time_sec, self.water_flow.flow_vx)

        # =====================================================================
        # Angelic White Halfmoon Betta Fish (Z ~ 0.65)
        # =====================================================================
        if self.white_betta:
            ox_wb, oy_wb = self.camera.get_offset(self.white_betta.z)
            self.white_betta.draw(surface, (ox_wb, oy_wb), self.time_sec, self.water_flow.flow_vx)

        # =====================================================================
        # Golden Seahorse Hovering by Ancient Ruins Column (Z ~ 0.72)
        # =====================================================================
        if self.seahorse:
            ox_sh, oy_sh = self.camera.get_offset(self.seahorse.z)
            self.seahorse.draw(surface, (ox_sh, oy_sh), self.time_sec)

        # Legacy objects drawn only if explicitly instantiated
        if self.distant_shoal:
            ox_dist, oy_dist = self.camera.get_offset(0.25)
            self.distant_shoal.draw(surface, (ox_dist, oy_dist), self.time_sec)
        if self.shark:
            ox_shark, oy_shark = self.camera.get_offset(0.45)
            self.shark.draw(surface, (ox_shark, oy_shark), self.time_sec)
        if self.midground_school:
            ox_mid_fish, oy_mid_fish = self.camera.get_offset(0.58)
            self.midground_school.draw(surface, (ox_mid_fish, oy_mid_fish), self.time_sec)
        if self.turtle:
            ox_turtle, oy_turtle = self.camera.get_offset(0.72)
            self.turtle.draw(surface, (ox_turtle, oy_turtle), self.time_sec)
        for j in self.jellyfish_list:
            ox_j, oy_j = self.camera.get_offset(0.74)
            j.draw(surface, (ox_j, oy_j))

        # =====================================================================
        # Layer 8: Dynamic Dual-Layer Caustics Network
        # =====================================================================
        if self.surf_caustics:
            caustic_layer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            cw, ch = 512, 512
            offset_x1 = int(self.caustic_scroll_1)
            offset_y1 = int(self.caustic_scroll_2)
            offset_x2 = int(-self.caustic_scroll_2 * 0.8)
            offset_y2 = int(self.caustic_scroll_1 * 0.7)

            start_caustic_y = int(SCREEN_HEIGHT * 0.40) if is_front_page else int(SCREEN_HEIGHT * 0.28)
            for tx in range(-cw, SCREEN_WIDTH + cw, cw):
                for ty in range(start_caustic_y, SCREEN_HEIGHT + ch, ch):
                    caustic_layer.blit(self.surf_caustics, (tx + offset_x1 % cw, ty + offset_y1 % ch))
            caustic_layer.set_alpha(int(22 + 6 * math.sin(self.time_sec * 1.6)))
            surface.blit(caustic_layer, (0, 0))

            caustic_layer_2 = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            for tx in range(-cw, SCREEN_WIDTH + cw, cw):
                for ty in range(int(start_caustic_y + 30), SCREEN_HEIGHT + ch, ch):
                    caustic_layer_2.blit(self.surf_caustics, (tx + offset_x2 % cw, ty + offset_y2 % ch))
            caustic_layer_2.set_alpha(int(14 + 4 * math.cos(self.time_sec * 1.2)))
            surface.blit(caustic_layer_2, (0, 0))

        # =====================================================================
        # Layer 8b: Leaf Sheep / Sea Angel Nudibranch on Seabed Floor (Z ~ 0.88)
        # =====================================================================
        if self.nudibranch:
            ox_nd, oy_nd = self.camera.get_offset(self.nudibranch.z)
            self.nudibranch.draw(surface, (ox_nd, oy_nd), self.time_sec, self.water_flow.flow_vx)

        # =====================================================================
        # Layer 9: Foreground Tropical Reef School (Z ~ 0.88)
        # =====================================================================
        ox_fg_fish, oy_fg_fish = self.camera.get_offset(0.88)
        if self.foreground_school:
            self.foreground_school.draw(surface, (ox_fg_fish, oy_fg_fish), self.time_sec)

        # =====================================================================
        # Layer 9b: Resident Anemone Clownfish Pair (Z ~ 0.86)
        # =====================================================================
        for c in self.anemone_clownfish:
            c.draw(surface, (ox_fg_fish, oy_fg_fish), self.time_sec)

        if not is_front_page:
            # =====================================================================
            # Layer 10: Swaying Kelp Forest Fronds (Z ~ 0.94)
            # =====================================================================
            ox_near, oy_near = self.camera.get_offset(0.94)
            for k in self.kelp_forest:
                k.draw(surface, self.time_sec, (ox_near, oy_near), self.water_flow.flow_vx)

        # =====================================================================
        # Layer 11: 3D Antique Treasure Chest (Radiance Aura & Sparkles, Z ~ 1.0)
        # =====================================================================
        ox_chest, oy_chest = self.camera.get_offset(1.0)
        chest_fx = 1080.0 if is_front_page else self.chest_x
        chest_fy = 570.0 if is_front_page else self.chest_y

        if show_chest and not is_front_page and self.surf_chest:
            cw = int(self.surf_chest.get_width() * self.chest_scale)
            ch = int(self.surf_chest.get_height() * self.chest_scale)
            scaled_chest = pygame.transform.smoothscale(self.surf_chest, (cw, ch))
            cx = int(chest_fx + ox_chest - cw / 2)
            cy = int(chest_fy + oy_chest - ch / 2)
            surface.blit(scaled_chest, (cx, cy))

        if show_chest:
            pulse_gold = math.sin(self.time_sec * 2.4) * 0.2 + 0.8
            aura_w = 170 if is_front_page else 190
            aura_h = 80 if is_front_page else 100
            aura_surf = pygame.Surface((aura_w, aura_h), pygame.SRCALPHA)
            pygame.draw.ellipse(aura_surf, (255, 215, 65, int(26 * pulse_gold)), (0, 0, aura_w, aura_h))
            surface.blit(aura_surf, (int(chest_fx + (0 if is_front_page else ox_chest) - aura_w // 2), int(chest_fy + (0 if is_front_page else oy_chest) - aura_h // 2 + 10)))

            for sp in self.gold_sparkles:
                sp.draw(surface, ((0, 0) if is_front_page else (ox_chest, oy_chest)))

        # =====================================================================
        # Layer 12: Real 3D Moving Water Surface Swells & Volumetric Sunbeams
        # =====================================================================
        self.living_water.draw_surface_and_rays(surface, self.water_flow.flow_vx, self.time_sec)

        # =====================================================================
        # Layer 13: Marine Snow & Rising 3D Refraction Bubbles
        # =====================================================================
        ox_part, oy_part = self.camera.get_offset(0.85)
        for s in self.marine_snow:
            s.draw(surface, (ox_part, oy_part))
        for b in self.bubbles:
            b.draw(surface, (ox_part, oy_part))
