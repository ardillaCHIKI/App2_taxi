"""
sistema_central.py - Sistema Central de Atención al Cliente UNIETAXI

Este es el núcleo del sistema que implementa:
- Gestión de hilos concurrentes
- Sincronización con semáforos
- Asignación cliente-taxi
- Reportes y cierre contable
"""

import threading
import time
import random
import math
import json
from typing import List, Optional
from queue import Queue

import config
from models import Cliente, Taxi, Servicio

# ==================== SISTEMA CENTRAL ====================

class SistemaCentral:
    """
    Sistema Central de Atención al Cliente UNIETAXI.
    
    Gestiona:
    - Afiliación de clientes y taxis
    - Asignación cliente-taxi
    - Seguimiento de servicios
    - Cierre contable
    - Reportes diarios y mensuales
    """
    
    def __init__(self, num_dias: int = config.SIMULACION["DIAS_POR_DEFECTO"]):
        # ==================== DATOS DEL SISTEMA ====================
        self.taxis: List[Taxi] = []
        self.clientes: List[Cliente] = []
        self.servicios_completados: List[Servicio] = []
        self.servicios_seguimiento: List[Servicio] = []
        self.cola_solicitudes: Queue = Queue()
        
        # ==================== CONTROL DE SISTEMA ====================
        self.num_dias = num_dias
        self.dia_actual = 1
        self.servicios_activos = 0
        self.fin_del_dia = False
        self.fin_sistema = False
        self.contador_servicios = 0
        
        # ==================== SEMÁFOROS PARA SINCRONIZACIÓN ====================
        # SECCIÓN CRÍTICA 1: Lista de taxis
        self.mutex_taxis = threading.Semaphore(1)
        
        # SECCIÓN CRÍTICA 2: Lista de clientes
        self.mutex_clientes = threading.Semaphore(1)
        
        # SECCIÓN CRÍTICA 3: Función match (asignación)
        self.mutex_match = threading.Semaphore(1)
        
        # SECCIÓN CRÍTICA 4: Control de fin del día
        self.mutex_fin_del_dia = threading.Semaphore(1)
        
        # SECCIÓN CRÍTICA 5: Servicios de seguimiento
        self.mutex_servicios_seguimiento = threading.Semaphore(1)
        
        # SECCIÓN CRÍTICA 6: Servicios completados
        self.mutex_servicios_completados = threading.Semaphore(1)
        
        # SECCIÓN CRÍTICA 7: Cola de solicitudes
        self.mutex_solicitudes = threading.Semaphore(1)
        
        # SECCIÓN CRÍTICA 8: Afiliaciones
        self.mutex_afiliacion = threading.Semaphore(1)
        
        # Semáforo para esperar fin de servicios activos
        self.sem_no_hay_servicios_activos = threading.Semaphore(0)
        
        # ==================== REPORTES ====================
        self.ganancia_total_empresa = 0.0
        self.reportes_diarios = []
        
        print(config.MENSAJES["SEPARADOR"])
        print("SISTEMA UNIETAXI INICIALIZADO")
        print(config.MENSAJES["SEPARADOR"])
    
    # ==================== AFILIACIÓN ====================
    
    def afiliar_cliente(self, cedula: int, nombre: str, apellido: str, tarjeta: str) -> bool:
        """
        Afilia un nuevo cliente al sistema.
        SECCIÓN CRÍTICA: Protegida por mutex_afiliacion
        
        Args:
            cedula: Identificación del cliente
            nombre: Nombre del cliente
            apellido: Apellido del cliente
            tarjeta: Número de tarjeta de crédito (16 dígitos)
        
        Returns:
            True si se afilió correctamente, False en caso contrario
        """
        self.mutex_afiliacion.acquire()
        try:
            # Validar tarjeta (16 dígitos)
            tarjeta_limpia = tarjeta.replace(" ", "").replace("-", "")
            if len(tarjeta_limpia) != config.VALIDACIONES["TARJETA_DIGITOS"] or not tarjeta_limpia.isdigit():
                print(f"❌ Cliente {nombre} {apellido}: Tarjeta inválida (debe tener {config.VALIDACIONES['TARJETA_DIGITOS']} dígitos)")
                return False
            
            # Verificar que no exista
            for cliente in self.clientes:
                if cliente.cedula == cedula:
                    print(f"❌ Cliente ya registrado: {cedula}")
                    return False
            
            # Crear cliente
            nuevo_cliente = Cliente(cedula, nombre, apellido, tarjeta_limpia)
            self.clientes.append(nuevo_cliente)
            print(f"✅ Cliente afiliado: {nuevo_cliente}")
            return True
            
        finally:
            self.mutex_afiliacion.release()
    
    def afiliar_taxi(self, cedula: int, nombre: str, apellido: str, 
                     placa: str, marca: str, modelo: str, velocidad: int) -> bool:
        """
        Afilia un nuevo taxi al sistema.
        SECCIÓN CRÍTICA: Protegida por mutex_afiliacion
        
        Args:
            cedula: Identificación del conductor
            nombre: Nombre del conductor
            apellido: Apellido del conductor
            placa: Placa del vehículo
            marca: Marca del vehículo
            modelo: Modelo del vehículo
            velocidad: Velocidad promedio en km/h
        
        Returns:
            True si se afilió correctamente, False en caso contrario
        """
        self.mutex_afiliacion.acquire()
        try:
            # Validaciones básicas
            if velocidad <= 0:
                print(f"❌ Taxi {placa}: Velocidad inválida")
                return False
            
            if len(placa) < config.VALIDACIONES["PLACA_MIN_CHARS"]:
                print(f"❌ Taxi {placa}: Placa debe tener al menos {config.VALIDACIONES['PLACA_MIN_CHARS']} caracteres")
                return False
            
            # Verificar que no exista
            for taxi in self.taxis:
                if taxi.placa == placa:
                    print(f"❌ Taxi ya registrado: {placa}")
                    return False
            
            # Crear taxi
            id_taxi = len(self.taxis) + 1
            nuevo_taxi = Taxi(id_taxi, cedula, nombre, apellido, placa, 
                            marca, modelo, velocidad)
            
            # Ubicación aleatoria inicial (dentro de Madrid)
            punto_inicio = random.choice(config.PUNTOS_INICIO_TAXIS)
            nuevo_taxi.ubicacion = (punto_inicio[0], punto_inicio[1])
            
            # Asignar color para el mapa
            if id_taxi - 1 < len(config.COLORES_TAXIS):
                nuevo_taxi.color_mapa = config.COLORES_TAXIS[id_taxi - 1]["color"]
            
            self.taxis.append(nuevo_taxi)
            print(f"✅ Taxi afiliado: {nuevo_taxi} en posición {nuevo_taxi.ubicacion}")
            return True
            
        finally:
            self.mutex_afiliacion.release()
    
    # ==================== BÚSQUEDA Y ASIGNACIÓN ====================
    
    def calcular_distancia(self, punto1: tuple, punto2: tuple) -> float:
        """
        Calcula la distancia euclidiana entre dos puntos.
        
        Args:
            punto1: Tupla (lat, lng)
            punto2: Tupla (lat, lng)
        
        Returns:
            Distancia en kilómetros
        """
        return math.sqrt((punto2[0] - punto1[0])**2 + (punto2[1] - punto1[1])**2)
    
    def buscar_taxi_cercano(self, origen: tuple) -> Optional[Taxi]:
        """
        Busca el taxi más cercano dentro del radio configurado.
        SECCIÓN CRÍTICA: Protegida por mutex_match
        
        Algoritmo:
        1. Busca taxis disponibles dentro de RADIO_BUSQUEDA_KM
        2. Selecciona el más cercano
        3. Si hay empate, desempata por calificación
        4. Marca el taxi como ocupado
        
        Args:
            origen: Coordenadas (lat, lng) del cliente
        
        Returns:
            Taxi asignado o None si no hay disponibles
        """
        self.mutex_match.acquire()
        try:
            taxi_elegido = None
            distancia_minima = config.TAXI_CONFIG["RADIO_BUSQUEDA_KM"]
            
            self.mutex_taxis.acquire()
            try:
                for taxi in self.taxis:
                    if taxi.disponible and taxi.estado == "activo":
                        distancia = self.calcular_distancia(origen, taxi.ubicacion)
                        
                        if distancia < distancia_minima:
                            distancia_minima = distancia
                            taxi_elegido = taxi
                        elif distancia == distancia_minima and taxi_elegido:
                            # Desempate por calificación
                            if taxi.calcular_calificacion_promedio() > taxi_elegido.calcular_calificacion_promedio():
                                taxi_elegido = taxi
                
                # Marcar taxi como ocupado
                if taxi_elegido:
                    taxi_elegido.disponible = False
                    
            finally:
                self.mutex_taxis.release()
            
            return taxi_elegido
            
        finally:
            self.mutex_match.release()
    
    def asignar_taxi(self, cliente: Cliente) -> Optional[Taxi]:
        """
        Asigna un taxi a un cliente.
        
        Args:
            cliente: Cliente que solicita el taxi
        
        Returns:
            Taxi asignado o None
        """
        taxi = self.buscar_taxi_cercano(cliente.ubicacion_actual)
        
        if taxi:
            cliente.taxi_asignado = taxi.id_taxi
            taxi.cliente_actual = cliente.cedula
            
            distancia = self.calcular_distancia(taxi.ubicacion, cliente.ubicacion_actual)
            tiempo_llegada = (distancia / taxi.velocidad) * 60  # minutos
            
            print(f"🚖 MATCH: {cliente} ← {taxi}")
            print(f"   Distancia: {distancia:.2f} km | Tiempo llegada: {tiempo_llegada:.1f} min")
            return taxi
        else:
            print(f"❌ No hay taxis disponibles para {cliente}")
            return None
    
    # ==================== GESTIÓN DE SERVICIOS ====================
    
    def activar_servicio(self) -> bool:
        """
        Incrementa el contador de servicios activos.
        SECCIÓN CRÍTICA: Protegida por mutex_fin_del_dia
        
        Returns:
            True si se puede activar, False si ya es fin del día
        """
        self.mutex_fin_del_dia.acquire()
        try:
            if not self.fin_del_dia:
                self.servicios_activos += 1
            return not self.fin_del_dia
        finally:
            self.mutex_fin_del_dia.release()
    
    def desactivar_servicio(self):
        """
        Decrementa el contador de servicios activos.
        SECCIÓN CRÍTICA: Protegida por mutex_fin_del_dia
        
        Si no hay servicios activos y es fin de día, señala al sistema principal.
        """
        self.mutex_fin_del_dia.acquire()
        try:
            self.servicios_activos -= 1
            
            # Si no hay servicios activos y es fin de día, señalar al sistema
            if self.servicios_activos == 0 and self.fin_del_dia:
                self.sem_no_hay_servicios_activos.release()
                
        finally:
            self.mutex_fin_del_dia.release()
    
    def realizar_servicio(self, cliente: Cliente, taxi: Taxi):
        """
        Simula la realización completa de un servicio.
        
        Flujo:
        1. Calcula distancia y costo
        2. Simula el traslado
        3. Cliente califica
        4. Actualiza estadísticas del taxi
        5. Registra el servicio
        6. Libera recursos
        
        Args:
            cliente: Cliente del servicio
            taxi: Taxi asignado
        """
        
        # Calcular costo del servicio
        distancia_km = self.calcular_distancia(cliente.ubicacion_actual, cliente.destino)
        # Convertir a metros
        distancia_m = distancia_km * 1000.0
        tarifa_metro = config.TAXI_CONFIG.get("TARIFA_POR_METRO")
        if tarifa_metro is not None:
            # Cobrar por metro (prioridad si está configurado)
            costo = distancia_m * tarifa_metro
        else:
            costo = distancia_km * config.TAXI_CONFIG["TARIFA_POR_KM"]
        
        # Crear registro de servicio
        self.contador_servicios += 1
        servicio = Servicio(
            id_servicio=self.contador_servicios,
            id_taxi=taxi.id_taxi,
            id_cliente=cliente.cedula,
            origen=cliente.ubicacion_actual,
            destino=cliente.destino,
            distancia_km=distancia_km,
            costo=costo,
            dia=self.dia_actual
        )
        
        print(f"\n🚗 INICIO SERVICIO #{servicio.id_servicio}")
        print(f"   Cliente: {cliente}")
        print(f"   Taxi: {taxi}")
        print(f"   Ruta: {servicio.origen} → {servicio.destino}")
        print(f"   Distancia: {distancia_km:.2f} km | Costo: ${costo:.2f}")
        
        # Simular traslado
        tiempo_viaje = (distancia_km / taxi.velocidad) * 3600  # segundos
        time.sleep(tiempo_viaje / 1000)  # Simulación ultra-acelerada
        
        # Actualizar ubicación del taxi
        taxi.ubicacion = cliente.destino
        
        # Cliente califica el servicio (entre 3 y 5 estrellas)
        calificacion = random.randint(3, 5)
        servicio.calificacion = calificacion
        servicio.completado = True
        
        # Actualizar estadísticas del taxi
        taxi.agregar_calificacion(calificacion)
        taxi.agregar_ganancia(costo)
        
        print(f"✅ SERVICIO COMPLETADO")
        print(f"   Calificación: {calificacion}⭐ | Promedio taxi: {taxi.calcular_calificacion_promedio():.2f}⭐")
        
        # Registrar servicio
        self.mutex_servicios_completados.acquire()
        try:
            self.servicios_completados.append(servicio)
            
            # Agregar a seguimiento (primeros N del día)
            self.mutex_servicios_seguimiento.acquire()
            try:
                if len(self.servicios_seguimiento) < config.SEGUIMIENTO["SERVICIOS_POR_DIA"]:
                    servicio.en_seguimiento = True
                    self.servicios_seguimiento.append(servicio)
                    print(f"📊 Servicio agregado a seguimiento diario ({len(self.servicios_seguimiento)}/{config.SEGUIMIENTO['SERVICIOS_POR_DIA']})")
            finally:
                self.mutex_servicios_seguimiento.release()
                
        finally:
            self.mutex_servicios_completados.release()
        
        # Liberar recursos
        taxi.disponible = True
        taxi.cliente_actual = None
        cliente.taxi_asignado = None
        cliente.en_servicio = False
    
    # ==================== REPORTES ====================
    
    def generar_reporte_diario(self):
        """
        Genera el reporte diario de servicios en seguimiento.
        SECCIÓN CRÍTICA: Debe esperar a que no haya servicios activos
        """
        print(f"\n{config.MENSAJES['SEPARADOR']}")
        print(f"📋 REPORTE DÍA {self.dia_actual}")
        print(f"{config.MENSAJES['SEPARADOR']}")
        
        ganancia_dia = 0.0
        
        if len(self.servicios_seguimiento) > 0:
            print(f"\n🔍 SERVICIOS EN SEGUIMIENTO:")
            for i, servicio in enumerate(self.servicios_seguimiento, 1):
                print(f"\n{i}. Servicio #{servicio.id_servicio}")
                print(f"   Taxi: {servicio.id_taxi} | Cliente: {servicio.id_cliente}")
                print(f"   Origen: ({servicio.origen[0]:.4f}, {servicio.origen[1]:.4f})")
                print(f"   Destino: ({servicio.destino[0]:.4f}, {servicio.destino[1]:.4f})")
                print(f"   Distancia: {servicio.distancia_km:.2f} km | Costo: ${servicio.costo:.2f}")
                print(f"   Calificación: {servicio.calificacion}⭐ | Hora: {servicio.timestamp}")
                ganancia_dia += servicio.costo
        else:
            print("No hubo servicios en seguimiento hoy")
        
        print(f"\n💰 Ganancia total del día: ${ganancia_dia:.2f}")
        print(f"{config.MENSAJES['SEPARADOR']}\n")
        
        # Guardar reporte
        self.reportes_diarios.append({
            'dia': self.dia_actual,
            'servicios': [s.to_dict() for s in self.servicios_seguimiento],
            'ganancia': ganancia_dia
        })
        
        # Limpiar servicios de seguimiento para el próximo día
        self.servicios_seguimiento.clear()
    
    def cierre_contable_diario(self):
        """
        Realiza el cierre contable del día.
        Descuenta 20% a cada taxista y transfiere el monto.
        """
        print(f"\n{config.MENSAJES['SEPARADOR']}")
        print(f"💼 CIERRE CONTABLE - DÍA {self.dia_actual} (12:00 PM)")
        print(f"{config.MENSAJES['SEPARADOR']}\n")
        
        ganancia_empresa_dia = 0.0
        
        self.mutex_taxis.acquire()
        try:
            for taxi in self.taxis:
                if taxi.ganancia_diaria > 0:
                    descuento_empresa = taxi.ganancia_diaria * config.TAXI_CONFIG["COMISION_EMPRESA"]
                    ganancia_taxista = taxi.ganancia_diaria * (1 - config.TAXI_CONFIG["COMISION_EMPRESA"])
                    ganancia_empresa_dia += descuento_empresa
                    
                    print(f"🚖 {taxi}")
                    print(f"   Total generado: ${taxi.ganancia_diaria:.2f}")
                    print(f"   Comisión UNIETAXI ({int(config.TAXI_CONFIG['COMISION_EMPRESA']*100)}%): ${descuento_empresa:.2f}")
                    print(f"   Ganancia taxista ({int((1-config.TAXI_CONFIG['COMISION_EMPRESA'])*100)}%): ${ganancia_taxista:.2f}\n")
                    
                    # Resetear ganancia diaria
                    taxi.resetear_ganancia_diaria()
            
            self.ganancia_total_empresa += ganancia_empresa_dia
            
        finally:
            self.mutex_taxis.release()
        
        print(f"💰 Ganancia empresa del día: ${ganancia_empresa_dia:.2f}")
        print(f"💰 Ganancia acumulada empresa: ${self.ganancia_total_empresa:.2f}")
        print(f"{config.MENSAJES['SEPARADOR']}\n")
    
    def generar_reporte_mensual(self):
        """Genera el reporte mensual final con estadísticas completas"""
        print(f"\n{config.MENSAJES['SEPARADOR']}")
        print(f"📊 REPORTE MENSUAL FINAL")
        print(f"{config.MENSAJES['SEPARADOR']}\n")
        
        self.mutex_taxis.acquire()
        try:
            for taxi in self.taxis:
                if taxi.cantidad_servicios > 0:
                    descuento_total = taxi.calcular_comision_empresa()
                    ganancia_final = taxi.calcular_ganancia_neta()
                    
                    print(f"ID Taxista: {taxi.id_taxi} :: Nombre: {taxi.nombre_completo()}")
                    print(f"Placa: {taxi.placa} :: Marca: {taxi.marca} :: Modelo: {taxi.modelo}")
                    print(f"Total Generado: ${taxi.ganancia_total:.2f}")
                    print(f"Importe Mensual ({int(config.TAXI_CONFIG['COMISION_EMPRESA']*100)}%): ${descuento_total:.2f}")
                    print(f"Ganancia del taxista ({int((1-config.TAXI_CONFIG['COMISION_EMPRESA'])*100)}%): ${ganancia_final:.2f}")
                    print(f"Servicios realizados: {taxi.cantidad_servicios}")
                    print(f"Calificación promedio: {taxi.calcular_calificacion_promedio():.2f}⭐")
                    print(f"{config.MENSAJES['SEPARADOR_MENOR']}\n")
                    
        finally:
            self.mutex_taxis.release()
        
        print(f"💰 GANANCIA TOTAL EMPRESA: ${self.ganancia_total_empresa:.2f}")
        print(f"📈 Total servicios realizados: {len(self.servicios_completados)}")
        print(f"📊 Total clientes atendidos: {len(set(s.id_cliente for s in self.servicios_completados))}")
        print(f"🚖 Total taxis activos: {len([t for t in self.taxis if t.cantidad_servicios > 0])}")
        print(f"{config.MENSAJES['SEPARADOR']}\n")
    
    # ==================== CONTROL DE DÍAS ====================
    
    def iniciar_nuevo_dia(self):
        """Inicia un nuevo día en el sistema"""
        print(f"\n\n{'#'*60}")
        print(f"🌅 INICIO DÍA {self.dia_actual} - {config.obtener_fecha_legible()}")
        print(f"{'#'*60}\n")
        
        self.mutex_fin_del_dia.acquire()
        try:
            self.fin_del_dia = False
        finally:
            self.mutex_fin_del_dia.release()
    
    def finalizar_dia(self):
        """Finaliza el día actual"""
        print(f"\n🌙 Finalizando día {self.dia_actual}...")
        
        # Marcar fin del día
        self.mutex_fin_del_dia.acquire()
        try:
            self.fin_del_dia = True
        finally:
            self.mutex_fin_del_dia.release()
        
        # Esperar a que terminen todos los servicios activos
        if self.servicios_activos > 0:
            print(f"⏳ Esperando finalización de {self.servicios_activos} servicios activos...")
            self.sem_no_hay_servicios_activos.acquire()
        
        # Generar reportes
        self.generar_reporte_diario()
        self.cierre_contable_diario()
        
        # Incrementar día
        self.dia_actual += 1
    
    # ==================== EXPORTACIÓN DE DATOS ====================
    
    def exportar_datos_json(self):
        """Exporta todos los datos del sistema a archivos JSON"""
        
        # Exportar servicios completados
        with open(config.SERVICIOS_JSON, 'w', encoding='utf-8') as f:
            servicios_data = [s.to_dict() for s in self.servicios_completados]
            json.dump(servicios_data, f, indent=2, ensure_ascii=False)
        
        # Exportar ubicaciones en tiempo real para el mapa
        ubicaciones = {
            "taxis": [t.to_dict() for t in self.taxis],
            "clientes": [c.to_dict() for c in self.clientes if c.en_servicio],
            "timestamp": config.obtener_fecha_legible()
        }
        with open(config.UBICACIONES_TIEMPO_REAL, 'w', encoding='utf-8') as f:
            json.dump(ubicaciones, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Datos exportados a JSON")


# ==================== FUNCIONES AUXILIARES ====================

def cargar_clientes_desde_json(sistema: SistemaCentral) -> int:
    """
    Carga clientes desde el archivo JSON de registro_unificado.py
    
    Returns:
        Número de clientes cargados
    """
    try:
        with open(config.CLIENTES_JSON, "r", encoding="utf-8") as f:
            clientes_data = json.load(f)
        
        contador = 0
        for cliente_data in clientes_data:
            if cliente_data.get("estado") == "activo":
                # Generar ID numérico desde la identificación
                cedula_numerica = abs(hash(cliente_data["identificacion"])) % 10**8
                
                # Separar nombre y apellido
                partes_nombre = cliente_data["nombre"].split(maxsplit=1)
                nombre = partes_nombre[0]
                apellido = partes_nombre[1] if len(partes_nombre) > 1 else ""
                
                if sistema.afiliar_cliente(
                    cedula=cedula_numerica,
                    nombre=nombre,
                    apellido=apellido,
                    tarjeta=cliente_data["tarjeta"]
                ):
                    contador += 1
        
        print(f"✅ Cargados {contador} clientes desde JSON\n")
        return contador
        
    except FileNotFoundError:
        print(f"⚠️ No se encontró {config.CLIENTES_JSON}")
        return 0
    except Exception as e:
        print(f"❌ Error cargando clientes: {e}")
        return 0


def cargar_taxis_desde_json(sistema: SistemaCentral) -> int:
    """
    Carga taxis desde el archivo JSON de registro_unificado.py
    
    Returns:
        Número de taxis cargados
    """
    try:
        with open(config.TAXIS_JSON, "r", encoding="utf-8") as f:
            taxis_data = json.load(f)
        
        contador = 0
        for taxi_data in taxis_data:
            if taxi_data.get("estado") == "activo":
                # Generar ID numérico desde la identificación
                cedula_numerica = abs(hash(taxi_data["identificacion"])) % 10**8
                
                # Separar nombre y apellido
                partes_nombre = taxi_data["nombre"].split(maxsplit=1)
                nombre = partes_nombre[0]
                apellido = partes_nombre[1] if len(partes_nombre) > 1 else ""
                
                if sistema.afiliar_taxi(
                    cedula=cedula_numerica,
                    nombre=nombre,
                    apellido=apellido,
                    placa=taxi_data["placa"],
                    marca="Toyota",  # Valor por defecto
                    modelo="Corolla",
                    velocidad=config.TAXI_CONFIG["VELOCIDAD_PROMEDIO_KMH"]
                ):
                    contador += 1
        
        print(f"✅ Cargados {contador} taxis desde JSON\n")
        return contador
        
    except FileNotFoundError:
        print(f"⚠️ No se encontró {config.TAXIS_JSON}")
        return 0
    except Exception as e:
        print(f"❌ Error cargando taxis: {e}")
        return 0


if __name__ == "__main__":
    print("Este módulo debe ser importado desde main.py")
    print("No debe ejecutarse directamente.")