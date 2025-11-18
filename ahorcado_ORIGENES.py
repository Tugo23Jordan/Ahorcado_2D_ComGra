
import pygame, sys, random, unicodedata, math, os



# -------------------- CONFIGURACIÓN --------------------
WIDTH, HEIGHT = 1100, 700
FPS = 30
MAX_ERRORS = 9

WRONG_COLOR = (255, 80, 80)
RANKING_FILE = "ranking.txt"
PALABRAS_FILE = "palabras.txt"



def quitar_tildes(s: str) -> str:
    """Quita tildes de un texto para comparar letras."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )


def draw_neon_text(surface, text, font, pos, color, glow_size=8):
    """Dibuja texto con efecto neón (brillo)."""
    x, y = pos
    base = font.render(text, True, color)
    for i in range(glow_size, 0, -2):
        glow = font.render(
            text, True,
            (color[0] // 3, color[1] // 3, color[2] // 3)
        )
        surface.blit(glow, (x - i // 2, y - i // 2))
    surface.blit(base, (x, y))


def draw_glitch(surface, text, font, pos):
    """Texto rojo con efecto glitch (para el GAME OVER)."""
    x, y = pos
    base = font.render(text, True, (255, 0, 0))
    surface.blit(base, (x, y))
    for _ in range(3):
        dx = random.randint(-4, 4)
        dy = random.randint(-2, 2)
        glitch = font.render(
            text, True,
            random.choice([(255, 80, 80), (255, 200, 200)])
        )
        surface.blit(glitch, (x + dx, y + dy))




def draw_crt_background(surface):
    """Fondo con grid y scanlines estilo monitor retro."""
    surface.fill((0, 0, 0))

    grid_color = (0, 90, 120)

    # Líneas verticales
    for x in range(0, WIDTH, 45):
        pygame.draw.line(surface, grid_color, (x, 0), (x, HEIGHT), 1)

    # Líneas horizontales
    for y in range(0, HEIGHT, 45):
        pygame.draw.line(surface, grid_color, (0, y), (WIDTH, y), 1)

    # Curvatura CRT
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.ellipse(
        overlay, (0, 0, 0, 130),
        (-250, -100, WIDTH + 500, HEIGHT + 300)
    )
    surface.blit(overlay, (0, 0))

    # Scanlines
    for y in range(0, HEIGHT, 4):
        pygame.draw.line(surface, (0, 0, 0, 140), (0, y), (WIDTH, y))


def draw_crt_frame(surface):
    """Marco del televisor CRT."""
    frame = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(frame, (25, 25, 25),
                     (0, 0, WIDTH, HEIGHT), border_radius=55)
    pygame.draw.rect(frame, (10, 10, 10),
                     (20, 20, WIDTH - 40, HEIGHT - 40), border_radius=40)

    pygame.draw.rect(frame, (90, 90, 90),
                     (30, 30, WIDTH - 60, HEIGHT - 60), 5, border_radius=40)

    surface.blit(frame, (0, 0))




particles_global = [
    [random.randint(0, WIDTH),
     random.randint(0, HEIGHT),
     random.choice([(0, 255, 255), (255, 0, 255), (0, 200, 255)]),
     random.uniform(0.8, 2.0)]
    for _ in range(100)
]


def draw_particles(surface):
    """Partículas de colores que caen en el fondo."""
    for p in particles_global:
        pygame.draw.circle(surface, p[2], (int(p[0]), int(p[1])), 2)
        p[1] += p[3]
        if p[1] > HEIGHT:
            p[0] = random.randint(0, WIDTH)
            p[1] = 0




def crt_startup(screen, clock):
    """Animación de encendido de monitor CRT."""
    # Línea horizontal que se abre
    for i in range(40):
        screen.fill((0, 0, 0))
        h = max(3, int(HEIGHT * i / 40))
        rect = pygame.Rect(0, HEIGHT // 2 - h // 2, WIDTH, h)
        pygame.draw.rect(screen, (255, 255, 255), rect)
        pygame.display.flip()
        clock.tick(60)

    # Fade con curvatura CRT
    for alpha in range(255, -1, -12):
        draw_crt_background(screen)
        draw_crt_frame(screen)

        fade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        fade.fill((0, 0, 0, alpha))
        screen.blit(fade, (0, 0))

        pygame.display.flip()
        clock.tick(60)




def dibujar_ahorcado(screen, errores, fall_y=0, offset_x=0, offset_y=0):
    base_x = 200 + offset_x
    base_y = HEIGHT - 120 + offset_y

    # ----- Estructura -----
    pygame.draw.line(screen, (230,230,230), (base_x-60, base_y), (base_x+120, base_y), 8)
    pygame.draw.line(screen, (230,230,230), (base_x, base_y), (base_x, base_y-300), 8)
    pygame.draw.line(screen, (230,230,230), (base_x, base_y-300), (base_x+140, base_y-300), 8)
    pygame.draw.line(screen, (255,0,80), (base_x+140, base_y-300), (base_x+140, base_y-250), 4)

    # Coordenadas del muñeco + caída
    cx = base_x + 140
    cy = base_y - 220 + fall_y

    # ---------- 1. Cabeza ----------
    if errores >= 1:
        pygame.draw.circle(screen, (255,255,255), (cx, cy), 30, 4)

    # ---------- 2. Ojo izquierdo ----------
    if errores >= 2:
        pygame.draw.line(screen, (255,255,255), (cx-12, cy-8), (cx-4, cy), 3)
        pygame.draw.line(screen, (255,255,255), (cx-4, cy-8), (cx-12, cy), 3)

    # ---------- 3. Ojo derecho ----------
    if errores >= 3:
        pygame.draw.line(screen, (255,255,255), (cx+12, cy-8), (cx+4, cy), 3)
        pygame.draw.line(screen, (255,255,255), (cx+4, cy-8), (cx+12, cy), 3)

    # ---------- 4. Boca triste ----------
    if errores >= 4:
        pygame.draw.arc(screen, (255,255,255), (cx-15, cy+5, 30, 20), 0, math.pi, 3)

    # ---------- 5. Cuerpo ----------
    if errores >= 5:
        pygame.draw.line(screen, (255,255,255), (cx, cy+30), (cx, cy+110), 4)

    # ---------- 6. Brazo izquierdo ----------
    if errores >= 6:
        pygame.draw.line(screen, (255,255,255), (cx, cy+45), (cx-35, cy+80), 4)

    # ---------- 7. Brazo derecho ----------
    if errores >= 7:
        pygame.draw.line(screen, (255,255,255), (cx, cy+45), (cx+35, cy+80), 4)

    # ---------- 8. Pierna izquierda ----------
    if errores >= 8:
        pygame.draw.line(screen, (255,255,255), (cx, cy+110), (cx-35, cy+150), 4)

    # ---------- 9. Pierna derecha ----------
    if errores >= 9:
        pygame.draw.line(screen, (255,255,255), (cx, cy+110), (cx+35, cy+150), 4)


def cargar_palabras():
    categorias = {}
    if not os.path.exists(PALABRAS_FILE):
        with open(PALABRAS_FILE, "w", encoding="utf-8") as f:
            f.write(
                "Tecnologia: computadora, algoritmo, inteligencia, robot, programacion\n"
                "Ciencia: gravedad, celula, atomo, molecula, energia\n"
                "Peliculas: matrix, avatar, titanic, gladiador, interestelar\n"
                "Paises: peru, argentina, japon, canada, francia\n"
                "Animales: perro, gato, leon, tigre, elefante\n"
            )
    with open(PALABRAS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                cat, words = line.strip().split(":", 1)
                categorias[cat.strip()] = [
                    w.strip().lower() for w in words.split(",")
                ]
    return categorias




def guardar_puntaje(nombre, puntos_ganados):
    """
    Suma puntos y victorias al usuario.
    Formato en archivo: NOMBRE|PUNTOS|VICTORIAS
    """
    nombre = nombre.strip()
    if not nombre:
        return

    ranking = {}

    if os.path.exists(RANKING_FILE):
        with open(RANKING_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "|" not in line:
                    continue
                parts = line.strip().split("|")
                if not parts[0]:
                    continue
                n = parts[0]
                try:
                    pts = int(parts[1]) if len(parts) > 1 and parts[1] else 0
                except ValueError:
                    pts = 0
                try:
                    vic = int(parts[2]) if len(parts) > 2 and parts[2] else 0
                except ValueError:
                    vic = 0
                ranking[n] = [pts, vic]

    if nombre in ranking:
        ranking[nombre][0] += puntos_ganados
        ranking[nombre][1] += 1
    else:
        ranking[nombre] = [puntos_ganados, 1]

    with open(RANKING_FILE, "w", encoding="utf-8") as f:
        for n, (pts, vic) in ranking.items():
            f.write(f"{n}|{pts}|{vic}\n")


def leer_ranking():
    lista = []
    if not os.path.exists(RANKING_FILE):
        return lista
    with open(RANKING_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if "|" not in line:
                continue
            parts = line.strip().split("|")
            while len(parts) < 3:
                parts.append("0")
            nombre = parts[0] if parts[0] else "SIN_NOMBRE"
            try:
                pts = int(parts[1]) if parts[1] else 0
            except ValueError:
                pts = 0
            try:
                vic = int(parts[2]) if parts[2] else 0
            except ValueError:
                vic = 0
            lista.append((nombre, pts, vic))
    lista.sort(key=lambda x: x[1], reverse=True)
    return lista[:5]



def pantalla_nombre(screen, font_big, font_medium, clock):
    nombre = ""
    cursor_visible = True
    cursor_timer = 0
    float_timer = 0

    crt_startup(screen, clock)

    while True:
        draw_crt_background(screen)
        draw_particles(screen)
        draw_crt_frame(screen)

        offset = int(math.sin(float_timer / 15) * 6)
        float_timer += 1

        draw_neon_text(
            screen,
            "INGRESA TU NOMBRE:",
            font_big,
            (WIDTH // 2 - 360, 150 + offset),
            (0, 255, 255),
            12
        )

        box_w, box_h = 650, 90
        box_x = WIDTH // 2 - box_w // 2
        box_y = 310

        pygame.draw.rect(screen, (255, 0, 255),
                         (box_x - 4, box_y - 4, box_w + 8, box_h + 8), 4)
        pygame.draw.rect(screen, (255, 0, 255),
                         (box_x, box_y, box_w, box_h), 3)

        draw_neon_text(
            screen, "NOMBRE:",
            font_medium,
            (box_x + 30, box_y + 22),
            (0, 255, 255),
            6
        )

        cursor_timer += 1
        if cursor_timer % 25 == 0:
            cursor_visible = not cursor_visible
        cursor = "_" if cursor_visible else " "

        draw_neon_text(
            screen,
            nombre + cursor,
            font_medium,
            (box_x + 250, box_y + 22),
            (255, 120, 255),
            6
        )

        msg = "Presiona ENTER para continuar"
        temp = font_medium.render(msg, True, (0, 255, 180))
        screen.blit(temp, (WIDTH // 2 - temp.get_width() // 2, HEIGHT - 90))

        pygame.display.flip()
        clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN and nombre.strip():
                    return nombre.upper()
                elif e.key == pygame.K_BACKSPACE:
                    nombre = nombre[:-1]
                else:
                    if e.unicode.isalpha() or e.unicode == " ":
                        if len(nombre) < 10:
                            nombre += e.unicode.upper()





def pantalla_categoria(screen, categorias, font_big, font_medium, clock):
    opcion = 1
    total = len(categorias)

    while True:
        draw_crt_background(screen)
        draw_particles(screen)
        draw_crt_frame(screen)

        draw_neon_text(
            screen, "Elige una categoría:",
            font_big,
            (WIDTH // 2 - 350, 150),
            (0, 255, 255),
            10
        )

        y0 = 260
        for i, cat in enumerate(categorias.keys(), start=1):
            color = (0, 255, 150) if i == opcion else (255, 100, 255)
            text = f"{i}. {cat}"
            draw_neon_text(
                screen,
                text,
                font_medium,
                (WIDTH // 2 - 180, y0 + (i - 1) * 55),
                color,
                6
            )
            if i == opcion:
                pygame.draw.rect(
                    screen, color,
                    (WIDTH // 2 - 200, y0 + (i - 1) * 55 - 5, 360, 45),
                    2
                )

        msg = "Usa ↑ ↓ para moverte  |  ENTER para confirmar"
        temp = font_medium.render(msg, True, (0, 255, 180))
        screen.blit(temp, (WIDTH // 2 - temp.get_width() // 2, HEIGHT - 90))

        pygame.display.flip()
        clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    opcion -= 1
                    if opcion < 1:
                        opcion = total
                if e.key == pygame.K_DOWN:
                    opcion += 1
                    if opcion > total:
                        opcion = 1
                if e.key == pygame.K_RETURN:
                    return list(categorias.keys())[opcion - 1]




def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ahorcado Neon Deluxe")
    clock = pygame.time.Clock()

    font_small = pygame.font.SysFont("Consolas", 20, bold=True)
    font_medium = pygame.font.SysFont("Consolas", 26, bold=True)
    font_big = pygame.font.SysFont("Arial Black", 52, bold=True)
    font_word = pygame.font.SysFont("Consolas", 40, bold=True)
    font_end = pygame.font.SysFont("Arial Black", 40, bold=True)

    categorias = cargar_palabras()

    nombre = pantalla_nombre(screen, font_big, font_medium, clock)
    categoria_elegida = pantalla_categoria(screen, categorias,
                                           font_big, font_medium, clock)

    # Estado del juego
    palabra = random.choice(categorias[categoria_elegida])
    palabra_comp = quitar_tildes(palabra)
    letras_acertadas = set()
    letras_erradas = []
    errores = 0
    juego_terminado = False
    mensaje = ""
    timer = 0

    shake_frames = 0
    fall_y = 0
    fall_speed = 0
    death_particles = []

    boton_reiniciar = pygame.Rect(WIDTH // 2 - 70, HEIGHT - 95, 160, 50)

    def reiniciar():
        nonlocal palabra, palabra_comp, letras_acertadas, letras_erradas
        nonlocal errores, juego_terminado, mensaje
        nonlocal shake_frames, fall_y, fall_speed, death_particles

        palabra_nueva = random.choice(categorias[categoria_elegida])
        palabra_local = palabra_nueva
        palabra_local_comp = quitar_tildes(palabra_local)

        palabra = palabra_local
        palabra_comp = palabra_local_comp
        letras_acertadas.clear()
        letras_erradas.clear()
        errores = 0
        juego_terminado = False
        mensaje = ""
        shake_frames = 0
        fall_y = 0
        fall_speed = 0
        death_particles = []

    # Bucle principal
    while True:
        clock.tick(FPS)
        timer += 1

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if juego_terminado and e.key == pygame.K_RETURN:
                    reiniciar()
                    continue

                if e.unicode.isalpha() and not juego_terminado:
                    letra = quitar_tildes(e.unicode.lower())
                    if letra in letras_acertadas or letra in letras_erradas:
                        continue
                    if letra in palabra_comp:
                        letras_acertadas.add(letra)
                        if set(c for c in palabra_comp
                               if c.isalpha()).issubset(letras_acertadas):
                            juego_terminado = True
                            mensaje = "VICTORIA"
                            guardar_puntaje(nombre, 10)

                    else:
                        letras_erradas.append(letra)
                        errores += 1
                        shake_frames = 6
                        if errores >= MAX_ERRORS:
                            juego_terminado = True
                            mensaje = f"GAME OVER - Era: {palabra.upper()}"
                            fall_speed = 3
                            head_x = 150 + 190
                            head_y = (HEIGHT - 130) - 230
                            death_particles = [
                                [head_x, head_y,
                                 random.uniform(-3, 3),
                                 random.uniform(-4, 2),
                                 random.choice([(255, 0, 80),
                                                (255, 40, 140)])]
                                for _ in range(30)
                            ]

            if e.type == pygame.MOUSEBUTTONDOWN and juego_terminado:
                if boton_reiniciar.collidepoint(e.pos):
                    reiniciar()

        # Caída al morir
        if errores >= MAX_ERRORS and fall_speed > 0:
            fall_y += fall_speed
            fall_speed += 0.6
            if fall_y > 160:
                fall_speed = 0

        # Shake leve
        offset_x = offset_y = 0
        if shake_frames > 0:
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-3, 3)
            shake_frames -= 1

        # Fondo CRT
        draw_crt_background(screen)
        draw_particles(screen)
        draw_crt_frame(screen)

        # Título
        glow = int((math.sin(timer / 15) + 1) * 120)
        title_color = (255, glow, 255)
        draw_neon_text(
            screen, "AHORCADO NEON",
            font_big,
            (WIDTH // 2 - 260, 60),
            title_color,
            12
        )

        # Muñeco
        dibujar_ahorcado(screen, errores, fall_y, offset_x, offset_y)

        # Partículas de muerte
        for p in death_particles:
            p[0] += p[2]
            p[1] += p[3]
            pygame.draw.circle(
                screen, p[4],
                (int(p[0] + offset_x), int(p[1] + offset_y)), 3
            )

        # Panel info jugador (derecha)
        panel_x = WIDTH // 2 + 80
        panel_y = 190
        panel_w = 360
        panel_h = 240

        pygame.draw.rect(
            screen, (0, 255, 255),
            (panel_x - 4, panel_y - 4, panel_w + 8, panel_h + 8), 3
        )
        pygame.draw.rect(
            screen, (0, 120, 160),
            (panel_x, panel_y, panel_w, panel_h), 2
        )

        # Palabra
        x0 = panel_x
        y0 = 140
        spacing = 45
        for i, l in enumerate(palabra):
            rect_x = x0 + i * spacing
            pygame.draw.line(screen, (255, 0, 180),
                             (rect_x, y0 + 35),
                             (rect_x + 30, y0 + 35), 4)
            if quitar_tildes(l) in letras_acertadas:
                letter = font_word.render(l.upper(), True, (0, 200, 255))
                screen.blit(letter, (rect_x, y0))

        # Info en panel
        screen.blit(
            font_medium.render(f"Jugador: {nombre}",
                               True, (255, 255, 255)),
            (panel_x + 10, panel_y + 15)
        )
        screen.blit(
            font_medium.render(f"Categoría: {categoria_elegida}",
                               True, (180, 255, 180)),
            (panel_x + 10, panel_y + 45)
        )
        screen.blit(
            font_medium.render(f"Errores: {errores}/{MAX_ERRORS}",
                               True, (255, 255, 255)),
            (panel_x + 10, panel_y + 75)
        )

        if letras_erradas:
            txt = "Fallos: " + " ".join(letras_erradas).upper()
            screen.blit(
                font_medium.render(txt, True, WRONG_COLOR),
                (panel_x + 10, panel_y + 105)
            )

        
            # ------------ ENTER y ESC centrados -------------
        txt1 = font_small.render("ENTER = reiniciar", True, (200, 200, 200))
        txt2 = font_small.render("ESC = salir", True, (200, 200, 200))

        # CENTRAR LOS TEXTOS DENTRO DEL PANEL
        screen.blit(txt1, (panel_x + (panel_w - txt1.get_width()) // 2, panel_y + 140))
        screen.blit(txt2, (panel_x + (panel_w - txt2.get_width()) // 2, panel_y + 170))
# ------------------------------------------------


        # Panel ranking
        rank_x = panel_x
        rank_y = panel_y + panel_h + 40
        rank_w = 360
        rank_h = 170

        pygame.draw.rect(
            screen, (0, 255, 255),
            (rank_x - 4, rank_y - 4, rank_w + 8, rank_h + 8), 3
        )
        pygame.draw.rect(
            screen, (0, 120, 160),
            (rank_x, rank_y, rank_w, rank_h), 2
        )

        draw_neon_text(screen, "🏆 RANKING", font_medium,
                       (rank_x + 90, rank_y + 5),
                       (0, 255, 255), 6)

        ranking = leer_ranking()
        for i, (n, pts, vic) in enumerate(ranking, start=1):
            linea = f"{i}. {n[:9]:9} {pts:3} pts | {vic} vict."
            screen.blit(
                font_small.render(linea, True, (220, 220, 220)),
                (rank_x + 10, rank_y + 40 + (i - 1) * 24)
            )

        # Botón Reiniciar y mensaje final
        if juego_terminado:
            pygame.draw.rect(
                screen, (0, 255, 120),
                boton_reiniciar, border_radius=10
            )
            draw_neon_text(
                screen, "Reiniciar",
                font_medium,
                (boton_reiniciar.x + 12, boton_reiniciar.y + 8),
                (0, 0, 0), 4
            )

            w = font_end.size(mensaje)[0]
            if "VICTORIA" in mensaje:
                draw_neon_text(
                    screen, mensaje, font_end,
                    (WIDTH // 2 - w // 2, HEIGHT - 150),
                    (0, 255, 0), 12
                )
            else:
                draw_glitch(
                    screen, mensaje, font_end,
                    (WIDTH // 2 - w // 2, HEIGHT - 150)
                )

        pygame.display.flip()



if __name__ == "__main__":
    main()
