# coding=utf-8
"""Tarea 4"""

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
from auxiliarT4 import *
from operator import add

#Este código está basado en el código de Valentina Aguilar.

__author__ = "Valentina Aguilar  - Ivan Sipiran"


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True
        self.X = 2.0 #posicion X de donde esta el auto
        self.Y = -0.037409 #posicion Y de donde esta el auto
        self.Z = 5.0 #posicion Z de donde esta el auto
        #lo siguiente se creo para poder usar coordenadas esfericas
        self.cameraPhiAngle = -np.pi/4 #inclinacion de la camara 
        self.cameraThetaAngle = np.pi/2 #rotacion con respecto al eje y
        self.r = 2 #radio

#TAREA4: Esta clase contiene todos los parámetros de una luz Spotlight. Sirve principalmente para tener
# un orden sobre los atributos de las luces
class Spotlight:
    def __init__(self):
        self.ambient = np.array([0,0,0])
        self.diffuse = np.array([0,0,0])
        self.specular = np.array([0,0,0])
        self.constant = 0
        self.linear = 0
        self.quadratic = 0
        self.position = np.array([0,0,0])
        self.direction = np.array([0,0,0])
        self.cutOff = 0
        self.outerCutOff = 0

controller = Controller()

#TAREA4: aquí se crea el pool de luces spotlight (como un diccionario)
spotlightsPool = dict()

#TAREA4: Esta función ejemplifica cómo podemos crear luces para nuestra escena. En este caso creamos 2 luces con diferentes 
# parámetros

def setLights():
    #TAREA4: Primera luz spotlight
    spot1 = Spotlight()
    spot1.ambient = np.array([0.0, 0.0, 0.0])
    spot1.diffuse = np.array([1.0, 1.0, 1.0])
    spot1.specular = np.array([1.0, 1.0, 1.0])
    spot1.constant = 1.0
    spot1.linear = 0.09
    spot1.quadratic = 0.032
    spot1.position = np.array([2, 5, 0]) #TAREA4: esta ubicada en esta posición
    spot1.direction = np.array([0, -1, 0]) #TAREA4: está apuntando perpendicularmente hacia el terreno (Y-, o sea hacia abajo)
    spot1.cutOff = np.cos(np.radians(12.5)) #TAREA4: corte del ángulo para la luz
    spot1.outerCutOff = np.cos(np.radians(45)) #TAREA4: la apertura permitida de la luz es de 45°
                                                #mientras más alto es este ángulo, más se difumina su efecto
    
    spotlightsPool['spot1'] = spot1 #TAREA4: almacenamos la luz en el diccionario, con una clave única

    #TAREA4: Segunda luz spotlight
    spot2 = Spotlight()
    spot2.ambient = np.array([0.0, 0.0, 0.0])
    spot2.diffuse = np.array([1.0, 1.0, 1.0])
    spot2.specular = np.array([1.0, 1.0, 1.0])
    spot2.constant = 1.0
    spot2.linear = 0.09
    spot2.quadratic = 0.032
    spot2.position = np.array([-2, 5, 0]) #TAREA4: Está ubicada en esta posición
    spot2.direction = np.array([0, -1, 0]) #TAREA4: también apunta hacia abajo
    spot2.cutOff = np.cos(np.radians(12.5))
    spot2.outerCutOff = np.cos(np.radians(15)) #TAREA4: Esta luz tiene menos apertura, por eso es más focalizada
    spotlightsPool['spot2'] = spot2 #TAREA4: almacenamos la luz en el diccionario

    #Tarea4: luces autos
    #auto manejado por usuario:
    userCarL = Spotlight()
    userCarL.ambient = np.array([0.0, 0.0, 0.0])
    userCarL.diffuse = np.array([1.0, 1.0, 1.0])
    userCarL.specular = np.array([1.0, 1.0, 1.0])
    userCarL.constant = 1.0
    userCarL.linear = 0.09
    userCarL.quadratic = 0.032
    userCarL.position = np.array([2.05, 0.1, 5.0]) 
    userCarL.direction = np.array([0, -1, -5])
    userCarL.cutOff = np.cos(np.radians(12.5))
    userCarL.outerCutOff = np.cos(np.radians(15)) 
    spotlightsPool['uCarL'] = userCarL 
    
    userCarR = Spotlight()
    userCarR.ambient = np.array([0.0, 0.0, 0.0])
    userCarR.diffuse = np.array([1.0, 1.0, 1.0])
    userCarR.specular = np.array([1.0, 1.0, 1.0])
    userCarR.constant = 1.0
    userCarR.linear = 0.09
    userCarR.quadratic = 0.032
    userCarR.position = np.array([1.95, 0.1, 5.0]) 
    userCarR.direction = np.array([0, -1, -5])
    userCarR.cutOff = np.cos(np.radians(12.5))
    userCarR.outerCutOff = np.cos(np.radians(15)) 
    spotlightsPool['uCarR'] = userCarR 

    #Auto de la escena
    sceneCarL = Spotlight()
    sceneCarL.ambient = np.array([0.0, 0.0, 0.0])
    sceneCarL.diffuse = np.array([1.0, 1.0, 1.0])
    sceneCarL.specular = np.array([1.0, 1.0, 1.0])
    sceneCarL.constant = 1.0
    sceneCarL.linear = 0.09
    sceneCarL.quadratic = 0.032
    sceneCarL.position = np.array([0, 0, 0]) #todo 0 ya que los cambio en el while
    sceneCarL.direction = np.array([0, -1, -5])
    sceneCarL.cutOff = np.cos(np.radians(12.5))
    sceneCarL.outerCutOff = np.cos(np.radians(15)) 
    spotlightsPool['sCarL'] = sceneCarL 
    
    sceneCarR = Spotlight()
    sceneCarR.ambient = np.array([0.0, 0.0, 0.0])
    sceneCarR.diffuse = np.array([1.0, 1.0, 1.0])
    sceneCarR.specular = np.array([1.0, 1.0, 1.0])
    sceneCarR.constant = 1.0
    sceneCarR.linear = 0.09
    sceneCarR.quadratic = 0.032
    sceneCarR.position = np.array([0, 0, 0])  #todo 0 ya que los cambio en el while
    sceneCarR.direction = np.array([0, -1, -5])
    sceneCarR.cutOff = np.cos(np.radians(12.5))
    sceneCarR.outerCutOff = np.cos(np.radians(15)) 
    spotlightsPool['sCarR'] = sceneCarR 



#TAREA4: modificamos esta función para poder configurar todas las luces del pool
def setPlot(texPipeline, axisPipeline, lightPipeline):
    projection = tr.perspective(60, float(width)/float(height), 0.1, 100) #el primer parametro se cambia a 60 para que se vea más escena

    glUseProgram(axisPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(axisPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

    #TAREA4: Como tenemos 2 shaders con múltiples luces, tenemos que enviar toda esa información a cada shader
    #TAREA4: Primero al shader de color
    glUseProgram(lightPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(lightPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
    
    #TAREA4: Enviamos la información de la luz puntual y del material
    #TAREA4: La luz puntual está desactivada por defecto (ya que su componente ambiente es 0.0, 0.0, 0.0), pero pueden usarla
    # para añadir más realismo a la escena
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "pointLights[0].ambient"), 0.2, 0.2, 0.2)
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "pointLights[0].diffuse"), 0.0, 0.0, 0.0)
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "pointLights[0].specular"), 0.0, 0.0, 0.0)
    glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, "pointLights[0].constant"), 0.1)
    glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, "pointLights[0].linear"), 0.1)
    glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, "pointLights[0].quadratic"), 0.01)
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "pointLights[0].position"), 5, 5, 5)

    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "material.ambient"), 0.2, 0.2, 0.2)
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "material.diffuse"), 0.9, 0.9, 0.9)
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "material.specular"), 1.0, 1.0, 1.0)
    glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, "material.shininess"), 32)

    #TAREA4: Aprovechamos que las luces spotlight están almacenadas en el diccionario para mandarlas al shader
    for i, (k,v) in enumerate(spotlightsPool.items()):
        baseString = "spotLights[" + str(i) + "]."
        glUniform3fv(glGetUniformLocation(lightPipeline.shaderProgram, baseString + "ambient"), 1, v.ambient)
        glUniform3fv(glGetUniformLocation(lightPipeline.shaderProgram, baseString + "diffuse"), 1, v.diffuse)
        glUniform3fv(glGetUniformLocation(lightPipeline.shaderProgram, baseString + "specular"), 1, v.specular)
        glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, baseString + "constant"), v.constant)
        glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, baseString + "linear"), 0.09)
        glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, baseString + "quadratic"), 0.032)
        glUniform3fv(glGetUniformLocation(lightPipeline.shaderProgram, baseString + "position"), 1, v.position)
        glUniform3fv(glGetUniformLocation(lightPipeline.shaderProgram, baseString + "direction"), 1, v.direction)
        glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, baseString + "cutOff"), v.cutOff)
        glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, baseString + "outerCutOff"), v.outerCutOff)

    #TAREA4: Ahora repetimos todo el proceso para el shader de texturas con mútiples luces
    glUseProgram(texPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
    

    glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "pointLights[0].ambient"), 0.2, 0.2, 0.2)
    glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "pointLights[0].diffuse"), 0.0, 0.0, 0.0)
    glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "pointLights[0].specular"), 0.0, 0.0, 0.0)
    glUniform1f(glGetUniformLocation(texPipeline.shaderProgram, "pointLights[0].constant"), 0.1)
    glUniform1f(glGetUniformLocation(texPipeline.shaderProgram, "pointLights[0].linear"), 0.1)
    glUniform1f(glGetUniformLocation(texPipeline.shaderProgram, "pointLights[0].quadratic"), 0.01)
    glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "pointLights[0].position"), 5, 5, 5)

    glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "material.ambient"), 0.2, 0.2, 0.2)
    glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "material.diffuse"), 0.9, 0.9, 0.9)
    glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "material.specular"), 1.0, 1.0, 1.0)
    glUniform1f(glGetUniformLocation(texPipeline.shaderProgram, "material.shininess"), 32)

    for i, (k,v) in enumerate(spotlightsPool.items()):
        baseString = "spotLights[" + str(i) + "]."
        glUniform3fv(glGetUniformLocation(texPipeline.shaderProgram, baseString + "ambient"), 1, v.ambient)
        glUniform3fv(glGetUniformLocation(texPipeline.shaderProgram, baseString + "diffuse"), 1, v.diffuse)
        glUniform3fv(glGetUniformLocation(texPipeline.shaderProgram, baseString + "specular"), 1, v.specular)
        glUniform1f(glGetUniformLocation(texPipeline.shaderProgram, baseString + "constant"), v.constant)
        glUniform1f(glGetUniformLocation(texPipeline.shaderProgram, baseString + "linear"), 0.09)
        glUniform1f(glGetUniformLocation(texPipeline.shaderProgram, baseString + "quadratic"), 0.032)
        glUniform3fv(glGetUniformLocation(texPipeline.shaderProgram, baseString + "position"), 1, v.position)
        glUniform3fv(glGetUniformLocation(texPipeline.shaderProgram, baseString + "direction"), 1, v.direction)
        glUniform1f(glGetUniformLocation(texPipeline.shaderProgram, baseString + "cutOff"), v.cutOff)
        glUniform1f(glGetUniformLocation(texPipeline.shaderProgram, baseString + "outerCutOff"), v.outerCutOff)

#TAREA4: Esta función controla la cámara
def setView(texPipeline, axisPipeline, lightPipeline):
    #la idea de usar coordenadas esfericas para la camara fue extraida del auxiliar 6
    #como el auto reposa en el plano XZ, no sera necesaria la coordenada Y esferica.
    Xesf = controller.r * np.sin(controller.cameraPhiAngle)*np.cos(controller.cameraThetaAngle) #coordenada X esferica
    Zesf = controller.r * np.sin(controller.cameraPhiAngle)*np.sin(controller.cameraThetaAngle) #coordenada Y esferica

    viewPos = np.array([controller.X-Xesf,0.5,controller.Z-Zesf])
    view = tr.lookAt(
            viewPos, #eye
            np.array([controller.X,controller.Y,controller.Z]),     #at
            np.array([0, 1, 0])   #up
        )

    glUseProgram(axisPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(axisPipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    glUseProgram(texPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
    glUniform3f(glGetUniformLocation(texPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])

    glUseProgram(lightPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(lightPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
    
    

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

    else:
        print('Unknown key')

#Tarea 4: función extraida de ejemplos de clases
def bezierMatrix(P0, P1, P2, P3):
    
    # Generate a matrix concatenating the columns
    G = np.concatenate((P0, P1, P2, P3), axis=1)

    # Bezier base matrix is a constant
    Mb = np.array([[1, -3, 3, -1], [0, 3, -6, 3], [0, 0, 3, -3], [0, 0, 0, 1]])
    
    return np.matmul(G, Mb)

#Tarea 4: función extraida de ejemplos de clases
# M is the cubic curve matrix, N is the number of samples between 0 and 1
def evalCurve(M, N):
    # The parameter t should move between 0 and 1
    ts = np.linspace(0.0, 1.0, N)
    
    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(N, 3), dtype=float)
    
    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T
        
    return curve

#Tarea 4: función extraida de ejemplos de clases
def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T
    
if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 800
    height = 800
    title = "Tarea 4"
    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program (pipeline) with both shaders
    #TAREA4: Se usan los shaders de múltiples luces
    axisPipeline = es.SimpleModelViewProjectionShaderProgram()
    texPipeline = ls.MultipleLightTexturePhongShaderProgram()
    lightPipeline = ls.MultipleLightPhongShaderProgram()
    
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
    #TAREA4: Se cargan las texturas y se configuran las luces
    ##para el skyblock
    sky=np.random.randint(3)
    loadTextures(sky+1)
    setLights()

    dibujo = createStaticScene(texPipeline)
    car = createCarScene(lightPipeline)
    
    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)

    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)

    #parametro iniciales
    t0 = glfw.get_time()
    coord_X = 0 
    coord_Z = 0
    angulo = 0

    #auto que se va moviendo
    sceneCar = createCarScene(lightPipeline)

    ##Curva para el movimiento del auto
    N = 900
    R0 = np.array([[1.75, -0.037409, 5.5]]).T
    R1 = np.array([[1.75, -0.037409, 7.8]]).T
    R2 = np.array([[-1.75, -0.037409, 7.8]]).T
    R3 = np.array([[-1.75, -0.037409, 5.5]]).T
    M1 = bezierMatrix(R0, R1, R2, R3)
    bezierCurve1 = evalCurve(M1, N)

    R0 = np.array([[-1.75, -0.037409, 5.5]]).T
    R1 = np.array([[-1.75, -0.037409, 3]]).T
    R2 = np.array([[-1.75, -0.037409, 0.5]]).T
    R3 = np.array([[-1.75, -0.037409, -4.5]]).T
    M2 = bezierMatrix(R0, R1, R2, R3)
    bezierCurve2 = evalCurve(M2, N)

    R0 = np.array([[-1.75, -0.037409, -4.5]]).T
    R1 = np.array([[-1.75, -0.037409, -6.9]]).T
    R2 = np.array([[1.75, -0.037409, -6.9]]).T
    R3 = np.array([[1.75, -0.037409, -4.5]]).T
    M3 = bezierMatrix(R0, R1, R2, R3)
    bezierCurve3 = evalCurve(M3, N)

    R0 = np.array([[1.75, -0.037409, -4.5]]).T
    R1 = np.array([[1.75, -0.037409, -2]]).T
    R2 = np.array([[1.75, -0.037409, 0.4]]).T
    R3 = np.array([[1.75, -0.037409, 5.5]]).T
    M4 = bezierMatrix(R0, R1, R2, R3)
    bezierCurve4 = evalCurve(M4, N)

    C = np.concatenate((bezierCurve1,bezierCurve2,bezierCurve3,bezierCurve4), axis=0)
    print(C.shape)
    step=0

    while not glfw.window_should_close(window):

        # Measuring performance
        perfMonitor.update(glfw.get_time())
        glfw.set_window_title(window, title + str(perfMonitor))

        # Using GLFW to check for input events
        glfw.poll_events()

        #Se obtiene una diferencia de tiempo con respecto a la iteracion anterior.
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        #TAREA4: Se manejan las teclas de la animación
        #ir hacia adelante 
        if(glfw.get_key(window, glfw.KEY_W) == glfw.PRESS):
            controller.X -= 1.5 * dt * np.sin(angulo) #avanza la camara
            controller.Z -= 1.5 * dt * np.cos(angulo) #avanza la camara
            coord_X -= 1.5 * dt * np.sin(angulo) #avanza el auto
            coord_Z -= 1.5 * dt * np.cos(angulo) #avanza el auto

        #ir hacia atras
        if(glfw.get_key(window, glfw.KEY_S) == glfw.PRESS):
            controller.X += 1.5 * dt * np.sin(angulo) #retrocede la camara
            controller.Z += 1.5 * dt * np.cos(angulo) #retrocede la cmara
            coord_X += 1.5 * dt * np.sin(angulo) #retrocede el auto
            coord_Z += 1.5 * dt * np.cos(angulo) #retrocede el auto

        #ir hacia la izquierda
        if(glfw.get_key(window, glfw.KEY_A) == glfw.PRESS):
            controller.cameraThetaAngle -= dt  #camara se gira a la izquierda
            angulo += dt #auto gira a la izquierda

        #ir hacia la derecha
        if(glfw.get_key(window, glfw.KEY_D) == glfw.PRESS):
            controller.cameraThetaAngle += dt #camara se gira a la derecha
            angulo -= dt #auto gira a la derecha

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        #TAREA4: Ojo aquí! Se configura la cámara y el dibujo en cada iteración. Esto es porque necesitamos que en cada iteración
        # las luces de los faros de los carros se actualicen en posición y dirección
        setView(texPipeline, axisPipeline, lightPipeline)
        setPlot(texPipeline, axisPipeline,lightPipeline)

        if controller.showAxis:
            glUseProgram(axisPipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(axisPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
            axisPipeline.drawCall(gpuAxis, GL_LINES)

        #NOTA: Aquí dibujas tu objeto de escena
        glUseProgram(texPipeline.shaderProgram)
        sg.drawSceneGraphNode(dibujo, texPipeline, "model")
        
        glUseProgram(lightPipeline.shaderProgram)

        ################################################################################
        ################################################################################
        #aqui se mueve el auto
        sg.drawSceneGraphNode(car, lightPipeline, "model")
        Auto = sg.findNode(car,'system-car')
        Auto.transform = tr.matmul([tr.translate(coord_X+2,-0.037409,coord_Z+5),tr.rotationY(np.pi+angulo),tr.rotationY(-np.pi),tr.translate(-2,0.037409,-5)])
        #transformación que hace que el auto se ponga en el origen, para luego trasladarlo al punto (2.0, −0.037409, 5.0) para despés poder moverlo.

        #Mover luces auto usuario
        spotlightsPool['uCarL'].position=np.array([2.05+coord_X, 0.1, 5.0+coord_Z])
        spotlightsPool['uCarL'].direction=np.array([-np.sin(angulo), -0.2, -np.cos(angulo)])

        spotlightsPool['uCarR'].position=np.array([1.95+coord_X, 0.1, 5.0+coord_Z])
        spotlightsPool['uCarR'].direction=np.array([-np.sin(angulo), -0.2, -np.cos(angulo)])

        #Auto moviendose por curva
        if step > N*4-2:
            step = 0

        if step < N*4-2:
            angle = np.arctan2(C[step+1,0]-C[step,0], C[step+1,2]-C[step,2])
        else:
            angle = np.arctan2(C[0,0]-C[step,0],C[0,2]-C[step,2])
        
        carNode = sg.findNode(sceneCar, 'system-car')
        carNode.transform = tr.matmul([tr.translate(C[step,0], C[step,1], C[step,2]), tr.rotationY(angle),tr.rotationY(-np.pi),tr.translate(-2,0.037409,-5)])

        step = step + 1

        #NOTA: Aquí dibujas tu objeto de escena
        glUseProgram(lightPipeline.shaderProgram)
        sg.drawSceneGraphNode(sceneCar, lightPipeline, "model")
        
        #Mover luces auto escena
        spotlightsPool['sCarL'].position=np.array([0.05+C[step,0], 0.2, C[step,2]])
        spotlightsPool['sCarL'].direction=np.array([np.sin(angle), -0.2, np.cos(angle)])

        spotlightsPool['sCarR'].position=np.array([-0.05+C[step,0], 0.2, C[step,2]])
        spotlightsPool['sCarR'].direction=np.array([np.sin(angle), -0.2, np.cos(angle)])

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuAxis.clear()
    dibujo.clear()
    

    glfw.terminate()