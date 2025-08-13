from datetime import datetime

class Cliente:
    def __init__(self, nombre: str, identificacion: str):
        self.nombre = nombre
        self.identificacion = identificacion

    def obtener_datos(self) -> str:
        return f"Cliente: {self.nombre}, ID: {self.identificacion}"

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

class CuentaAhorros:
    def __init__(self, numero_cuenta: str, cliente: Cliente):
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

class Cajero:
    def __init__(self, nombre: str, id_cajero: str = None):
        self.nombre = nombre
        self.id = id_cajero

    def crear_cuenta(self, cliente: Cliente, numero_cuenta: str) -> CuentaAhorros:
        cuenta = CuentaAhorros(numero_cuenta, cliente)
        print(f"Cajero {self.nombre} creó la cuenta {numero_cuenta} para el cliente {cliente.nombre}.")
        return cuenta

    def registrar_deposito(self, cuenta: CuentaAhorros, monto: float):
        print(f"Cajero {self.nombre} procesa depósito de ${monto:.2f} en la cuenta {cuenta.numero_cuenta}.")
        exitosa = cuenta.depositar(monto)
        if exitosa:
            print(f"Depósito realizado correctamente. Nuevo saldo: ${cuenta.obtener_saldo():.2f}\n")

    def registrar_retiro(self, cuenta: CuentaAhorros, monto: float):
        print(f"Cajero {self.nombre} procesa retiro de ${monto:.2f} en la cuenta {cuenta.numero_cuenta}.")
        exitosa = cuenta.retirar(monto)
        if exitosa:
            print(f"Retiro realizado correctamente. Nuevo saldo: ${cuenta.obtener_saldo():.2f}\n")
