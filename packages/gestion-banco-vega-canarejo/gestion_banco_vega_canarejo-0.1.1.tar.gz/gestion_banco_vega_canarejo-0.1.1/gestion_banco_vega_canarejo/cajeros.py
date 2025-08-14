from .cuentas import CuentaAhorros

class Cajero:
    """Clase que representa un cajero bancario"""
    
    def __init__(self, nombre: str, id_cajero: str = None):
        """
        Inicializa un nuevo cajero
        
        Args:
            nombre (str): Nombre o ubicación del cajero
            id_cajero (str, optional): Identificador único del cajero
        """
        self.nombre = nombre
        self.id = id_cajero

    def crear_cuenta(self, cliente, numero_cuenta: str) -> CuentaAhorros:
        """
        Crea una nueva cuenta de ahorros
        
        Args:
            cliente (Cliente): Cliente asociado a la cuenta
            numero_cuenta (str): Número de cuenta
            
        Returns:
            CuentaAhorros: La nueva cuenta creada
        """
        cuenta = CuentaAhorros(numero_cuenta, cliente)
        print(f"Cajero {self.nombre} creó la cuenta {numero_cuenta} para el cliente {cliente.nombre}.")
        return cuenta

    def registrar_deposito(self, cuenta: CuentaAhorros, monto: float):
        """
        Registra un depósito en una cuenta
        
        Args:
            cuenta (CuentaAhorros): Cuenta destino
            monto (float): Cantidad a depositar
        """
        print(f"Cajero {self.nombre} procesa depósito de ${monto:.2f} en la cuenta {cuenta.numero_cuenta}.")
        exitosa = cuenta.depositar(monto)
        if exitosa:
            print(f"Depósito realizado correctamente. Nuevo saldo: ${cuenta.obtener_saldo():.2f}\n")

    def registrar_retiro(self, cuenta: CuentaAhorros, monto: float):
        """
        Registra un retiro de una cuenta
        
        Args:
            cuenta (CuentaAhorros): Cuenta origen
            monto (float): Cantidad a retirar
        """
        print(f"Cajero {self.nombre} procesa retiro de ${monto:.2f} en la cuenta {cuenta.numero_cuenta}.")
        exitosa = cuenta.retirar(monto)
        if exitosa:
            print(f"Retiro realizado correctamente. Nuevo saldo: ${cuenta.obtener_saldo():.2f}\n")
            