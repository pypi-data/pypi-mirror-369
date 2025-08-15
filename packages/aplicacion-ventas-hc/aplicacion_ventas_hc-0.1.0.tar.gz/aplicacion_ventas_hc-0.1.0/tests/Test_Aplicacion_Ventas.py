#Libreria interna de python para pruebas
import unittest
from SubAplicacion_Ventas.Gestor_Ventas import Gestion_Ventas
from SubAplicacion_Ventas.Exceptions import ImpuestoInvalidoError,DescuentoInvalidoError

class TestGestorVentas(unittest.TestCase):
    def test_calculo_precio_final(self):
        gestor = Gestion_Ventas(100,0.15,0.10)
        self.assertEqual(gestor.calcular_precio_final(),95.00)
        #El resultado esperado es 105, al ponerle 95 sera diferente y marcara error

    def test_impuesto_invalido(self):
        with self.assertRaises(ImpuestoInvalidoError):
            Gestion_Ventas(100.0,1.5,0.10) #La tasa de impuesto intencinalmente mayor a 1

    def test_descuento_invalido(self):
        with self.assertRaises(DescuentoInvalidoError):
            Gestion_Ventas(100.00,0.05,1.5) #Descuento mayor a 1 para detectar si lo valida

if __name__ == "__main__":
    unittest.main()

