# coding=utf-8
"""Tarea 2"""

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

__author__ = "Felix Melo"
__license__ = "MIT"

# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True
        self.viewPos = np.array([10,10,10])
        self.camUp = np.array([0, 1, 0])
        self.distance = 10


controller = Controller()

def setPlot(pipeline, mvpPipeline):
    projection = tr.perspective(45, float(width)/float(height), 0.1, 100)

    glUseProgram(mvpPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

    glUseProgram(pipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
    
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), 5, 5, 5)
    
    glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 1000)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.001)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.1)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.01)

def setView(pipeline, mvpPipeline):
    view = tr.lookAt(
            controller.viewPos,
            np.array([0,0,0]),
            controller.camUp
        )

    glUseProgram(mvpPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    glUseProgram(pipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), controller.viewPos[0], controller.viewPos[1], controller.viewPos[2])
    

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
    
    else:
        print('Unknown key')

def createGPUShape(pipeline, shape):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)

    return gpuShape

#NOTA: Aqui creas tu escena. En escencia, sólo tendrías que modificar esta función.
def createScene(pipeline):
    graySphere = createGPUShape(pipeline, bs.createColorSphereTarea2(140/255,140/255,140/255))
    greenCone = createGPUShape(pipeline, bs.createColorConeTarea2(0.0,1.0,0.0))
    copperCone = createGPUShape(pipeline, bs.createColorConeTarea2(0.7216,0.451,0.2))
    yellowCone = createGPUShape(pipeline, bs.createColorConeTarea2(1, 1, 0))
    whiteCone = createGPUShape(pipeline, bs.createColorConeTarea2(1,1.0,1.0))
    greenCube = createGPUShape(pipeline, bs.createColorCubeTarea2(0.0,1.0,0.0))
    greenCylinder = createGPUShape(pipeline, bs.createColorCylinderTarea2(0.0,1.0,0.0))
    copperCylinder= createGPUShape(pipeline, bs.createColorCylinderTarea2(0.7216,0.451,0.2))
    grayCylinder = createGPUShape(pipeline, bs.createColorCylinderTarea2(140/255,140/255,140/255))
    whiteCylinder = createGPUShape(pipeline, bs.createColorCylinderTarea2(1,1.0,1.0))


                                                #Cuerpo del Avion:
    #---------------------------------------------------------------------------------------------------------------------------#
    #cono verde del cuerpo
    coneBodyNode =sg.SceneGraphNode('coneBody')
    coneBodyNode.transform = tr.matmul([tr.translate(-1,0,0),tr.rotationZ(np.pi/2), tr.scale(0.5,2.0,0.5)])
    coneBodyNode.childs += [greenCone]

    #parbrisas:
    windShieldNode = sg.SceneGraphNode('windshield')
    windShieldNode.transform= tr.matmul([tr.translate(0,0.35,0.0),tr.rotationZ(-1.3*np.pi/3),tr.scale(0.25,0.005,0.25)])
    windShieldNode.childs+=[whiteCylinder]
    #-----------parte de la helice------------#
    #helice
    helixNode=sg.SceneGraphNode('propeller')
    helixNode.transform = tr.matmul([tr.translate(0,0.05,0),tr.rotationZ(-glfw.get_time()),tr.scale(1.0, 0.03, 0.01)])
    helixNode.childs+=[grayCylinder]
    

    #soporte
    helSupNode=sg.SceneGraphNode('helixStand')
    helSupNode.transform = tr.matmul([tr.translate(0,0.045,0),tr.scale(0.07, 0.07, 0.07)])
    helSupNode.childs+=[grayCylinder]

    #base
    engBaseNode=sg.SceneGraphNode('helixBase')
    engBaseNode.transform=tr.matmul([tr.scale(0.5,0.03,0.5)])
    engBaseNode.childs+=[grayCylinder]

    #assemble and possition
    engineNode=sg.SceneGraphNode('fullEngine')
    engineNode.transform=tr.matmul([tr.translate(1,0,0),tr.rotationZ(np.pi*3/2),tr.rotationY(np.pi/2)])
    engineNode.childs+=[engBaseNode,helSupNode,helixNode]

    #----parte de la cola----#
    whiteTrNode = sg.SceneGraphNode('tailWhiteTriangle')
    whiteTrNode.transform=tr.matmul([tr.translate(-2, 0.3, 0), tr.rotationZ(np.pi/6), tr.rotationY(np.pi/2), tr.scale(0.01,0.3,0.25)])
    whiteTrNode.childs +=[whiteCone]

    yellowTrNode= sg.SceneGraphNode('tailYellowTriangle')
    yellowTrNode.transform=tr.matmul([tr.translate(-2, -0.19, 0), tr.rotationZ(-2.55*np.pi/6), tr.rotationY(np.pi/2), tr.scale(0.0015,0.2,0.15)])
    yellowTrNode.childs+=[yellowCone]

    greenTr= sg.SceneGraphNode('tailGreenTriangle')
    greenTr.transform= tr.matmul([tr.translate(-2,0,0.25),tr.rotationX(np.pi/2), tr.rotationY(np.pi/2),tr.scale(0.01,0.3,0.25)])
    greenTr.childs+=[greenCone]

    greenTr2= sg.SceneGraphNode('tailGreenTriangle2')
    greenTr2.transform= tr.matmul([tr.translate(-2,0,-0.25),tr.rotationX(-np.pi/2), tr.rotationY(np.pi/2),tr.scale(0.01,0.3,0.25)])
    greenTr2.childs+=[greenCone]
    #-----ensamblaje del cuerpo-----#
    planeBodyNode=sg.SceneGraphNode('planeBody')
    planeBodyNode.childs+=[coneBodyNode, engineNode, windShieldNode, whiteTrNode, yellowTrNode, greenTr, greenTr2]
    #---------------------------------------------------------------------------------------------------------------------------#


                                             #Alas del avion:
    #--------------------------------------------------------------------------------------------------------#
    #cuerpo principa del ala
    wingMainNode = sg.SceneGraphNode('wingMain')
    wingMainNode.transform = tr.matmul([tr.scale(0.45,0.06,1.6)])
    wingMainNode.childs += [greenCube]

    #bordes circulares:
    curvedEdge = sg.SceneGraphNode('wingEdge')
    curvedEdge.transform = tr.matmul([tr.translate(0.0, 0, 1.6) , tr.scale(0.45, 0.055, 0.45)])
    curvedEdge.childs += [greenCylinder]

    curvedEdge2 = sg.SceneGraphNode('wingEdge')
    curvedEdge2.transform = tr.matmul([tr.rotationY(np.pi),tr.translate(0.0, 0, 1.6) , tr.scale(0.45, 0.055, 0.45)])
    curvedEdge2.childs += [greenCylinder]

    #Nodo con la forma de las alas completas
    wingNode = sg.SceneGraphNode('wing')
    wingNode.childs+=[wingMainNode,curvedEdge, curvedEdge2]

    #----Ala superior---#

    #Circulos en el ala superior
    circleNode = sg.SceneGraphNode('bigCircle')
    circleNode.transform = tr.matmul([tr.scale(1,0.03,1)])
    circleNode.childs += [grayCylinder]

    smallCircleNode = sg.SceneGraphNode('smallCircle')
    smallCircleNode.transform=tr.matmul([tr.scale(0.15,0.05,0.15)])
    smallCircleNode.childs += [grayCylinder]

    #definimos ambos circulos en una variable
    wingAttachment=[circleNode, smallCircleNode]

    firstCircle = sg.SceneGraphNode('firstAttatchment')
    firstCircle.transform = tr.matmul([tr.translate(0,0.05,1), tr.scale(0.4,0.4,0.4)])
    firstCircle.childs += wingAttachment

    secondCircle = sg.SceneGraphNode('secondAttatchment')
    secondCircle.transform = tr.matmul([tr.translate(0,0.05,-1), tr.scale(0.4,0.4,0.4)])
    secondCircle.childs += wingAttachment

    #guardamos las partes del ala superior en una variable
    upperWing=[firstCircle, secondCircle, wingNode]

    upWingNode=sg.SceneGraphNode('upperWing')
    upWingNode.transform=tr.matmul([tr.translate(0.5,0.8,0)])
    upWingNode.childs+=upperWing

    lowWingNode=sg.SceneGraphNode('lowerWing')
    lowWingNode.transform=tr.matmul([tr.translate(0.5,-0.5,0)])
    lowWingNode.childs+=[wingNode]


    #-----------------------------------Varas que unen alas-----------------------------------------------#
    #primero se escalan al tamaño adecuado
    sticksNode = sg.SceneGraphNode('stick')
    sticksNode.transform = tr.matmul([tr.scale(0.02, 0.6, 0.02)])
    sticksNode.childs+=[copperCylinder]

    #se crean las varas verticales
    verticalStick1 = sg.SceneGraphNode('verticalStick1')
    verticalStick1.transform= tr.matmul([tr.translate(0.7 , 0.14, 1)])
    verticalStick1.childs+=[sticksNode]

    verticalStick2 = sg.SceneGraphNode('verticalStick2')
    verticalStick2.transform= tr.matmul([tr.translate(0.3 , 0.14, 1)])
    verticalStick2.childs+=[sticksNode]

    #se crean las varas diagonales
    diagStick1 = sg.SceneGraphNode('diagStrick1')
    diagStick1.transform= tr.matmul([tr.translate(0.7 , 0.3, 0.3), tr.rotationX(np.pi/4)])
    diagStick1.childs+=[sticksNode]

    diagStick2= sg.SceneGraphNode('diagStrick2')
    diagStick2.transform= tr.matmul([tr.translate(0.3 , 0.3, 0.3), tr.rotationX(np.pi/4)])
    diagStick2.childs+=[sticksNode]

    stickSet1=sg.SceneGraphNode('sticksLeft')
    stickSet1.childs+=[verticalStick1, verticalStick2, diagStick1, diagStick2]

    stickSet2=sg.SceneGraphNode('sticksRight')
    stickSet2.transform=tr.matmul([tr.translate(1, 0, 0),tr.rotationY(np.pi)])
    stickSet2.childs+=[stickSet1]

    #assemble de las alas
    wingsAndSticks=sg.SceneGraphNode('wingsAndSticks')
    wingsAndSticks.childs+=[upWingNode, lowWingNode, stickSet1, stickSet2]
        #assemble con el cuerpo del avion
    planeWihtWingNode=sg.SceneGraphNode('wingedPlane')
    planeWihtWingNode.childs+=[planeBodyNode, wingsAndSticks]
    #---------------------------------------------------------------------------------------------------------------------------#


                                                    #Ruedas
    #---------------------------------------------------------------------------------------------------------------------------#
    #soporte de las ruedas
    theFoolNode=sg.SceneGraphNode('wheelStand')
    theFoolNode.transform=tr.matmul([tr.rotationZ(np.pi),tr.scale(0.25,0.25,0.0)])
    theFoolNode.childs+=[copperCone]

    #ruedas
    wheelNode = sg.SceneGraphNode('wheel')
    wheelNode.transform=tr.matmul([tr.translate(0,-0.3,0.035),tr.scale(0.25,0.25,0.03)])
    wheelNode.childs+=[graySphere]

    #rueda+soporte
    wheelAndStand1 = sg.SceneGraphNode('wheelWithStand1')
    wheelAndStand1.transform=tr.matmul([tr.translate(0,0,0.45)])
    wheelAndStand1.childs+=[theFoolNode, wheelNode]
    
    wheelAndStand2 = sg.SceneGraphNode('wheelWithStand2')
    wheelAndStand2.transform=tr.matmul([tr.translate(0,0,-0.45),tr.rotationY(np.pi)])
    wheelAndStand2.childs+=[theFoolNode, wheelNode]

    #union entre ruedas
    wheelUnionNode=sg.SceneGraphNode('wheelUnion')
    wheelUnionNode.transform=tr.matmul([tr.translate(0,-0.285,0),tr.rotationX(np.pi/2),tr.scale(0.06,0.5,0.03)])
    wheelUnionNode.childs+=[whiteCylinder]

    #tren de aterrizaje
    landingNode = sg.SceneGraphNode('landingGear')
    landingNode.transform= tr.matmul([tr.translate(0.5,-0.75,0)])
    landingNode.childs+=[wheelAndStand1,wheelAndStand2,wheelUnionNode]
    #---------------------------------------------------------------------------------------------------------------------------#

    #Assemble del avion,
    fullPlaneNode = sg.SceneGraphNode('completePlane')
    fullPlaneNode.childs+=[planeWihtWingNode, landingNode]

    #multiples aviones rotando c:
    PlaneNode1 = sg.SceneGraphNode('PlaneNode1')
    PlaneNode1.transform=tr.matmul([tr.translate(0,-2,0)])
    PlaneNode1.childs+=[fullPlaneNode]

    PlaneNode2 = sg.SceneGraphNode('PlaneNode2')
    PlaneNode2.transform=tr.matmul([tr.translate(-4,4,0)])
    PlaneNode2.childs+=[fullPlaneNode]

    PlaneNode3 = sg.SceneGraphNode('PlaneNode3')
    PlaneNode3.transform=tr.matmul([tr.translate(4,4,0)])
    PlaneNode3.childs+=[fullPlaneNode]

    allPlanes=sg.SceneGraphNode('scenePlanes')
    allPlanes.childs+=[PlaneNode1, PlaneNode2, PlaneNode3]
    scene = sg.SceneGraphNode('system')
    scene.childs +=[allPlanes]






    
    return scene

if __name__ == "__main__":

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
    mvpPipeline = es.SimpleModelViewProjectionShaderProgram()
    pipeline = ls.SimpleGouraudShaderProgram()
    
    # Telling OpenGL to use our shader program
    glUseProgram(mvpPipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    cpuAxis = bs.createAxis(7)
    gpuAxis = es.GPUShape().initBuffers()
    mvpPipeline.setupVAO(gpuAxis)
    gpuAxis.fillBuffers(cpuAxis.vertices, cpuAxis.indices, GL_STATIC_DRAW)

    #NOTA: Aqui creas un objeto con tu escena
    dibujo = createScene(pipeline)

    setPlot(pipeline, mvpPipeline)

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)

    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)

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

        setView(pipeline, mvpPipeline)

        if controller.showAxis:
            glUseProgram(mvpPipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
            mvpPipeline.drawCall(gpuAxis, GL_LINES)

        #NOTA: Aquí dibujas tu objeto de escena

        #Para rotar la helice
        helice=sg.findNode(dibujo, "propeller")
        helice.transform=tr.matmul([tr.translate(0,0.05,0),tr.rotationY(-15*glfw.get_time()),tr.scale(1.0, 0.03, 0.01)])
        
        #Para que el avion haga un monki flip  (no supe insertar audio, pero hubiera sido chistoso)
        plane=sg.findNode(dibujo, "completePlane")
        plane.transform=tr.matmul([tr.rotationZ(glfw.get_time()),tr.translate(0,-2,0)])
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(dibujo, pipeline, "model")

        planes=sg.findNode(dibujo,"scenePlanes")
        planes.transform=tr.matmul([tr.rotationX(glfw.get_time())])
        

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuAxis.clear()
    dibujo.clear()
    

    glfw.terminate()