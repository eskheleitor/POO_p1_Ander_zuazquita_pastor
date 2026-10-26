
class CintaTransportadora:

    def __init__(self, nombre, velocidad, direccion):
        self.nombre = nombre
        self.velocidad = velocidad
        self.direccion = direccion
        self.activa = True

    def arrancar(self):
        self.activa = True

    def detener(self):
        self.activa = False

    def conmutar(self):
        self.activa = not self.activa

    def esta_activa(self):
        return self.activa
    
    def obtener_direccion(self):
        return self.direccion
