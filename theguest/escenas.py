import os


import pygame as pg


from .import (ALTO, ANCHO, CENTRO_X, CENTRO_Y, COLORES, FPS, FUENTES, IMAGENES,
              MARGEN_INF, MARGEN_IZQ, MARGEN_SUP, TAM_FUENTE, TIEMPO_NIVEL)

from .entidades import IndicadorVida, Nave, Obstaculo, Planeta


class Escena:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.reloj = pg.time.Clock()
        self.tipo1 = pg.font.Font(FUENTES['nasa'], TAM_FUENTE['1'])
        self.tipo2 = pg.font.Font(FUENTES['nasa'], TAM_FUENTE['2'])
        self.tipo3 = pg.font.Font(FUENTES['nasa'], TAM_FUENTE['3'])
        self.tipo4 = pg.font.Font(FUENTES['contraste'], TAM_FUENTE['3'])
        self.tipo5 = pg.font.Font(FUENTES['contraste'], TAM_FUENTE['4'])
        ruta_sonido_explosion = os.path.join(
            'resources', 'music', 'explosion.mp3')
        self.efecto_sonido = pg.mixer.Sound(ruta_sonido_explosion)
        self.imagenes = []
        for i in range(2):
            ruta_image = os.path.join(
                'resources', 'images', f'sonido{i}.png')
            image = pg.image.load(ruta_image)
            self.imagenes.append(image)
        self.parpadeo_visible = True

    def bucle_principal(self):
        print('Metodo vacio bucle principal de escena')
        pass

    def pintar_texto(self, mensaje, tipo, pos_x, pos_y, alineacion, color, fondo):
        if fondo == True:
            self.pantalla.blit(self.image, (0, 0))
        for linea in mensaje:
            if '\n' in linea:
                linea = linea[:-1]
            texto = tipo.render(linea, True, color)
            if alineacion == 'centro':
                pos_x_centro = pos_x - (texto.get_width() / 2)
                self.pantalla.blit(texto, (pos_x_centro, pos_y))
            elif alineacion == 'derecha':
                pos_x_centro = pos_x - texto.get_width()
                self.pantalla.blit(texto, (pos_x_centro, pos_y))
            else:
                self.pantalla.blit(texto, (pos_x, pos_y))
            pos_y += texto.get_height()

    def comprobar_sonido(self):
        if self.sonido_activo:
            self.pantalla.blit(
                self.imagenes[0], (0, 0))
            self.musica = pg.mixer_music.set_volume(1.0)
            pg.mixer.Sound.set_volume(self.efecto_sonido, 1.0)
        else:
            self.pantalla.blit(
                self.imagenes[1], (0, 0))
            self.musica = pg.mixer_music.set_volume(0.0)
            pg.mixer.Sound.set_volume(self.efecto_sonido, 0.0)

    def temporizador(self, tiempo_inicial, tiempo_parpadeo):
        tiempo_actual = pg.time.get_ticks()
        if tiempo_actual - tiempo_inicial >= tiempo_parpadeo:
            self.parpadeo_visible = not self.parpadeo_visible
            self.tiempo_inicial = tiempo_actual


class Portada(Escena):
    tiempo_parpadeo = 600

    def __init__(self, pantalla, sonido_activo):
        super().__init__(pantalla)
        self.sonido_activo = sonido_activo
        self.image = pg.image.load(IMAGENES['portada']).convert()
        self.image = pg.transform.scale(self.image, (ANCHO, ALTO))
        self.tiempo_inicial = pg.time.get_ticks()

    def bucle_principal(self):
        super().bucle_principal()
        print('Estamos en la escena portada')
        while True:
            self.pintar_portada()
            self.comprobar_sonido()
            for evento in pg.event.get():
                if evento.type == pg.QUIT:
                    return 'salir', self.sonido_activo
                if evento.type == pg.KEYDOWN and evento.key == pg.K_SPACE:
                    return 'partida', self.sonido_activo
                if evento.type == pg.KEYDOWN and evento.key == pg.K_s:
                    self.sonido_activo = not self.sonido_activo

            pg.display.flip()

    def pintar_portada(self):
        estado_teclas = pg.key.get_pressed()
        self.pintar_titulo()
        self.pintar_info()
        self.pintar_historia()
        self.mostrar_instrucciones(estado_teclas)
        self.mostrar_records(estado_teclas)

    def pintar_titulo(self):
        self.pintar_texto(['THE QUEST',], self.tipo5, CENTRO_X,
                          ALTO * 16/20, 'centro', COLORES['verde'], True)

    def pintar_info(self):
        ruta_info = os.path.join('data', 'info.txt')
        with open(ruta_info, 'r', encoding='utf-8') as contenido:
            info = contenido.readlines()
        self.temporizador(self.tiempo_inicial, self.tiempo_parpadeo)
        if self.parpadeo_visible:
            self.pintar_texto(info, self.tipo2, CENTRO_X,
                              0, 'centro', COLORES['blanco'], False)

    def pintar_historia(self):
        ruta_historia = os.path.join('data', 'historia.txt')
        with open(ruta_historia, 'r', encoding='utf-8') as contenido:
            historia = contenido.readlines()
        self.pintar_texto(historia, self.tipo1, CENTRO_X,
                          ALTO * 10/20, 'centro', COLORES['blanco'], False)

    def mostrar_instrucciones(self, estado_teclas):
        ruta_instrucciones = os.path.join('data', 'instrucciones.txt')
        with open(ruta_instrucciones, 'r', encoding='utf-8') as contenido:
            instrucciones = contenido.readlines()
        if estado_teclas[pg.K_i]:
            self.pintar_texto(instrucciones, self.tipo1, MARGEN_IZQ,
                              ALTO * 7/20, '', COLORES['blanco'], True)

    def mostrar_records(self, estado_teclas):
        if estado_teclas[pg.K_r]:
            self.pantalla.blit(self.image, (0, 0))


class Partida(Escena):
    VEL_FONDO_PARTIDA = 1
    tiempo_parpadeo = 600

    def __init__(self, pantalla, dificultad, vidas, puntos, nivel, sonido_activo):
        super().__init__(pantalla)
        self.dificultad = self.dificultad_inicial = dificultad
        self.vidas = vidas
        self.puntos = puntos
        self.nivel = nivel
        self.sonido_activo = sonido_activo
        self.image = pg.image.load(IMAGENES['partida']).convert()
        self.image = pg.transform.scale(self.image, (ANCHO, ALTO))
        self.nave = Nave()
        self.planeta = Planeta()
        self.obstaculos = pg.sprite.Group()
        self.contador = 0
        self.crear_obstaculos()
        self.indicador_vidas = pg.sprite.Group()
        self.crear_vidas(self.vidas)
        self.pos_x_fondo = 0
        self.tiempo_inicial = pg.time.get_ticks()
        self.cambio_nivel_activo = False
        self.tiempo_nivel = pg.USEREVENT
        pg.time.set_timer(self.tiempo_nivel, TIEMPO_NIVEL)

    def bucle_principal(self):
        super().bucle_principal()
        print('Estamos en la escena partida')
        while True:
            self.reloj.tick(FPS)
            for evento in pg.event.get():
                if evento.type == pg.QUIT:
                    return 'salir', self.dificultad, self.vidas, self.puntos, self.nivel, self.sonido_activo
                if evento.type == pg.KEYDOWN and evento.key == pg.K_s:
                    self.sonido_activo = not self.sonido_activo
                if evento.type == pg.KEYDOWN and evento.key == pg.K_SPACE and self.cambio_nivel_activo:
                    self.nivel += 1
                    return 'partida', self.dificultad, self.vidas, self.puntos, self.nivel, self.sonido_activo
                if evento.type == pg.USEREVENT and not self.colision:
                    self.cambio_nivel_activo = True
            self.pintar_fondo()
            self.comprobar_sonido()
            self.pantalla.blit(self.nave.image, self.nave.rect)
            self.obstaculos.draw(self.pantalla)
            self.indicador_vidas.update()
            self.indicador_vidas.draw(self.pantalla)
            self.pintar_info()
            self.pantalla.blit(self.planeta.image, self.planeta.rect)
            if self.cambio_nivel_activo:
                self.update_obstaculos()
                self.planeta.update()
                self.nave.aterrizar_nave(self.planeta)
            else:
                accion = self.detectar_colision_nave()
                if accion == 'partida':
                    return 'partida', self.dificultad_inicial, self.vidas, self.puntos, self.nivel, self.sonido_activo
                elif accion == 'records':
                    return 'records', self.dificultad, self.vidas, self.puntos, self.nivel, self.sonido_activo

            pg.display.flip()

    def pintar_fondo(self):
        x_relativa = self.pos_x_fondo % ANCHO
        self.pantalla.blit(self.image, (x_relativa - ANCHO, 0))
        if x_relativa < ANCHO:
            self.pantalla.blit(self.image, (x_relativa, 0))
        self.pos_x_fondo -= self.nivel
        pg.draw.line(self.pantalla, COLORES['blanco'],
                     (0, MARGEN_INF), (ANCHO, MARGEN_INF))
        pg.draw.line(self.pantalla, COLORES['blanco'],
                     (0, MARGEN_SUP), (ANCHO, MARGEN_SUP))

    def crear_obstaculos(self):
        for i in range(self.dificultad):
            obstaculo = Obstaculo(self.dificultad)
            self.obstaculos.add(obstaculo)

    def update_obstaculos(self):
        for obstaculo in self.obstaculos:
            if not self.cambio_nivel_activo:
                self.puntos += obstaculo.update(self.obstaculos)
            else:
                obstaculo.update(self.obstaculos)
        if len(self.obstaculos) < self.dificultad - 3 and not self.cambio_nivel_activo:
            self.contador += 1
            if self.contador % 2 == 0:
                self.dificultad += 1
            self.crear_obstaculos()

    def detectar_colision_nave(self):
        for obstaculo in self.obstaculos:
            self.colision = pg.sprite.collide_mask(self.nave, obstaculo)
            if self.colision:
                break
        if self.colision:
            tiempo_actual = pg.time.get_ticks()
            self.nave.explosion_nave()
            if tiempo_actual - self.tiempo_inicial1 < FPS * 2:
                self.efecto_sonido.play()
            duracion_sonido = int(
                self.efecto_sonido.get_length() * 1000)
            if tiempo_actual - self.tiempo_inicial1 >= duracion_sonido:
                if len(self.indicador_vidas) > 1:
                    self.vidas -= 1
                    self.indicador_vidas.sprites()[-1].kill()
                    return 'partida'
                else:
                    return 'records'
        else:
            self.tiempo_inicial1 = pg.time.get_ticks()
            self.nave.update()
            self.update_obstaculos()
            return 'continuar'

    def crear_vidas(self, vidas):
        for vida in range(vidas):
            indicador = IndicadorVida()
            separador = indicador.rect.width / 2
            indicador.rect.center = (indicador.rect.width * vida + MARGEN_IZQ + separador * vida + indicador.rect.width / 2,
                                     ALTO - (ALTO - MARGEN_INF) / 2)
            self.indicador_vidas.add(indicador)

    def pintar_info(self):
        # Pintar Puntos
        self.pintar_texto([str(self.puntos),], self.tipo3, MARGEN_IZQ,
                          0, '', COLORES['blanco'], False)
        # Pintar Nivel
        self.pintar_texto(['Nivel ' + str(self.nivel),], self.tipo3, ANCHO * 4/5,
                          0, '', COLORES['blanco'], False)
        # Pintar Titulo
        self.pintar_texto(['The Guest',], self.tipo4, CENTRO_X,
                          0, 'centro', COLORES['blanco'], False)
        # Pintar mejor jugador
        self.pintar_texto(['High Score' + str(self.nivel),], self.tipo3, CENTRO_X,
                          MARGEN_INF, '', COLORES['blanco'], False)
        # Pintar instrucciones para continuar
        self.temporizador(self.tiempo_inicial, self.tiempo_parpadeo)
        if self.parpadeo_visible and self.cambio_nivel_activo:
            self.pintar_texto(['Nivel completado pulsar <ESPACIO> para continuar',], self.tipo2, CENTRO_X,
                              MARGEN_SUP, 'centro', COLORES['blanco'], False)


class Records(Escena):
    def __init__(self, pantalla, sonido_activo):
        super().__init__(pantalla)
        self.sonido_activo = sonido_activo
        self.image = pg.image.load(IMAGENES['records']).convert()
        self.image = pg.transform.scale(self.image, (ANCHO, ALTO))

    def bucle_principal(self):
        super().bucle_principal()
        print('Estamos en la escena records')
        while True:
            for evento in pg.event.get():
                if evento.type == pg.QUIT:
                    return 'salir', self.sonido_activo
                if evento.type == pg.KEYDOWN and evento.key == pg.K_s:
                    self.sonido_activo = not self.sonido_activo
            self.pantalla.blit(self.image, (0, 0))
            self.comprobar_sonido()
            pg.display.flip()