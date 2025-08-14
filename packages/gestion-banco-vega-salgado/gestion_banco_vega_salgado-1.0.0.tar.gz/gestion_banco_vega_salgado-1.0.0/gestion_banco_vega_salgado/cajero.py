from .cuenta import CuentaAhorros

class Cajero:
    def __init__(self, nombre: str, id_cajero: str = None):
        self.nombre = nombre
        self.id = id_cajero

    def crear_cuenta(self, cliente, numero_cuenta: str) -> CuentaAhorros:
        cuenta = CuentaAhorros(numero_cuenta, cliente)
        print(f"Cajero {self.nombre} creó la cuenta {numero_cuenta} para el cliente {cliente.nombre}.")
        return cuenta

    def registrar_deposito(self, cuenta: CuentaAhorros, monto: float):
        print(f"Cajero {self.nombre} procesa depósito de ${monto:.2f} en la cuenta {cuenta.numero_cuenta}.")
        if cuenta.depositar(monto):
            print(f"Depósito realizado correctamente. Nuevo saldo: ${cuenta.obtener_saldo():.2f}\n")

    def registrar_retiro(self, cuenta: CuentaAhorros, monto: float):
        print(f"Cajero {self.nombre} procesa retiro de ${monto:.2f} en la cuenta {cuenta.numero_cuenta}.")
        if cuenta.retirar(monto):
            print(f"Retiro realizado correctamente. Nuevo saldo: ${cuenta.obtener_saldo():.2f}\n")
