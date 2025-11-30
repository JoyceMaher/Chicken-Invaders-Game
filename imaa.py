import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random
import time

glutInit()

# Player and Bullet properties / Saleh
player_x = 0
player_y = -5
player_z = 0
player_radius = 0.1
player_width = 1
player_height = 0.4
player_speed = 0.3
bullet_speed = 0.2
bullet_width = 0.1
bullet_height = 0.3
angle_rocket = 0
power_level=1

ship_destroyed = False
ship_respawn_timer = 0
ship_respawn_delay = 2000  # 2 seconds respawn delay
ship_explosion_particles = []

# Score properties / Jojo 
score = 0
lives = 3
max_lives = 5


# Omar functions
def draw_sphere(x, y, z, radius, r, g, b):
    glColor3f(r, g, b)
    quadric = gluNewQuadric()
    glPushMatrix()
    glTranslatef(x, y, z)
    gluSphere(quadric, radius, 32, 32)
    glPopMatrix()

def draw_oval(x, y, z, radius_x, radius_y, r, g, b):  
    glColor3f(r, g, b)
    quadric = gluNewQuadric()
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(1, radius_y/radius_x, 1) 
    gluSphere(quadric, radius_x, 32, 32)
    glPopMatrix()

def increase_chicken_speed(chickens, last_increase_time, interval=10, speed_increment=0.03):
    current_time = time.time()
    if current_time - last_increase_time >= interval:
        for c in chickens:
            c['rand_speed_x'] += speed_increment
            c['rand_speed_y'] += speed_increment
        last_increase_time = current_time
        print(f"Chicken speed increased! Current speeds: {chickens[0]['rand_speed_x']:.2f}, {chickens[0]['rand_speed_y']:.2f}")
    return last_increase_time    

def draw_cube(x, y, z, size, r, g, b):
    vertices = [
        [1,1,-1],[1,-1,-1],[-1,-1,-1],[-1,1,-1],
        [1,1,1],[1,-1,1],[-1,-1,1],[-1,1,1]
    ]
    vertices = [[v[0]*size + x, v[1]*size + y, v[2]*size + z] for v in vertices]
    surfaces = [(0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(1,2,6,5),(0,3,7,4)]
    edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
    
    glBegin(GL_QUADS)
    glColor3f(r, g, b)
    for surface in surfaces:
        for vertex in surface:
            glVertex3fv(vertices[vertex])
    glEnd()
    
    glColor3f(0,0,0)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def draw_chicken_3d(x, y, z, scale=1.0, type="white"):
    if type == "white":
        body_color = (1,1,1)
    elif type == "black":
        body_color = (0.1,0.1,0.1)
    elif type == "gold":
        body_color = (1,0.84,0)
    
    # Body
    draw_oval(x, y, z, 0.5*scale, 0.6*scale, *body_color)
    draw_sphere(x, y+0.7*scale, z, 0.3*scale, *body_color)  # Fixed: removed extra parameter
    
    # Beak
    draw_sphere(x+0.35*scale, y+0.7*scale, z, 0.1*scale, 1,0.5,0)  # Fixed: removed extra parameter
    
    # Comb
    draw_sphere(x-0.15*scale, y+1.0*scale, z, 0.1*scale, 1,0,0)  # Fixed: removed extra parameter
    draw_sphere(x, y+1.05*scale, z, 0.1*scale, 1,0,0)  # Fixed: removed extra parameter
    draw_sphere(x+0.15*scale, y+1.0*scale, z, 0.1*scale, 1,0,0)  # Fixed: removed extra parameter
    
    # Wings
    draw_sphere(x-0.45*scale, y+0.2*scale, z, 0.25*scale, *body_color)  # Fixed: removed extra parameter
    draw_sphere(x+0.45*scale, y+0.2*scale, z, 0.25*scale, *body_color)  # Fixed: removed extra parameter
    
    # Legs
    draw_cube(x-0.15*scale, y-0.7*scale, z, 0.1*scale, 1,0.7,0)
    draw_cube(x+0.15*scale, y-0.7*scale, z, 0.1*scale, 1,0.7,0)

def generate_chickens(n):
    num_white = int(n*0.6)
    num_gold = int(n*0.4)
    types_list = ["white"]*num_white + ["gold"]*num_gold
    random.shuffle(types_list)
    
    chickens = []
    for idx, t in enumerate(types_list):
        chickens.append({
            'base_x': 0,
            'base_y': -6,
            'target_x': 0,
            'target_y': 0,
            'type': t,
            'angle': 0,
            'arrived': False,
            'drop_delay': idx*0.5,
            'last_drop': time.time(),
            'offset_x': 0,
            'offset_y': 0,
            'rand_phase': random.uniform(0, 2*math.pi),
            'rand_speed_x': random.uniform(0.5,1.5),
            'rand_speed_y': random.uniform(0.5,1.5),
            'rand_amp_x': random.uniform(0.2,0.5),
            'rand_amp_y': random.uniform(0.1,0.3),
            'direction': random.choice([-1,1]),
            'alive': True
        })
    return chickens

def setup_chicken_positions(chickens, n):
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    spacing_x = 12 / (cols - 1) if cols > 1 else 0
    top_y = 4
    bottom_y = 2
    spacing_y = (top_y - bottom_y) / max(rows-1,1)
    
    k = 0
    for r in range(rows):
        for c_idx in range(cols):
            if k >= n:
                break
            chickens[k]['target_x'] = -6 + c_idx*spacing_x + random.uniform(-0.3,0.3)
            chickens[k]['target_y'] = top_y - r*spacing_y + random.uniform(-0.2,0.2)
            k += 1
    return chickens

def update_chicken_movement(chickens, fixed_speed=0.08):
    current_time = time.time()
    for c in chickens:
        if not c['alive']:
            continue
            
        if not c['arrived']:
            if abs(c['base_x'] - c['target_x']) > fixed_speed:
                c['base_x'] += fixed_speed if c['base_x'] < c['target_x'] else -fixed_speed
            else:
                c['base_x'] = c['target_x']

            if abs(c['base_y'] - c['target_y']) > fixed_speed:
                c['base_y'] += fixed_speed if c['base_y'] < c['target_y'] else -fixed_speed
            else:
                c['base_y'] = c['target_y']

            if c['base_x'] == c['target_x'] and c['base_y'] == c['target_y']:
                c['arrived'] = True
        else:
            t = time.time()
            c['offset_x'] = math.sin(t*c['rand_speed_x'] + c['rand_phase']) * c['rand_amp_x']
            c['offset_y'] = math.sin(t*c['rand_speed_y'] + c['rand_phase']) * c['rand_amp_y']

            c['base_x'] += c['direction'] * 0.02
            if c['base_x'] >= 6 or c['base_x'] <= -6:
                c['direction'] *= -1
    return chickens

def draw_chickens(chickens):
    for c in chickens:
        if not c['alive']:
            continue
            
        c['angle'] += 2
        draw_x = c['base_x'] + (c['offset_x'] if c['arrived'] else 0)
        draw_y = c['base_y'] + (c['offset_y'] if c['arrived'] else 0)
        
        glPushMatrix()
        glTranslatef(draw_x, draw_y, 0)
        glRotatef(c['angle'], 0, 1, 0)
        draw_chicken_3d(0, 0, 0, 0.45, c['type'])
        glPopMatrix()

def drop_eggs(chickens, eggs, start_time):
    current_time = time.time()
    for c in chickens:
        if c['alive'] and c['arrived'] and current_time - start_time >= c['drop_delay']:
            # Use individual random offset for each chicken
            if 'egg_offset' not in c:
                c['egg_offset'] = random.uniform(0, 3)  # Random offset between 0-3 seconds
            
            base_interval = { 'white': 5, 'gold': 7}[c['type']]
            drop_interval = base_interval
            
            # Apply the individual offset
            adjusted_time = current_time + c['egg_offset']
            
            if adjusted_time - c['last_drop'] >= drop_interval:
                eggs.append({'x': c['base_x'], 'y': c['base_y'] - 0.7, 'type': c['type']})
                c['last_drop'] = current_time
    return eggs

def draw_eggs(eggs):
    for egg in eggs:
        color = {'white': (1,1,1), 'gold': (1,0.84,0)}[egg['type']]
        draw_oval(egg['x'], egg['y'], 0, 0.1,0.2,*color )  # Changed to sphere

def welcome_screen():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("intro.wav")  
    pygame.mixer.music.play(0) 

    display = (1400, 800)
    screen = pygame.display.set_mode(display)
    pygame.display.set_caption("Chicken Invaders - Welcome")

    try:
        background_image = pygame.image.load(r"background.jpeg")
        background_image = pygame.transform.scale(background_image, display)
    except:
        print("Background image not found. Using black background.")
        background_image = None

    font_title = pygame.font.SysFont("Arial", 70, bold=True)  # Increased font size
    font_option = pygame.font.SysFont("Arial", 35, bold=True)  # Increased font size

    button_width = 300  # Increased button size
    button_height = 70  # Increased button size
    button_spacing = 30
    
    # Center buttons for 1400x800 screen
    start_y = 600  # Adjusted position
    start_button = pygame.Rect((1400 - button_width) // 2, start_y, button_width, button_height)
    quit_button = pygame.Rect((1400 - button_width) // 2, start_y + button_height + button_spacing, button_width, button_height)

    while True:
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill((0, 0, 0))

        title = font_title.render("Chicken Invaders", True, (255, 255, 0))
        screen.blit(title, ((1400 - title.get_width()) // 2, 150))  # Centered title

        mouse_pos = pygame.mouse.get_pos()
        
        start_hover = start_button.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (0, 0, 0), start_button, border_radius=15)
        border_color = (255, 255, 255) if start_hover else (200, 200, 200)
        pygame.draw.rect(screen, border_color, start_button, 3, border_radius=15)
        start_text = font_option.render("START GAME", True, (255, 255, 255))
        screen.blit(start_text, (start_button.x + 60, start_button.y + 20))  # Adjusted text position

        quit_hover = quit_button.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (0, 0, 0), quit_button, border_radius=15)
        border_color = (255, 255, 255) if quit_hover else (200, 200, 200)
        pygame.draw.rect(screen, border_color, quit_button, 3, border_radius=15)
        quit_text = font_option.render("QUIT GAME", True, (255, 255, 255))
        screen.blit(quit_text, (quit_button.x + 70, quit_button.y + 20))  # Adjusted text position

        instruction_font = pygame.font.SysFont("Arial", 24)
        instruction = instruction_font.render("", True, (255, 255, 255))
        screen.blit(instruction, ((1400 - instruction.get_width()) // 2, 500))  # Centered instruction

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(mouse_pos):
                    pygame.mixer.music.stop()
                    return True 
                if quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    quit()

        pygame.display.update()

def game_over_screen(win=False):
    pygame.init()
    display = (1400, 800)  # Updated to new screen size
    screen = pygame.display.set_mode(display)
    
    if win:
        pygame.display.set_caption("Chicken Invaders - You Win!")
        title_text = "YOU WIN!"
        title_color = (0, 255, 0)  # Green for win
    else:
        pygame.display.set_caption("Chicken Invaders - Game Over")
        title_text = "GAME OVER"
        title_color = (255, 0, 0)  # Red for loss

    try:
        # Use relative path instead of absolute path
        background_image = pygame.image.load("background.jpeg")  # Changed to relative path
        background_image = pygame.transform.scale(background_image, display)
    except:
        print("Background image not found. Using black background.")
        background_image = None

    font_title = pygame.font.SysFont("Arial", 80, bold=True)  # Increased font size
    font_option = pygame.font.SysFont("Arial", 35, bold=True)  # Increased font size
    font_score = pygame.font.SysFont("Arial", 30)  # Increased font size

    button_width = 300  # Increased button size
    button_height = 70  # Increased button size
    button_spacing = 30
    
    # Center buttons for 1400x800 screen
    play_again_button = pygame.Rect((1400 - button_width) // 2, 450, button_width, button_height)
    quit_button = pygame.Rect((1400 - button_width) // 2, 450 + button_height + button_spacing, button_width, button_height)

    while True:
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill((0, 0, 0))

        # Draw title
        title_surface = font_title.render(title_text, True, title_color)
        screen.blit(title_surface, ((1400 - title_surface.get_width()) // 2, 150))

        # Draw score
        score_surface = font_score.render(f"Final Score: {score}", True, (255, 255, 255))
        screen.blit(score_surface, ((1400 - score_surface.get_width()) // 2, 250))

        mouse_pos = pygame.mouse.get_pos()
        
        # Play Again button
        play_again_hover = play_again_button.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (0, 100, 0) if play_again_hover else (0, 150, 0), play_again_button, border_radius=15)
        pygame.draw.rect(screen, (255, 255, 255), play_again_button, 3, border_radius=15)
        play_again_text = font_option.render("PLAY AGAIN", True, (255, 255, 255))
        screen.blit(play_again_text, (play_again_button.x + 60, play_again_button.y + 20))

        # Quit button
        quit_hover = quit_button.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (100, 0, 0) if quit_hover else (150, 0, 0), quit_button, border_radius=15)
        pygame.draw.rect(screen, (255, 255, 255), quit_button, 3, border_radius=15)
        quit_text = font_option.render("QUIT GAME", True, (255, 255, 255))
        screen.blit(quit_text, (quit_button.x + 70, quit_button.y + 20))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_button.collidepoint(mouse_pos):
                    return True  # Play again
                if quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    quit()

        pygame.display.update()


# Saleh functions
def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    
    light_pos = [2.0,4.0,2.0,1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    
    ambient = [0.3,0.3,0.3,1.0]
    diffuse = [0.8,0.8,0.8,1.0]
    specular = [1.0,1.0,1.0,1.0]
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular)
    
    glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
    glMateriali(GL_FRONT, GL_SHININESS, 64)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

def draw_player(speed, height, radius, x, y, z, angle_rocket):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(angle_rocket, 0, 1, 0)
    glColor3f(0, 0, 1)
    quadric = gluNewQuadric()
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)   
    gluCylinder(quadric, radius, radius, height, 20, 20)
    glPopMatrix()
    glColor3f(0, 0, 1)
    quadric = gluNewQuadric()
    glPushMatrix()
    glTranslatef(0, height, 0)   
    gluSphere(quadric, radius, 20, 20)
    glPopMatrix()
    glPushMatrix()
    window_radius = radius * 0.6     
    window_y = height * 0.5           
    glTranslatef(0, window_y, radius + 0.001) 
    glRotatef(0, 0, 0, 1) 
    glColor3f(1, 1, 1) 
    quad2 = gluNewQuadric()
    gluDisk(quad2, 0.0, window_radius, 32, 1)
    glPopMatrix()
    wing_y = height * 0.5
    wing_out = radius * 2.0
    wing_up = radius * 1.2   
    glPushMatrix()
    glColor3f(1, 0, 0)
    glTranslatef(0, wing_y, 0)
    glBegin(GL_TRIANGLES)
    glVertex3f(radius, -0.2, 0)    
    glVertex3f(radius,  0.2, 0)   
    glVertex3f(radius + wing_out/2, 0, 0)
    glEnd()
    glPopMatrix()
    glPushMatrix()
    glColor3f(1, 0, 0)
    glTranslatef(0, wing_y, 0)
    glBegin(GL_TRIANGLES)
    glVertex3f(-radius, -0.2, 0)    
    glVertex3f(-radius,  0.2, 0)  
    glVertex3f(-(radius + wing_out/2), 0, 0)
    glEnd()
    glPopMatrix()
    glPopMatrix()

def draw_bullet(bullet):
    glColor3f(1, 1, 0)
    glBegin(GL_QUADS)
    glVertex3f(bullet["x"] - bullet_width/2, bullet["y"] - bullet_height/2, 0)
    glVertex3f(bullet["x"] + bullet_width/2, bullet["y"] - bullet_height/2, 0)
    glVertex3f(bullet["x"] + bullet_width/2, bullet["y"] + bullet_height/2, 0)
    glVertex3f(bullet["x"] - bullet_width/2, bullet["y"] + bullet_height/2, 0)
    glEnd()

def handle_player_input(can_shoot, bullets):
    keys = pygame.key.get_pressed()
    
    # Movement
    global player_x
    if keys[pygame.K_LEFT]: 
        player_x -= player_speed
    if keys[pygame.K_RIGHT]: 
        player_x += player_speed
    player_x = max(min(player_x, 7), -7)

    # Shooting
    if keys[pygame.K_SPACE] and can_shoot:
        # create bullets according to current power level and add them
        new_bullets = create_power_bullets(player_x, player_y + player_height/2)
        for b in new_bullets:
            bullets.append(b)
            shoot_sound.play()
        can_shoot = False
    
    return can_shoot, bullets

def update_bullets(bullets):
    for bullet in bullets: 
        bullet["y"] += bullet_speed
    bullets = [b for b in bullets if b["y"] < 6]
    return bullets

def draw_bullets(bullets):
    for bullet in bullets: 
        draw_bullet(bullet)

def collect_gold_egg():
    """Increase power level when collecting a golden egg"""
    global power_level
    if power_level < 3:
        power_level += 1

def create_power_bullets(player_x, player_y):
    """Create 1, 2 or 3 bullets depending on power_level"""
    bullets = []

    if power_level == 1:
        bullets.append({"x": player_x, "y": player_y})

    elif power_level == 2:
        bullets.append({"x": player_x - 0.2, "y": player_y})
        bullets.append({"x": player_x + 0.2, "y": player_y})

    elif power_level == 3:
        bullets.append({"x": player_x,       "y": player_y})
        bullets.append({"x": player_x - 0.25, "y": player_y})
        bullets.append({"x": player_x + 0.25, "y": player_y})

    return bullets

# Jojo functions 

def draw_score(score_value):
    glPushAttrib(GL_LIGHTING_BIT)
    glDisable(GL_LIGHTING)
    glColor3f(1, 1, 0)            
    glRasterPos3f(-9, 5, 0)  
    for ch in f"Score: {score_value}":
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))
    glPopAttrib()

def draw_hearts(lives):
    rotation_angle = pygame.time.get_ticks() * 0.05
    total_hearts = min(max_lives, lives)
    
    for i in range(total_hearts):
        x = 7 - i * 1.0 
        glPushMatrix()
        glTranslatef(x, 5.2, 0)
        glRotatef(rotation_angle, 0, 1, 0)
        glScalef(0.8, 0.8, 0.8)
        glColor3f(1, 0, 0)
        
        # Simple heart shape - triangle + two circles
        glBegin(GL_TRIANGLES)
        glVertex3f(0, -0.5, 0)
        glVertex3f(0.3, 0, 0)
        glVertex3f(-0.3, 0, 0)
        glEnd()
        
        # Left circle
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(-0.15, 0, 0)
        for angle in range(0, 181, 20):  # Reduced resolution
            rad = 0.15
            glVertex3f(-0.15 + rad * math.cos(math.radians(angle)), 
                       rad * math.sin(math.radians(angle)), 0)
        glEnd()
        
        # Right circle
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0.15, 0, 0)
        for angle in range(0, 181, 20):  # Reduced resolution
            rad = 0.15
            glVertex3f(0.15 + rad * math.cos(math.radians(angle)), 
                       rad * math.sin(math.radians(angle)), 0)
        glEnd()
        
        glPopMatrix()

def update_eggs(eggs, current_lives, current_power):
    eggs_to_remove = []
    new_lives = current_lives
    new_power = current_power
    
    for egg in eggs:
        egg['y'] -= 0.1
        
        # Simple collision check
        if (abs(egg['x'] - player_x) < 0.6 and 
            abs(egg['y'] - player_y) < 0.3):
            
            if egg["type"] == "white":
                if new_lives > 0:
                    new_lives -= 1
                    new_power = 1
                if 'whiteegg_sound' in globals():
                    whiteegg_sound.play()
            else:  # gold egg
                if new_power < 3:
                    new_power += 1
                if 'goldegg_sound' in globals():
                    goldegg_sound.play()
            eggs_to_remove.append(egg)
    
    new_eggs = [egg for egg in eggs if egg not in eggs_to_remove]
    return new_eggs, new_lives, new_power

def check_bullet_chicken_collisions(bullets, chickens):
    new_bullets = []
    
    for bullet in bullets:
        hit = False
        for chicken in chickens:
            if chicken['alive']:
                # Simple distance-based collision
                actual_x = chicken['base_x'] + (chicken['offset_x'] if chicken['arrived'] else 0)
                actual_y = chicken['base_y'] + (chicken['offset_y'] if chicken['arrived'] else 0)
                
                if (abs(bullet["x"] - actual_x) < 0.4 and 
                    abs(bullet["y"] - actual_y) < 0.4):
                    chicken['alive'] = False
                    if 'kill_sound' in globals():
                        kill_sound.play()
                    # Add score
                    global score
                    score += 20 if chicken['type'] == "gold" else 10
                    hit = True
                    break
        
        if not hit:
            new_bullets.append(bullet)
    
    return new_bullets, chickens

def update_last_chicken_time(chickens, last_chicken_time):
    if last_chicken_time is None:
        # Check if all chickens are dead
        all_dead = True
        for chicken in chickens:
            if chicken['alive']:
                all_dead = False
                break
        
        if all_dead:
            last_chicken_time = pygame.time.get_ticks()
            if 'kill_sound' in globals():
                kill_sound.play()
    
    return last_chicken_time

def check_game_state(last_chicken_time):
    # Check win condition
    if last_chicken_time and pygame.time.get_ticks() - last_chicken_time >= 1000:
        return handle_game_end(True)
    
    # Check lose condition  
    if lives <= 0:
        return handle_game_end(False)
    
    return None

def handle_game_end(is_win):
    pygame.mixer.music.stop()
    
    try:
        if is_win and 'win_sound' in globals():
            win_sound.play()
        elif not is_win and 'gameover_sound' in globals():
            gameover_sound.play()
    except:
        pass
    
    play_again = game_over_screen(win=is_win)
    
    # Restart menu music
    try:
        pygame.mixer.music.load("intro.wav")
        pygame.mixer.music.play(0)
    except:
        pass
    
    return play_again

def initialize_game():
    pygame.init()
    display = (1400, 800)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, display[0] / display[1], 0.1, 50.0)
    glTranslatef(0, 0, -15)
    setup_lighting()
    return pygame.time.Clock()

def main():
    global player_x, lives, score, angle_rocket, power_level
    global shoot_sound, whiteegg_sound, goldegg_sound, kill_sound, gameover_sound, win_sound
    # Add these global variables for explosion
    global ship_destroyed, ship_respawn_timer, ship_explosion_particles

    while True: 
        # Omar - welcome screen
        welcome_screen()
        
        # Reset game variables
        player_x = 0
        lives = 3
        score = 0
        power_level = 1
        # Add explosion reset variables
        ship_destroyed = False
        ship_respawn_timer = 0
        ship_explosion_particles = []

        # Load sounds / Jojo
        try:
            shoot_sound = pygame.mixer.Sound("shoot.wav")
            whiteegg_sound = pygame.mixer.Sound("boom.wav")
            win_sound = pygame.mixer.Sound("win.wav")
            goldegg_sound = pygame.mixer.Sound("gold.wav")
            kill_sound = pygame.mixer.Sound("kill.wav")
            gameover_sound = pygame.mixer.Sound("gameover.wav")
        except:
            print("Some sound files not found. Game will continue without sounds.")

        # Play background music with lower volume
        try:
            pygame.mixer.music.load("song.wav")
            pygame.mixer.music.play(-1)  
            print("Background music started at lower volume")
        except:
            print("Background music file 'song.wav' not found. Game will continue without background music.")

        # Initialize game after welcome screen
        clock = initialize_game()
        can_shoot = True
        last_chicken_time = None
        bullets = []
        eggs = []
        start_time = time.time()
        last_speed_increase = time.time()
        
        # Omar: Initialize chickens
        n = 15
        chickens = generate_chickens(n)
        chickens = setup_chicken_positions(chickens, n)
        
        game_running = True
        while game_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                    can_shoot = True

            # MODIFIED: Check if ship should respawn and update explosion
            if ship_destroyed:
                update_ship_explosion()
                if check_ship_respawn():
                    print("Ship respawned!")
            else:
                # Saleh: Handle player input and update bullets (only if ship is not destroyed)
                can_shoot, bullets = handle_player_input(can_shoot, bullets)
                bullets = update_bullets(bullets)
            
            # Clear screen
            glClearColor(0.2, 0.6, 1.0, 1)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            # Jojo
            eggs, lives, power_level = update_eggs(eggs, lives, power_level)
            bullets, chickens = check_bullet_chicken_collisions(bullets, chickens)
            last_chicken_time = update_last_chicken_time(chickens, last_chicken_time)
            
            result = check_game_state(last_chicken_time)
            if result is not None:
                if result: 
                    pygame.mixer.music.stop()  
                    game_running = False
                    break
                else:      
                    pygame.mixer.music.stop()  
                    pygame.quit()
                    quit()
            
            # MODIFIED: Draw player only if not destroyed, otherwise draw explosion
            if not ship_destroyed:
                draw_player(player_speed, player_height, player_radius, player_x, player_y, player_z, angle_rocket)               
                angle_rocket += 1
            else:
                # Draw explosion instead of ship
                draw_ship_explosion()
            
            draw_bullets(bullets)         

            # Jojo 
            draw_hearts(lives)     
            draw_score(score)             

            # Omar
            draw_eggs(eggs)          
            chickens = update_chicken_movement(chickens)
            draw_chickens(chickens)
            eggs = drop_eggs(chickens, eggs, start_time)
            last_speed_increase = increase_chicken_speed(chickens, last_speed_increase, interval=10, speed_increment=0.03)
            
            pygame.display.flip()
            clock.tick(60)
        
        print("Restarting game...")

if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    main()