class Cliente:
    """Clase que representa a un cliente del banco"""
    
    def __init__(self, nombre: str, identificacion: str):
        """
        Inicializa un nuevo cliente
        
        Args:
            nombre (str): Nombre completo del cliente
            identificacion (str): Número de identificación
        """
        self.nombre = nombre
        self.identificacion = identificacion

    def obtener_datos(self) -> str:
        """Devuelve los datos del cliente en formato string"""
        return f"Cliente: {self.nombre}, ID: {self.identificacion}"
    