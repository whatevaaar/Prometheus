import pygame

import config
from geometry.point.point import get_entity_screen_pos


def draw_entity(screen, e, anim, tile_px_w, tile_px_h, tile_offset_x=0, tile_offset_y=0):
    cx, cy = get_entity_screen_pos(e, anim, tile_px_w, tile_px_h, tile_offset_x, tile_offset_y)
    color = e.faction.color if e.faction else (180, 180, 180)
    body_w = tile_px_w * config.ENTITY_SCALE
    body_h = tile_px_h * config.ENTITY_SCALE
    if anim["accessory"] == "cape":
        cape_color = (max(0, color[0] - 40), max(0, color[1] - 40), max(0, color[2] - 40),)

        cape_points = [(cx - body_w * 0.45, cy - body_h * 0.2), (cx + body_w * 0.45, cy - body_h * 0.2),
                       (cx + body_w * 0.3, cy + body_h * 0.7), (cx - body_w * 0.3, cy + body_h * 0.7), ]

        pygame.draw.polygon(screen, cape_color, cape_points)

    # cuerpo
    body_rect = pygame.Rect(cx - body_w / 2, cy - body_h / 2, body_w, body_h)
    pygame.draw.ellipse(screen, color, body_rect)

    # ojos (cute)
    eye_offset_x = int(body_w * 0.2)
    eye_offset_y = int(body_h * 0.2)
    pygame.draw.circle(screen, (0, 0, 0), (cx - eye_offset_x, cy - eye_offset_y), config.ENTITY_EYE_RADIUS)
    pygame.draw.circle(screen, (0, 0, 0), (cx + eye_offset_x, cy - eye_offset_y), config.ENTITY_EYE_RADIUS)

    # boca feliz
    happiness = anim.get("happiness", 0.6)
    mouth_y = cy + int(body_h * 0.2)
    mouth_w = int(body_w * 0.5)
    mouth_h = int(2 * happiness)
    pygame.draw.arc(screen, (0, 0, 0), (cx - mouth_w // 2, mouth_y, mouth_w, mouth_h), 3.14, 0, 1)

    arm_length = body_w * 0.25
    pygame.draw.line(screen, color, (cx - body_w / 2, cy), (cx - body_w / 2 - arm_length, cy + arm_length / 2), 3)
    pygame.draw.line(screen, color, (cx + body_w / 2, cy), (cx + body_w / 2 + arm_length, cy + arm_length / 2), 3)

    shadow_rect = pygame.Rect(cx - body_w / 2, cy + body_h / 2 * 0.8, body_w, body_h * 0.3)
    pygame.draw.ellipse(screen, (0, 0, 0, 50), shadow_rect)  # alpha si usas Surface con SRCALPHA

    # accesorios
    if anim["accessory"] == "hat":
        hat_rect = pygame.Rect(cx - body_w / 4, cy - body_h / 2, body_w / 2, body_h / 4)
        pygame.draw.rect(screen, (255, 200, 0), hat_rect)
    elif anim["accessory"] == "flag":
        pygame.draw.line(screen, (255, 255, 255), (cx, cy - body_h / 2), (cx, cy - body_h), 2)
        pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(cx, cy - body_h, body_w / 4, body_h / 4))

    # nombre
    font = pygame.font.SysFont("consolas", 12)
    name_surf = font.render(e.name, True, (255, 255, 255))
    screen.blit(name_surf, (cx - name_surf.get_width() // 2, cy - body_h / 2 - 12))
