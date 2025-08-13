# gestion_banco_taipe

Paquete Python para gestionar operaciones bancarias con Programación Orientada a Objetos.

## Instalación
```bash
pip install gestion_banco_taipe

from gestion_banco_taipe import Cliente, Cajero

cliente1 = Cliente("Juan Pérez", "12345")
cajero = Cajero("Pedro Gómez")
cuenta = cajero.crear_cuenta(cliente1, "001")

cajero.registrar_deposito(cuenta, 1000)
cajero.registrar_retiro(cuenta, 200)
