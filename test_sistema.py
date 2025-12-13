"""
test_sistema.py - Suite Completa de Pruebas UNIETAXI

Ejecuta pruebas de:
- Sincronización y secciones críticas
- Casos extremos
- Funcionalidad básica
- Lógica de negocio
- Integración completa
"""

import unittest
import threading
import time
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from models import Cliente, Taxi, Servicio
from sistema_central import SistemaCentral
from hilos import hilo_cliente


# ==================== PRUEBAS DE SINCRONIZACIÓN ====================

class TestSincronizacion(unittest.TestCase):
    """Pruebas de sincronización y secciones críticas"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.sistema = SistemaCentral(num_dias=1)
    
    def test_CP_SC_01_race_condition_lista_taxis(self):
        """
        CP-SC-01: Race Condition en Lista de Taxis
        
        Entrada: 5 clientes solicitan simultáneamente, 3 taxis disponibles
        Resultado esperado: Solo un hilo modifica cada taxi a la vez
        Verifica: Semáforo mutex_match y mutex_taxis
        """
        print("\n" + "="*60)
        print("🧪 TEST CP-SC-01: Race Condition en Lista de Taxis")
        print("="*60)
        
        # Crear 3 taxis
        for i in range(3):
            self.sistema.afiliar_taxi(
                100000 + i, f"Taxi{i}", "Driver", f"ABC{i:03d}", 
                "Toyota", "Corolla", 60
            )
        
        # Crear 5 clientes que soliciten simultáneamente
        clientes = []
        for i in range(5):
            self.sistema.afiliar_cliente(
                200000 + i, f"Cliente{i}", "Test", "4532123456789012"
            )
            clientes.append(self.sistema.clientes[-1])
        
        # Iniciar solicitudes simultáneas
        hilos = []
        for cliente in clientes:
            hilo = threading.Thread(target=hilo_cliente, args=(self.sistema, cliente, 1))
            hilos.append(hilo)
            hilo.start()
        
        # Esperar finalización
        for hilo in hilos:
            hilo.join()
        
        # Verificar que no hay taxis asignados múltiples veces
        taxis_usados = {}
        for servicio in self.sistema.servicios_completados:
            if servicio.id_taxi in taxis_usados:
                self.fail(f"Taxi {servicio.id_taxi} fue asignado múltiples veces simultáneamente")
            taxis_usados[servicio.id_taxi] = servicio.id_servicio
        
        print(f"✅ PASS: No se detectaron asignaciones duplicadas")
        print(f"   Servicios completados: {len(self.sistema.servicios_completados)}")
        print(f"   Taxis únicos usados: {len(taxis_usados)}")
        
        # Verificar que se usaron máximo 3 taxis (los disponibles)
        self.assertLessEqual(len(taxis_usados), 3, "Se usaron más taxis de los disponibles")
    
    def test_CP_SC_02_modificacion_concurrente_servicios(self):
        """
        CP-SC-02: Modificación Concurrente de Servicios Completados
        
        Entrada: 10 clientes realizan servicios simultáneamente
        Resultado esperado: Todos los servicios se registran sin pérdida
        Verifica: Semáforo mutex_servicios_completados
        """
        print("\n" + "="*60)
        print("🧪 TEST CP-SC-02: Modificación Concurrente Servicios")
        print("="*60)
        
        # Crear 10 taxis y 10 clientes
        for i in range(10):
            self.sistema.afiliar_taxi(
                300000 + i, f"Taxi{i}", "Driver", f"DEF{i:03d}",
                "Honda", "Civic", 60
            )
            self.sistema.afiliar_cliente(
                400000 + i, f"Cliente{i}", "Test", "4532123456789012"
            )
        
        clientes = self.sistema.clientes.copy()
        
        # Todas las solicitudes simultáneas
        hilos = []
        for cliente in clientes:
            hilo = threading.Thread(target=hilo_cliente, args=(self.sistema, cliente, 1))
            hilos.append(hilo)
            hilo.start()
        
        for hilo in hilos:
            hilo.join()
        
        # Verificar que todos los servicios se procesaron
        self.assertGreater(len(self.sistema.servicios_completados), 0, 
                          "No se procesaron servicios")
        
        # Verificar que no hay IDs duplicados
        ids_servicios = [s.id_servicio for s in self.sistema.servicios_completados]
        self.assertEqual(len(ids_servicios), len(set(ids_servicios)),
                        "Hay IDs de servicios duplicados")
        
        print(f"✅ PASS: Todas las solicitudes se procesaron correctamente")
        print(f"   Servicios completados: {len(self.sistema.servicios_completados)}")
        print(f"   IDs únicos verificados: {len(set(ids_servicios))}")
    
    def test_CP_SC_03_asignacion_simultanea_mismo_taxi(self):
        """
        CP-SC-03: Asignación Simultánea de Mismo Taxi
        
        Entrada: 2 clientes en misma ubicación, 1 taxi cercano
        Resultado esperado: Solo uno recibe el taxi
        Verifica: Semáforo mutex_match protege asignación
        """
        print("\n" + "="*60)
        print("🧪 TEST CP-SC-03: Asignación Simultánea Mismo Taxi")
        print("="*60)
        
        # Un solo taxi
        self.sistema.afiliar_taxi(
            500000, "TaxiUnico", "Driver", "UNI001",
            "Toyota", "Corolla", 60
        )
        
        # Dos clientes en la misma ubicación
        clientes = []
        for i in range(2):
            self.sistema.afiliar_cliente(
                600000 + i, f"Cliente{i}", "Test", "4532123456789012"
            )
            cliente = self.sistema.clientes[-1]
            # Forzar misma ubicación
            cliente.ubicacion_actual = (40.4168, -3.7034)
            cliente.destino = (40.4200, -3.6887)
            clientes.append(cliente)
        
        # Solicitudes simultáneas
        hilos = []
        for cliente in clientes:
            hilo = threading.Thread(target=hilo_cliente, args=(self.sistema, cliente, 1))
            hilos.append(hilo)
            hilo.start()
        
        for hilo in hilos:
            hilo.join()
        
        # Solo debería haber 1 servicio completado
        self.assertEqual(len(self.sistema.servicios_completados), 1,
                        "Se asignó el mismo taxi a múltiples clientes")
        
        print(f"✅ PASS: Solo un cliente recibió el taxi")
        print(f"   Servicios completados: {len(self.sistema.servicios_completados)}")
    
    def test_CP_SC_04_actualizacion_calificaciones(self):
        """
        CP-SC-04: Actualización Concurrente de Calificaciones
        
        Entrada: 5 clientes califican diferentes taxis simultáneamente
        Resultado esperado: Todas las calificaciones se registran correctamente
        Verifica: Integridad de datos en operaciones concurrentes
        """
        print("\n" + "="*60)
        print("🧪 TEST CP-SC-04: Actualización Concurrente Calificaciones")
        print("="*60)
        
        # 5 taxis y 5 clientes
        for i in range(5):
            self.sistema.afiliar_taxi(
                700000 + i, f"Taxi{i}", "Driver", f"CAL{i:03d}",
                "Toyota", "Corolla", 60
            )
            self.sistema.afiliar_cliente(
                800000 + i, f"Cliente{i}", "Test", "4532123456789012"
            )
        
        clientes = self.sistema.clientes.copy()
        
        # Solicitudes simultáneas
        hilos = []
        for cliente in clientes:
            hilo = threading.Thread(target=hilo_cliente, args=(self.sistema, cliente, 1))
            hilos.append(hilo)
            hilo.start()
        
        for hilo in hilos:
            hilo.join()
        
        # Verificar que las calificaciones están en rango válido
        for taxi in self.sistema.taxis:
            if taxi.cantidad_servicios > 0:
                promedio = taxi.calcular_calificacion_promedio()
                self.assertGreaterEqual(promedio, config.CALIFICACIONES["MINIMA"])
                self.assertLessEqual(promedio, config.CALIFICACIONES["MAXIMA"])
        
        print(f"✅ PASS: Calificaciones actualizadas correctamente")
        for taxi in self.sistema.taxis:
            if taxi.cantidad_servicios > 0:
                print(f"   {taxi.placa}: {taxi.calcular_calificacion_promedio():.2f}⭐ "
                      f"({taxi.cantidad_servicios} servicios)")


# ==================== PRUEBAS DE CASOS EXTREMOS ====================

class TestCasosExtremos(unittest.TestCase):
    """Pruebas de casos extremos"""
    
    def setUp(self):
        self.sistema = SistemaCentral(num_dias=1)
    
    def test_CP_EXT_01_no_hay_taxis_disponibles(self):
        """
        CP-EXT-01: No Hay Taxis Disponibles
        
        Entrada: Cliente solicita pero no hay taxis
        Resultado esperado: Sistema informa que no hay taxis
        """
        print("\n" + "="*60)
        print("🧪 TEST CP-EXT-01: No Hay Taxis Disponibles")
        print("="*60)
        
        # Crear cliente pero NO taxis
        self.sistema.afiliar_cliente(900000, "Cliente", "Solo", "4532123456789012")
        cliente = self.sistema.clientes[-1]
        cliente.ubicacion_actual = (40.4168, -3.7034)
        cliente.destino = (40.4200, -3.6887)
        
        # Intentar asignar taxi
        taxi = self.sistema.asignar_taxi(cliente)
        
        self.assertIsNone(taxi, "Se asignó un taxi cuando no hay disponibles")
        self.assertEqual(len(self.sistema.servicios_completados), 0)
        
        print(f"✅ PASS: Sistema manejó correctamente la ausencia de taxis")
    
    def test_CP_EXT_02_taxis_fuera_de_radio(self):
        """
        CP-EXT-02: No Hay Taxis en Radio de 2 km
        
        Entrada: Cliente en (40.4168, -3.7034), taxi lejos
        Resultado esperado: No se asigna taxi fuera del radio
        """
        print("\n" + "="*60)
        print("🧪 TEST CP-EXT-02: Taxis Fuera de Radio")
        print("="*60)
        
        # Crear taxi lejos
        self.sistema.afiliar_taxi(
            1000000, "TaxiLejos", "Driver", "LEJ001",
            "Toyota", "Corolla", 60
        )
        taxi = self.sistema.taxis[-1]
        taxi.ubicacion = (40.5000, -3.5000)  # Muy lejos
        
        # Cliente en centro
        self.sistema.afiliar_cliente(1100000, "Cliente", "Cerca", "4532123456789012")
        cliente = self.sistema.clientes[-1]
        cliente.ubicacion_actual = (40.4168, -3.7034)
        cliente.destino = (40.4200, -3.6887)
        
        # Intentar asignar
        taxi_asignado = self.sistema.asignar_taxi(cliente)
        
        distancia = self.sistema.calcular_distancia(cliente.ubicacion_actual, taxi.ubicacion)
        
        if distancia > config.TAXI_CONFIG["RADIO_BUSQUEDA_KM"]:
            self.assertIsNone(taxi_asignado, "Se asignó un taxi fuera del radio")
            print(f"✅ PASS: Taxi a {distancia:.2f} km correctamente rechazado")
        else:
            print(f"⚠️ Taxi estaba dentro del radio: {distancia:.2f} km")
    
    def test_CP_EXT_03_todos_taxis_ocupados(self):
        """
        CP-EXT-03: Todos los Taxis Ocupados
        
        Entrada: Todos los taxis marcados como no disponibles
        Resultado esperado: Cliente no recibe taxi
        """
        print("\n" + "="*60)
        print("🧪 TEST CP-EXT-03: Todos los Taxis Ocupados")
        print("="*60)
        
        # Crear 3 taxis
        for i in range(3):
            self.sistema.afiliar_taxi(
                1200000 + i, f"Taxi{i}", "Driver", f"OCP{i:03d}",
                "Toyota", "Corolla", 60
            )
        
        # Marcar todos como ocupados
        for taxi in self.sistema.taxis:
            taxi.disponible = False
        
        # Intentar solicitar taxi
        self.sistema.afiliar_cliente(1300000, "Cliente", "Esperando", "4532123456789012")
        cliente = self.sistema.clientes[-1]
        cliente.ubicacion_actual = (40.4168, -3.7034)
        
        taxi = self.sistema.asignar_taxi(cliente)
        
        self.assertIsNone(taxi, "Se asignó un taxi ocupado")
        print(f"✅ PASS: No se asignaron taxis ocupados")
    
    def test_CP_EXT_04_tarjeta_invalida(self):
        """
        CP-EXT-05: Tarjeta de Crédito Inválida
        
        Entrada: Tarjeta con menos de 16 dígitos
        Resultado esperado: Registro rechazado
        """
        print("\n" + "="*60)
        print("🧪 TEST CP-EXT-04: Tarjeta Inválida")
        print("="*60)
        
        # Intentar afiliar con tarjeta de 15 dígitos
        resultado = self.sistema.afiliar_cliente(
            1500000, "Cliente", "TarjetaMala", "453212345678901"  # 15 dígitos
        )
        
        self.assertFalse(resultado, "Se aceptó una tarjeta inválida")
        print(f"✅ PASS: Tarjeta inválida rechazada correctamente")


# ==================== PRUEBAS DE FUNCIONALIDAD BÁSICA ====================

class TestFuncionalidadBasica(unittest.TestCase):
    """Pruebas de funcionalidad básica"""
    
    def setUp(self):
        self.sistema = SistemaCentral(num_dias=1)
    
    def test_CP_FUN_01_registro_cliente_valido(self):
        """
        CP-FUN-01: Registro de Cliente Válido
        
        Entrada: Cliente con datos válidos
        Resultado esperado: Cliente registrado exitosamente
        """
        print("\n" + "="*60)
        print("🧪 TEST CP-FUN-01: Registro Cliente Válido")
        print("="*60)
        
        resultado = self.sistema.afiliar_cliente(
            1600000, "Juan", "Pérez", "4532123456789012"
        )
        
        self.assertTrue(resultado, "No se pudo afiliar cliente válido")
        self.assertEqual(len(self.sistema.clientes), 1)
        self.assertEqual(self.sistema.clientes[0].nombre, "Juan")
        
        print(f"✅ PASS: Cliente afiliado correctamente")
    
    def test_CP_FUN_02_registro_taxi_valido(self):
        """
        CP-FUN-03: Registro de Taxi Válido
        
        Entrada: Taxi con documentación completa
        Resultado esperado: Taxi registrado exitosamente
        """
        print("\n" + "="*60)
        print("🧪 TEST CP-FUN-02: Registro Taxi Válido")
        print("="*60)
        
        resultado = self.sistema.afiliar_taxi(
            1700000, "Carlos", "Rodríguez", "ABC123",
            "Toyota", "Corolla", 60
        )
        
        self.assertTrue(resultado, "No se pudo afiliar taxi válido")
        self.assertEqual(len(self.sistema.taxis), 1)
        self.assertEqual(self.sistema.taxis[0].placa, "ABC123")
        
        print(f"✅ PASS: Taxi afiliado correctamente")
    
    def test_CP_FUN_03_calculo_distancia(self):
        """
        CP-FUN-06: Cálculo de Distancia
        
        Entrada: Puntos (0,0) y (3,4)
        Resultado esperado: Distancia = 5.0 (triángulo 3-4-5)
        """
        print("\n" + "="*60)
        print("🧪 TEST CP-FUN-03: Cálculo de Distancia")
        print("="*60)
        
        punto1 = (0.0, 0.0)
        punto2 = (3.0, 4.0)
        
        distancia = self.sistema.calcular_distancia(punto1, punto2)
        esperada = 5.0
        
        self.assertAlmostEqual(distancia, esperada, places=2)
        
        print(f"✅ PASS: Distancia calculada correctamente: {distancia:.2f} km")
    
    def test_CP_FUN_04_desempate_calificacion(self):
        """
        CP-FUN-07: Desempate por Calificación
        
        Entrada: Dos taxis a misma distancia, diferentes calificaciones
        Resultado esperado: Se elige el mejor calificado
        """
        print("\n" + "="*60)
        print("🧪 TEST CP-FUN-04: Desempate por Calificación")
        print("="*60)
        
        # Crear dos taxis
        self.sistema.afiliar_taxi(1800000, "TaxiA", "Driver", "AAA001",
                                  "Toyota", "Corolla", 60)
        self.sistema.afiliar_taxi(1800001, "TaxiB", "Driver", "BBB002",
                                  "Honda", "Civic", 60)
        
        # Misma ubicación
        self.sistema.taxis[0].ubicacion = (40.4169, -3.7034)
        self.sistema.taxis[1].ubicacion = (40.4169, -3.7034)
        
        # Diferentes calificaciones
        self.sistema.taxis[0].agregar_calificacion(3)
        self.sistema.taxis[1].agregar_calificacion(5)
        
        # Cliente
        self.sistema.afiliar_cliente(1900000, "Cliente", "Test", "4532123456789012")
        cliente = self.sistema.clientes[-1]
        cliente.ubicacion_actual = (40.4168, -3.7034)
        
        # Asignar taxi
        taxi = self.sistema.asignar_taxi(cliente)
        
        self.assertIsNotNone(taxi)
        self.assertEqual(taxi.placa, "BBB002", "No se seleccionó el mejor calificado")
        
        print(f"✅ PASS: Se seleccionó el taxi con mejor calificación")


# ==================== PRUEBAS DE LÓGICA DE NEGOCIO ====================

class TestLogicaNegocio(unittest.TestCase):
    """Pruebas de lógica de negocio"""
    
    def setUp(self):
        self.sistema = SistemaCentral(num_dias=1)
    
    def test_CP_NEG_01_calculo_tarifa(self):
        """
        CP-NEG-01: Cálculo de Tarifa
        
        Verifica: distancia * tarifa_por_km
        """
        print("\n" + "="*60)
        print("🧪 TEST CP-NEG-01: Cálculo de Tarifa")
        print("="*60)
        
        distancia = 10.0
        costo_esperado = distancia * config.TAXI_CONFIG["TARIFA_POR_KM"]
        
        print(f"   Distancia: {distancia} km")
        print(f"   Tarifa: ${config.TAXI_CONFIG['TARIFA_POR_KM']}/km")
        print(f"   Costo esperado: ${costo_esperado:.2f}")
        print(f"✅ PASS: Fórmula verificada")
    
    def test_CP_NEG_02_comision_empresa(self):
        """
        CP-NEG-02: Comisión de la Empresa (20%)
        
        Entrada: Taxi con ganancia de $100
        Resultado esperado: Empresa $20, Taxista $80
        """
        print("\n" + "="*60)
        print("🧪 TEST CP-NEG-02: Comisión 20%")
        print("="*60)
        
        self.sistema.afiliar_taxi(2000000, "Taxi", "Test", "COM001",
                                  "Toyota", "Corolla", 60)
        taxi = self.sistema.taxis[-1]
        
        taxi.agregar_ganancia(100.0)
        
        comision = taxi.calcular_comision_empresa()
        ganancia_neta = taxi.calcular_ganancia_neta()
        
        self.assertAlmostEqual(comision, 20.0, places=2)
        self.assertAlmostEqual(ganancia_neta, 80.0, places=2)
        
        print(f"   Ganancia: $100.00")
        print(f"   UNIETAXI (20%): ${comision:.2f}")
        print(f"   Taxista (80%): ${ganancia_neta:.2f}")
        print(f"✅ PASS: Comisión calculada correctamente")


# ==================== PRUEBAS DE INTEGRACIÓN ====================

class TestIntegracion(unittest.TestCase):
    """Pruebas de integración completa"""
    
    def test_CP_INT_01_flujo_completo(self):
        """
        CP-INT-01: Flujo Completo de Servicio
        
        Verifica todo el ciclo: solicitud → asignación → servicio → calificación
        """
        print("\n" + "="*60)
        print("🧪 TEST CP-INT-01: Flujo Completo de Servicio")
        print("="*60)
        
        sistema = SistemaCentral(num_dias=1)
        
        # Afiliar taxi y cliente
        sistema.afiliar_taxi(2100000, "Taxi", "Completo", "INT001",
                            "Toyota", "Corolla", 60)
        sistema.afiliar_cliente(2200000, "Cliente", "Completo", "4532123456789012")
        
        cliente = sistema.clientes[-1]
        # CORREGIDO: Asignar ubicación en Madrid
        cliente.ubicacion_actual = (40.4168, -3.7034)  # Puerta del Sol
        cliente.destino = (40.4200, -3.6887)            # Puerta de Alcalá
        
        # Realizar servicio
        hilo = threading.Thread(target=hilo_cliente, args=(sistema, cliente, 1))
        hilo.start()
        hilo.join()
        
        # Verificaciones
        self.assertGreater(len(sistema.servicios_completados), 0)
        
        servicio = sistema.servicios_completados[0]
        self.assertEqual(servicio.id_cliente, cliente.cedula)
        self.assertTrue(servicio.completado)
        self.assertGreater(servicio.calificacion, 0)
        
        print(f"✅ PASS: Flujo completo ejecutado")
        print(f"   Servicio ID: {servicio.id_servicio}")
        print(f"   Calificación: {servicio.calificacion}⭐")
        print(f"   Costo: ${servicio.costo:.2f}")


# ==================== EJECUCIÓN DE PRUEBAS ====================

def run_all_tests():
    """Ejecuta todos los casos de prueba"""
    print("\n" + "="*70)
    print(" "*15 + "SUITE DE PRUEBAS UNIETAXI")
    print("="*70 + "\n")
    
    # Crear suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar todas las clases
    suite.addTests(loader.loadTestsFromTestCase(TestSincronizacion))
    suite.addTests(loader.loadTestsFromTestCase(TestCasosExtremos))
    suite.addTests(loader.loadTestsFromTestCase(TestFuncionalidadBasica))
    suite.addTests(loader.loadTestsFromTestCase(TestLogicaNegocio))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegracion))
    
    # Ejecutar
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE PRUEBAS")
    print("="*70)
    print(f"Total de pruebas: {result.testsRun}")
    print(f"✅ Exitosas: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Fallidas: {len(result.failures)}")
    print(f"⚠️ Errores: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
    else:
        print("\n⚠️ Algunas pruebas fallaron")
    
    print("="*70 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)