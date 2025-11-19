import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
import random
import time
import math

def increase_chicken_speed(chicken_speed, last_time, interval, amount):
    current = time.time()
    if current - last_time >= interval:
        chicken_speed += amount
        last_time = current
    return chicken_speed, last_time

def draw_sphere(x,y,z,radius,r,g,b):
    glColor3f(r,g,b)
    quadric = gluNewQuadric()
    glPushMatrix()
    glTranslatef(x,y,z)
    gluSphere(quadric,radius,32,32)
    glPopMatrix()

def draw_cube(x,y,z,size,r,g,b):
    vertices = [
        [1,1,-1],[1,-1,-1],[-1,-1,-1],[-1,1,-1],
        [1,1,1],[1,-1,1],[-1,-1,1],[-1,1,1]
    ]
    vertices = [[v[0]*size + x, v[1]*size + y, v[2]*size + z] for v in vertices]
    surfaces = [(0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(1,2,6,5),(0,3,7,4)]
    edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
    glBegin(GL_QUADS)
    glColor3f(r,g,b)
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

def draw_chicken_3d(x,y,z,scale=1.0,type="white"):
    if type=="white":
        body_color=(1,1,1)
    elif type=="black":
        body_color=(0.1,0.1,0.1)
    elif type=="gold":
        body_color=(1,0.84,0)
    draw_sphere(x,y,z,0.5*scale,*body_color)
    draw_sphere(x,y+0.7*scale,z,0.3*scale,*body_color)
    draw_sphere(x+0.35*scale,y+0.7*scale,z,0.1*scale,1,0.5,0)
    draw_sphere(x-0.15*scale,y+1.0*scale,z,0.1*scale,1,0,0)
    draw_sphere(x,y+1.05*scale,z,0.1*scale,1,0,0)
    draw_sphere(x+0.15*scale,y+1.0*scale,z,0.1*scale,1,0,0)
    draw_sphere(x-0.45*scale,y+0.2*scale,z,0.25*scale,*body_color)
    draw_sphere(x+0.45*scale,y+0.2*scale,z,0.25*scale,*body_color)
    draw_cube(x-0.15*scale,y-0.7*scale,z,0.1*scale,1,0.7,0)
    draw_cube(x+0.15*scale,y-0.7*scale,z,0.1*scale,1,0.7,0)

def generate_chickens(n):
    num_black=int(n*0.6)
    num_white=int(n*0.3)
    num_gold=n-num_black-num_white
    types_list=["black"]*num_black + ["white"]*num_white + ["gold"]*num_gold
    random.shuffle(types_list)
    chickens=[]
    for idx,t in enumerate(types_list):
        chickens.append({
            'base_x':0,
            'base_y':-6,
            'target_x':0,
            'target_y':3,
            'type':t,
            'angle':0,
            'arrived':False,
            'drop_delay':idx*0.5,
            'last_drop':time.time(),
            'offset_x':0,
            'offset_y':0,
            'rand_phase':random.uniform(0, 2*math.pi),
            'rand_speed_x':random.uniform(0.5,1.5),
            'rand_speed_y':random.uniform(0.5,1.5),
            'rand_amp_x':random.uniform(0.2,0.5),
            'rand_amp_y':random.uniform(0.1,0.3),
            'direction': random.choice([-1,1])
        })
    return chickens

def draw_eggs(eggs):
    for egg in eggs[:]:
        egg['y'] -= 0.1
        if egg['y'] < -6:
            eggs.remove(egg)
        else:
            color={'black':(0,0,0),'white':(1,1,1),'gold':(1,0.84,0)}[egg['type']]
            draw_sphere(egg['x'],egg['y'],0,0.15,*color)

def main():
    pg.init()
    display=(800,600)
    pg.display.set_mode(display, DOUBLEBUF|OPENGL)
    gluPerspective(45, display[0]/display[1], 0.1, 50.0)
    glTranslatef(0,0,-20)

    n=25
    chickens=generate_chickens(n)
    eggs=[]
    start_time=time.time()
    fixed_speed = 0.1

    chicken_speed = 0.05
    interval = 10
    amount = 0.02
    last_time = time.time()

    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    spacing_x = 16 / (cols - 1)
    top_y = 5
    bottom_y = 2
    spacing_y = (top_y - bottom_y) / max(rows-1,1)
    k = 0
    for r in range(rows):
        for c_idx in range(cols):
            if k >= n:
                break
            chickens[k]['target_x'] = -8 + c_idx*spacing_x + random.uniform(-0.3,0.3)
            chickens[k]['target_y'] = top_y - r*spacing_y + random.uniform(-0.2,0.2)
            k += 1

    while True:
        for event in pg.event.get():
            if event.type==pg.QUIT:
                pg.quit()
                return

        glClearColor(0.5,0.5,0.5,1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        current_time=time.time()

        chicken_speed, last_time = increase_chicken_speed(
            chicken_speed, last_time, interval, amount
        )

        for c in chickens:
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
                c['base_x'] += c['direction'] * chicken_speed
                if c['base_x'] >= 8 or c['base_x'] <= -8:
                    c['direction'] *= -1

        for c in chickens:
            c['angle'] += 2
            draw_x = c['base_x'] + (c['offset_x'] if c['arrived'] else 0)
            draw_y = c['base_y'] + (c['offset_y'] if c['arrived'] else 0)
            glPushMatrix()
            glTranslatef(draw_x, draw_y,0)
            glRotatef(c['angle'],0,1,0)
            draw_chicken_3d(0,0,0,0.5,c['type'])
            glPopMatrix()

            if c['arrived'] and current_time-start_time >= c['drop_delay']:
                drop_interval={'black':6,'white':5,'gold':7}[c['type']]
                if current_time-c['last_drop'] >= drop_interval:
                    eggs.append({'x':c['base_x'],'y':c['base_y']-0.7,'type':c['type']})
                    c['last_drop']=current_time

        draw_eggs(eggs)
        pg.display.flip()
        pg.time.wait(10)

main()
