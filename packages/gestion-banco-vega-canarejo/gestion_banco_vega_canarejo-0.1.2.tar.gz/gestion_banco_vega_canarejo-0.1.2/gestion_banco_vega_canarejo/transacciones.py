from datetime import datetime

class Transaccion:
    """Clase que representa una transacción bancaria"""
    
    def __init__(self, tipo: str, monto: float):
        """
        Inicializa una nueva transacción
        
        Args:
            tipo (str): Tipo de transacción ("Depósito" o "Retiro")
            monto (float): Cantidad de dinero involucrada
        """
        self.tipo = tipo
        self.monto = monto
        self.fecha = datetime.now()
        self.estado = "Exitosa"

    def obtener_detalles(self) -> str:
        """Devuelve los detalles de la transacción"""
        return (f"Tipo: {self.tipo}\n"
                f"Monto: ${self.monto:.2f}\n"
                f"Fecha: {self.fecha.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Estado: {self.estado}")

    def imprimir_comprobante(self):
        """Imprime un comprobante de la transacción"""
        print("----- Comprobante de Transacción -----")
        print(self.obtener_detalles())
        print("-------------------------------------\n")
        