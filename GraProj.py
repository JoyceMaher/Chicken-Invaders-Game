import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
import math
import random
import time

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
            'x':0,
            'y':-6,
            'target_y':3,   # vertical target before splitting
            'type':t,
            'angle':0,
            'curve_done':False,
            'drop_delay':idx*0.5, # staggered drop delay
            'last_drop':time.time()
        })
    return chickens

def main():
    pg.init()
    display=(800,600)
    pg.display.set_mode(display, DOUBLEBUF|OPENGL)
    gluPerspective(45, display[0]/display[1], 0.1, 50.0)
    glTranslatef(0,0,-20)

    n=20
    chickens=generate_chickens(n)
    eggs=[]
    move_speed=0.08
    split_done=False
    start_time=time.time()

    while True:
        for event in pg.event.get():
            if event.type==pg.QUIT:
                pg.quit()
                return

        glClearColor(0.5,0.5,0.5,1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        current_time=time.time()

        # Vertical movement first
        if not split_done:
            for c in chickens:
                if c['y'] < c['target_y']:
                    c['y'] += move_speed
                else:
                    c['curve_done']=True

            if all(c['curve_done'] for c in chickens):
                split_done=True
                start_x=-8
                end_x=8
                row1=chickens[:n//2]
                row2=chickens[n//2:]
                spacing1=(end_x-start_x)/max(len(row1)-1,1)
                spacing2=(end_x-start_x)/max(len(row2)-1,1)
                for j,c in enumerate(row1):
                    c['x']=start_x+j*spacing1
                    c['y']=3.5
                for j,c in enumerate(row2):
                    c['x']=start_x+j*spacing2
                    c['y']=2.5

        # Draw and rotate chickens
        for c in chickens:
            c['angle']+=2
            glPushMatrix()
            glTranslatef(c['x'],c['y'],0)
            glRotatef(c['angle'],0,1,0)
            draw_chicken_3d(0,0,0,0.5,c['type'])
            glPopMatrix()

            # Drop eggs only after split and staggered
            if split_done and current_time-start_time>=c['drop_delay']:
                drop_interval={'black':4,'white':3,'gold':5}[c['type']]
                if current_time-c['last_drop']>=drop_interval:
                    eggs.append({'x':c['x'],'y':c['y']-0.7,'type':c['type']})
                    c['last_drop']=current_time

        # Update eggs
        for egg in eggs[:]:
            egg['y']-=0.1
            if egg['y']<-6:
                eggs.remove(egg)
            else:
                color={'black':(0,0,0),'white':(1,1,1),'gold':(1,0.84,0)}[egg['type']]
                draw_sphere(egg['x'],egg['y'],0,0.15,*color)

        pg.display.flip()
        pg.time.wait(10)

main()
