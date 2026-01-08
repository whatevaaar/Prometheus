import pygame

import config
from geometry.point.point import get_entity_screen_pos


def draw_entity(screen, e, anim, tile_px):
    """
    Dibuja una entidad con estilo en TileView.
    anim: diccionario con offsets, accesorios y blink
    """
    cx, cy = get_entity_screen_pos(e, anim, tile_px)

    # cuerpo
    body_w = tile_px * config.ENTITY_SCALE
    body_h = tile_px * config.ENTITY_SCALE
    body_rect = pygame.Rect(cx - body_w / 2, cy - body_h / 2, body_w, body_h)
    color = e.faction.color if e.faction else (180, 180, 180)
    pygame.draw.ellipse(screen, color, body_rect)

    # ojos cute, proporcionales al cuerpo
    eye_radius = int(body_w * 0.08)
    eye_offset_x = int(body_w * 0.18)
    eye_offset_y = int(body_h * 0.18)
    pygame.draw.circle(screen, (0, 0, 0), (cx - eye_offset_x, cy - eye_offset_y), eye_radius)
    pygame.draw.circle(screen, (0, 0, 0), (cx + eye_offset_x, cy - eye_offset_y), eye_radius)

    # accesorios
    if anim["accessory"] == "hat":
        hat_rect = pygame.Rect(cx - body_w / 4, cy - body_h / 2, body_w / 2, body_h / 4)
        pygame.draw.rect(screen, (255, 200, 0), hat_rect)
    elif anim["accessory"] == "cape":
        cape_rect = pygame.Rect(cx - body_w / 3, cy, body_w * 2 / 3, body_h / 2)
        pygame.draw.rect(screen, (200, 0, 200), cape_rect)
    elif anim["accessory"] == "flag":
        pygame.draw.line(screen, (255, 255, 255), (cx, cy - body_h / 2), (cx, cy - body_h), 2)
        pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(cx, cy - body_h, body_w / 4, body_h / 4))

    # boca feliz
    happiness = anim.get("happiness", 0.6)  # 0 a 1
    mouth_w = int(body_w * 0.5)
    mouth_h = int(body_h * 0.15 * happiness)
    mouth_y = cy + int(body_h * 0.2)
    pygame.draw.arc(screen, (0, 0, 0), (cx - mouth_w // 2, mouth_y, mouth_w, mouth_h), 3.14, 0, 1)

    # nombre
    font = pygame.font.SysFont("consolas", 12)
    name_surf = font.render(e.name, True, (255, 255, 255))
    screen.blit(name_surf, (cx - name_surf.get_width() // 2, cy - body_h / 2 - 14))
