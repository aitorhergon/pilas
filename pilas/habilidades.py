# -*- encoding: utf-8 -*-
# Pilas engine - A video game framework.
#
# Copyright 2010 - Hugo Ruscitti
# License: LGPLv3 (see http://www.gnu.org/licenses/lgpl.html)
#
# Website - http://www.pilas-engine.com.ar

import random
import pilas
from math import atan2, pi

class Habilidad(object):

    def __init__(self, receptor):
        self.receptor = receptor

    def actualizar(self):
        pass

    def eliminar(self):
        pass

class RebotarComoPelota(Habilidad):

    def __init__(self, receptor):
        Habilidad.__init__(self, receptor)
        error = random.randint(-10, 10) / 10.0

        circulo = pilas.fisica.Circulo(receptor.x + error,
                                       receptor.y + error,
                                       receptor.radio_de_colision)
        receptor.aprender(pilas.habilidades.Imitar, circulo)
        self.circulo = circulo
        receptor.impulsar = self.impulsar
        receptor.empujar = self.empujar

    def eliminar(self):
        self.circulo.eliminar()

    def impulsar(self, dx, dy):
        self.circulo.impulsar(dx, dy)

    def empujar(self, dx, dy):
        self.circulo.empujar(dx, dy)

class RebotarComoCaja(Habilidad):

    def __init__(self, receptor):
        Habilidad.__init__(self, receptor)
        error = random.randint(-10, 10) / 10.0
        rectangulo = pilas.fisica.Rectangulo(receptor.x + error,
                                             receptor.y + error,
                                             receptor.radio_de_colision*2 - 4,
                                             receptor.radio_de_colision*2 - 4,
                                             )
        receptor.aprender(pilas.habilidades.Imitar, rectangulo)
        self.rectangulo = rectangulo

    def eliminar(self):
        self.rectangulo.eliminar()


class ColisionableComoPelota(RebotarComoPelota):

    def __init__(self, receptor):
        RebotarComoPelota.__init__(self, receptor)

    def actualizar(self):
        self.figura.body.position.x = self.receptor.x
        self.figura.body.position.y = self.receptor.y

    def eliminar(self):
        pilas.fisica.fisica.eliminar(self.figura)

class SeguirAlMouse(Habilidad):
    "Hace que un actor siga la posición del mouse en todo momento."

    def __init__(self, receptor):
        Habilidad.__init__(self, receptor)
        pilas.escena_actual().mueve_mouse.conectar(self.mover)

    def mover(self, evento):
        self.receptor.x = evento.x
        self.receptor.y = evento.y

class RotarConMouse(Habilidad):
    """"Hace que un actor rote con respecto a la posicion del mouse.
    
    param: lado_seguimiento: Establece el lado del actor que rotará para estar
    encarado hacia el puntero del mouse.
    
        >>> actor.aprender(pilas.habilidades.RotarConMouse, lado_seguimiento=pilas.habilidades.RotarConMouse.ABAJO)
    
    """
    ARRIBA = 270
    ABAJO = 90
    IZQUIERDA = 180
    DERECHA = 0
    
    def __init__(self, receptor, lado_seguimiento=ARRIBA):
        Habilidad.__init__(self, receptor)
        pilas.escena_actual().mueve_mouse.conectar(self.rotar)
        self.lado_seguimiento = lado_seguimiento

    def rotar(self, evento):
        deltax = evento.x - self.receptor.x
        deltay = evento.y - self.receptor.y

        angle_rad = atan2(deltay, deltax)
        angle_deg = angle_rad * 180.0 / pi

        self.receptor.rotacion = -(angle_deg) - self.lado_seguimiento

class AumentarConRueda(Habilidad):
    "Permite cambiar el tamaño de un actor usando la ruedita scroll del mouse."

    def __init__(self, receptor):
        Habilidad.__init__(self, receptor)
        pilas.escena_actual().mueve_rueda.conectar(self.cambiar_de_escala)

    def cambiar_de_escala(self, evento):
        self.receptor.escala += (evento.delta / 4.0)


class SeguirClicks(Habilidad):
    "Hace que el actor se coloque la posición del cursor cuando se hace click."

    def __init__(self, receptor):
        Habilidad.__init__(self, receptor)
        pilas.escena_actual().click_de_mouse.conectar(self.moverse_a_este_punto)

    def moverse_a_este_punto(self, evento):
        if (evento.boton == 1):
            self.receptor.x = [evento.x], 0.5
            self.receptor.y = [evento.y], 0.5


class Arrastrable(Habilidad):
    """Hace que un objeto se pueda arrastrar con el puntero del mouse.

    Cuando comienza a mover al actor se llama al metodo ''comienza_a_arrastrar''
    y cuando termina llama a ''termina_de_arrastrar''. Estos nombres
    de metodos se llaman para que puedas personalizar estos eventos, dado
    que puedes usar polimorfismo para redefinir el comportamiento
    de estos dos metodos. Observa un ejemplo de esto en
    el ejemplo ``pilas.ejemplos.Piezas``.
    """

    def __init__(self, receptor):
        Habilidad.__init__(self, receptor)
        pilas.escena_actual().click_de_mouse.conectar(self.cuando_intenta_arrastrar)

    def cuando_intenta_arrastrar(self, evento):
        "Intenta mover el objeto con el mouse cuando se pulsa sobre el."
        if (evento.boton == 1):
            if self.receptor.colisiona_con_un_punto(evento.x, evento.y):
                pilas.escena_actual().termina_click.conectar(self.cuando_termina_de_arrastrar, id='cuando_termina_de_arrastrar')
                pilas.escena_actual().mueve_mouse.conectar(self.cuando_arrastra, id='cuando_arrastra')
                self.comienza_a_arrastrar()

    def cuando_arrastra(self, evento):
        "Arrastra el actor a la posicion indicada por el puntero del mouse."
        if self._el_receptor_tiene_fisica():
            pilas.escena_actual().fisica.cuando_mueve_el_mouse(evento.x, evento.y)
        else:
            self.receptor.x += evento.dx
            self.receptor.y += evento.dy

    def cuando_termina_de_arrastrar(self, evento):
        "Suelta al actor porque se ha soltado el botón del mouse."
        pilas.escena_actual().mueve_mouse.desconectar_por_id(id='cuando_arrastra')
        self.termina_de_arrastrar()
        pilas.escena_actual().termina_click.desconectar_por_id(id='cuando_termina_de_arrastrar')

    def comienza_a_arrastrar(self):
        if self._el_receptor_tiene_fisica():
            pilas.escena_actual().fisica.capturar_figura_con_el_mouse(self.receptor.figura)

    def termina_de_arrastrar(self):
        if self._el_receptor_tiene_fisica():
            pilas.escena_actual().fisica.cuando_suelta_el_mouse()

    def _el_receptor_tiene_fisica(self):
        return hasattr(self.receptor, 'figura')


class MoverseConElTeclado(Habilidad):
    """Hace que un actor cambie de posición con pulsar el teclado.
    
    param: con_wasd: Valor booleano que indica si se desea que el movimientos
    se realice con las teclas W,A,S,D."""

    def __init__(self, receptor, control=None):
        Habilidad.__init__(self, receptor)
        pilas.escena_actual().actualizar.conectar(self.on_key_press)

        if control == None:
            self.control = self.receptor.escena.control
        else:
            self.control = control

    def on_key_press(self, evento):
        velocidad = 5
        
        c = self.control

        if c.izquierda:
            self.receptor.x -= velocidad
        elif c.derecha:
            self.receptor.x += velocidad

        if c.arriba:
            self.receptor.y += velocidad
        elif c.abajo:
            self.receptor.y -= velocidad

class PuedeExplotar(Habilidad):
    "Hace que un actor se pueda hacer explotar invocando al metodo eliminar."

    def __init__(self, receptor):
        Habilidad.__init__(self, receptor)
        receptor.eliminar = self.eliminar_y_explotar

    def eliminar_y_explotar(self):
        explosion = pilas.actores.Explosion()
        explosion.x = self.receptor.x
        explosion.y = self.receptor.y
        explosion.escala = self.receptor.escala * 2
        pilas.actores.Actor.eliminar(self.receptor)


class SeMantieneEnPantalla(Habilidad):
    """Se asegura de que el actor regrese a la pantalla si sale o que no
    salga en nigún momento de la pantalla.

    Si el actor sale por la derecha de la pantalla, entonces regresa
    por la izquiera. Si sale por arriba regresa por abajo y asi...
    
    param: permitir_salida: Valor booleano que establece si el actor
    puede salir por los lados de la ventana y regresar por el lado opuesto.
    Si se establece a False, el actor no puede salir de la ventana en ningún
    momento.
    """
    def __init__(self, receptor, permitir_salida=True):
        Habilidad.__init__(self, receptor)
        self.ancho, self.alto = pilas.mundo.motor.obtener_area()
        self.permitir_salida = permitir_salida

    def actualizar(self):
        if self.permitir_salida :
            # Se asegura de regresar por izquierda y derecha.
            if self.receptor.derecha < -(self.ancho/2):
                self.receptor.izquierda = (self.ancho/2)
            elif self.receptor.izquierda > (self.ancho/2):
                self.receptor.derecha = -(self.ancho/2)
    
            # Se asegura de regresar por arriba y abajo.
            if self.receptor.abajo > (self.alto/2):
                self.receptor.arriba = -(self.alto/2)
            elif self.receptor.arriba < -(self.alto/2):
                self.receptor.abajo = (self.alto/2)
        else:
            if self.receptor.izquierda <= -(self.ancho/2):
                self.receptor.izquierda = -(self.ancho/2)
            elif self.receptor.derecha >=  (self.ancho/2):
                self.receptor.derecha = self.ancho/2

            if self.receptor.arriba > (self.alto/2):
                self.receptor.arriba = (self.alto/2)
            elif self.receptor.abajo < -(self.alto/2):
                self.receptor.abajo = -(self.alto/2)

class PisaPlataformas(Habilidad):

    def __init__(self, receptor):
        Habilidad.__init__(self, receptor)
        error = random.randint(-10, 10) / 10.0
        self.figura = pilas.fisica.fisica.crear_figura_cuadrado(receptor.x + error,
                                                               receptor.y + error,
                                                               receptor.radio_de_colision,
                                                               masa=10,
                                                               elasticidad=0,
                                                               friccion=0)
        self.ultimo_x = receptor.x
        self.ultimo_y = receptor.y

    def actualizar(self):
        # Mueve el objeto siempre y cuando no parezca que algo
        # no fisico (es decir de pymunk) lo ha afectado.
        self.receptor.x = self.figura.body.position.x
        self.receptor.y = self.figura.body.position.y

    def eliminar(self):
        pilas.fisica.fisica.eliminar(self.figura)

class Imitar(Habilidad):

    def __init__(self, receptor, objeto_a_imitar, con_rotacion=True):
        Habilidad.__init__(self, receptor)
        self.objeto_a_imitar = objeto_a_imitar

        # Establecemos el mismo id para el actor y el objeto fisico
        # al que imita. Así luego en las colisiones fisicas sabremos a que
        # actor corresponde esa colisión.
        receptor.id = objeto_a_imitar.id

        # Y nos guardamos una referencia al objeto físico al que imita.
        # Posterormente en las colisiones fisicas comprobaremos si el
        # objeto tiene el atributo "figura" para saber si estamos delante
        # de una figura fisica o no.
        receptor.figura = objeto_a_imitar

        self.con_rotacion = con_rotacion

    def actualizar(self):
        self.receptor.x = self.objeto_a_imitar.x
        self.receptor.y = self.objeto_a_imitar.y
        if (self.con_rotacion):
            self.receptor.rotacion = self.objeto_a_imitar.rotacion

    def eliminar(self):
        if isinstance(self.objeto_a_imitar, pilas.fisica.Figura):
            self.objeto_a_imitar.eliminar()

