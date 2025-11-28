"""
simulacion_web.py - Simulación en Tiempo Real con Visualización Web

Este módulo ejecuta la simulación del sistema UNIETAXI y genera
una página web que se actualiza en tiempo real mostrando:
- Taxis moviéndose por el mapa
- Clientes solicitando servicios
- Asignaciones en tiempo real
- Estadísticas actualizadas
- Servicios completados
"""

import json
import os
import time
import threading
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser

import config
from sistema_central import SistemaCentral, cargar_clientes_desde_json, cargar_taxis_desde_json
from main import hilo_cliente, hilo_sistema_principal

# ==================== GENERADOR DE HTML EN TIEMPO REAL ====================

class SimulacionWebGenerator:
    """Genera y actualiza la página web de simulación en tiempo real"""
    
    def __init__(self, sistema: SistemaCentral):
        self.sistema = sistema
        self.eventos = []  # Log de eventos para mostrar
        self.archivo_html = os.path.join(config.BASE_DIR, "simulacion_tiempo_real.html")
        self.archivo_datos = os.path.join(config.DATA_DIR, "simulacion_live.json")
        self.running = True
        
    def agregar_evento(self, tipo: str, mensaje: str, datos: dict = None):
        """Agrega un evento al log"""
        evento = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "tipo": tipo,
            "mensaje": mensaje,
            "datos": datos or {}
        }
        self.eventos.append(evento)
        
        # Mantener solo los últimos 50 eventos
        if len(self.eventos) > 50:
            self.eventos.pop(0)
        
        # Actualizar archivo de datos
        self.actualizar_datos_live()
    
    def actualizar_datos_live(self):
        """Actualiza el archivo JSON con datos en tiempo real"""
        datos = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "dia_actual": self.sistema.dia_actual,
            "servicios_activos": self.sistema.servicios_activos,
            "total_servicios": len(self.sistema.servicios_completados),
            "ganancia_empresa": round(self.sistema.ganancia_total_empresa, 2),
            "eventos": self.eventos[-20:],  # Últimos 20 eventos
            "taxis": [],
            "clientes_activos": [],
            "estadisticas": {
                "taxis_disponibles": len([t for t in self.sistema.taxis if t.disponible]),
                "taxis_ocupados": len([t for t in self.sistema.taxis if not t.disponible]),
                "clientes_en_servicio": len([c for c in self.sistema.clientes if c.en_servicio])
            }
        }
        
        # Datos de taxis
        for taxi in self.sistema.taxis:
            datos["taxis"].append({
                "id": taxi.id_taxi,
                "placa": taxi.placa,
                "nombre": taxi.nombre_completo(),
                "ubicacion": list(taxi.ubicacion),
                "disponible": taxi.disponible,
                "cliente_actual": taxi.cliente_actual,
                "calificacion": round(taxi.calcular_calificacion_promedio(), 2),
                "servicios": taxi.cantidad_servicios,
                "ganancia": round(taxi.ganancia_total, 2),
                "color": taxi.color_mapa
            })
        
        # Clientes activos
        for cliente in self.sistema.clientes:
            if cliente.en_servicio:
                datos["clientes_activos"].append({
                    "cedula": cliente.cedula,
                    "nombre": cliente.nombre_completo(),
                    "ubicacion": list(cliente.ubicacion_actual),
                    "destino": list(cliente.destino),
                    "taxi_asignado": cliente.taxi_asignado
                })
        
        # Guardar
        with open(self.archivo_datos, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
    
    def generar_html(self):
        """Genera el archivo HTML de la simulación"""
        
        # Obtener configuración inicial
        centro = config.CENTRO_MADRID
        radio = config.TAXI_CONFIG["RADIO_BUSQUEDA_KM"] * 1000
        
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UNIETAXI - Simulación en Tiempo Real</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a1a;
            color: #fff;
            overflow: hidden;
        }}
        
        .container {{
            display: grid;
            grid-template-columns: 300px 1fr 350px;
            grid-template-rows: 60px 1fr;
            height: 100vh;
            gap: 0;
        }}
        
        .header {{
            grid-column: 1 / -1;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}
        
        .header h1 {{
            font-size: 24px;
            font-weight: 600;
        }}
        
        .header-stats {{
            display: flex;
            gap: 30px;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
        }}
        
        .stat-label {{
            font-size: 11px;
            opacity: 0.9;
        }}
        
        .sidebar-left {{
            background: #2d2d2d;
            padding: 20px;
            overflow-y: auto;
            border-right: 1px solid #444;
        }}
        
        .sidebar-right {{
            background: #2d2d2d;
            padding: 20px;
            overflow-y: auto;
            border-left: 1px solid #444;
        }}
        
        #map {{
            height: 100%;
            background: #1a1a1a;
        }}
        
        .section-title {{
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
            color: #667eea;
        }}
        
        .taxi-item {{
            background: #3a3a3a;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid;
        }}
        
        .taxi-item.disponible {{
            border-left-color: #27ae60;
        }}
        
        .taxi-item.ocupado {{
            border-left-color: #e74c3c;
        }}
        
        .taxi-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        
        .taxi-placa {{
            font-weight: bold;
            font-size: 14px;
        }}
        
        .taxi-estado {{
            font-size: 11px;
            padding: 3px 8px;
            border-radius: 12px;
            background: rgba(255,255,255,0.1);
        }}
        
        .taxi-info {{
            font-size: 12px;
            color: #aaa;
            line-height: 1.6;
        }}
        
        .evento-item {{
            background: #3a3a3a;
            padding: 10px;
            margin-bottom: 8px;
            border-radius: 6px;
            font-size: 12px;
            border-left: 3px solid;
        }}
        
        .evento-item.solicitud {{ border-left-color: #3498db; }}
        .evento-item.asignacion {{ border-left-color: #f39c12; }}
        .evento-item.completado {{ border-left-color: #27ae60; }}
        .evento-item.sistema {{ border-left-color: #9b59b6; }}
        
        .evento-time {{
            font-size: 10px;
            color: #888;
            margin-bottom: 4px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 20px;
        }}
        
        .stat-card {{
            background: #3a3a3a;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stat-card-value {{
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-card-label {{
            font-size: 11px;
            color: #aaa;
        }}
        
        .loading {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0,0,0,0.9);
            padding: 30px 50px;
            border-radius: 10px;
            text-align: center;
            z-index: 10000;
        }}
        
        .spinner {{
            border: 4px solid #333;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .taxi-marker {{
            width: 40px;
            height: 40px;
            border: 3px solid #fff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.4);
        }}
        
        .cliente-marker {{
            width: 35px;
            height: 35px;
            border: 2px solid #3498db;
            border-radius: 50%;
            background: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }}
        
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: #1a1a1a;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: #667eea;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div id="loading" class="loading">
        <div class="spinner"></div>
        <div>Cargando simulación...</div>
    </div>
    
    <div class="container">
        <header class="header">
            <h1>🚖 UNIETAXI - Simulación en Tiempo Real</h1>
            <div class="header-stats">
                <div class="stat-item">
                    <div class="stat-value" id="stat-dia">1</div>
                    <div class="stat-label">DÍA</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="stat-servicios">0</div>
                    <div class="stat-label">SERVICIOS</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="stat-ganancia">$0</div>
                    <div class="stat-label">GANANCIA</div>
                </div>
            </div>
        </header>
        
        <aside class="sidebar-left">
            <div class="section-title">🚕 TAXIS ACTIVOS</div>
            <div id="lista-taxis"></div>
            
            <div class="section-title" style="margin-top: 20px;">📊 ESTADÍSTICAS</div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-card-value" id="taxis-disponibles">0</div>
                    <div class="stat-card-label">Disponibles</div>
                </div>
                <div class="stat-card">
                    <div class="stat-card-value" id="taxis-ocupados">0</div>
                    <div class="stat-card-label">Ocupados</div>
                </div>
            </div>
        </aside>
        
        <main id="map"></main>
        
        <aside class="sidebar-right">
            <div class="section-title">📋 EVENTOS EN TIEMPO REAL</div>
            <div id="eventos-lista"></div>
        </aside>
    </div>
    
    <script>
        // Variables globales
        let map;
        let taxiMarkers = {{}};
        let clienteMarkers = {{}};
        let routeLines = {{}};
        
        // Inicializar mapa
        function initMap() {{
            map = L.map('map').setView([{centro['lat']}, {centro['lng']}], 13);
            
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '© OpenStreetMap | UNIETAXI'
            }}).addTo(map);
            
            // Círculo de radio de búsqueda
            L.circle([{centro['lat']}, {centro['lng']}], {{
                radius: {radio},
                color: '#667eea',
                fillColor: '#667eea',
                fillOpacity: 0.1,
                weight: 2
            }}).addTo(map).bindPopup('Radio de búsqueda: {config.TAXI_CONFIG["RADIO_BUSQUEDA_KM"]} km');
            
            // Marcador central (Sol)
            L.marker([{centro['lat']}, {centro['lng']}], {{
                icon: L.divIcon({{
                    className: 'centro-marker',
                    html: '<div style="font-size: 30px;">⭐</div>',
                    iconSize: [40, 40]
                }})
            }}).addTo(map).bindPopup('<b>Puerta del Sol</b><br>Centro de operaciones');
        }}
        
        // Actualizar datos
        async function actualizarDatos() {{
            try {{
                const response = await fetch('data/simulacion_live.json?t=' + Date.now());
                const datos = await response.json();
                
                // Actualizar estadísticas header
                document.getElementById('stat-dia').textContent = datos.dia_actual;
                document.getElementById('stat-servicios').textContent = datos.total_servicios;
                document.getElementById('stat-ganancia').textContent = '$' + datos.ganancia_empresa.toFixed(2);
                
                // Actualizar estadísticas sidebar
                document.getElementById('taxis-disponibles').textContent = datos.estadisticas.taxis_disponibles;
                document.getElementById('taxis-ocupados').textContent = datos.estadisticas.taxis_ocupados;
                
                // Actualizar taxis
                actualizarTaxis(datos.taxis);
                
                // Actualizar clientes
                actualizarClientes(datos.clientes_activos);
                
                // Actualizar eventos
                actualizarEventos(datos.eventos);
                
            }} catch (error) {{
                console.error('Error actualizando datos:', error);
            }}
        }}
        
        // Actualizar taxis en mapa y lista
        function actualizarTaxis(taxis) {{
            const listaTaxis = document.getElementById('lista-taxis');
            listaTaxis.innerHTML = '';
            
            taxis.forEach(taxi => {{
                // Actualizar marcador en mapa
                if (!taxiMarkers[taxi.id]) {{
                    const icon = L.divIcon({{
                        className: 'taxi-marker',
                        html: `<div style="background: ${{taxi.color}}; width: 100%; height: 100%; border-radius: 50%; display: flex; align-items: center; justify-content: center;">🚕</div>`,
                        iconSize: [40, 40]
                    }});
                    
                    taxiMarkers[taxi.id] = L.marker(taxi.ubicacion, {{ icon: icon }}).addTo(map);
                }} else {{
                    // Animar movimiento
                    taxiMarkers[taxi.id].setLatLng(taxi.ubicacion);
                }}
                
                // Actualizar popup
                let popupContent = `<b>${{taxi.placa}}</b><br>`;
                popupContent += `👤 ${{taxi.nombre}}<br>`;
                popupContent += `⭐ ${{taxi.calificacion}}<br>`;
                popupContent += `📊 ${{taxi.servicios}} servicios<br>`;
                popupContent += `💰 $${{taxi.ganancia}}<br>`;
                popupContent += `Estado: ${{taxi.disponible ? '✅ Disponible' : '🚗 En servicio'}}`;
                taxiMarkers[taxi.id].bindPopup(popupContent);
                
                // Agregar a lista
                const taxiItem = document.createElement('div');
                taxiItem.className = `taxi-item ${{taxi.disponible ? 'disponible' : 'ocupado'}}`;
                taxiItem.innerHTML = `
                    <div class="taxi-header">
                        <div class="taxi-placa">🚕 ${{taxi.placa}}</div>
                        <div class="taxi-estado">${{taxi.disponible ? 'LIBRE' : 'OCUPADO'}}</div>
                    </div>
                    <div class="taxi-info">
                        👤 ${{taxi.nombre}}<br>
                        ⭐ ${{taxi.calificacion}} | 📊 ${{taxi.servicios}}<br>
                        💰 $${{taxi.ganancia}}
                    </div>
                `;
                listaTaxis.appendChild(taxiItem);
            }});
        }}
        
        // Actualizar clientes en mapa
        function actualizarClientes(clientes) {{
            // Limpiar marcadores antiguos
            Object.values(clienteMarkers).forEach(marker => map.removeLayer(marker));
            clienteMarkers = {{}};
            
            // Limpiar líneas de ruta
            Object.values(routeLines).forEach(line => map.removeLayer(line));
            routeLines = {{}};
            
            clientes.forEach(cliente => {{
                // Marcador de cliente
                const icon = L.divIcon({{
                    className: 'cliente-marker',
                    html: '<div>🧍</div>',
                    iconSize: [35, 35]
                }});
                
                clienteMarkers[cliente.cedula] = L.marker(cliente.ubicacion, {{ icon: icon }}).addTo(map);
                clienteMarkers[cliente.cedula].bindPopup(`<b>${{cliente.nombre}}</b><br>Taxi: ${{cliente.taxi_asignado}}`);
                
                // Línea hacia destino
                routeLines[cliente.cedula] = L.polyline([cliente.ubicacion, cliente.destino], {{
                    color: '#3498db',
                    weight: 2,
                    dashArray: '5, 10',
                    opacity: 0.6
                }}).addTo(map);
            }});
        }}
        
        // Actualizar eventos
        function actualizarEventos(eventos) {{
            const listaEventos = document.getElementById('eventos-lista');
            listaEventos.innerHTML = '';
            
            eventos.reverse().forEach(evento => {{
                const eventoItem = document.createElement('div');
                eventoItem.className = `evento-item ${{evento.tipo}}`;
                eventoItem.innerHTML = `
                    <div class="evento-time">${{evento.timestamp}}</div>
                    <div>${{evento.mensaje}}</div>
                `;
                listaEventos.appendChild(eventoItem);
            }});
        }}
        
        // Inicializar
        document.addEventListener('DOMContentLoaded', () => {{
            initMap();
            document.getElementById('loading').style.display = 'none';
            
            // Actualizar cada 500ms
            setInterval(actualizarDatos, 500);
            actualizarDatos();
        }});
    </script>
</body>
</html>"""
        
        with open(self.archivo_html, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Archivo HTML generado: {self.archivo_html}")
        return self.archivo_html


# ==================== WRAPPER DEL SISTEMA CON LOGGING ====================

class SistemaCentralWeb(SistemaCentral):
    """Extensión del sistema central que registra eventos para la web"""
    
    def __init__(self, num_dias: int, web_gen: SimulacionWebGenerator):
        super().__init__(num_dias)
        self.web_gen = web_gen
    
    def asignar_taxi(self, cliente):
        """Override para registrar evento"""
        taxi = super().asignar_taxi(cliente)
        
        if taxi:
            self.web_gen.agregar_evento(
                "asignacion",
                f"🚖 {cliente.nombre_completo()} ← Taxi {taxi.placa}",
                {
                    "cliente": cliente.cedula,
                    "taxi": taxi.id_taxi,
                    "origen": cliente.ubicacion_actual,
                    "destino": cliente.destino
                }
            )
        else:
            self.web_gen.agregar_evento(
                "solicitud",
                f"❌ No hay taxis para {cliente.nombre_completo()}",
                {"cliente": cliente.cedula}
            )
        
        return taxi
    
    def realizar_servicio(self, cliente, taxi):
        """Override para registrar eventos"""
        self.web_gen.agregar_evento(
            "solicitud",
            f"🚗 Servicio iniciado: {cliente.nombre_completo()} en {taxi.placa}",
            {"cliente": cliente.cedula, "taxi": taxi.id_taxi}
        )
        
        super().realizar_servicio(cliente, taxi)
        
        servicio = self.servicios_completados[-1]
        self.web_gen.agregar_evento(
            "completado",
            f"✅ Servicio #{servicio.id_servicio} completado: ${servicio.costo:.2f} - {servicio.calificacion}⭐",
            {"servicio": servicio.id_servicio}
        )
    
    def iniciar_nuevo_dia(self):
        """Override para registrar evento"""
        super().iniciar_nuevo_dia()
        self.web_gen.agregar_evento(
            "sistema",
            f"🌅 Inicio del Día {self.dia_actual}",
            {"dia": self.dia_actual}
        )
    
    def finalizar_dia(self):
        """Override para registrar evento"""
        self.web_gen.agregar_evento(
            "sistema",
            f"🌙 Finalizando Día {self.dia_actual}...",
            {"dia": self.dia_actual}
        )
        super().finalizar_dia()


# ==================== FUNCIÓN PRINCIPAL ====================

def iniciar_simulacion_web(num_dias: int = 2):
    """Inicia la simulación con visualización web"""
    
    print("="*60)
    print("UNIETAXI - Simulación Web en Tiempo Real")
    print("="*60)
    
    # Crear directorio data si no existe
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    # Crear sistema
    web_gen = SimulacionWebGenerator(None)  # Temporal
    sistema = SistemaCentralWeb(num_dias=num_dias, web_gen=web_gen)
    web_gen.sistema = sistema
    
    # Cargar datos
    print("\n📂 Cargando datos...")
    num_taxis = cargar_taxis_desde_json(sistema)
    num_clientes = cargar_clientes_desde_json(sistema)
    
    # Si no hay datos, usar ejemplos
    if num_taxis == 0:
        print("⚠️ Usando taxis de ejemplo...")
        for i in range(5):
            sistema.afiliar_taxi(
                100000 + i, f"Taxi{i+1}", "Driver", f"TX{i+1:03d}",
                "Toyota", "Corolla", 60
            )
    
    if num_clientes == 0:
        print("⚠️ Usando clientes de ejemplo...")
        for i in range(8):
            sistema.afiliar_cliente(
                200000 + i, f"Cliente{i+1}", "Test", "4532123456789012"
            )
    
    print(f"\n✅ Sistema listo:")
    print(f"   🚖 Taxis: {len(sistema.taxis)}")
    print(f"   🧍 Clientes: {len(sistema.clientes)}")
    print(f"   📅 Días: {num_dias}")
    
    # Generar HTML
    print("\n🌐 Generando interfaz web...")
    archivo_html = web_gen.generar_html()
    
    # Inicializar datos live
    web_gen.actualizar_datos_live()
    
    # Iniciar hilo del sistema
    def sistema_thread():
        for dia in range(sistema.num_dias):
            sistema.iniciar_nuevo_dia()
            time.sleep(3)  # 3 segundos por día
            sistema.finalizar_dia()
        
        sistema.fin_sistema = True
        web_gen.agregar_evento("sistema", "🏁 Simulación finalizada", {})
        print("\n✅ Simulación completada")
    
    hilo_sistema = threading.Thread(target=sistema_thread, daemon=True)
    hilo_sistema.start()
    
    # Iniciar hilos de clientes
    def iniciar_clientes():
        time.sleep(1)  # Esperar a que empiece el día
        hilos = []
        for cliente in sistema.clientes[:10]:
            hilo = threading.Thread(
                target=hilo_cliente,
                args=(sistema, cliente, 2),
                daemon=True
            )
            hilos.append(hilo)
            hilo.start()
            time.sleep(0.2)
        
        for hilo in hilos:
            hilo.join()
    
    threading.Thread(target=iniciar_clientes, daemon=True).start()
    
    # Abrir navegador
    print(f"\n🌐 Abriendo navegador en: {archivo_html}")
    webbrowser.open('file://' + os.path.abspath(archivo_html))
    
    print("\n✅ Simulación web iniciada")
    print("📊 La página se actualiza automáticamente cada 500ms")
    print("⏹️  Presiona Ctrl+C para detener\n")
    
    # Mantener el script corriendo
    try:
        while not sistema.fin_sistema:
            time.sleep(1)
            web_gen.actualizar_datos_live()
    except KeyboardInterrupt:
        print("\n\n⚠️ Simulación detenida por el usuario")
    
    # Generar reporte final
    sistema.generar_reporte_mensual()
    print("\n✅ Sistema finalizado")


if __name__ == "__main__":
    import sys
    
    # Permitir especificar días
    num_dias = 2
    if len(sys.argv) > 1:
        try:
            num_dias = int(sys.argv[1])
        except:
            pass
    
    iniciar_simulacion_web(num_dias)