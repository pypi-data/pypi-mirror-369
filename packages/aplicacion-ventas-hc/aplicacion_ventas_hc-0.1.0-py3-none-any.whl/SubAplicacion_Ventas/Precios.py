class Precios:
    @staticmethod
    def calcular_precio_final(precio_base,impuesto,descuento):
        return precio_base + impuesto - descuento