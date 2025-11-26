"""
models.py - Modelos de Datos del Sistema UNIETAXI

Define las clases Cliente, Taxi y Servicio con toda su lógica.
"""

from dataclasses import dataclass, field
from typing import Tuple, Optional
from datetime import datetime
import config

# ==================== CLASE CLIENTE ====================

@dataclass
class Cliente:
    """
    Representa un cliente del sistema UNIETAXI.
    
    Atributos:
        cedula: Identificador único del cliente
        nombre: Nombre del cliente
        apellido: Apellido del cliente
        tarjeta: Número de tarjeta de crédito
        ubicacion_actual: Coordenadas (lat, lng) actuales
        destino: Coordenadas (lat, lng) de destino
        taxi_asignado: ID del taxi asignado (si hay)
        en_servicio: Si está actualmente en un servicio
    """
    cedula: int
    nombre: str
    apellido: str
    tarjeta: str
    ubicacion_actual: Tuple[float, float] = (0.0, 0.0)
    destino: Tuple[float, float] = (0.0, 0.0)
    taxi_asignado: Optional[int] = None
    en_servicio: bool = False
    fecha_registro: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    estado: str = "activo"
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} (CI: {self.cedula})"
    
    def nombre_completo(self):
        """Retorna el nombre completo del cliente"""
        return f"{self.nombre} {self.apellido}"
    
    def tarjeta_enmascarada(self):
        """Retorna la tarjeta enmascarada para seguridad"""
        return f"**** **** **** {self.tarjeta[-4:]}"
    
    def to_dict(self):
        """Convierte el cliente a diccionario para JSON"""
        return {
            "cedula": self.cedula,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "nombre_completo": self.nombre_completo(),
            "tarjeta": self.tarjeta,
            "tarjeta_enmascarada": self.tarjeta_enmascarada(),
            "ubicacion_actual": self.ubicacion_actual,
            "destino": self.destino,
            "taxi_asignado": self.taxi_asignado,
            "en_servicio": self.en_servicio,
            "fecha_registro": self.fecha_registro,
            "estado": self.estado
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea un cliente desde un diccionario"""
        return cls(
            cedula=data.get("cedula", 0),
            nombre=data.get("nombre", ""),
            apellido=data.get("apellido", ""),
            tarjeta=data.get("tarjeta", ""),
            ubicacion_actual=tuple(data.get("ubicacion_actual", (0.0, 0.0))),
            destino=tuple(data.get("destino", (0.0, 0.0))),
            taxi_asignado=data.get("taxi_asignado"),
            en_servicio=data.get("en_servicio", False),
            fecha_registro=data.get("fecha_registro", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            estado=data.get("estado", "activo")
        )


# ==================== CLASE TAXI ====================

@dataclass
class Taxi:
    """
    Representa un taxi del sistema UNIETAXI.
    
    Atributos:
        id_taxi: Identificador único del taxi en el sistema
        cedula: Cédula del conductor
        nombre: Nombre del conductor
        apellido: Apellido del conductor
        placa: Placa del vehículo
        marca: Marca del vehículo
        modelo: Modelo del vehículo
        velocidad: Velocidad promedio en km/h
        ubicacion: Coordenadas (lat, lng) actuales
        disponible: Si está disponible para asignación
        calificacion_total: Suma de todas las calificaciones
        cantidad_servicios: Número total de servicios realizados
        ganancia_diaria: Ganancias del día actual
        ganancia_total: Ganancias acumuladas
        cliente_actual: Cédula del cliente asignado
    """
    id_taxi: int
    cedula: int
    nombre: str
    apellido: str
    placa: str
    marca: str
    modelo: str
    velocidad: int  # km/h
    ubicacion: Tuple[float, float] = (0.0, 0.0)
    disponible: bool = True
    calificacion_total: float = config.CALIFICACIONES["INICIAL"]
    cantidad_servicios: int = 0
    ganancia_diaria: float = 0.0
    ganancia_total: float = 0.0
    cliente_actual: Optional[int] = None
    fecha_registro: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    estado: str = "activo"
    color_mapa: str = "blue"  # Color para visualización en mapa
    
    def calcular_calificacion_promedio(self) -> float:
        """Retorna la calificación promedio del taxi"""
        if self.cantidad_servicios == 0:
            return config.CALIFICACIONES["INICIAL"]
        return self.calificacion_total / self.cantidad_servicios
    
    def agregar_calificacion(self, calificacion: int):
        """Agrega una nueva calificación al taxi"""
        if config.CALIFICACIONES["MINIMA"] <= calificacion <= config.CALIFICACIONES["MAXIMA"]:
            self.calificacion_total += calificacion
            self.cantidad_servicios += 1
        else:
            raise ValueError(f"Calificación debe estar entre {config.CALIFICACIONES['MINIMA']} y {config.CALIFICACIONES['MAXIMA']}")
    
    def agregar_ganancia(self, monto: float):
        """Agrega ganancia al taxi"""
        if monto > 0:
            self.ganancia_diaria += monto
            self.ganancia_total += monto
    
    def resetear_ganancia_diaria(self):
        """Resetea la ganancia diaria (usado en cierre contable)"""
        self.ganancia_diaria = 0.0
    
    def calcular_comision_empresa(self) -> float:
        """Calcula la comisión que se lleva UNIETAXI (20%)"""
        return self.ganancia_total * config.TAXI_CONFIG["COMISION_EMPRESA"]
    
    def calcular_ganancia_neta(self) -> float:
        """Calcula la ganancia neta del taxista (80%)"""
        return self.ganancia_total * (1 - config.TAXI_CONFIG["COMISION_EMPRESA"])
    
    def __str__(self):
        return f"Taxi {self.placa} - {self.nombre} {self.apellido}"
    
    def nombre_completo(self):
        """Retorna el nombre completo del conductor"""
        return f"{self.nombre} {self.apellido}"
    
    def to_dict(self):
        """Convierte el taxi a diccionario para JSON"""
        return {
            "id_taxi": self.id_taxi,
            "cedula": self.cedula,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "nombre_completo": self.nombre_completo(),
            "placa": self.placa,
            "marca": self.marca,
            "modelo": self.modelo,
            "velocidad": self.velocidad,
            "ubicacion": self.ubicacion,
            "disponible": self.disponible,
            "calificacion_promedio": round(self.calcular_calificacion_promedio(), 2),
            "cantidad_servicios": self.cantidad_servicios,
            "ganancia_diaria": round(self.ganancia_diaria, 2),
            "ganancia_total": round(self.ganancia_total, 2),
            "comision_empresa": round(self.calcular_comision_empresa(), 2),
            "ganancia_neta": round(self.calcular_ganancia_neta(), 2),
            "cliente_actual": self.cliente_actual,
            "fecha_registro": self.fecha_registro,
            "estado": self.estado,
            "color_mapa": self.color_mapa
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea un taxi desde un diccionario"""
        return cls(
            id_taxi=data.get("id_taxi", 0),
            cedula=data.get("cedula", 0),
            nombre=data.get("nombre", ""),
            apellido=data.get("apellido", ""),
            placa=data.get("placa", ""),
            marca=data.get("marca", "Toyota"),
            modelo=data.get("modelo", "Corolla"),
            velocidad=data.get("velocidad", 60),
            ubicacion=tuple(data.get("ubicacion", (0.0, 0.0))),
            disponible=data.get("disponible", True),
            calificacion_total=data.get("calificacion_total", config.CALIFICACIONES["INICIAL"]),
            cantidad_servicios=data.get("cantidad_servicios", 0),
            ganancia_diaria=data.get("ganancia_diaria", 0.0),
            ganancia_total=data.get("ganancia_total", 0.0),
            cliente_actual=data.get("cliente_actual"),
            fecha_registro=data.get("fecha_registro", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            estado=data.get("estado", "activo"),
            color_mapa=data.get("color_mapa", "blue")
        )


# ==================== CLASE SERVICIO ====================

@dataclass
class Servicio:
    """
    Representa un servicio de taxi.
    
    Atributos:
        id_servicio: Identificador único del servicio
        id_taxi: ID del taxi que realizó el servicio
        id_cliente: Cédula del cliente
        origen: Coordenadas de origen
        destino: Coordenadas de destino
        distancia_km: Distancia en kilómetros
        costo: Costo total del servicio
        calificacion: Calificación otorgada por el cliente
        dia: Día en que se realizó el servicio
        completado: Si el servicio fue completado
        timestamp: Hora exacta del servicio
        en_seguimiento: Si el servicio está siendo monitoreado
    """
    id_servicio: int
    id_taxi: int
    id_cliente: int
    origen: Tuple[float, float]
    destino: Tuple[float, float]
    distancia_km: float
    costo: float
    calificacion: int = 0
    dia: int = 0
    completado: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
    fecha_completa: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    en_seguimiento: bool = False
    
    def calcular_tiempo_estimado(self, velocidad_kmh: int) -> float:
        """Calcula el tiempo estimado del viaje en minutos"""
        if velocidad_kmh <= 0:
            return 0.0
        return (self.distancia_km / velocidad_kmh) * 60
    
    def calcular_comision_empresa(self) -> float:
        """Calcula la comisión de UNIETAXI sobre este servicio"""
        return self.costo * config.TAXI_CONFIG["COMISION_EMPRESA"]
    
    def calcular_ganancia_taxista(self) -> float:
        """Calcula la ganancia del taxista en este servicio"""
        return self.costo * (1 - config.TAXI_CONFIG["COMISION_EMPRESA"])
    
    def __str__(self):
        estado = "✅ Completado" if self.completado else "⏳ En curso"
        return f"Servicio #{self.id_servicio} - {estado} - ${self.costo:.2f}"
    
    def to_dict(self):
        """Convierte el servicio a diccionario para JSON"""
        return {
            "id_servicio": self.id_servicio,
            "id_taxi": self.id_taxi,
            "id_cliente": self.id_cliente,
            "origen": self.origen,
            "destino": self.destino,
            "distancia_km": round(self.distancia_km, 2),
            "costo": round(self.costo, 2),
            "comision_empresa": round(self.calcular_comision_empresa(), 2),
            "ganancia_taxista": round(self.calcular_ganancia_taxista(), 2),
            "calificacion": self.calificacion,
            "dia": self.dia,
            "completado": self.completado,
            "timestamp": self.timestamp,
            "fecha_completa": self.fecha_completa,
            "en_seguimiento": self.en_seguimiento
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea un servicio desde un diccionario"""
        return cls(
            id_servicio=data.get("id_servicio", 0),
            id_taxi=data.get("id_taxi", 0),
            id_cliente=data.get("id_cliente", 0),
            origen=tuple(data.get("origen", (0.0, 0.0))),
            destino=tuple(data.get("destino", (0.0, 0.0))),
            distancia_km=data.get("distancia_km", 0.0),
            costo=data.get("costo", 0.0),
            calificacion=data.get("calificacion", 0),
            dia=data.get("dia", 0),
            completado=data.get("completado", False),
            timestamp=data.get("timestamp", datetime.now().strftime("%H:%M:%S")),
            fecha_completa=data.get("fecha_completa", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            en_seguimiento=data.get("en_seguimiento", False)
        )


# ==================== FUNCIONES AUXILIARES ====================

def crear_cliente_desde_json_registro(data: dict, cedula_numerica: int) -> Cliente:
    """
    Crea un objeto Cliente desde los datos del JSON de registro_unificado.py
    
    Args:
        data: Diccionario con datos del cliente desde el JSON
        cedula_numerica: ID numérico generado para el sistema
    
    Returns:
        Objeto Cliente
    """
    partes_nombre = data["nombre"].split(maxsplit=1)
    nombre = partes_nombre[0] if len(partes_nombre) > 0 else data["nombre"]
    apellido = partes_nombre[1] if len(partes_nombre) > 1 else ""
    
    return Cliente(
        cedula=cedula_numerica,
        nombre=nombre,
        apellido=apellido,
        tarjeta=data["tarjeta"],
        fecha_registro=data.get("fecha_registro", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        estado=data.get("estado", "activo")
    )


def crear_taxi_desde_json_registro(data: dict, id_taxi: int, cedula_numerica: int) -> Taxi:
    """
    Crea un objeto Taxi desde los datos del JSON de registro_unificado.py
    
    Args:
        data: Diccionario con datos del taxi desde el JSON
        id_taxi: ID único del taxi en el sistema
        cedula_numerica: ID numérico generado para el sistema
    
    Returns:
        Objeto Taxi
    """
    partes_nombre = data["nombre"].split(maxsplit=1)
    nombre = partes_nombre[0] if len(partes_nombre) > 0 else data["nombre"]
    apellido = partes_nombre[1] if len(partes_nombre) > 1 else ""
    
    return Taxi(
        id_taxi=id_taxi,
        cedula=cedula_numerica,
        nombre=nombre,
        apellido=apellido,
        placa=data["placa"],
        marca="Toyota",  # Valor por defecto
        modelo="Corolla",  # Valor por defecto
        velocidad=config.TAXI_CONFIG["VELOCIDAD_PROMEDIO_KMH"],
        fecha_registro=data.get("fecha_registro", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        estado=data.get("estado", "activo")
    )


# ==================== TESTS BÁSICOS ====================

if __name__ == "__main__":
    print("Probando modelos...\n")
    
    # Test Cliente
    cliente = Cliente(
        cedula=12345678,
        nombre="Juan",
        apellido="Pérez",
        tarjeta="1234567890123456"
    )
    print(f"Cliente: {cliente}")
    print(f"Tarjeta enmascarada: {cliente.tarjeta_enmascarada()}")
    print(f"Dict: {cliente.to_dict()}\n")
    
    # Test Taxi
    taxi = Taxi(
        id_taxi=1,
        cedula=87654321,
        nombre="Carlos",
        apellido="Rodríguez",
        placa="ABC123",
        marca="Toyota",
        modelo="Corolla",
        velocidad=60
    )
    print(f"Taxi: {taxi}")
    taxi.agregar_calificacion(5)
    taxi.agregar_calificacion(4)
    print(f"Calificación promedio: {taxi.calcular_calificacion_promedio():.2f}")
    taxi.agregar_ganancia(100.50)
    print(f"Ganancia total: ${taxi.ganancia_total:.2f}")
    print(f"Comisión empresa: ${taxi.calcular_comision_empresa():.2f}")
    print(f"Ganancia neta: ${taxi.calcular_ganancia_neta():.2f}")
    print(f"Dict: {taxi.to_dict()}\n")
    
    # Test Servicio
    servicio = Servicio(
        id_servicio=1,
        id_taxi=1,
        id_cliente=12345678,
        origen=(40.4168, -3.7034),
        destino=(40.4200, -3.6887),
        distancia_km=5.5,
        costo=13.75,
        calificacion=5,
        dia=1,
        completado=True
    )
    print(f"Servicio: {servicio}")
    print(f"Tiempo estimado: {servicio.calcular_tiempo_estimado(60):.1f} minutos")
    print(f"Dict: {servicio.to_dict()}\n")
    
    print("✅ Todos los tests pasaron correctamente")
