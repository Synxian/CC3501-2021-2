# coding=utf-8
"""Tarea 3"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
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
import objects
from playsound import *

__author__ = "Felix Melo"
__license__ = "MIT"

# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True
        self.viewPos = np.array([12,12,12])
        self.at = np.array([0,0,0])
        self.camUp = np.array([0, 1, 0])
        self.distance = 20
        self.follow=False


controller = Controller()

def setPlot(texPipeline, axisPipeline, lightPipeline):
    projection = tr.perspective(45, float(width)/float(height), 0.1, 100)

    glUseProgram(axisPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(axisPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

    glUseProgram(texPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

    glUseProgram(lightPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(lightPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
    
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "lightPosition"), 5, 5, 5)
    
    glUniform1ui(glGetUniformLocation(lightPipeline.shaderProgram, "shininess"), 1000)
    glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, "constantAttenuation"), 0.1)
    glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, "linearAttenuation"), 0.1)
    glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

def setView(texPipeline, axisPipeline, lightPipeline):
    view = tr.lookAt(
            controller.viewPos,
            controller.at,
            controller.camUp
        )

    glUseProgram(axisPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(axisPipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    glUseProgram(texPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    glUseProgram(lightPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(lightPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "viewPosition"), controller.viewPos[0], controller.viewPos[1], controller.viewPos[2])
    

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_LEFT_CONTROL:
        controller.showAxis = not controller.showAxis

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)
    
    elif key == glfw.KEY_1:
        controller.viewPos = np.array([controller.distance,controller.distance,controller.distance]) #Vista diagonal 1
        controller.camUp = np.array([0,1,0])
    
    elif key == glfw.KEY_2:
        controller.viewPos = np.array([0,0,controller.distance]) #Vista frontal
        controller.camUp = np.array([0,1,0])

    elif key == glfw.KEY_3:
        controller.viewPos = np.array([controller.distance,0,controller.distance]) #Vista lateral
        controller.camUp = np.array([0,1,0])

    elif key == glfw.KEY_4:
        controller.viewPos = np.array([0,controller.distance,0]) #Vista superior
        controller.camUp = np.array([1,0,0])
    
    elif key == glfw.KEY_5:
        controller.viewPos = np.array([controller.distance,controller.distance,-controller.distance]) #Vista diagonal 2
        controller.camUp = np.array([0,1,0])
    
    elif key == glfw.KEY_6:
        controller.viewPos = np.array([-controller.distance,controller.distance,-controller.distance]) #Vista diagonal 2
        controller.camUp = np.array([0,1,0])
    
    elif key == glfw.KEY_7:
        controller.viewPos = np.array([-controller.distance,controller.distance,controller.distance]) #Vista diagonal 2
        controller.camUp = np.array([0,1,0])
    
    elif key == glfw.KEY_8:
        controller.follow=not controller.follow

    else:
        print('Unknown key')

def createOFFShape(pipeline, filename, r,g, b):
    shape = readOFF(getAssetPath(filename), (r, g, b))
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)

    return gpuShape

def readOFF(filename, color):
    vertices = []
    normals= []
    faces = []

    with open(filename, 'r') as file:
        line = file.readline().strip()
        assert line=="OFF"

        line = file.readline().strip()
        aux = line.split(' ')

        numVertices = int(aux[0])
        numFaces = int(aux[1])

        for i in range(numVertices):
            aux = file.readline().strip().split(' ')
            vertices += [float(coord) for coord in aux[0:]]
        
        vertices = np.asarray(vertices)
        vertices = np.reshape(vertices, (numVertices, 3))
        print(f'Vertices shape: {vertices.shape}')

        normals = np.zeros((numVertices,3), dtype=np.float32)
        print(f'Normals shape: {normals.shape}')

        for i in range(numFaces):
            aux = file.readline().strip().split(' ')
            aux = [int(index) for index in aux[0:]]
            faces += [aux[1:]]
            
            vecA = [vertices[aux[2]][0] - vertices[aux[1]][0], vertices[aux[2]][1] - vertices[aux[1]][1], vertices[aux[2]][2] - vertices[aux[1]][2]]
            vecB = [vertices[aux[3]][0] - vertices[aux[2]][0], vertices[aux[3]][1] - vertices[aux[2]][1], vertices[aux[3]][2] - vertices[aux[2]][2]]

            res = np.cross(vecA, vecB)
            normals[aux[1]][0] += res[0]  
            normals[aux[1]][1] += res[1]  
            normals[aux[1]][2] += res[2]  

            normals[aux[2]][0] += res[0]  
            normals[aux[2]][1] += res[1]  
            normals[aux[2]][2] += res[2]  

            normals[aux[3]][0] += res[0]  
            normals[aux[3]][1] += res[1]  
            normals[aux[3]][2] += res[2]  
        #print(faces)
        norms = np.linalg.norm(normals,axis=1)
        normals = normals/norms[:,None]

        color = np.asarray(color)
        color = np.tile(color, (numVertices, 1))

        vertexData = np.concatenate((vertices, color), axis=1)
        vertexData = np.concatenate((vertexData, normals), axis=1)

        print(vertexData.shape)

        indices = []
        vertexDataF = []
        index = 0

        for face in faces:
            vertex = vertexData[face[0],:]
            vertexDataF += vertex.tolist()
            vertex = vertexData[face[1],:]
            vertexDataF += vertex.tolist()
            vertex = vertexData[face[2],:]
            vertexDataF += vertex.tolist()
            
            indices += [index, index + 1, index + 2]
            index += 3        



        return bs.Shape(vertexDataF, indices)

def createGPUShape(pipeline, shape):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)

    return gpuShape

def createTexturedArc(d):
    vertices = [d, 0.0, 0.0, 0.0, 0.0,
                d+1.0, 0.0, 0.0, 1.0, 0.0]
    
    currentIndex1 = 0
    currentIndex2 = 1

    indices = []

    cont = 1
    cont2 = 1

    for angle in range(4, 185, 5):
        angle = np.radians(angle)
        rot = tr.rotationY(angle)
        p1 = rot.dot(np.array([[d],[0],[0],[1]]))
        p2 = rot.dot(np.array([[d+1],[0],[0],[1]]))

        p1 = np.squeeze(p1)
        p2 = np.squeeze(p2)
        
        vertices.extend([p2[0], p2[1], p2[2], 1.0, cont/4])
        vertices.extend([p1[0], p1[1], p1[2], 0.0, cont/4])
        
        indices.extend([currentIndex1, currentIndex2, currentIndex2+1])
        indices.extend([currentIndex2+1, currentIndex2+2, currentIndex1])

        if cont > 4:
            cont = 0


        vertices.extend([p1[0], p1[1], p1[2], 0.0, cont/4])
        vertices.extend([p2[0], p2[1], p2[2], 1.0, cont/4])

        currentIndex1 = currentIndex1 + 4
        currentIndex2 = currentIndex2 + 4
        cont2 = cont2 + 1
        cont = cont + 1

    return bs.Shape(vertices, indices)

def createTiledFloor(dim):
    vert = np.array([[-0.5,0.5,0.5,-0.5],[-0.5,-0.5,0.5,0.5],[0.0,0.0,0.0,0.0],[1.0,1.0,1.0,1.0]], np.float32)
    rot = tr.rotationX(-np.pi/2)
    vert = rot.dot(vert)

    indices = [
         0, 1, 2,
         2, 3, 0]

    vertFinal = []
    indexFinal = []
    cont = 0

    for i in range(-dim,dim,1):
        for j in range(-dim,dim,1):
            tra = tr.translate(i,0.0,j)
            newVert = tra.dot(vert)

            v = newVert[:,0][:-1]
            vertFinal.extend([v[0], v[1], v[2], 0, 1])
            v = newVert[:,1][:-1]
            vertFinal.extend([v[0], v[1], v[2], 1, 1])
            v = newVert[:,2][:-1]
            vertFinal.extend([v[0], v[1], v[2], 1, 0])
            v = newVert[:,3][:-1]
            vertFinal.extend([v[0], v[1], v[2], 0, 0])
            
            ind = [elem + cont for elem in indices]
            indexFinal.extend(ind)
            cont = cont + 4

    return bs.Shape(vertFinal, indexFinal)

#Extra: Crea un triangulo con textura, utilizado para las partes laterales del techo
def createTextureTriangle(nx, ny):

    # Defining locations and texture coordinates for each vertex of the shape    
    vertices = [
    #   positions        texture
        -0.5, -0.5, 0.0,  0, ny,
         0.5, -0.5, 0.0, nx, ny,
         0.5,  0.5, 0.0,  nx, 0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices= [0,1,2]

    return bs.Shape(vertices, indices)


# TAREA3: Implementa la función "createHouse" que crea un objeto que representa una casa
# y devuelve un nodo de un grafo de escena (un objeto sg.SceneGraphNode) que representa toda la geometría y las texturas
# Esta función recibe como parámetro el pipeline que se usa para las texturas (texPipeline) y un entero, que determina que textura se utilizará

def createHouse(pipeline, i):
    #eligiendo el techo:
    if i==1:
        k=3
    elif i==2:
        k=5
    elif i==3 :
        k=4
    elif i==4:
        k=2
    elif i==5:
        k=1

    #instanciamos un muro con la textura
    singleWall = createGPUShape(pipeline, bs.createTextureQuad(1.0, 1.0))
    singleWall.texture =es.textureSimpleSetup(
        getAssetPath("wall"+str(i)+".jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR_MIPMAP_LINEAR, GL_NEAREST)
    glGenerateMipmap(GL_TEXTURE_2D)

    #triangleTest
    singlTriangle = createGPUShape(pipeline, createTextureTriangle(1.0, 1.0))
    singlTriangle.texture =es.textureSimpleSetup(
        getAssetPath("roof"+str(k)+".jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR_MIPMAP_LINEAR, GL_NEAREST)
    glGenerateMipmap(GL_TEXTURE_2D)

    #instanciando un cuadrado con el techo
    singleRoof= createGPUShape(pipeline, bs.createTextureQuad(1.0, 1.0))
    singleRoof.texture =es.textureSimpleSetup(
        getAssetPath("roof"+str(k)+".jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR_MIPMAP_LINEAR, GL_NEAREST)
    glGenerateMipmap(GL_TEXTURE_2D)

    #instanciamos una puerta
    j=np.random.randint(3)
    j=j+1
    singleDoor= createGPUShape(pipeline, bs.createTextureQuad(1.0, 1.0))
    singleDoor.texture =es.textureSimpleSetup(
        getAssetPath("door"+str(j)+".jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR_MIPMAP_LINEAR, GL_NEAREST)
    glGenerateMipmap(GL_TEXTURE_2D)

    #instanciamos una ventana
    singleWindow = createGPUShape(pipeline, bs.createTextureQuad(1.0, 1.0))
    singleWindow.texture =es.textureSimpleSetup(
        getAssetPath("window2.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR_MIPMAP_LINEAR, GL_NEAREST)
    glGenerateMipmap(GL_TEXTURE_2D)
    #----------------------------------------------------------------------------------#
                                        #Muros
    #----------------------------------------------------------------------------------#
    #aquí se preparan 2 muros, formando un angulo de 90 grados para tener un muro en forma de L
    rotatedWall= sg.SceneGraphNode('rotatedWall')
    rotatedWall.transform=tr.matmul([tr.translate(0.5,0,0.5),tr.rotationY(np.pi/2)])
    rotatedWall.childs+=[singleWall]

    normalWall= sg.SceneGraphNode('normalWall')
    normalWall.childs+=[singleWall]

    lShapeWalls=sg.SceneGraphNode('lShapeWalls')
    lShapeWalls.childs+=[normalWall]
    lShapeWalls.childs+=[rotatedWall]

    #aquí se rota la estructura en forma de L para tener la base de la casa
    rotatedLShape=sg.SceneGraphNode('rotatedLShape')
    rotatedLShape.transform=tr.matmul([tr.translate(0,0,1),tr.rotationY(np.pi)])
    rotatedLShape.childs+=[lShapeWalls]

    #se traslada para que quede instanciada en el origen
    allWalls=sg.SceneGraphNode('allWalls')
    allWalls.transform=tr.matmul([tr.translate(0,0,-0.5)])
    allWalls.childs+=[lShapeWalls, rotatedLShape]

    #se pone la puerta
    doorPlaced=sg.SceneGraphNode('door')
    doorPlaced.transform=tr.matmul([tr.translate(0.21,-0.1,0.51),tr.uniformScale(0.8),tr.scale(0.42/1.5,0.8,1)])
    doorPlaced.childs+=[singleDoor]

    #se pone la ventana
    windowPlaced=sg.SceneGraphNode('window')
    windowPlaced.transform=tr.matmul([tr.translate(-0.25,0.047,0.51),tr.uniformScale(0.8),tr.scale(0.4,0.48,1)])
    windowPlaced.childs+=[singleWindow]
    #----------------------------------------------------------------------------------#
                                        #Techos
    #----------------------------------------------------------------------------------#
    ffRRoof=sg.SceneGraphNode('ffRoof')
    ffRRoof.transform=tr.matmul([tr.translate(0,0.7,-0.30292),tr.rotationX(np.pi/4),tr.scale(1,0.85,1)])
    ffRRoof.childs+=[singleRoof]
    
    ffRRoof2=sg.SceneGraphNode('ffRoof2')
    ffRRoof2.transform=tr.matmul([tr.rotationY(np.pi)])
    ffRRoof2.childs+= [ffRRoof]

    sideRoof=sg.SceneGraphNode('sideRoof')
    sideRoof.transform=tr.matmul([tr.translate(0.45,0.35,0),tr.uniformScale(0.9),tr.rotationY(np.pi/2),tr.rotationZ(np.pi*3/4)])
    sideRoof.childs+=[singlTriangle]

    otherSideRoof=sg.SceneGraphNode('otherSideRoof')
    otherSideRoof.transform=tr.matmul([tr.rotationY(np.pi)])
    otherSideRoof.childs+=[sideRoof]
    
    #------------------------------------------------------------------------------------#
                                        #casa
    #------------------------------------------------------------------------------------#
    houseNode=sg.SceneGraphNode('house')
    houseNode.transform = tr.scale(1.5,1,1)
    houseNode.childs+=[windowPlaced,allWalls,doorPlaced, ffRRoof2,ffRRoof, otherSideRoof, sideRoof]

    
    return houseNode

# TAREA3: Implementa la función "createWall" que crea un objeto que representa un muro
# y devuelve un nodo de un grafo de escena (un objeto sg.SceneGraphNode) que representa toda la geometría y las texturas
# Esta función recibe como parámetro el pipeline que se usa para las texturas (texPipeline)

def createWall(pipeline):
    #instanciamos un muro con la textura
    singleWall = createGPUShape(pipeline, bs.createTextureQuad(1.0, 1.0))
    singleWall.texture =es.textureSimpleSetup(
        getAssetPath("wall3.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR_MIPMAP_LINEAR, GL_NEAREST)
    glGenerateMipmap(GL_TEXTURE_2D)

    #laterales
    normalWall=sg.SceneGraphNode('normalWall')
    normalWall.childs+=[singleWall]

    secondWall=sg.SceneGraphNode('secondWall')
    secondWall.transform=tr.matmul([tr.translate(0,0,0.13)])
    secondWall.childs+=[singleWall]

    #relleno inferior-superior
    upFill=sg.SceneGraphNode('upperFill')
    upFill.transform=tr.matmul([tr.translate(0,0.5,0.13/2),tr.rotationX(np.pi/2),tr.scale(1,0.15,1)])
    upFill.childs+=[singleWall]

    downFill=sg.SceneGraphNode('lowerFill')
    downFill.transform=tr.matmul([tr.translate(0,-1,0)])
    downFill.childs+=[upFill]

    #side fills
    leftFill=sg.SceneGraphNode('leftFill')
    leftFill.transform=tr.matmul([tr.translate(0.5,0,0.13/2),tr.rotationY(np.pi/2),tr.scale(0.15,1,1)])
    leftFill.childs+=[singleWall]

    rightFill=sg.SceneGraphNode('rightFill')
    rightFill.transform=tr.matmul([tr.translate(-1,0,0)])
    rightFill.childs+=[leftFill]


    walls=sg.SceneGraphNode('conWalls')
    walls.transform=tr.matmul([tr.scale(0.7,0.15,1),tr.translate(-0.13/2,0.5,0),tr.rotationY(np.pi/2)])
    walls.childs+=[normalWall,secondWall, upFill, downFill, leftFill, rightFill]

    
    return walls

# Extra: Implementa la función "createBuilding" que crea un objeto que representa un edificio
# y devuelve un nodo de un grafo de escena (un objeto sg.SceneGraphNode) que representa toda la geometría y las texturas
# Esta función recibe como parámetro el pipeline que se usa para las texturas (texPipeline) y un entero, que determina que textura se utilizará
def createBuilding(pipeline, i):
    #instanciamos un muro con la textura
    singleWall = createGPUShape(pipeline, bs.createTextureQuad(1.0, 1.0))
    singleWall.texture =es.textureSimpleSetup(
        getAssetPath("building"+str(i)+".jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR_MIPMAP_LINEAR, GL_NEAREST)
    glGenerateMipmap(GL_TEXTURE_2D)

    #techo
    j=np.random.randint(2)
    j=j+1
    singleRoof= createGPUShape(pipeline, bs.createTextureQuad(1.0, 1.0))
    singleRoof.texture =es.textureSimpleSetup(
        getAssetPath("rooftop"+str(j)+".jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR_MIPMAP_LINEAR, GL_NEAREST)
    glGenerateMipmap(GL_TEXTURE_2D)

    #----------------------------------------------------------------------------------#
                                        #Muros
    #----------------------------------------------------------------------------------#
    #aquí se preparan 2 muros, formando un angulo de 90 grados para tener un muro en forma de L
    rotatedWall= sg.SceneGraphNode('rotatedWall')
    rotatedWall.transform=tr.matmul([tr.translate(0.5,0,0.5),tr.rotationY(np.pi/2)])
    rotatedWall.childs+=[singleWall]

    normalWall= sg.SceneGraphNode('normalWall')
    normalWall.childs+=[singleWall]

    lShapeWalls=sg.SceneGraphNode('lShapeWalls')
    lShapeWalls.childs+=[normalWall]
    lShapeWalls.childs+=[rotatedWall]

    #aquí se rota la estructura en forma de L para tener la base de la casa
    rotatedLShape=sg.SceneGraphNode('rotatedLShape')
    rotatedLShape.transform=tr.matmul([tr.translate(0,0,1),tr.rotationY(np.pi)])
    rotatedLShape.childs+=[lShapeWalls]

    #se traslada para que quede instanciada en el origen
    allWalls=sg.SceneGraphNode('4thwall')
    allWalls.transform=tr.matmul([tr.scale(1,3,1),tr.translate(0,0.5,-0.5)])
    allWalls.childs+=[lShapeWalls, rotatedLShape]

    #------------techo-----------#
    roofTop=sg.SceneGraphNode('roofTop')
    roofTop.transform=tr.matmul([tr.translate(0,3,0),tr.rotationX(np.pi/2)])
    roofTop.childs+=[singleRoof]

    #building
    building=sg.SceneGraphNode('building')
    building.childs+=[allWalls,roofTop]

    return building

# Extra: Implementa la función "createSkyBlock" que crea un objeto que representa un paisaje de fondo (no se pone cara superior para que no sea más costoso, aparte no se apreciaría)
# y devuelve un nodo de un grafo de escena (un objeto sg.SceneGraphNode) que representa toda la geometría y las texturas
# Esta función recibe como parámetro el pipeline que se usa para las texturas (texPipeline) y un entero, que determina que textura se utilizará
def createSkyBlock(pipeline, i):
    skyBlockShape = createGPUShape(pipeline, bs.createTextureQuad(1.0, 1.0))
    skyBlockShape.texture = es.textureSimpleSetup(
        getAssetPath("skyblock"+str(i)+".jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR_MIPMAP_LINEAR, GL_NEAREST)
    glGenerateMipmap(GL_TEXTURE_2D)

    #aquí se preparan 2 planos, formando un angulo de 90 grados para tener un muro en forma de L
    rotatedWall= sg.SceneGraphNode('rotatedSky')
    rotatedWall.transform=tr.matmul([tr.translate(0.5,0,0.5),tr.rotationY(np.pi/2)])
    rotatedWall.childs+=[skyBlockShape]

    normalWall= sg.SceneGraphNode('normalSky')
    normalWall.childs+=[skyBlockShape]

    lShapeWalls=sg.SceneGraphNode('lShapeSky')
    lShapeWalls.childs+=[normalWall]
    lShapeWalls.childs+=[rotatedWall]

    #aquí se rota la estructura en forma de L para tener la base del paisaje
    rotatedLShape=sg.SceneGraphNode('rotatedLShapeSky')
    rotatedLShape.transform=tr.matmul([tr.translate(0,0,1),tr.rotationY(np.pi)])
    rotatedLShape.childs+=[lShapeWalls]

    #se traslada para que quede instanciada en el origen
    Background=sg.SceneGraphNode('SkyAssemble')
    Background.transform=tr.matmul([tr.uniformScale(120), tr.translate(0,0.35,-0.5)])
    Background.childs+=[lShapeWalls, rotatedLShape]

    return Background



# TAREA3: Esta función crea un grafo de escena especial para el auto.
def createCarScene(pipeline):
    chasis = createOFFShape(pipeline, 'alfa2.off', 1.0, 0.0, 0.0)
    wheel = createOFFShape(pipeline, 'wheel.off', 0.0, 0.0, 0.0)

    scale = 2.0
    rotatingWheelNode = sg.SceneGraphNode('rotatingWheel')
    rotatingWheelNode.childs += [wheel]

    chasisNode = sg.SceneGraphNode('chasis')
    chasisNode.transform = tr.uniformScale(scale)
    chasisNode.childs += [chasis]

    wheel1Node = sg.SceneGraphNode('wheel1')
    wheel1Node.transform = tr.matmul([tr.uniformScale(scale),tr.translate(0.056390,0.037409,0.091705)])
    wheel1Node.childs += [rotatingWheelNode]

    wheel2Node = sg.SceneGraphNode('wheel2')
    wheel2Node.transform = tr.matmul([tr.uniformScale(scale),tr.translate(-0.060390,0.037409,-0.091705)])
    wheel2Node.childs += [rotatingWheelNode]

    wheel3Node = sg.SceneGraphNode('wheel3')
    wheel3Node.transform = tr.matmul([tr.uniformScale(scale),tr.translate(-0.056390,0.037409,0.091705)])
    wheel3Node.childs += [rotatingWheelNode]

    wheel4Node = sg.SceneGraphNode('wheel4')
    wheel4Node.transform = tr.matmul([tr.uniformScale(scale),tr.translate(0.066090,0.037409,-0.091705)])
    wheel4Node.childs += [rotatingWheelNode]

    car1 = sg.SceneGraphNode('car1')
    car1.transform = tr.matmul([tr.translate(2.0, -0.037409, 5.0), tr.rotationY(np.pi)])
    car1.childs += [chasisNode]
    car1.childs += [wheel1Node]
    car1.childs += [wheel2Node]
    car1.childs += [wheel3Node]
    car1.childs += [wheel4Node]

    scene = sg.SceneGraphNode('system')
    scene.childs += [car1]

    return scene

# TAREA3: Esta función crea toda la escena estática y texturada de esta aplicación.
# Por ahora ya están implementadas: la pista y el terreno
# En esta función debes incorporar las casas y muros alrededor de la pista

def createStaticScene(pipeline):

    roadBaseShape = createGPUShape(pipeline, bs.createTextureQuad(1.0, 1.0))
    roadBaseShape.texture = es.textureSimpleSetup(
        getAssetPath("Road_001_basecolor.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR_MIPMAP_LINEAR, GL_NEAREST)
    glGenerateMipmap(GL_TEXTURE_2D)

    

    grassBaseShape = createGPUShape(pipeline, createTiledFloor(17))
    grassBaseShape.texture = es.textureSimpleSetup(
        getAssetPath("grass.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR_MIPMAP_LINEAR, GL_NEAREST)
    glGenerateMipmap(GL_TEXTURE_2D)

    sandBaseShape = createGPUShape(pipeline, createTiledFloor(51))
    sandBaseShape.texture = es.textureSimpleSetup(
        getAssetPath("Sand 002_COLOR.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR_MIPMAP_LINEAR, GL_NEAREST)
    glGenerateMipmap(GL_TEXTURE_2D)

    arcShape = createGPUShape(pipeline, createTexturedArc(1.5))
    arcShape.texture = roadBaseShape.texture
    
    roadBaseNode = sg.SceneGraphNode('plane')
    roadBaseNode.transform = tr.rotationX(-np.pi/2)
    roadBaseNode.childs += [roadBaseShape]

    arcNode = sg.SceneGraphNode('arc')
    arcNode.childs += [arcShape]
    #---------------------------------------poner un poco de pasto---------------------------------------------#
    grassCorners=sg.SceneGraphNode('grassCorners')
    j=1
    for i in range (4):
        if i<2:
            gnode= sg.SceneGraphNode('cornerGrass'+str(i))
            gnode.transform = tr.translate((i-j)*(51-17), -0.035, 51-17)
            gnode.childs+=[grassBaseShape]
            j=0
            grassCorners.childs+=[gnode]
        if i>=2:
            gnode = gnode= sg.SceneGraphNode('cornerGrass'+str(i))
            gnode.transform = tr.translate(((i+1)%2-j)*(51-17), -0.035, -(51-17))
            gnode.childs+=[grassBaseShape]
            j=1
            grassCorners.childs+=[gnode]

    grassCenter=sg.SceneGraphNode('grassBetweenCorners')
    j=1
    for i in range(4):
        if i<2:
            gnode= sg.SceneGraphNode('betweenCornerGrass'+str(i))
            gnode.transform = tr.translate((i-j)*(51-17), -0.035, 0)
            gnode.childs+=[grassBaseShape]
            j=0
            grassCenter.childs+=[gnode]
        if i>=2:
            gnode= sg.SceneGraphNode('betweenCornerGrass'+str(i))
            gnode.transform = tr.translate(0, -0.035, ((i+1)%2-j)*(51-17))
            gnode.childs+=[grassBaseShape]
            j=1
            grassCenter.childs+=[gnode]

    field =sg.SceneGraphNode('grassField')
    field.childs+=[grassCorners, grassCenter]
    #--------------------------------------------------------------------------------------------------------------#
    sandNode = sg.SceneGraphNode('sand')
    sandNode.transform = tr.translate(0.0,-0.05,0.0)
    sandNode.childs += [sandBaseShape]

    linearSector = sg.SceneGraphNode('linearSector')
        
    for i in range(10):
        node = sg.SceneGraphNode('road'+str(i)+'_ls')
        node.transform = tr.translate(0.0,0.0,-1.0*i)
        node.childs += [roadBaseNode]

        #-----------------------muros de contención-------------------#
        nodeLeftContWall=sg.SceneGraphNode('leftContWall'+str(i))
        nodeLeftContWall.transform= tr.translate(0.5+(0.13/2)*0.7,0,-1.0*i)
        nodeLeftContWall.childs+=[createWall(pipeline)]

        nodeRightContWall=sg.SceneGraphNode('rightContWall'+str(i))
        nodeRightContWall.transform= tr.translate(-(0.5+(0.13/2)*0.7),0,-1.0*i)
        nodeRightContWall.childs+=[createWall(pipeline)]
        #--------------------------------------------------------------#
        linearSector.childs += [node,nodeLeftContWall, nodeRightContWall]

    linearSectorLeft = sg.SceneGraphNode('lsLeft')
    linearSectorLeft.transform = tr.translate(-2.0, 0.0, 5.0)
    linearSectorLeft.childs += [linearSector]

    linearSectorRight = sg.SceneGraphNode('lsRight')
    linearSectorRight.transform = tr.translate(2.0, 0.0, 5.0)
    linearSectorRight.childs += [linearSector]

    arcTop = sg.SceneGraphNode('arcTop')
    arcTop.transform = tr.translate(0.0,0.0,-4.5)
    arcTop.childs += [arcNode]

    arcBottom = sg.SceneGraphNode('arcBottom')
    arcBottom.transform = tr.matmul([tr.translate(0.0,0.0,5.5), tr.rotationY(np.pi)])
    arcBottom.childs += [arcNode]
    
    #--------------------------Structures Placement------------------------------------------#
                    #casas#
    structures=sg.SceneGraphNode('structures')
    j=1
    for i in range(6):
        k=np.random.randint(5)
        #necesito que parta desde el 1 en vez del 0
        k=k+1 
        if i<3:
            hnode=sg.SceneGraphNode('house'+str(i))
            hnode.transform = tr.matmul([tr.rotationY((i-j)*np.pi/4),tr.uniformScale(0.7), tr.translate(0,0.5,-18)])
            hnode.childs+=[createHouse(pipeline, k)]
        elif i>=3:
            hnode=sg.SceneGraphNode('house'+str(i))
            hnode.transform = tr.matmul([tr.rotationY((i%3-j)*np.pi/4), tr.uniformScale(0.7), tr.translate(0,0.5,18), tr.rotationY(np.pi)])
            hnode.childs+=[createHouse(pipeline, k)]
        structures.childs+=[hnode]
    
                    #edificios
    for i in range(6):
        k=np.random.randint(4)
        #necesito que parta desde el 1 en vez del 0
        k=k+1 
        if i<2:
            bnode=sg.SceneGraphNode('building'+str(i))
            bnode.transform = tr.matmul([tr.rotationY((i-j)*np.pi/6), tr.translate(-16,-0.04,0)])
            bnode.childs+=[createBuilding(pipeline, k)]
            j=0
        elif i==2:
            bnode=sg.SceneGraphNode('building'+str(i))
            bnode.transform = tr.matmul([tr.translate(-11,-0.04,0)])
            bnode.childs+=[createBuilding(pipeline, k)]
            j=1
        elif i>=3 and i<5:
            bnode=sg.SceneGraphNode('building'+str(i))
            bnode.transform = tr.matmul([tr.rotationY(((i-1)%2-j)*np.pi/6), tr.translate(16,-0.04,0)])
            bnode.childs+=[createBuilding(pipeline, k)]
            j=0
        elif i==5:
            bnode=sg.SceneGraphNode('building'+str(i))
            bnode.transform = tr.matmul([tr.translate(11,-0.04,0)])
            bnode.childs+=[createBuilding(pipeline, k)]
        structures.childs+=[bnode]
            
    #----------------------------------------------------------------------------------------#

    #--------------Generar Paisaje ----------------------------------------------------------#
    skyBlock=sg.SceneGraphNode('skyBlock')
    l=np.random.randint(3)
    skyBlock.childs+=[createSkyBlock(pipeline, l+1)]
    #----------------------------------------------------------------------------------------#

    scene = sg.SceneGraphNode('system')
    scene.childs += [linearSectorLeft]
    scene.childs += [linearSectorRight]
    scene.childs += [arcTop]
    scene.childs += [arcBottom]
    scene.childs += [sandNode]
    scene.childs += [field]
    scene.childs += [structures]
    scene.childs += [skyBlock]

    return scene

if __name__ == "__main__":
    
    window=None
    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 800
    height = 800
    title = "Tarea 2"
    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program (pipeline) with both shaders
    axisPipeline = es.SimpleModelViewProjectionShaderProgram()
    texPipeline = es.SimpleTextureModelViewProjectionShaderProgram()
    lightPipeline = ls.SimpleGouraudShaderProgram()
    
    # Telling OpenGL to use our shader program
    glUseProgram(axisPipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)
    
    # Creating shapes on GPU memory
    cpuAxis = bs.createAxis(7)
    gpuAxis = es.GPUShape().initBuffers()
    axisPipeline.setupVAO(gpuAxis)
    gpuAxis.fillBuffers(cpuAxis.vertices, cpuAxis.indices, GL_STATIC_DRAW)

    #NOTA: Aqui creas un objeto con tu escena
    dibujo = createStaticScene(texPipeline)
    car=createCarScene(lightPipeline)
    #instanciamos la clase del auto:
    carClass=objects.Car()

    setPlot(texPipeline, axisPipeline, lightPipeline)

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)

    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)
    playsound(os.path.join("t3", "TokyoDrift.mp3"), block=False)
    while not glfw.window_should_close(window):

        # Measuring performance
        perfMonitor.update(glfw.get_time())
        glfw.set_window_title(window, title + str(perfMonitor))

        # Using GLFW to check for input events
        glfw.poll_events()

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        setView(texPipeline, axisPipeline, lightPipeline)

        if controller.showAxis:
            glUseProgram(axisPipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(axisPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
            axisPipeline.drawCall(gpuAxis, GL_LINES)
        #NOTA: Aquí dibujas tu objeto de escena
        glUseProgram(texPipeline.shaderProgram)
        sg.drawSceneGraphNode(dibujo, texPipeline, "model")

        glUseProgram(lightPipeline.shaderProgram)
        #se procesan las acciones del auto (movimiento y dibujo)
        cars=sg.findNode(car, 'car1')
        cars.transform=tr.matmul([tr.translate(carClass.position[0], carClass.position[1], carClass.position[2]), tr.rotationY(np.pi+carClass.theta)])

        sg.drawSceneGraphNode(car, lightPipeline, "model")
        carClass.move(window)

        #la camara se pone detrás del auto solo si se aprieta el 8, si se vuelve apretar deja de seguirlo
        if controller.follow:
            #posicionamos la camara detrás del auto
            controller.viewPos = np.array([carClass.position[0]-2*np.sin(-carClass.theta), carClass.position[1]+0.6, carClass.position[2]+2*np.cos(carClass.theta)])
            controller.at=np.array([carClass.position[0], 0, carClass.position[2]])

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuAxis.clear()
    dibujo.clear()
    

    glfw.terminate()