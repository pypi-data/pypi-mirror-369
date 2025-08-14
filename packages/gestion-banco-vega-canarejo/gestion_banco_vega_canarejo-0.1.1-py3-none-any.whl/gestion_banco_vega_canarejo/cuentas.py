from .transacciones import Transaccion

class CuentaAhorros:
    """Clase que representa una cuenta de ahorros bancaria"""
    
    def __init__(self, numero_cuenta: str, cliente):
        """
        Inicializa una nueva cuenta de ahorros
        
        Args:
            numero_cuenta (str): Número de cuenta
            cliente (Cliente): Objeto Cliente asociado a la cuenta
        """
        self.numero_cuenta = numero_cuenta
        self.cliente = cliente
        self.saldo = 0.0
        self.transacciones = []

    def depositar(self, monto: float) -> bool:
        """
        Realiza un depósito en la cuenta
        
        Args:
            monto (float): Cantidad a depositar
            
        Returns:
            bool: True si el depósito fue exitoso, False en caso contrario
        """
        if monto <= 0:
            print("Error: El monto a depositar debe ser positivo.")
            return False
        self.saldo += monto
        transaccion = Transaccion("Depósito", monto)
        self.transacciones.append(transaccion)
        transaccion.imprimir_comprobante()
        return True

    def retirar(self, monto: float) -> bool:
        """
        Realiza un retiro de la cuenta
        
        Args:
            monto (float): Cantidad a retirar
            
        Returns:
            bool: True si el retiro fue exitoso, False en caso contrario
        """
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
        """Devuelve el saldo actual de la cuenta"""
        return self.saldo

    def obtener_historial(self) -> list:
        """Devuelve el historial de transacciones"""
        return self.transacciones
    