"""
hilos.py - Módulo con hilos de trabajo (cliente y sistema principal)

Funciones exportadas:
- hilo_cliente(sistema, cliente, num_solicitudes)
- hilo_sistema_principal(sistema)

Este módulo evita importaciones circulares al centralizar los hilos.
"""

import time
import random
import threading
import config
from sistema_central import SistemaCentral


def hilo_cliente(sistema: SistemaCentral, cliente, num_solicitudes: int = 1):
    """
    Hilo simulado que representa la actividad de un cliente.

    Repetirá `num_solicitudes` intentos de solicitar taxi y realizar el servicio.
    """
    for i in range(num_solicitudes):
        # Intentar activar servicio (verifica fin de día)
        if not sistema.activar_servicio():
            # Si no se puede activar, salir
            return

        try:
            # Intentar asignar un taxi
            taxi = sistema.asignar_taxi(cliente)
            if taxi:
                cliente.en_servicio = True
                sistema.realizar_servicio(cliente, taxi)
            else:
                # No hay taxi disponible - esperar un poco antes de reintentar
                time.sleep(0.1)

        except Exception as e:
            # Registrar error leve y continuar
            print(f"⚠️ Error en hilo_cliente: {e}")
        finally:
            # Finalizar servicio (reducir contador de servicios)
            try:
                sistema.desactivar_servicio()
            except Exception:
                pass

            # Pausa entre solicitudes
            time.sleep(random.uniform(0.05, 0.2))


def hilo_sistema_principal(sistema: SistemaCentral):
    """
    Hilo principal que recorre los días de simulación del sistema.

    Ejecuta: iniciar_nuevo_dia(), crea hilos de clientes, espera, finalizar_dia().
    """
    import random
    
    for dia in range(sistema.num_dias):
        sistema.iniciar_nuevo_dia()
        
        # ✅ CREAR HILOS DE CLIENTES PARA ESTE DÍA
        hilos_clientes = []
        clientes_activos = sistema.clientes[:min(10, len(sistema.clientes))]
        
        for cliente in clientes_activos:
            # Asignar ubicaciones aleatorias cada día
            try:
                punto = random.choice(config.PUNTOS_INICIO_TAXIS)
                destino = random.choice(config.RUTA_PRINCIPAL)
                cliente.ubicacion_actual = (punto[0], punto[1])
                cliente.destino = (destino[0], destino[1])
            except Exception:
                pass
            
            # Crear hilo para este cliente (1-3 solicitudes por día)
            num_solicitudes = random.randint(1, 3)
            hilo = threading.Thread(
                target=hilo_cliente,
                args=(sistema, cliente, num_solicitudes)
            )
            hilos_clientes.append(hilo)
            hilo.start()
            time.sleep(0.1)
        
        # Esperar la duración configurada de simulación por día
        duracion = getattr(config, 'SIMULACION', {}).get('TIEMPO_SIMULACION_DIA', 6.0)
        try:
            time.sleep(duracion)
        except Exception:
            time.sleep(2.0)
        
        # Esperar a que terminen todos los hilos de este día
        for hilo in hilos_clientes:
            hilo.join(timeout=2.0)
        
        sistema.finalizar_dia()

    sistema.fin_sistema = True
    print("✅ hilo_sistema_principal: Simulación completada")
