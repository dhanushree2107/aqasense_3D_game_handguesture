import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame

from game.game_manager import GameManager, GameState

def main():
    gm = GameManager(initial_state=GameState.MUSEUM)
    gm.museum.unlock_all()
    # Fully unlocked campaign progression for gallery snapshots
    gm.completed_levels = {1, 2, 3, 4, 5}
    gm.unlocked_levels = 5
    # Place cursor away from cards for clear screenshots
    gm.hand_cursor.x = 640
    gm.hand_cursor.y = 250
    screen_dir = os.path.dirname(__file__)

    # 1. Monumental Ancient Entrance Preview
    gm.current_state = GameState.MUSEUM
    gm.museum_screen.active_chamber = "entrance"
    gm.museum_screen.selected_relic_id = "pearl"
    for _ in range(15):
        gm._update(0.016)
    gm._render()
    p1 = os.path.join(screen_dir, "museum_hd_entrance_preview.png")
    pygame.image.save(gm.screen, p1)
    print(f"Saved: {p1}")

    # 2. Treasure Gallery Preview (Gold Coin featured)
    gm.current_state = GameState.MUSEUM
    gm.museum_screen.active_chamber = "gallery"
    gm.museum_screen.selected_relic_id = "gold_coin"
    for _ in range(15):
        gm._update(0.016)
    gm._render()
    p2 = os.path.join(screen_dir, "museum_hd_gallery_preview.png")
    pygame.image.save(gm.screen, p2)
    print(f"Saved: {p2}")

    # 3. Deep Ocean Archive Preview (Level 3)
    gm.current_state = GameState.MUSEUM
    gm.museum_screen.active_chamber = "archive"
    gm.museum_screen.selected_relic_id = "sapphire_chalice"
    for _ in range(15):
        gm._update(0.016)
    gm._render()
    p3 = os.path.join(screen_dir, "museum_hd_archive_preview.png")
    pygame.image.save(gm.screen, p3)
    print(f"Saved: {p3}")

    # 4. Coral Gallery Preview (Level 2)
    gm.current_state = GameState.MUSEUM
    gm.museum_screen.active_chamber = "coral_gallery"
    gm.museum_screen.selected_relic_id = "coral_compass"
    for _ in range(15):
        gm._update(0.016)
    gm._render()
    p_coral = os.path.join(screen_dir, "museum_hd_coral_preview.png")
    pygame.image.save(gm.screen, p_coral)
    print(f"Saved: {p_coral}")

    # 5. Shipwreck Gallery Preview (Level 4)
    gm.current_state = GameState.MUSEUM
    gm.museum_screen.active_chamber = "shipwreck_gallery"
    gm.museum_screen.selected_relic_id = "ancient_vase"
    for _ in range(15):
        gm._update(0.016)
    gm._render()
    p_ship = os.path.join(screen_dir, "museum_hd_shipwreck_preview.png")
    pygame.image.save(gm.screen, p_ship)
    print(f"Saved: {p_ship}")

    # 6. Ancient Ruins Gallery Preview (Level 5)
    gm.current_state = GameState.MUSEUM
    gm.museum_screen.active_chamber = "ruins_gallery"
    gm.museum_screen.selected_relic_id = "guardian_seal"
    for _ in range(15):
        gm._update(0.016)
    gm._render()
    p_ruins = os.path.join(screen_dir, "museum_hd_ruins_preview.png")
    pygame.image.save(gm.screen, p_ruins)
    print(f"Saved: {p_ruins}")

    # 7. Legendary Chamber Preview (Final Rank)
    gm.current_state = GameState.MUSEUM
    gm.museum_screen.active_chamber = "legendary"
    gm.museum_screen.selected_relic_id = "ancient_crown"
    for _ in range(15):
        gm._update(0.016)
    gm._render()
    p4 = os.path.join(screen_dir, "museum_hd_legendary_preview.png")
    pygame.image.save(gm.screen, p4)
    print(f"Saved: {p4}")

    # 8. Physical Locked Stone Door Preview
    gm.completed_levels = {1}  # Only Level 1 completed
    gm.unlocked_levels = 2
    gm.museum_screen.curator_mode_active = False
    gm.museum_screen.active_chamber = "archive"
    gm.museum_screen.door_open_progress["archive"] = 0.0
    gm.museum_screen.inspected_exhibit = None
    for _ in range(15):
        gm._update(0.016)
    gm._render()
    p_door = os.path.join(screen_dir, "museum_hd_locked_door_preview.png")
    pygame.image.save(gm.screen, p_door)
    print(f"Saved: {p_door}")

    # 9. Inspection Modal on Ancient Gold Coin (3D Pitch/Yaw rotation & user dossier fields)
    gm.current_state = GameState.MUSEUM
    gm.museum.unlock_all()
    gm.completed_levels = {1, 2, 3, 4, 5}
    gm.museum_screen.inspected_exhibit = gm.museum.exhibits["gold_coin"]
    gm.museum_screen.last_triggered_gesture = None
    gm.museum_screen.gesture_action_cooldown = 5.0
    for _ in range(5):
        gm.museum_screen.update(cursor_x=640, cursor_y=360, is_clicked=False, dt=0.016)
    gm._render()
    p_coin = os.path.join(screen_dir, "museum_hd_coin_inspection_preview.png")
    pygame.image.save(gm.screen, p_coin)
    print(f"Saved: {p_coin}")

    # 10. Two-Hand Inspection Modal on Heavy Treasure Chest
    gm.current_state = GameState.MUSEUM
    gm.museum_screen.inspected_exhibit = gm.museum.exhibits["heavy_chest"]
    gm.museum_screen.last_triggered_gesture = None
    gm.museum_screen.gesture_action_cooldown = 5.0
    for _ in range(5):
        gm.museum_screen.update(cursor_x=640, cursor_y=360, is_clicked=False, dt=0.016)
    gm._render()
    p_chest = os.path.join(screen_dir, "museum_hd_chest_inspection_preview.png")
    pygame.image.save(gm.screen, p_chest)
    print(f"Saved: {p_chest}")

    gm.hand_detector.stop()
    pygame.quit()
    print("All museum snapshots updated successfully!")

if __name__ == "__main__":
    main()
