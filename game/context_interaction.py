"""
Underwater Treasure Hunt - Context-Aware Gesture Interaction Engine
AquaSense Core Innovation:
    GESTURE + CONTEXT + NEARBY OBJECT + OBJECT STATE = ACTION

Interprets player hand gestures based on environmental context rather than static buttons:
- PINCH + TREASURE CHEST       -> GRAB TREASURE
- PINCH + ANCIENT ARTIFACT     -> INSPECT ARTIFACT (3D interactive inspection mode)
- PINCH + ANCIENT LOCKED DOOR   -> ATTEMPT TO UNLOCK (checks required relic / key)
- PINCH + UNDERWATER MAP       -> OPEN EXPEDITION SEA CHART
- PINCH + CORAL SAMPLE         -> EXAMINE & SAMPLE BIOLOGICAL SPECIMEN
- PINCH + SECRET MECHANISM     -> ACTIVATE ANCIENT SLUICE / SWITCH
- PINCH + SMALL COLLECTIBLE    -> COLLECT ITEM
- TWO HANDS + HEAVY TREASURE   -> LIFT HEAVY STRONGBOX
- TWO FINGERS + SONAR          -> CONTEXT-AWARE ACOUSTIC SCAN (Treasure, Artifact, Door, Danger)
"""

import os
from enum import Enum
import math
import random
import time
from typing import Dict, List, Optional, Tuple, Any
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
from hand_tracking.gesture_detector import GestureType

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
_PEDESTAL_TEX: Optional[pygame.Surface] = None

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


class InteractionType(Enum):
    GRAB_TREASURE = "GRAB_TREASURE"
    INSPECT_ARTIFACT = "INSPECT_ARTIFACT"
    UNLOCK_DOOR = "UNLOCK_DOOR"
    OPEN_MAP = "OPEN_MAP"
    SAMPLE_CORAL = "SAMPLE_CORAL"
    COLLECT_CORAL = "COLLECT_CORAL"
    ACTIVATE_MECHANISM = "ACTIVATE_MECHANISM"
    LIFT_HEAVY = "LIFT_HEAVY"
    DEPOSIT_CHEST = "DEPOSIT_CHEST"
    COLLECT_ITEM = "COLLECT_ITEM"
    AIR_RECHARGE = "AIR_RECHARGE"


class InteractableState(Enum):
    AVAILABLE = "AVAILABLE"
    FOCUSED = "FOCUSED"
    IN_RANGE = "IN_RANGE"
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    UNLOCKED = "UNLOCKED"
    COLLECTED = "COLLECTED"
    INSPECTING = "INSPECTING"


class SonarEchoCategory(Enum):
    TREASURE = "TREASURE"
    ARTIFACT = "ARTIFACT"
    SECRET_DOOR = "SECRET_DOOR"
    DANGER = "DANGER"
    COLLECTIBLE = "COLLECTIBLE"
    OBJECTIVE = "OBJECTIVE"


class InteractionResult:
    """Represents the outcome of a context-aware gesture action."""

    def __init__(
        self,
        success: bool,
        action_type: InteractionType,
        feedback_message: str,
        sound_effect: Optional[str] = None,
        score_delta: int = 0,
        oxygen_delta: float = 0.0,
        opens_modal: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ):
        self.success = success
        self.action_type = action_type
        self.feedback_message = feedback_message
        self.sound_effect = sound_effect
        self.score_delta = score_delta
        self.oxygen_delta = oxygen_delta
        self.opens_modal = opens_modal
        self.data = data or {}


class IInteractable:
    """Abstract interface for all context-aware interactive underwater objects."""

    def __init__(
        self,
        object_id: str,
        name: str,
        x: float,
        y: float,
        radius: float = 34.0,
        interaction_type: InteractionType = InteractionType.GRAB_TREASURE,
        interaction_range: float = 95.0,
        required_gesture: GestureType = GestureType.PINCH,
        priority: int = 50,
        prompt_label: str = "INTERACT",
        icon: str = "🤏",
        sonar_category: SonarEchoCategory = SonarEchoCategory.TREASURE,
    ):
        self.object_id = object_id
        self.name = name
        self.x = x
        self.y = y
        self.radius = radius
        self.interaction_type = interaction_type
        self.interaction_range = interaction_range
        self.required_gesture = required_gesture
        self.priority = priority
        self.prompt_label = prompt_label
        self.icon = icon
        self.sonar_category = sonar_category
        self.state = InteractableState.AVAILABLE
        self.highlight_anim = 0.0
        self.last_interact_time = 0.0

    def can_interact(self, player: Any, gesture: GestureType, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Returns (can_interact, reason_or_status)."""
        if self.state == InteractableState.COLLECTED:
            return False, "Already Collected"
        return True, "Ready"

    def interact(self, player: Any, game_manager: Any, context: Dict[str, Any]) -> InteractionResult:
        """Executes the contextual action."""
        raise NotImplementedError

    def update(self, dt: float) -> None:
        self.highlight_anim += 4.0 * dt

    def draw_context_reticle(self, surface: pygame.Surface, is_focused: bool, in_range: bool, time_sec: float) -> None:
        """Draws subtle tactical underwater brackets and highlight glow around the object."""
        cx, cy = int(self.x), int(self.y)
        r = int(self.radius + 10)
        pulse = math.sin(time_sec * 6.0) * 3.0
        draw_r = max(12, int(r + pulse))

        color = COLOR_GOLD if in_range else (COLOR_NEON_TEAL if is_focused else COLOR_OCEAN_CYAN)
        alpha = 210 if in_range else (160 if is_focused else 90)

        # 4 Corner Target Brackets
        bracket_len = 10
        gap = draw_r
        pts_tl = [(cx - gap, cy - gap + bracket_len), (cx - gap, cy - gap), (cx - gap + bracket_len, cy - gap)]
        pts_tr = [(cx + gap - bracket_len, cy - gap), (cx + gap, cy - gap), (cx + gap, cy - gap + bracket_len)]
        pts_bl = [(cx - gap, cy + gap - bracket_len), (cx - gap, cy + gap), (cx - gap + bracket_len, cy + gap)]
        pts_br = [(cx + gap - bracket_len, cy + gap), (cx + gap, cy + gap), (cx + gap, cy + gap - bracket_len)]

        b_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.lines(b_surf, (*color[:3], alpha), False, pts_tl, 2)
        pygame.draw.lines(b_surf, (*color[:3], alpha), False, pts_tr, 2)
        pygame.draw.lines(b_surf, (*color[:3], alpha), False, pts_bl, 2)
        pygame.draw.lines(b_surf, (*color[:3], alpha), False, pts_br, 2)

        # Subtle pulsing inner reticle ring
        pygame.draw.circle(b_surf, (*color[:3], int(alpha * 0.4)), (cx, cy), draw_r - 4, 1)
        surface.blit(b_surf, (0, 0))


# =========================================================================
# 1. CONTEXTUAL OBJECT IMPLEMENTATIONS
# =========================================================================

class ContextTreasure(IInteractable):
    """Wraps treasures with context-aware grab and heavy-relic logic."""

    def __init__(self, raw_treasure: Any):
        t_type = getattr(raw_treasure, "type", None)
        t_val = getattr(t_type, "value", "TREASURE") if t_type else "TREASURE"
        is_heavy = (t_val == "HEAVY")
        is_key = (t_val == "KEY")
        is_locked_chest = (t_val == "LOCKED_CHEST")
        
        if is_heavy:
            name = "Heavy Sunken Strongbox"
            prompt = "LIFT HEAVY TREASURE"
        elif is_key:
            name = "Ancient Golden Key"
            prompt = "GRAB GOLDEN KEY"
        elif is_locked_chest:
            name = "Locked Treasure Chest"
            prompt = "UNLOCK CHEST (NEEDS KEY)"
        else:
            name = f"{t_val.title()} Relic"
            prompt = "GRAB TREASURE"

        req_gesture = GestureType.PINCH
        sonar_cat = SonarEchoCategory.DANGER if t_val in ("TRAP", "FAKE") else SonarEchoCategory.TREASURE

        super().__init__(
            object_id=f"treasure_{id(raw_treasure)}",
            name=name,
            x=raw_treasure.x,
            y=raw_treasure.y,
            radius=raw_treasure.radius,
            interaction_type=InteractionType.LIFT_HEAVY if is_heavy else InteractionType.GRAB_TREASURE,
            interaction_range=115.0 if (is_heavy or is_locked_chest) else 95.0,
            required_gesture=req_gesture,
            priority=75 if (is_key or is_locked_chest) else (65 if is_heavy else 55),
            prompt_label=prompt,
            icon="KEY" if is_key else ("DOOR" if is_locked_chest else "TREASURE"),
            sonar_category=sonar_cat,
        )
        self.raw_treasure = raw_treasure

    def can_interact(self, player: Any, gesture: GestureType, context: Dict[str, Any]) -> Tuple[bool, str]:
        if self.raw_treasure.collected:
            return False, "Already Collected"
        
        t_type = getattr(self.raw_treasure, "type", None)
        t_val = getattr(t_type, "value", "")

        # Locked chest checks for key in hands or inventory
        if t_val == "LOCKED_CHEST":
            inv = context.get("inventory")
            has_key = False
            if inv and getattr(inv, "items", {}).get("key", 0) > 0:
                has_key = True
            if player.carried_treasure:
                c_val = getattr(getattr(player.carried_treasure, "type", None), "value", "").lower()
                if "key" in c_val:
                    has_key = True
            if not has_key:
                return False, "Locked! Find the Ancient Golden Key 🗝️"
            return True, "Ready to Unlock"

        if player.carried_treasure is not None:
            return False, "Hands Already Full"
        
        # Heavy treasure dual-hand verification
        if t_val == "HEAVY":
            has_dual = context.get("has_dual_hands", False)
            if not has_dual:
                return False, "Heavy Relic: Use Both Hands"
        return True, "Ready"

    def interact(self, player: Any, game_manager: Any, context: Dict[str, Any]) -> InteractionResult:
        t_type = getattr(self.raw_treasure, "type", None)
        t_val = getattr(t_type, "value", "")

        # Trap Handling
        if t_val == "TRAP":
            self.raw_treasure.collected = True
            player.lose_life()
            return InteractionResult(
                success=False,
                action_type=InteractionType.GRAB_TREASURE,
                feedback_message="SEA MINE TRIGGERED!",
                sound_effect="trap",
                oxygen_delta=-25.0,
                data={"treasure": self.raw_treasure},
            )

        # Fake Handling
        if t_val == "FAKE":
            self.raw_treasure.collected = True
            player.reduce_oxygen(15.0)
            return InteractionResult(
                success=False,
                action_type=InteractionType.GRAB_TREASURE,
                feedback_message="CURSED MIMIC PENALTY!",
                sound_effect="fake_warning",
                score_delta=self.raw_treasure.score_value,
                oxygen_delta=-15.0,
                data={"treasure": self.raw_treasure},
            )

        # Locked Chest Unlock
        if t_val == "LOCKED_CHEST":
            inv = context.get("inventory")
            has_key = False
            if inv and getattr(inv, "items", {}).get("key", 0) > 0:
                has_key = True
            if player.carried_treasure:
                c_val = getattr(getattr(player.carried_treasure, "type", None), "value", "").lower()
                if "key" in c_val:
                    has_key = True
                    # Consume carried key
                    player.release_carried_treasure()

            if has_key:
                self.raw_treasure.collected = True
                self.state = InteractableState.UNLOCKED
                player.score += 500
                player.oxygen = min(100.0, player.oxygen + 30.0)
                return InteractionResult(
                    success=True,
                    action_type=self.interaction_type,
                    feedback_message="🏆 CHEST UNLOCKED! +500 PTS & +30% AIR 🫧",
                    sound_effect="puzzle_success",
                    score_delta=500,
                    oxygen_delta=30.0,
                    data={"treasure": self.raw_treasure, "unlocked_chest": True},
                )
            else:
                return InteractionResult(
                    success=False,
                    action_type=self.interaction_type,
                    feedback_message="🔒 LOCKED! FIND THE GOLDEN KEY 🗝️",
                    sound_effect="fake_warning",
                    data={"treasure": self.raw_treasure},
                )

        # Key Grab
        if t_val == "KEY":
            player.grab_treasure(self.raw_treasure)
            return InteractionResult(
                success=True,
                action_type=self.interaction_type,
                feedback_message="🗝️ GOLDEN KEY OBTAINED! UNLOCK THE CHEST OR PORTAL",
                sound_effect="treasure",
                score_delta=0,
                data={"treasure": self.raw_treasure},
            )

        # Genuine Grab
        player.grab_treasure(self.raw_treasure)
        is_heavy = (t_val == "HEAVY")
        msg = "👐 HEAVY RELIC HOISTED! SWIM TO VAULT" if is_heavy else "🤏 TREASURE GRABBED! SWIM TO VAULT"
        return InteractionResult(
            success=True,
            action_type=self.interaction_type,
            feedback_message=msg,
            sound_effect="treasure",
            score_delta=0,
            data={"treasure": self.raw_treasure},
        )


class ContextArtifact(IInteractable):
    """Ancient archaeological artifact on seabed triggering 3D Interactive Inspection Mode."""

    def __init__(
        self,
        artifact_id: str,
        name: str,
        era: str,
        lore: str,
        x: float,
        y: float,
        score_val: int = 350,
    ):
        super().__init__(
            object_id=artifact_id,
            name=name,
            x=x,
            y=y,
            radius=38.0,
            interaction_type=InteractionType.INSPECT_ARTIFACT,
            interaction_range=110.0,
            required_gesture=GestureType.PINCH,
            priority=85,
            prompt_label=f"INSPECT {name.upper()}",
            icon="ARTIFACT",
            sonar_category=SonarEchoCategory.ARTIFACT,
        )
        self.era = era
        self.lore = lore
        self.score_val = score_val
        self.is_inspected = False
        self.rot_yaw = random.uniform(0, 360)
        self.rot_pitch = 15.0
        self.shimmer_phase = random.uniform(0, math.pi * 2)

    def interact(self, player: Any, game_manager: Any, context: Dict[str, Any]) -> InteractionResult:
        first_time = not self.is_inspected
        self.is_inspected = True
        score_add = self.score_val if first_time else 25

        # Register discovery in Museum
        if hasattr(game_manager, "museum") and game_manager.museum:
            game_manager.museum.unlock_exhibit(self.object_id, getattr(game_manager, "current_level_id", 1))

        return InteractionResult(
            success=True,
            action_type=InteractionType.INSPECT_ARTIFACT,
            feedback_message=f"INSPECTING: {self.name}!",
            sound_effect="rare_treasure",
            score_delta=score_add,
            opens_modal="INSPECT_ARTIFACT",
            data={
                "artifact_id": self.object_id,
                "name": self.name,
                "era": self.era,
                "lore": self.lore,
                "score_val": self.score_val,
                "first_time": first_time,
            }
        )

    def draw(self, surface: pygame.Surface) -> None:
        """Renders the ancient artifact resting on the seabed with golden particle aura."""
        cx, cy = int(self.x), int(self.y)
        self.shimmer_phase += 0.05
        pulse = math.sin(self.shimmer_phase) * 0.2 + 0.8

        rendered_with_hd = False
        try:
            from ui.relic_renderer import HDRelicRenderer
            if HDRelicRenderer.get_texture("ancient_vase") is not None:
                HDRelicRenderer.draw_relic(
                    surface,
                    relic_id="ancient_vase",
                    cx=cx,
                    cy=cy - 6,
                    radius=28,
                    is_unlocked=True,
                    is_modal=False,
                    light_offset=(math.cos(self.shimmer_phase * 0.8) * 12.0, -18.0),
                    yaw=math.sin(self.shimmer_phase * 0.6) * 0.22,
                    pitch=0.06,
                    pulse_phase=self.shimmer_phase,
                )
                rendered_with_hd = True
        except Exception:
            rendered_with_hd = False

        if not rendered_with_hd:
            # Fallback procedural amphora
            # Stone plinth
            pygame.draw.ellipse(surface, (28, 42, 60), (cx - 24, cy + 12, 48, 16))
            pygame.draw.ellipse(surface, (14, 25, 40), (cx - 24, cy + 12, 48, 16), 1)

            # Luminous Grecian Amphora / Atlantean Vase Vector
            body_col = (215, 165, 80) if self.is_inspected else COLOR_GOLD
            neck_col = (245, 205, 110)

            # Glowing aura
            aura = pygame.Surface((70, 70), pygame.SRCALPHA)
            pygame.draw.circle(aura, (255, 215, 60, int(35 * pulse)), (35, 35), 32)
            surface.blit(aura, (cx - 35, cy - 35))

            # Amphora body
            pygame.draw.polygon(surface, body_col, [
                (cx - 14, cy + 12),
                (cx + 14, cy + 12),
                (cx + 20, cy - 4),
                (cx + 10, cy - 18),
                (cx - 10, cy - 18),
                (cx - 20, cy - 4),
            ])
            # Neck & rim
            pygame.draw.rect(surface, neck_col, (cx - 7, cy - 28, 14, 12), border_radius=2)
            pygame.draw.ellipse(surface, (255, 235, 140), (cx - 9, cy - 31, 18, 6))

            # Handles
            pygame.draw.arc(surface, (180, 130, 50), (cx - 24, cy - 24, 14, 20), 0.5, 3.5, 3)
            pygame.draw.arc(surface, (180, 130, 50), (cx + 10, cy - 24, 14, 20), -0.3, 2.7, 3)


class ContextDoor(IInteractable):
    """Submerged Atlantean Stone Portal that checks for required keys/relics."""

    def __init__(
        self,
        door_id: str,
        name: str,
        x: float,
        y: float,
        required_relic: str = "pearl",
        required_relic_name: str = "Iridescent Pearl",
        target_zone: str = "Ancient Sunken Vault",
    ):
        super().__init__(
            object_id=door_id,
            name=name,
            x=x,
            y=y,
            radius=55.0,
            interaction_type=InteractionType.UNLOCK_DOOR,
            interaction_range=135.0,
            required_gesture=GestureType.PINCH,
            priority=95,
            prompt_label="UNLOCK PORTAL (NEEDS KEY 🗝️)",
            icon="DOOR",
            sonar_category=SonarEchoCategory.SECRET_DOOR,
        )
        self.required_relic = required_relic
        self.required_relic_name = required_relic_name
        self.target_zone = target_zone
        self.is_unlocked = False
        self.open_progress = 0.0  # 0.0 to 1.0 opening slide
        self.lock_glow_phase = 0.0

    def can_interact(self, player: Any, gesture: GestureType, context: Dict[str, Any]) -> Tuple[bool, str]:
        if self.is_unlocked:
            return False, "Door Already Open"
        return True, "Ready to Attempt Unlock"

    def interact(self, player: Any, game_manager: Any, context: Dict[str, Any]) -> InteractionResult:
        if self.is_unlocked:
            return InteractionResult(
                success=True,
                action_type=InteractionType.UNLOCK_DOOR,
                feedback_message=f"{self.name} is wide open!",
            )

        # Check inventory or carried items for the required relic or golden key
        has_relic = False
        if hasattr(game_manager, "inventory") and game_manager.inventory:
            has_relic = (game_manager.inventory.items.get(self.required_relic, 0) > 0)
            if not has_relic and game_manager.inventory.items.get("key", 0) > 0:
                has_relic = True
        
        # Also check if player is currently carrying it
        if not has_relic and player.carried_treasure:
            t_type = getattr(player.carried_treasure, "type", None)
            t_val = getattr(t_type, "value", "").lower()
            if self.required_relic in t_val or "key" in t_val:
                has_relic = True

        if has_relic:
            self.is_unlocked = True
            self.state = InteractableState.UNLOCKED
            # If carrying key, consume it upon opening portal
            if player.carried_treasure and "key" in getattr(getattr(player.carried_treasure, "type", None), "value", "").lower():
                player.release_carried_treasure()

            return InteractionResult(
                success=True,
                action_type=InteractionType.UNLOCK_DOOR,
                feedback_message=f"UNLOCKED! {self.name} swings open!",
                sound_effect="puzzle_success",
                score_delta=500,
                data={"door_id": self.object_id, "zone": self.target_zone}
            )
        else:
            return InteractionResult(
                success=False,
                action_type=InteractionType.UNLOCK_DOOR,
                feedback_message=f"🔒 LOCKED PORTAL! Mechanism requires Golden Key 🗝️ or {self.required_relic_name} to unlock!",
                sound_effect="fake_warning",
                score_delta=0,
            )

    def update(self, dt: float) -> None:
        super().update(dt)
        self.lock_glow_phase += 3.5 * dt
        if self.is_unlocked and self.open_progress < 1.0:
            self.open_progress = min(1.0, self.open_progress + 1.2 * dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Renders massive Atlantean stone gate with carved relief pillars and runic locking rosette."""
        cx, cy = int(self.x), int(self.y)
        w, h = 94, 134
        left_slide = int(38 * self.open_progress)
        right_slide = int(38 * self.open_progress)

        # 1. Soft Ambient Occlusion Wall Shadow
        sh_surf = pygame.Surface((w + 24, h + 24), pygame.SRCALPHA)
        pygame.draw.rect(sh_surf, (4, 10, 18, 110), (0, 0, w + 24, h + 24), border_radius=10)
        surface.blit(sh_surf, (cx - (w + 24) // 2, cy - (h + 24) // 2 + 4))

        # 2. Carved Heavy Stone Archway Frame
        arch_col = (26, 38, 54)
        arch_border = (48, 70, 96)
        pygame.draw.rect(surface, arch_col, (cx - w // 2 - 8, cy - h // 2 - 8, w + 16, h + 16), border_radius=8)
        pygame.draw.rect(surface, arch_border, (cx - w // 2 - 8, cy - h // 2 - 8, w + 16, h + 16), 2, border_radius=8)
        # Keystone & plinth accents
        pygame.draw.rect(surface, (60, 85, 115), (cx - 14, cy - h // 2 - 12, 28, 10), border_radius=3)
        pygame.draw.rect(surface, (60, 85, 115), (cx - w // 2 - 12, cy + h // 2 + 2, w + 24, 10), border_radius=3)

        # 3. Left Stone Door Leaf with Carved Relief Insets
        lx = cx - w // 2 - left_slide
        ly = cy - h // 2
        lw = w // 2
        pygame.draw.rect(surface, (36, 52, 72), (lx, ly, lw, h))
        pygame.draw.rect(surface, (18, 28, 42), (lx, ly, lw, h), 2)
        # Carved relief panel inset
        pygame.draw.rect(surface, (28, 42, 60), (lx + 6, ly + 10, lw - 12, h - 20), border_radius=4)
        pygame.draw.rect(surface, (50, 75, 102), (lx + 6, ly + 10, lw - 12, h - 20), 1, border_radius=4)
        # Atlantean engraved runes
        pygame.draw.line(surface, (0, 200, 220, 130), (lx + 12, ly + 25), (lx + lw - 12, ly + 25), 1)
        pygame.draw.line(surface, (0, 200, 220, 130), (lx + 12, ly + h - 25), (lx + lw - 12, ly + h - 25), 1)

        # 4. Right Stone Door Leaf with Carved Relief Insets
        rx = cx + right_slide
        ry = cy - h // 2
        rw = w // 2
        pygame.draw.rect(surface, (36, 52, 72), (rx, ry, rw, h))
        pygame.draw.rect(surface, (18, 28, 42), (rx, ry, rw, h), 2)
        # Carved relief panel inset
        pygame.draw.rect(surface, (28, 42, 60), (rx + 6, ry + 10, rw - 12, h - 20), border_radius=4)
        pygame.draw.rect(surface, (50, 75, 102), (rx + 6, ry + 10, rw - 12, h - 20), 1, border_radius=4)
        # Atlantean engraved runes
        pygame.draw.line(surface, (0, 200, 220, 130), (rx + 12, ry + 25), (rx + rw - 12, ry + 25), 1)
        pygame.draw.line(surface, (0, 200, 220, 130), (rx + 12, ry + h - 25), (rx + rw - 12, ry + h - 25), 1)

        # 5. Center Keyhole Rosette (Glows Emerald if unlocked, Neon Cyan/Gold if locked)
        pulse = math.sin(self.lock_glow_phase) * 0.25 + 0.75
        col = COLOR_EMERALD if self.is_unlocked else (COLOR_GOLD if pulse > 0.8 else COLOR_NEON_TEAL)
        
        lock_x = cx - left_slide if self.is_unlocked else cx
        # Rosette outer glow
        aura_s = pygame.Surface((44, 44), pygame.SRCALPHA)
        pygame.draw.circle(aura_s, (*col[:3], int(45 * pulse)), (22, 22), 20)
        surface.blit(aura_s, (lock_x - 22, cy - 22))

        pygame.draw.circle(surface, (12, 20, 32), (lock_x, cy), 16)
        pygame.draw.circle(surface, col, (lock_x, cy), 16, 2)
        # Ancient Keyhole symbol
        pygame.draw.circle(surface, col, (lock_x, cy - 3), 4)
        pygame.draw.polygon(surface, col, [(lock_x - 3, cy), (lock_x + 3, cy), (lock_x + 4, cy + 7), (lock_x - 4, cy + 7)])

        # 6. Informative Badge / Status Indicator
        font = pygame.font.SysFont("segoeui", 11, bold=True)
        if not self.is_unlocked:
            badge_text = "ATLANTEAN PORTAL 🔒 [NEEDS KEY 🗝️]"
            badge_col = (255, 220, 110)
        else:
            badge_text = "PORTAL UNLOCKED 🔓 [OPEN]"
            badge_col = (80, 255, 180)

        txt_s = font.render(badge_text, True, badge_col)
        bg_w = txt_s.get_width() + 16
        bg_h = txt_s.get_height() + 8
        badge_surf = pygame.Surface((bg_w, bg_h), pygame.SRCALPHA)
        pygame.draw.rect(badge_surf, (10, 18, 30, 210), (0, 0, bg_w, bg_h), border_radius=6)
        pygame.draw.rect(badge_surf, (*badge_col[:3], 180), (0, 0, bg_w, bg_h), 1, border_radius=6)
        badge_surf.blit(txt_s, (8, 4))
        surface.blit(badge_surf, (cx - bg_w // 2, cy - h // 2 - bg_h - 6))



class ContextMap(IInteractable):
    """Ancient underwater sea chart table allowing divers to inspect discovered expedition zones."""

    def __init__(self, x: float, y: float):
        super().__init__(
            object_id="expedition_map_station",
            name="Ancient Expedition Sea Chart",
            x=x,
            y=y,
            radius=40.0,
            interaction_type=InteractionType.OPEN_MAP,
            interaction_range=110.0,
            required_gesture=GestureType.PINCH,
            priority=70,
            prompt_label="OPEN EXPEDITION MAP",
            icon="MAP",
            sonar_category=SonarEchoCategory.OBJECTIVE,
        )
        self.compass_phase = 0.0

    def interact(self, player: Any, game_manager: Any, context: Dict[str, Any]) -> InteractionResult:
        return InteractionResult(
            success=True,
            action_type=InteractionType.OPEN_MAP,
            feedback_message="OPENING EXPEDITION SEA CHART...",
            sound_effect="puzzle_success",
            score_delta=50,
            opens_modal="EXPEDITION_MAP",
        )

    def draw(self, surface: pygame.Surface) -> None:
        """Renders an authentic carved Atlantean stone pedestal with a 3D holographic sea chart projection."""
        cx, cy = int(self.x), int(self.y)
        self.compass_phase += 0.04
        pulse = (math.sin(self.compass_phase * 1.5) + 1.0) * 0.5

        ped_tex = _get_pedestal_texture()
        pw, ph = 62, 78

        if ped_tex:
            # 1. Soft Seabed Contact Shadow
            sh_w, sh_h = pw + 18, 20
            sh_surf = pygame.Surface((sh_w, sh_h), pygame.SRCALPHA)
            for step, a in [(1.0, 30), (0.75, 55), (0.50, 95)]:
                sw = int(sh_w * step)
                sh = max(3, int(sh_h * step))
                pygame.draw.ellipse(sh_surf, (4, 10, 20, a), ((sh_w - sw) // 2, (sh_h - sh) // 2, sw, sh))
            surface.blit(sh_surf, (cx - sh_w // 2, cy + ph // 2 - 14))

            # 2. Carved Stone Altar Pedestal
            scaled_ped = pygame.transform.smoothscale(ped_tex, (pw, ph))
            surface.blit(scaled_ped, (cx - pw // 2, cy - ph // 2))

            # 3. Glowing Basin Core
            basin_surf = pygame.Surface((32, 14), pygame.SRCALPHA)
            b_alpha = int(120 + 60 * pulse)
            pygame.draw.ellipse(basin_surf, (0, 240, 220, b_alpha), (0, 0, 32, 14))
            surface.blit(basin_surf, (cx - 16, cy - ph // 2 + 10))
        else:
            # Procedural fallback
            pygame.draw.polygon(surface, (25, 40, 58), [
                (cx - 24, cy + 18),
                (cx + 24, cy + 18),
                (cx + 18, cy - 10),
                (cx - 18, cy - 10),
            ])
            pygame.draw.ellipse(surface, (45, 68, 95), (cx - 28, cy - 18, 56, 18))

        # 4. Floating 3D Holographic Expedition Sea Chart Projection
        holo_y = cy - ph // 2 - 20
        # Holographic light cone from basin up to map
        cone_surf = pygame.Surface((64, 28), pygame.SRCALPHA)
        cone_poly = [(20, 26), (44, 26), (56, 0), (8, 0)]
        pygame.draw.polygon(cone_surf, (0, 220, 255, int(25 + 15 * pulse)), cone_poly)
        surface.blit(cone_surf, (cx - 32, holo_y + 4))

        # Rotating holographic bathymetry rings & compass star
        rad = self.compass_phase
        for ring_idx, (r_w, r_h) in enumerate([(44, 20), (32, 14)]):
            ring_s = pygame.Surface((r_w + 4, r_h + 4), pygame.SRCALPHA)
            r_alpha = int((50 + 30 * pulse) * (0.8 if ring_idx == 0 else 1.0))
            pygame.draw.ellipse(ring_s, (0, 240, 230, r_alpha), (2, 2, r_w, r_h), 1)
            surface.blit(ring_s, (cx - r_w // 2 - 2, holo_y - r_h // 2))

        # 4-pointed glowing holographic compass star
        for offset in [0, math.pi / 2, math.pi, math.pi * 1.5]:
            p_rad = rad + offset
            px1 = cx + math.cos(p_rad) * 14.0
            py1 = holo_y + math.sin(p_rad) * 6.5
            pygame.draw.line(surface, COLOR_NEON_TEAL, (cx, holo_y), (int(px1), int(py1)), 2)
            pygame.draw.circle(surface, COLOR_WHITE, (int(px1), int(py1)), 1)

        # Center holographic core beacon
        pygame.draw.circle(surface, COLOR_WHITE, (cx, holo_y), 2)


class ContextCoral(IInteractable):
    """Bioluminescent deep-sea coral specimen for scientific biological sampling."""

    def __init__(self, coral_id: str, name: str, x: float, y: float, species_color: Tuple[int, int, int] = (0, 240, 180)):
        super().__init__(
            object_id=coral_id,
            name=name,
            x=x,
            y=y,
            radius=32.0,
            interaction_type=InteractionType.SAMPLE_CORAL,
            interaction_range=90.0,
            required_gesture=GestureType.PINCH,
            priority=50,
            prompt_label=f"SAMPLE {name.upper()}",
            icon="CORAL",
            sonar_category=SonarEchoCategory.COLLECTIBLE,
        )
        self.species_color = species_color
        self.is_sampled = False
        self.glow_phase = random.uniform(0, math.pi * 2)

    def can_interact(self, player: Any, gesture: GestureType, context: Dict[str, Any]) -> Tuple[bool, str]:
        if self.is_sampled:
            return False, "Specimen Already Sampled"
        return True, "Ready to Sample"

    def interact(self, player: Any, game_manager: Any, context: Dict[str, Any]) -> InteractionResult:
        if self.is_sampled:
            return InteractionResult(
                success=False,
                action_type=InteractionType.SAMPLE_CORAL,
                feedback_message=f"{self.name} already in research pouch.",
            )

        self.is_sampled = True
        self.state = InteractableState.COLLECTED
        return InteractionResult(
            success=True,
            action_type=InteractionType.SAMPLE_CORAL,
            feedback_message=f"SAMPLED: {self.name}! +120 Bio-Research Points",
            sound_effect="bubble",
            score_delta=120,
            oxygen_delta=5.0,  # Coral oxygenation bonus!
        )

    def draw(self, surface: pygame.Surface) -> None:
        """Renders branching bioluminescent coral fronds with glowing tips."""
        cx, cy = int(self.x), int(self.y)
        self.glow_phase += 0.05
        pulse = math.sin(self.glow_phase) * 0.3 + 0.7

        base_col = (110, 110, 120) if self.is_sampled else self.species_color
        tip_col = (160, 160, 170) if self.is_sampled else (
            min(255, int(self.species_color[0] * 1.3)),
            min(255, int(self.species_color[1] * 1.3)),
            min(255, int(self.species_color[2] * 1.3)),
        )

        # Draw branching fan
        branches = [
            (-16, -26), (-8, -34), (0, -38), (8, -34), (16, -26),
            (-12, -18), (12, -18)
        ]
        for bx, by in branches:
            pygame.draw.line(surface, base_col, (cx, cy + 10), (cx + bx, cy + by), 3)
            # Glowing polyp tip
            r_tip = 3 if self.is_sampled else int(4 * pulse)
            pygame.draw.circle(surface, tip_col, (cx + bx, cy + by), r_tip)


class ContextMechanism(IInteractable):
    """Ancient Atlantean stone wheel / sluice gate switch activating environmental puzzles."""

    def __init__(self, mech_id: str, name: str, x: float, y: float, event_type: str = "TIDAL_SURGE"):
        super().__init__(
            object_id=mech_id,
            name=name,
            x=x,
            y=y,
            radius=44.0,
            interaction_type=InteractionType.ACTIVATE_MECHANISM,
            interaction_range=115.0,
            required_gesture=GestureType.PINCH,
            priority=80,
            prompt_label=f"ACTIVATE {name.upper()}",
            icon="MECHANISM",
            sonar_category=SonarEchoCategory.OBJECTIVE,
        )
        self.event_type = event_type
        self.is_activated = False
        self.turn_angle = 0.0

    def can_interact(self, player: Any, gesture: GestureType, context: Dict[str, Any]) -> Tuple[bool, str]:
        if self.is_activated:
            return False, "Mechanism Already Engaged"
        return True, "Ready to Operate"

    def interact(self, player: Any, game_manager: Any, context: Dict[str, Any]) -> InteractionResult:
        if self.is_activated:
            return InteractionResult(
                success=False,
                action_type=InteractionType.ACTIVATE_MECHANISM,
                feedback_message=f"{self.name} has already been engaged.",
            )

        self.is_activated = True
        self.state = InteractableState.ACTIVE

        # Trigger environmental consequence
        if self.event_type == "TIDAL_SURGE":
            player.activate_water_current()
            msg = f"{self.name} ACTIVATED! Cleansing tidal current released!"
        else:
            player.oxygen = min(100.0, player.oxygen + 35.0)
            msg = f"{self.name} ACTIVATED! Subsea oxygen vent unlocked! +35% Oxygen"

        return InteractionResult(
            success=True,
            action_type=InteractionType.ACTIVATE_MECHANISM,
            feedback_message=msg,
            sound_effect="puzzle_success",
            score_delta=250,
        )

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.is_activated and self.turn_angle < 90.0:
            self.turn_angle = min(90.0, self.turn_angle + 180.0 * dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Renders ornate ancient stone cogwheel with rune engravings."""
        cx, cy = int(self.x), int(self.y)
        r = 28
        col = COLOR_GOLD if self.is_activated else COLOR_NEON_TEAL

        # Base wall socket
        pygame.draw.circle(surface, (20, 32, 45), (cx, cy), r + 6)
        pygame.draw.circle(surface, (10, 18, 25), (cx, cy), r + 6, 2)

        # Cogwheel teeth
        rad = math.radians(self.turn_angle)
        for i in range(8):
            ang = rad + i * (math.pi / 4)
            tx = cx + math.cos(ang) * (r + 4)
            ty = cy + math.sin(ang) * (r + 4)
            pygame.draw.circle(surface, (45, 65, 85), (int(tx), int(ty)), 4)

        # Core hub
        pygame.draw.circle(surface, (35, 52, 70), (cx, cy), r)
        pygame.draw.circle(surface, col, (cx, cy), r, 2)

        # Crossbars
        for i in range(4):
            ang = rad + i * (math.pi / 2)
            x1 = cx + math.cos(ang) * (r - 2)
            y1 = cy + math.sin(ang) * (r - 2)
            pygame.draw.line(surface, col, (cx, cy), (int(x1), int(y1)), 2)

        pygame.draw.circle(surface, (15, 25, 35), (cx, cy), 8)
        pygame.draw.circle(surface, col, (cx, cy), 8, 1)


# =========================================================================
# 2. CONTEXT INTERACTION MANAGER
# =========================================================================

class ContextInteractionManager:
    """
    Central engine orchestrating:
        GESTURE + CONTEXT + NEARBY OBJECT + OBJECT STATE = ACTION

    - Identifies candidate interactables via spatial hashing / distance
    - Evaluates line-of-sight & player aim direction
    - Resolves optimal interaction target with priority weighting
    - Displays dynamic context-aware prompts (e.g. 'PINCH -> INSPECT ARTIFACT')
    - Handles debounce and executes object-specific actions
    - Drives Contextual Sonar acoustic echoes
    """

    def __init__(self):
        self.interactables: List[IInteractable] = []
        self.focused_target: Optional[IInteractable] = None
        self.best_in_range_target: Optional[IInteractable] = None
        self.last_action_time: float = 0.0
        self.action_cooldown: float = 0.35
        self.recent_feedback_message: str = ""
        self.feedback_timer: float = 0.0
        self.feedback_color: Tuple[int, int, int] = COLOR_GOLD

        # Active Modal Overlay State (e.g., 3D Artifact Inspect, Tactical Sea Chart)
        self.active_modal: Optional[str] = None
        self.modal_data: Dict[str, Any] = {}
        self.modal_rot_x: float = 0.0
        self.modal_rot_y: float = 0.0

        # Typography for Tactical Floating HUD Prompt
        if not pygame.font.get_init():
            pygame.font.init()
        self.font_prompt_action = pygame.font.SysFont("segoeui", 14, bold=True)
        self.font_prompt_obj = pygame.font.SysFont("segoeui", 11, bold=True)
        self.font_feedback = pygame.font.SysFont("segoeui", 15, bold=True)

    def clear(self) -> None:
        """Clears all registered interactables."""
        self.interactables.clear()
        self.focused_target = None
        self.best_in_range_target = None

    def register(self, item: IInteractable) -> None:
        """Registers an interactable object."""
        self.interactables.append(item)

    def populate_from_level(self, level: Any) -> None:
        """
        Scans an active game Level and automatically binds all treasures,
        crates, air stations, ancient doors, corals, sea charts, and puzzles!
        """
        self.clear()
        if not level:
            return

        # 1. Bind Seafloor Treasures
        if hasattr(level, "treasure_manager") and level.treasure_manager:
            for t in level.treasure_manager.treasures:
                if not t.collected:
                    self.register(ContextTreasure(t))

        # 2. Add Level-Specific Archaeological Artifacts
        lvl_id = getattr(level, "level_id", 1)
        if lvl_id == 1:
            self.register(ContextCoral(
                coral_id="coral_staghorn",
                name="Bioluminescent Staghorn",
                x=SCREEN_WIDTH * 0.72,
                y=SCREEN_HEIGHT * 0.82,
                species_color=(0, 240, 180),
            ))
            self.register(ContextMap(
                x=SCREEN_WIDTH * 0.50,
                y=SCREEN_HEIGHT * 0.88,
            ))

        elif lvl_id == 2:
            self.register(ContextCoral(
                coral_id="coral_brain_2",
                name="Vibrant Brain Coral Reef",
                x=SCREEN_WIDTH * 0.32,
                y=SCREEN_HEIGHT * 0.70,
                species_color=(235, 180, 80),
            ))

        elif lvl_id == 3:
            self.register(ContextArtifact(
                artifact_id="sapphire_chalice",
                name="Deep Abyssal Sapphire Chalice",
                era="Classical Hellenic Age",
                lore="Lined with raw sapphire veins that shimmer in the darkness.",
                x=SCREEN_WIDTH * 0.40,
                y=SCREEN_HEIGHT * 0.64,
                score_val=450,
            ))
            self.register(ContextDoor(
                door_id="abyssal_crypt_door",
                name="Abyssal Sanctum Portal",
                x=SCREEN_WIDTH * 0.12,
                y=SCREEN_HEIGHT * 0.48,
                required_relic="sapphire_chalice",
                required_relic_name="Sapphire Chalice",
            ))
            self.register(ContextCoral(
                coral_id="coral_brain",
                name="Elder Abyssal Brain Coral",
                x=SCREEN_WIDTH * 0.80,
                y=SCREEN_HEIGHT * 0.80,
                species_color=(220, 100, 255),
            ))

        elif lvl_id >= 4:
            self.register(ContextArtifact(
                artifact_id="guardian_seal",
                name="Atlantean Guardian Seal",
                era="Archaic Atlantis First Dynasty",
                lore="Inscribed with rotating celestial concentric bands.",
                x=SCREEN_WIDTH * 0.48,
                y=SCREEN_HEIGHT * 0.65,
                score_val=600,
            ))
            self.register(ContextDoor(
                door_id="atlantean_temple_arch",
                name="Monumental Atlantean Portal",
                x=SCREEN_WIDTH * 0.86,
                y=SCREEN_HEIGHT * 0.42,
                required_relic="guardian_seal",
                required_relic_name="Guardian Seal",
            ))
            self.register(ContextMechanism(
                mech_id="oxygen_vent_switch",
                name="Geothermal Vent Regulator",
                x=SCREEN_WIDTH * 0.18,
                y=SCREEN_HEIGHT * 0.58,
                event_type="OXYGEN_VENT",
            ))

    def sync_level_treasures(self, level: Any) -> None:
        """Ensures any dynamically added or spawned treasures are registered in context manager."""
        if not level or not hasattr(level, "treasure_manager") or not level.treasure_manager:
            return
        registered_raw = {item.raw_treasure for item in self.interactables if isinstance(item, ContextTreasure)}
        for t in level.treasure_manager.treasures:
            if not t.collected and t not in registered_raw:
                self.register(ContextTreasure(t))

    def update(
        self,
        dt: float,
        player: Any,
        cursor_x: float,
        cursor_y: float,
        current_gesture: GestureType,
        is_pinching: bool,
        has_dual_hands: bool = False,
    ) -> Optional[IInteractable]:
        """
        Evaluates nearby objects, player view direction, and distance.
        Selects the focused target and determines whether it's within reach.
        """
        now = time.time()
        if self.feedback_timer > 0:
            self.feedback_timer -= dt

        # Update all objects
        for item in self.interactables:
            item.update(dt)

        px, py = player.x, player.y
        best_candidate: Optional[IInteractable] = None
        best_score = -9999.0

        for item in self.interactables:
            if item.state == InteractableState.COLLECTED:
                continue

            dist_player = math.hypot(px - item.x, py - item.y)
            dist_cursor = math.hypot(cursor_x - item.x, cursor_y - item.y)

            # Max detection radius
            if dist_player > 320.0 and dist_cursor > 200.0:
                continue

            # Direction alignment (is player heading / aiming towards item?)
            # Heading vector from player to item
            dx = item.x - px
            dy = item.y - py
            dist_p = max(1.0, math.hypot(dx, dy))
            dir_x = dx / dist_p
            dir_y = dy / dist_p

            # Player facing vector (approximated by velocity or cursor target)
            p_facing_x = (cursor_x - px)
            p_facing_y = (cursor_y - py)
            p_mag = max(1.0, math.hypot(p_facing_x, p_facing_y))
            view_dot = (dir_x * (p_facing_x / p_mag) + dir_y * (p_facing_y / p_mag))

            # Score = Priority + Proximity weight + View alignment weight + Cursor hover bonus
            cursor_bonus = 250.0 if dist_cursor <= item.radius + 20.0 else max(0.0, 120.0 - dist_cursor)
            distance_score = max(0.0, 200.0 - dist_player * 0.6)
            view_score = max(0.0, view_dot * 60.0)

            total_score = item.priority * 1.5 + distance_score + cursor_bonus + view_score

            if total_score > best_score:
                best_score = total_score
                best_candidate = item

        self.focused_target = best_candidate

        # Check if the focused target is physically in reach
        self.best_in_range_target = None
        if self.focused_target:
            dist_p = math.hypot(px - self.focused_target.x, py - self.focused_target.y)
            dist_c = math.hypot(cursor_x - self.focused_target.x, cursor_y - self.focused_target.y)
            in_range = (dist_p <= self.focused_target.interaction_range or dist_c <= (self.focused_target.radius + 30.0))
            if in_range:
                self.best_in_range_target = self.focused_target

        return self.best_in_range_target

    def handle_gesture(
        self,
        gesture: GestureType,
        player: Any,
        game_manager: Any,
        context: Dict[str, Any],
    ) -> Optional[InteractionResult]:
        """
        Executes Context-Aware Interaction when a gesture triggers.
        GESTURE + CONTEXT + OBJECT = ACTION!
        """
        now = time.time()
        if now - self.last_action_time < self.action_cooldown:
            return None

        # Check if we have an active focused object in range
        target = self.best_in_range_target
        if not target:
            # Pinch with NO valid object nearby -> NO accidental action!
            return None

        # Validate required gesture
        can_act, reason = target.can_interact(player, gesture, context)
        if not can_act:
            self.show_feedback(f"ALERT: {reason}", COLOR_AMBER_WARNING)
            return None

        # Execute object-specific context interaction
        self.last_action_time = now
        res = target.interact(player, game_manager, context)

        # Apply score / oxygen deltas
        if res.score_delta != 0:
            player.add_score(res.score_delta)
        if res.oxygen_delta != 0:
            if res.oxygen_delta > 0:
                player.oxygen = min(100.0, player.oxygen + res.oxygen_delta)
            else:
                player.reduce_oxygen(abs(res.oxygen_delta))

        # Play sound effect
        if res.sound_effect and hasattr(game_manager, "sound_manager") and game_manager.sound_manager:
            game_manager.sound_manager.play(res.sound_effect)

        # Show feedback
        col = COLOR_EMERALD if res.success else COLOR_CORAL_RED
        self.show_feedback(res.feedback_message, col)

        # Check for interactive modal triggers (3D Artifact Inspection or Sea Chart)
        if res.opens_modal:
            self.active_modal = res.opens_modal
            self.modal_data = res.data
            self.modal_rot_x = 0.0
            self.modal_rot_y = 0.0
            self.modal_open_time = time.time()

        return res

    def show_feedback(self, msg: str, color: Tuple[int, int, int] = COLOR_GOLD) -> None:
        """Displays transient tactical feedback banner."""
        self.recent_feedback_message = msg
        self.feedback_timer = 2.4
        self.feedback_color = color

    def close_modal(self) -> None:
        """Closes any active modal overlay."""
        self.active_modal = None
        self.modal_data = {}

    def handle_artifact_rotation(self, dx: float, dy: float) -> None:
        """Rotates the 3D artifact model in inspection chamber using hand/cursor velocity."""
        self.modal_rot_y += dx * 0.45
        self.modal_rot_x += dy * 0.35

    def trigger_sonar(self, px: float, py: float, radius: float = 750.0) -> List[Tuple[IInteractable, SonarEchoCategory]]:
        """
        Context-Aware Sonar: Emits an acoustic wave scanning surrounding waters.
        Identifies and categorizes nearby objects:
        TREASURE, ARTIFACT, SECRET_DOOR, DANGER, COLLECTIBLE, OBJECTIVE.
        """
        echoes: List[Tuple[IInteractable, SonarEchoCategory]] = []
        for item in self.interactables:
            if item.state == InteractableState.COLLECTED:
                continue
            dist = math.hypot(px - item.x, py - item.y)
            if dist <= radius:
                if hasattr(item, "sonar_reveal_timer"):
                    item.sonar_reveal_timer = 4.0
                cat = getattr(item, "sonar_category", SonarEchoCategory.COLLECTIBLE)
                echoes.append((item, cat))
        return echoes

    def get_current_prompt(self, current_gesture: GestureType) -> Optional[Tuple[str, str, Tuple[int, int, int]]]:
        """
        Returns (icon, dynamic_prompt_text, color) for the HUD / cursor tooltip:
        Example: ('🏺', 'PINCH → INSPECT ANCIENT AMPHORA', (0, 240, 180))
        """
        if not self.focused_target:
            return None

        target = self.focused_target
        in_range = (target == self.best_in_range_target)
        prefix = "PINCH -> "
        if target.required_gesture == GestureType.TWO_FINGERS:
            prefix = "SONAR -> "
        elif target.interaction_type == InteractionType.LIFT_HEAVY:
            prefix = "TWO HANDS -> "

        text = f"{prefix}{target.prompt_label}"
        color = COLOR_GOLD if in_range else COLOR_NEON_TEAL
        return target.icon, text, color

    def draw(self, surface: pygame.Surface, time_sec: float) -> None:
        """Renders tactical reticles around objects, floating contextual prompt, and modals."""
        # 1. Draw Object Vectors & Reticles
        for item in self.interactables:
            if item.state != InteractableState.COLLECTED:
                # Call custom vector drawing if object defines it
                if hasattr(item, "draw"):
                    item.draw(surface)

                # Draw contextual target reticle when focused
                is_foc = (item == self.focused_target)
                in_rng = (item == self.best_in_range_target)
                if is_foc or in_rng:
                    item.draw_context_reticle(surface, is_foc, in_rng, time_sec)

        # 2. Render Active Modal Overlays (3D Artifact Inspection or Tactical Sea Chart)
        if self.active_modal == "INSPECT_ARTIFACT":
            self._render_3d_artifact_modal(surface, time_sec)
        elif self.active_modal == "EXPEDITION_MAP":
            self._render_sea_chart_modal(surface, time_sec)

    def _render_3d_artifact_modal(self, surface: pygame.Surface, time_sec: float) -> None:
        """Full interactive 3D Artifact Inspection Chamber with real-time hand rotation."""
        modal_w, modal_h = 760, 480
        mx = SCREEN_WIDTH // 2 - modal_w // 2
        my = SCREEN_HEIGHT // 2 - modal_h // 2

        # Dimmer backdrop
        dimmer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dimmer.fill((4, 12, 24, 210))
        surface.blit(dimmer, (0, 0))

        # Modal Chamber
        box = pygame.Surface((modal_w, modal_h), pygame.SRCALPHA)
        pygame.draw.rect(box, (10, 24, 42, 240), (0, 0, modal_w, modal_h), border_radius=12)
        pygame.draw.rect(box, COLOR_GOLD, (0, 0, modal_w, modal_h), 2, border_radius=12)

        # Header
        name = self.modal_data.get("name", "Ancient Relic")
        era = self.modal_data.get("era", "Antiquity")
        lore = self.modal_data.get("lore", "Discovered in the depths.")
        
        font_t = pygame.font.SysFont("segoeui", 22, bold=True)
        font_s = pygame.font.SysFont("segoeui", 13, bold=True)
        font_b = pygame.font.SysFont("segoeui", 13)

        t_surf = font_t.render(name.upper(), True, COLOR_GOLD)
        e_surf = font_s.render(f"ORIGIN: {era.upper()}  |  3D TOUCHLESS INSPECTION MODE", True, COLOR_NEON_TEAL)
        box.blit(t_surf, (modal_w // 2 - t_surf.get_width() // 2, 24))
        box.blit(e_surf, (modal_w // 2 - e_surf.get_width() // 2, 54))

        # 3D Rotating Artifact Viewport (Center Left)
        vp_cx, vp_cy = 220, 260
        # Pedestal
        pygame.draw.ellipse(box, (24, 40, 60), (vp_cx - 90, vp_cy + 90, 180, 40))
        pygame.draw.ellipse(box, (40, 65, 95), (vp_cx - 90, vp_cy + 90, 180, 40), 2)

        # Interactive 3D Rotated Vector Amphora
        self.modal_rot_y += 1.2
        rad_y = math.radians(self.modal_rot_y)
        shimmer = math.sin(time_sec * 3.0) * 0.2 + 0.8

        # Draw 3D wireframe / faceted body
        for step in range(-3, 4):
            offset_x = math.sin(rad_y + step * 0.4) * 55.0
            col = COLOR_GOLD if abs(offset_x) < 30 else (160, 120, 50)
            pygame.draw.line(box, col, (int(vp_cx + offset_x * 0.3), vp_cy - 80), (int(vp_cx + offset_x), vp_cy), 3)
            pygame.draw.line(box, col, (int(vp_cx + offset_x), vp_cy), (int(vp_cx + offset_x * 0.5), vp_cy + 80), 3)

        pygame.draw.ellipse(box, (255, 235, 140), (vp_cx - 24, vp_cy - 86, 48, 14), 2)
        pygame.draw.ellipse(box, COLOR_GOLD, (vp_cx - 65, vp_cy - 8, 130, 24), 2)

        # Right Info Panel
        px = 440
        desc_box = pygame.Rect(px, 110, 280, 260)
        pygame.draw.rect(box, (15, 32, 52, 180), desc_box, border_radius=8)
        pygame.draw.rect(box, (0, 180, 220, 120), desc_box, 1, border_radius=8)

        lbl_lore = font_s.render("ARCHAEOLOGICAL SIGNIFICANCE:", True, COLOR_OCEAN_CYAN)
        box.blit(lbl_lore, (px + 16, 126))

        # Word wrap lore
        words = lore.split(" ")
        line = ""
        ly = 150
        for w in words:
            test = line + w + " "
            if font_b.size(test)[0] < 248:
                line = test
            else:
                box.blit(font_b.render(line, True, COLOR_WHITE), (px + 16, ly))
                line = w + " "
                ly += 20
        if line:
            box.blit(font_b.render(line, True, COLOR_WHITE), (px + 16, ly))

        # Museum Registration Badge
        reg_txt = "EXHIBIT REGISTERED IN UNDERWATER MUSEUM"
        reg_surf = font_s.render(reg_txt, True, COLOR_EMERALD)
        box.blit(reg_surf, (px + 16, 335))

        # Bottom Instructions
        inst_txt = "MOVE HAND TO ROTATE 3D ARTIFACT  |  PINCH OR ESCAPE TO RETURN"
        inst_surf = font_s.render(inst_txt, True, (255, 225, 100))
        box.blit(inst_surf, (modal_w // 2 - inst_surf.get_width() // 2, modal_h - 38))

        surface.blit(box, (mx, my))

    def _render_sea_chart_modal(self, surface: pygame.Surface, time_sec: float) -> None:
        """Interactive Tactical Underwater Sea Chart Overlay."""
        modal_w, modal_h = 820, 520
        mx = SCREEN_WIDTH // 2 - modal_w // 2
        my = SCREEN_HEIGHT // 2 - modal_h // 2

        dimmer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dimmer.fill((4, 12, 24, 215))
        surface.blit(dimmer, (0, 0))

        chart = pygame.Surface((modal_w, modal_h), pygame.SRCALPHA)
        # Ancient Sea Chart Parchment + Holographic Grid
        pygame.draw.rect(chart, (12, 28, 48, 245), (0, 0, modal_w, modal_h), border_radius=10)
        pygame.draw.rect(chart, COLOR_OCEAN_CYAN, (0, 0, modal_w, modal_h), 2, border_radius=10)

        font_t = pygame.font.SysFont("segoeui", 20, bold=True)
        font_s = pygame.font.SysFont("segoeui", 12, bold=True)

        t_surf = font_t.render("TACTICAL EXPEDITION SEA CHART & SURVEY SECTORS", True, COLOR_GOLD)
        chart.blit(t_surf, (modal_w // 2 - t_surf.get_width() // 2, 20))

        # Sonar Topographic Bathymetry Grid
        gx, gy, gw, gh = 40, 65, 520, 390
        pygame.draw.rect(chart, (6, 16, 28), (gx, gy, gw, gh), border_radius=6)
        pygame.draw.rect(chart, (0, 160, 210, 150), (gx, gy, gw, gh), 1, border_radius=6)

        # Depth contour rings
        for i in range(1, 5):
            r = i * 45
            pygame.draw.circle(chart, (0, 120, 180, 60), (gx + gw // 2, gy + gh // 2), r, 1)

        # Plot discovered points of interest
        for item in self.interactables:
            norm_x = (item.x / SCREEN_WIDTH) * gw
            norm_y = (item.y / SCREEN_HEIGHT) * gh
            ix, iy = int(gx + norm_x), int(gy + norm_y)
            col = COLOR_GOLD if item.sonar_category == SonarEchoCategory.TREASURE else COLOR_NEON_TEAL
            pygame.draw.circle(chart, col, (ix, iy), 5)
            pygame.draw.circle(chart, COLOR_WHITE, (ix, iy), 2)

        # Right Legend & Objectives
        lx = 580
        chart.blit(font_s.render("CHART LEGEND & OBJECTIVES:", True, COLOR_NEON_TEAL), (lx, 75))
        legend_items = [
            ("Genuine Sunken Relics", COLOR_GOLD),
            ("Ancient Archaeological Artifacts", COLOR_PURPLE_MYSTIC),
            ("Sealed Atlantean Portals", COLOR_OCEAN_CYAN),
            ("Biological Coral Colonies", COLOR_EMERALD),
            ("Hydraulic Ancient Mechanisms", COLOR_NEON_TEAL),
            ("Abyssal Hazards & Mines", COLOR_CORAL_RED),
        ]
        ly = 110
        for l_txt, l_col in legend_items:
            pygame.draw.circle(chart, l_col, (lx + 8, ly + 8), 5)
            chart.blit(font_s.render(l_txt, True, COLOR_WHITE), (lx + 22, ly))
            ly += 32

        # Exit prompt
        c_txt = "PINCH ANYWHERE OR ESCAPE TO RESUME DIVE"
        c_surf = font_s.render(c_txt, True, (255, 220, 90))
        chart.blit(c_surf, (modal_w // 2 - c_surf.get_width() // 2, modal_h - 32))

        surface.blit(chart, (mx, my))
