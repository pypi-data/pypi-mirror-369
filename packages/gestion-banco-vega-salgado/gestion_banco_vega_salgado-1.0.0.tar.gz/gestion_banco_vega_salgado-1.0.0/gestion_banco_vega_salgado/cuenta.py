from .transaccion import Transaccion

class CuentaAhorros:
    def __init__(self, numero_cuenta: str, cliente):
        self.numero_cuenta = numero_cuenta
        self.cliente = cliente
        self.saldo = 0.0
        self.transacciones = []

    def depositar(self, monto: float) -> bool:
        if monto <= 0:
            print("Error: El monto a depositar debe ser positivo.")
            return False
        self.saldo += monto
        transaccion = Transaccion("Depósito", monto)
        self.transacciones.append(transaccion)
        transaccion.imprimir_comprobante()
        return True

    def retirar(self, monto: float) -> bool:
        if monto <= 0:
            print("Error: El monto a retirar debe ser positivo.")
            return False
        if monto > self.saldo:
            print("Error: Saldo insuficiente para realizar el retiro.")
            return False
        self.saldo -= monto
        transaccion = Transaccion("Retiro", monto)
        self.transacciones.append(transaccion)
        transaccion.imprimir_comprobante()
        return True

    def obtener_saldo(self) -> float:
        return self.saldo
