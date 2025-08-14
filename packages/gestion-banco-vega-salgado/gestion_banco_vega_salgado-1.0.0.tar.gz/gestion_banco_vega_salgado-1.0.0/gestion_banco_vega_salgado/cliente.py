class Cliente:
    def __init__(self, nombre: str, identificacion: str):
        self.nombre = nombre
        self.identificacion = identificacion

    def obtener_datos(self) -> str:
        return f"Cliente: {self.nombre}, ID: {self.identificacion}"
