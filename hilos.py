"""
hilos.py - Módulo con hilos de trabajo (cliente y sistema principal)

Funciones exportadas:
- hilo_cliente(sistema, cliente, num_solicitudes)
- hilo_sistema_principal(sistema)

Este módulo evita importaciones circulares al centralizar los hilos.
"""

import time
import random

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

    Ejecuta: iniciar_nuevo_dia(), espera breve, finalizar_dia().
    """
    for dia in range(sistema.num_dias):
        sistema.iniciar_nuevo_dia()
        # Tiempo real acelerado: dormir un poco para simular paso de días
        time.sleep(0.05)
        sistema.finalizar_dia()

    sistema.fin_sistema = True
    print("✅ hilo_sistema_principal: Simulación completada")
