import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import easy_shaders as es
import basic_shapes as bs
from gpu_shape import GPUShape, SIZE_IN_BYTES

__author__ = "Felix Melo"
__license__ = "MIT"

# We will use 32 bits data, so an integer has 4 bytes
# 1 byte = 8 bits
SIZE_IN_BYTES = 4

#Returns an array with the postion of a single star
#params x, y are the coordinates in which the piece will be placed, r, g, b are for colors and radius is the distance from the center of the star to the farthest point
def crear_estrella(x,y,r,g,b,radius):
    #cada array que se ve abajo representa una punta de la estrella
    vertical=1
    horizontal=0.9
    diag=0.7
    #puntas verticales
    star = [x, y+vertical*radius, 0.0,  r, g, b,
            x+-0.2*radius, y, 0.0,      r, g, b,
            x+0.2*radius, y, 0.0,       r, g, b]
    star.extend([x, y-vertical*radius, 0.0, r, g, b,
                x+-0.2*radius, y, 0.0,      r, g, b,
                x+0.2*radius, y, 0.0,       r, g, b])
    #puntas horizontales
    star.extend([x+horizontal*radius, y, 0.0,   r, g, b,
                x, y+-0.2*radius, 0.0,          r, g, b,
                x, y+0.2*radius, 0.0,           r, g, b])
    star.extend([x-horizontal*radius, y, 0.0, r, g, b,
                x, y+-0.2*radius, 0.0,        r, g, b,
                x, y+0.2*radius, 0.0,         r, g, b])
    #puntas diagonales
    star.extend([x+diag*radius, y+diag*radius, 0.0, r, g, b,
                x+0.2*radius, y, 0.0,               r, g, b,
                x, y+0.2*radius, 0.0,               r, g, b])
    star.extend([x+diag*radius, y-diag*radius, 0.0, r, g, b,
                x+0.2*radius, y, 0.0,               r, g, b,
                x, y-0.2*radius, 0.0,               r, g, b])     
    star.extend([x-diag*radius, y+diag*radius, 0.0, r, g, b,
                x-0.2*radius, y, 0.0,               r, g, b,
                x, y+0.2*radius, 0.0,               r, g, b])
    star.extend([x-diag*radius, y-diag*radius, 0.0, r, g, b,
                x-0.2*radius, y, 0.0,               r, g, b,
                x, y-0.2*radius, 0.0,               r, g, b])      
    
    return star


#Returns a bs.Shape object with all vertices and indexes for the 24 star-pawns
#param radio the distance from the center of the star to the farthest point
def crearEstrellas(radio, color):
    #variables auxiliar que ayudará a saber en que posición poner las piezas
    placex1=-0.7
    placey=0.7
    placex2=-0.5
    estrellas=[]
    r, b=1,0
    x1, x2= placex1, placex2
    #si se están dibujando las piezas azules deben cambiarse los siguientes valores
    if color=="blue":
        r, b=b, r
        placey=-0.3
        placex1, placex2 = placex2, placex1
        x1, x2= placex1, placex2

    for i in range(3):
        for j in range(4):
            #se separa en 2 casos para manejar como se posicionan las damas (a veces parten en el primer cuadro, otras en el segundo)
            if i%2==0:
                estrellas.extend(crear_estrella(placex1, placey, r, 0, b, radio))
                placex1+=0.4 #se salta un casillero
            elif i%2==1:
                estrellas.extend(crear_estrella(placex2, placey, r, 0, b, radio))
                placex2+=0.4 #se salta un casillero
        #se avanza a la fila de abajo y se reestablecen los valores de posición horizontal
        placey-= 0.2
        placex1=x1
        placex2=x2
    #se definen las conexiones entre vertices (por cada pieza hay 8 matrices con 3 vertices cada una, y se tienen 12 piezas en total)
    indices=[]
    for i in range(0,12*8*3,3):
        indices.extend([i,i+1,i+2])
    return bs.Shape(np.array(estrellas), np.array(indices))


#Returns an array with the postion of a pawn
#params x, y are the coordinates in which the piece will be placed, r, g, b are for colors and radius is the radius of the circle
def crear_dama(x,y,r,g,b,radius):
    circle = []
    for angle in range(0,360,10):
        circle.extend([x, y, 0.0, r, g, b])
        circle.extend([x+np.cos(np.radians(angle))*radius, 
                       y+np.sin(np.radians(angle))*radius, 
                       0.0, r, g, b])
        circle.extend([x+np.cos(np.radians(angle+10))*radius, 
                       y+np.sin(np.radians(angle+10))*radius, 
                       0.0, r, g, b])
    return circle

#Returns a bs.Shape object with all vertices and indexes for the 24 pawns
#param radio is the radius of the circle
def crearDamas(radio, color):
    #variables auxiliares que ayudarán a saber en que posición poner las piezas, así como que color ponerles
    placex1=-0.7
    placey=0.7
    placex2=-0.5
    damas=[]
    r, b=1,0
    x1, x2= placex1, placex2
    #si se están dibujando las piezas azules deben cambiarse los siguientes valores
    if color=="blue":
        r, b=b, r
        placey=-0.3
        placex1, placex2 = placex2, placex1
        x1, x2= placex1, placex2

    for i in range(3):
        for j in range(4):
            #se separa en 2 casos para manejar como se posicionan las damas (a veces parten en el primer cuadro, otras en el segundo)
            if i%2==0:
                damas.extend(crear_dama(placex1, placey, r, 0, b, radio))
                placex1+=0.4 #se salta un casillero
            elif i%2==1:
                damas.extend(crear_dama(placex2, placey, r, 0, b, radio))
                placex2+=0.4 #se salta un casillero
        #se avanza a la fila de abajo y se reestablecen los valores de posición horizontal
        placey-=0.2
        placex1=x1
        placex2=x2
    return bs.Shape(damas, range(len(damas)))


# A class to store the application control
class Controller:
    #atributos que indicas si se deben usar piezas con forma de estrella o no, un atributo para cada color
    star_pawn_red = True 
    star_pawn_blue = True

# we will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    #se alternan ambas piezas
    if key == glfw.KEY_SPACE:
        controller.star_pawn_red = not controller.star_pawn_red
        controller.star_pawn_blue = not controller.star_pawn_blue

    #se alterna las piezas de bajo (azules)
    elif key == glfw.KEY_DOWN:
        controller.star_pawn_blue = not controller.star_pawn_blue
    
    #se alternan las piezas de arriba (rojas)
    elif key == glfw.KEY_UP:
        controller.star_pawn_red = not controller.star_pawn_red

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    else:
        print('Unknown key')

#function in charge of creating the vertices and indexes for the board, a bigger white quad is created, then the smaller black quads are added (w:b = 8:1)
#Returns a bs.Shape object with all vertices and indexes for the board
def crear_tablero():
    #Se decidió crear el tablero con un tamaño de 1.6 total (de -0.8 a 0.8)
    vertexData =[
    #     x     y    z      colores
        -0.8, -0.8, 0.0,  1.0, 1.0, 1.0,
         0.8, -0.8, 0.0,  1.0, 1.0, 1.0,
         0.8,  0.8, 0.0,  1.0, 1.0, 1.0,
        -0.8,  0.8, 0.0,  1.0, 1.0, 1.0
        ]
    #se definen las conexiones con los vertices
    indices =[0, 1, 2,
             2, 3, 0]
    #Algunos vertices que ayudarán a construir los cuadrados negros (vexy para el eje y, vexx para el eje x)
    vexy1=0.8
    vexy2=0.6
    vexx1=-0.8
    vexx2=-0.6
    vexx3=-0.6
    vexx4=-0.4
    #variable que ayudará a ir indexando las conexiones entre vertices
    inx=4
    for i in range(8):
        for j in range(4):
            #filas que comienzan con cuadrado negro
            if i%2==0: 
                vertexData.extend([
            #     x      y     z      colores
                vexx1, vexy2, 0.0,  0.0, 0.0, 0.0,
                vexx2, vexy2, 0.0,  0.0, 0.0, 0.0,
                vexx2, vexy1, 0.0,  0.0, 0.0, 0.0,
                vexx1, vexy1, 0.0,  0.0, 0.0, 0.0
                ])
                #se conectan los indices
                indices.extend([inx, inx+1, inx+2,
                 inx+2, inx+3, inx])
                #se escala el asistente de los indices en 4, ya que para dibujar el siguiente...
                #... cuadrado se deben conectar nuevos vertices aparte de los 4 ya utilizados
                inx+=4
                #se suman 0.4 a cada vertice auxiliar del eje x, puesto que se tiene que dejar el espacio para que quede un cuadrado blanco
                vexx1 +=0.4
                vexx2 +=0.4
            #aquellas que comienzan con espacio blanco
            elif i%2==1:
                vertexData.extend([
            #     x      y     z      colores
                vexx3, vexy2, 0.0,  0.0, 0.0, 0.0,
                vexx4, vexy2, 0.0,  0.0, 0.0, 0.0,
                vexx4, vexy1, 0.0,  0.0, 0.0, 0.0,
                vexx3, vexy1, 0.0,  0.0, 0.0, 0.0
                ])
                #se conectan los indices
                indices.extend([inx, inx+1, inx+2,
                 inx+2, inx+3, inx])
                #se escala el asistente de los indices en 4, ya que para dibujar el siguiente...
                #... cuadrado se deben conectar nuevos vertices aparte de los 4 ya utilizados
                inx+=4
                #se suman 0.4 a cada vertice auxiliar del eje x, puesto que se tiene que dejar el espacio para que quede un cuadrado blanco
                vexx3 +=0.4
                vexx4 +=0.4
        #se reestablecen los valores originales de los vertices auxiliares del eje x para comenzar con las siguientes filas
        vexx1=-0.8
        vexx2=-0.6
        vexx3=-0.6
        vexx4=-0.4
        #Se restan 0.2 a los vertices auxiliares del eje y, puesto que hay que bajar a la siguiente fila
        vexy1-=0.2
        vexy2-=0.2
    
    return bs.Shape(np.array(vertexData, dtype = np.float32), np.array(indices, dtype = np.float32))

#Returns a bs.Shape object with all vertices and indexes for the background of the board
def crear_fondo():
    dim=0.9
    vertexData =[
    #     x     y    z           colores
        -dim, -dim, 0.0,  0.4139, 0.3342, 0.2519,
         dim, -dim, 0.0,  0.4139, 0.3342, 0.2519,
         dim,  dim, 0.0,  0.4139, 0.3342, 0.2519,
        -dim,  dim, 0.0,  0.4139, 0.3342, 0.2519
        ]
    #se definen las conexiones con los vertices
    indices =[0, 1, 2,
             2, 3, 0]
    return bs.Shape(np.array(vertexData, dtype = np.float32), np.array(indices, dtype = np.float32))

#Main body of the project, executes all that's necessary to generate the draughts board and the pawns
if __name__ == "__main__":

    window=None
    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    #dimensiones de la ventana
    width = 600
    height = 600

    window = glfw.create_window(width, height, "Tarea 1", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    #se inicia el pipeline para crear el shader program e indicarle a opengl que lo utilice
    pipeline = es.SimpleShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    #se crea el fondo
    bgShape= crear_fondo()# Creamos los vertices e indices (guardandolos en un objeto shape)
    gpuBgShape=GPUShape().initBuffers() # Se le pide memoria a la GPU para guardar la figura
    pipeline.setupVAO(gpuBgShape) # Se le dice al pipeline como leer esta parte de la memoria 
    gpuBgShape.fillBuffers(bgShape.vertices, bgShape.indices, GL_STATIC_DRAW) # Llenamos esta memoria de la GPU con los vertices e indices


    #se crea el tablero
    boardShape= crear_tablero() # Creamos los vertices e indices (guardandolos en un objeto shape)
    gpuBoardShape= GPUShape().initBuffers() # Se le pide memoria a la GPU para guardar la figura
    pipeline.setupVAO(gpuBoardShape) # Se le dice al pipeline como leer esta parte de la memoria 
    gpuBoardShape.fillBuffers(boardShape.vertices, boardShape.indices, GL_STATIC_DRAW) # Llenamos esta memoria de la GPU con los vertices e indices
     
    #se crean las piezas circulares rojas
    pawnShape1= crearDamas(0.08, "red") # Creamos los vertices e indices (guardandolos en un objeto shape)
    gpuPawnShape1= GPUShape().initBuffers() # Se le pide memoria a la GPU para guardar la figura
    pipeline.setupVAO(gpuPawnShape1) # Se le dice al pipeline como leer esta parte de la memoria 
    gpuPawnShape1.fillBuffers(pawnShape1.vertices, pawnShape1.indices, GL_STATIC_DRAW) # Llenamos esta memoria de la GPU con los vertices e indices

    #se crean las piezas circulares azules
    pawnShape2= crearDamas(0.08, "blue") # Creamos los vertices e indices (guardandolos en un objeto shape)
    gpuPawnShape2= GPUShape().initBuffers() # Se le pide memoria a la GPU para guardar la figura
    pipeline.setupVAO(gpuPawnShape2) # Se le dice al pipeline como leer esta parte de la memoria 
    gpuPawnShape2.fillBuffers(pawnShape2.vertices, pawnShape2.indices, GL_STATIC_DRAW) # Llenamos esta memoria de la GPU con los vertices e indices

    #se crean las piezas en forma de estrella rojas
    starShape1= crearEstrellas(0.1, "red") # Creamos los vertices e indices (guardandolos en un objeto shape)
    gpuStarShape1= GPUShape().initBuffers() # Se le pide memoria a la GPU para guardar la figura
    pipeline.setupVAO(gpuStarShape1) # Se le dice al pipeline como leer esta parte de la memoria 
    gpuStarShape1.fillBuffers(starShape1.vertices, starShape1.indices, GL_STATIC_DRAW) # Llenamos esta memoria de la GPU con los vertices e indices

    #se crean las piezas en forma de estrella azules
    starShape2= crearEstrellas(0.1, "blue") # Creamos los vertices e indices (guardandolos en un objeto shape)
    gpuStarShape2= GPUShape().initBuffers() # Se le pide memoria a la GPU para guardar la figura
    pipeline.setupVAO(gpuStarShape2) # Se le dice al pipeline como leer esta parte de la memoria 
    gpuStarShape2.fillBuffers(starShape2.vertices, starShape2.indices, GL_STATIC_DRAW) # Llenamos esta memoria de la GPU con los vertices e indices

    # Setting up the clear screen color
    glClearColor(0.25, 0.25, 0.25, 1.0)

    # Waiting to close the window
    while not glfw.window_should_close(window):

        # Getting events from GLFW
        glfw.poll_events()

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        #se dibuja el fondo del tablero
        pipeline.drawCall(gpuBgShape)

        #se dibuja el tabler
        pipeline.drawCall(gpuBoardShape)
        
        #se alternan el tipo de pieza de cada lado y se dibujan
        if (controller.star_pawn_blue):
            pipeline.drawCall(gpuStarShape2)
        else:
            pipeline.drawCall(gpuPawnShape2)
        if (controller.star_pawn_red):
            pipeline.drawCall(gpuStarShape1)
        else:
            pipeline.drawCall(gpuPawnShape1)
       

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    #liberando memoria
    gpuBoardShape.clear()
    gpuPawnShape1.clear()
    gpuStarShape1.clear()
    gpuStarShape2.clear()

    glfw.terminate()