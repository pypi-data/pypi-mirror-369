from datetime import datetime

class Transaccion:
    def __init__(self, tipo: str, monto: float):
        self.tipo = tipo
        self.monto = monto
        self.fecha = datetime.now()
        self.estado = "Exitosa"

    def obtener_detalles(self) -> str:
        return (f"Tipo: {self.tipo}\n"
                f"Monto: ${self.monto:.2f}\n"
                f"Fecha: {self.fecha.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Estado: {self.estado}")

    def imprimir_comprobante(self):
        print("----- Comprobante de Transacción -----")
        print(self.obtener_detalles())
        print("-------------------------------------\n")
