
import cv2


class CamaraInspeccion:
    def __init__(self, nombre, nombre_camara, cinta):
        self.nombre = nombre
        self.nombre_camara = nombre_camara
        self.cinta = cinta
        self.objeto_detectado = False
        self.forma_detectada = None

    def capturar(self, renderer, data):
        # Captura la imagen de la cámara de MuJoCo.
        renderer.update_scene(data, camera=self.nombre_camara)
        imagen_rgb = renderer.render()

        # Convierte la imagen de RGB a BGR para trabajar con OpenCV.
        imagen = cv2.cvtColor(imagen_rgb, cv2.COLOR_RGB2BGR)

        return imagen

    def actualizar(self, renderer, data):
        imagen = self.capturar(renderer, data)

        self.forma_detectada = self.detectar_forma(imagen)
        self.objeto_detectado = self.forma_detectada is not None

        if self.objeto_detectado and self.cinta.esta_activa():
            self.cinta.detener()

        return imagen
    
   
    def detectar_forma(self, imagen):
    # 1. Convierte la imagen a escala de grises.
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    # 2. Separa los objetos del fondo.
        _, umbral = cv2.threshold(
            gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

    # 3. Busca los contornos.
        contornos, _ = cv2.findContours(
            umbral, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if len(contornos) == 0:
            return None

        alto, ancho = gris.shape
        area_imagen = alto * ancho

    # 4. Examina los contornos de mayor a menor.
        contornos = sorted(contornos, key=cv2.contourArea, reverse=True)

        for contorno in contornos:
            area = cv2.contourArea(contorno)

        # Ignora objetos demasiado pequeños o grandes.
            if area < 500 or area > area_imagen * 0.40:
                continue

        # 5. Calcula el color medio dentro del contorno.
            mascara = imagen[:, :, 0] * 0
            cv2.drawContours(mascara, [contorno], -1, 255, -1)

            azul, verde, rojo, _ = cv2.mean(imagen, mask=mascara)

        # 6. Clasifica por el color de las piezas.
        # Azul y verde: cilindros.
            if azul > rojo * 1.25 and azul > verde * 1.15:
                return "circulo_cilindro"

            if verde > rojo * 1.15 and verde > azul * 1.10:
                return "circulo_cilindro"

        # Rojo, amarillo y morado: cajas.
            if rojo > verde * 1.25 and rojo > azul * 1.25:
                return "cuadrado_rectangulo"

            if rojo > azul * 1.20 and verde > azul * 1.15:
                return "cuadrado_rectangulo"

            if azul > verde * 1.15 and rojo > verde * 1.15:
                return "cuadrado_rectangulo"

        # 7. Si el color no es concluyente, usa la geometría.
            perimetro = cv2.arcLength(contorno, True)

            if perimetro == 0:
                continue

            aproximacion = cv2.approxPolyDP(
                contorno, 0.04 * perimetro, True
            )

            vertices = len(aproximacion)

            
            if vertices == 4:
                return "cuadrado_rectangulo"
            elif vertices >= 5:
                return "circulo_cilindro"

        return None

    
    def probar_deteccion(self, renderer, data):
        # Captura una imagen de esta cámara.
        imagen = self.capturar(renderer, data)

        # Intenta reconocer la forma que aparece en la imagen.
        forma = self.detectar_forma(imagen)

        # Muestra el resultado en la consola.
        print(self.nombre, "Forma detectada:", forma)

        # Devuelve la imagen para poder visualizarla.
        return imagen
