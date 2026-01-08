import pygame


def draw_entity(screen, e, anim, tile_px):
    """
    Dibuja una entidad con estilo en TileView
    anim: diccionario con offsets, accesorios y blink
    """
    cx = int((e.x + 0.5 + anim["offset_x"]) * tile_px)
    cy = int((e.y + 0.5 + anim["offset_y"]) * tile_px)

    # cuerpo
    body_w = tile_px * 0.6
    body_h = tile_px * 0.6
    body_rect = pygame.Rect(cx - body_w / 2, cy - body_h / 2, body_w, body_h)
    color = e.faction.color if e.faction else (180, 180, 180)
    pygame.draw.ellipse(screen, color, body_rect)

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

    # ojos grandes y carismáticos
    eye_radius = 2
    pygame.draw.circle(screen, (0, 0, 0), (cx - 4, cy - 5), eye_radius)
    pygame.draw.circle(screen, (0, 0, 0), (cx + 4, cy - 5), eye_radius)

    # boca feliz según "nivel de felicidad" estático por ahora
    happiness = 0.6  # 0 a 1
    mouth_y = cy + 4
    mouth_w = int(body_w * 0.5)
    mouth_h = int(2 * happiness)
    pygame.draw.arc(screen, (0, 0, 0), (cx - mouth_w // 2, mouth_y, mouth_w, mouth_h), 3.14, 0, 1)

    # nombre
    font = pygame.font.SysFont("consolas", 12)
    name_surf = font.render(e.name, True, (255, 255, 255))
    screen.blit(name_surf, (cx - name_surf.get_width() // 2, cy - body_h / 2 - 12))
