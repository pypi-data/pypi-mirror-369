from .Descuentos import Descuentos
from .Impuestos import Impuestos
from .Precios import Precios

class Gestion_Ventas:
    def __init__(self,precio_base,impuesto_porcentaje,descuento_porcentaje):
        self.precio_base = precio_base
        self.impuesto = Impuestos(impuesto_porcentaje)
        self.descuento = Descuentos(descuento_porcentaje)

    def calcular_precio_final(self):
        impuesto_aplicado = self.impuesto.aplicar_impuesto(self.precio_base)
        descuento_aplicado = self.descuento.aplicar_descuento(self.precio_base)
        precio_final = Precios.calcular_precio_final(self.precio_base,impuesto_aplicado,descuento_aplicado)
        return round(precio_final,2)

