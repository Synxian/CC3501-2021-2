# coding=utf-8
"""Tarea 3 car"""

import glfw
from OpenGL.GL import *
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.scene_graph as sg
import grafica.easy_shaders as es
import grafica.lighting_shaders as ls
import grafica.performance_monitor as pm
from grafica.assets_path import getAssetPath
from operator import add


__author__ = "Felix Melo"
__license__ = "MIT"

class Car():

    def __init__(self):
        #creamos los parametros posición, theta (angulo actual del auto), speed (la velocidad del auto), acceleration (la aceleración del auto)
        self.position = np.array([2,-0.037409,5])
        #ángulo al que apunta
        self.theta = 0
        #la velocidad del auto
        self.speed = 0
        #la aceleración dl aauto
        self.acceleration = 0.0007
        #velocidad máxima del auto
        self.maxSpeed= 0.1

    #función que maneja el movimiento del auto, si no está moviendose en ninguna dirección entonces no es posible moverse hacia los lados
    def move(self, window):
        #se define el movimiento al ir hacia adelante
        if (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS):
            self.speed = min(self.acceleration+self.speed, self.maxSpeed)

            #movimientos laterales
            if (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS):
                self.theta += 1.5*self.speed/3

            elif (glfw.get_key(window, glfw.KEY_D) == glfw.PRESS):
                self.theta -= 1.5*self.speed/3
        elif self.speed>0:
            self.speed = max(self.speed-self.acceleration, 0)
            #movimientos laterales
            if (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS):
                self.theta += 1.5*self.speed/3

            elif (glfw.get_key(window, glfw.KEY_D) == glfw.PRESS):
                self.theta -= 1.5*self.speed/3

        #se define el movimiento al ir hacia atras
        if (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS):
            self.speed = max(self.speed-self.acceleration, -(self.maxSpeed))

            #movimientos laterales
            if (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS):
                self.theta -= 1.5*self.speed/3

            elif (glfw.get_key(window, glfw.KEY_D) == glfw.PRESS):
                self.theta += 1.5*self.speed/3
        elif self.speed<0:
            self.speed = min(self.speed+self.acceleration, 0)
            #movimientos laterales
            if (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS):
                self.theta += 1.5*self.speed/3

            elif (glfw.get_key(window, glfw.KEY_D) == glfw.PRESS):
                self.theta -= 1.5*self.speed/3
        self.position[0] -= self.speed*np.sin(self.theta)
        self.position[2] -= self.speed*np.cos(self.theta)

