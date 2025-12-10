"""
visualizacion_mapa.py - Generador de Mapa Animado UNIETAXI

Este módulo genera un mapa interactivo HTML con animación de taxis
basado en los datos reales del sistema.
"""

import json
import os
import config

# ==================== CARGA DE DATOS ====================

def cargar_taxis_registrados():
    """
    Carga los taxis desde el archivo JSON en la raíz del proyecto.
    
    Returns:
        Lista de taxis o lista vacía si no existe
    """
    try:
        # Buscar taxis_registrados.json en la raíz del proyecto (fuera de data/)
        archivo_taxis = os.path.join(config.BASE_DIR, "taxis_registrados.json")
        with open(archivo_taxis, "r", encoding="utf-8") as f:
            taxistas_registrados = json.load(f)
        print(f"✅ Cargados {len(taxistas_registrados)} taxis desde {archivo_taxis}")
        return taxistas_registrados
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo en raíz: taxis_registrados.json")
        return []
    except json.JSONDecodeError:
        print(f"❌ Error al leer taxis_registrados.json")
        return []


def cargar_configuracion_mapa():
    """
    Carga la configuración del mapa si existe.
    
    Returns:
        Diccionario de configuración o None
    """
    config_file = os.path.join(config.DATA_DIR, "config_mapa.json")
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


# ==================== GENERACIÓN DE RUTAS ====================

def generar_rutas_taxis(num_taxis):
    """
    Genera rutas desde puntos de inicio hasta Sol para cada taxi.
    
    Args:
        num_taxis: Número de taxis a generar rutas
    
    Returns:
        Lista de diccionarios con rutas
    """
    # Ruta principal (destino común)
    sol = config.CENTRO_MADRID
    
    # Rutas predefinidas para diferentes taxis
    rutas_predefinidas = [
        # Taxi 1: Desde Ópera
        {
            "nombre": "Taxi 1 (Ópera)",
            "ruta": [
                [40.4178, -3.7094],
                [40.4177, -3.7085],
                [40.4168, -3.7047],
                [sol["lat"], sol["lng"]]
            ],
            "color": "orange",
            "bg": "orange"
        },
        # Taxi 2: Desde Plaza España
        {
            "nombre": "Taxi 2 (Plaza España)",
            "ruta": [
                [40.4234, -3.7109],
                [40.4203, -3.7059],
                [40.4200, -3.7014],
                [sol["lat"], sol["lng"]]
            ],
            "color": "purple",
            "bg": "purple"
        },
        # Taxi 3: Desde Retiro
        {
            "nombre": "Taxi 3 (Retiro)",
            "ruta": [
                [40.4153, -3.6840],
                [40.4170, -3.6890],
                [40.4185, -3.6950],
                [sol["lat"], sol["lng"]]
            ],
            "color": "red",
            "bg": "red"
        },
        # Taxi 4: Desde Embajadores
        {
            "nombre": "Taxi 4 (Embajadores)",
            "ruta": [
                [40.4050, -3.7026],
                [40.4075, -3.6934],
                [40.4087, -3.6920],
                [40.4152, -3.6943],
                [40.4193, -3.6936],
                [40.4178, -3.6995],
                [sol["lat"], sol["lng"]]
            ],
            "color": "darkgreen",
            "bg": "green"
        },
        # Taxi 5: Desde Argüelles
        {
            "nombre": "Taxi 5 (Argüelles)",
            "ruta": [
                [40.4306, -3.7162],
                [40.4263, -3.7132],
                [40.4235, -3.7148],
                [40.4219, -3.7132],
                [40.4203, -3.7154],
                [40.4203, -3.7200],
                [40.4139, -3.7209],
                [40.4139, -3.7168],
                [40.4110, -3.7183],
                [40.4087, -3.7167],
                [40.4065, -3.7114],
                [40.4086, -3.7131],
                [40.4106, -3.7139],
                [40.4150, -3.7135],
                [40.4155, -3.7104],
                [40.4161, -3.7078],
                [sol["lat"], sol["lng"]]
            ],
            "color": "gray",
            "bg": "gray"
        },
        # Taxi 6: Desde Gran Vía
        {
            "nombre": "Taxi 6 (Gran Vía)",
            "ruta": [
                [40.4200, -3.7100],
                [40.4190, -3.7070],
                [40.4175, -3.7045],
                [sol["lat"], sol["lng"]]
            ],
            "color": "blue",
            "bg": "blue"
        },
        # Taxi 7: Desde Atocha
        {
            "nombre": "Taxi 7 (Atocha)",
            "ruta": [
                [40.4100, -3.6900],
                [40.4120, -3.6920],
                [40.4145, -3.6980],
                [sol["lat"], sol["lng"]]
            ],
            "color": "pink",
            "bg": "pink"
        },
        # Taxi 8: Desde Salamanca
        {
            "nombre": "Taxi 8 (Salamanca)",
            "ruta": [
                [40.4250, -3.6850],
                [40.4220, -3.6900],
                [40.4190, -3.6950],
                [sol["lat"], sol["lng"]]
            ],
            "color": "brown",
            "bg": "brown"
        }
    ]
    
    # Devolver solo las rutas necesarias
    return rutas_predefinidas[:num_taxis]


# ==================== GENERACIÓN DE HTML ====================

def generar_mapa_html(taxistas_registrados):
    """
    Genera el archivo HTML del mapa animado.
    
    Args:
        taxistas_registrados: Lista de taxis desde el JSON
    
    Returns:
        Ruta del archivo HTML generado
    """
    num_taxis = min(len(taxistas_registrados), 8)  # Máximo 8 taxis
    
    # Asociar cada taxi con su taxista
    taxi_taxista_map = {}
    for i in range(num_taxis):
        taxi_id = f"taxi{i+1}"
        if i < len(taxistas_registrados):
            taxista = taxistas_registrados[i]
            taxi_taxista_map[taxi_id] = {
                "nombre": taxista.get("nombre", taxista.get("nombre_completo", "Taxista")),
                "placa": taxista.get("placa", "N/A"),
                "identificacion": taxista.get("identificacion", taxista.get("cedula", "N/A")),
                "fecha_registro": taxista.get("fecha_registro", "N/A"),
                "estado": taxista.get("estado", "activo"),
                "calificacion": taxista.get("calificacion_promedio", 5.0),
                "servicios": taxista.get("cantidad_servicios", 0)
            }
    
    # Generar rutas para los taxis
    rutas_taxis = generar_rutas_taxis(num_taxis)
    
    # Mostrar asociaciones
    print("\n🚕 ASOCIACIONES TAXI ↔ TAXISTA:")
    for taxi_id, taxista in taxi_taxista_map.items():
        print(f"   {taxi_id}: {taxista['nombre']} - Placa: {taxista['placa']}")
    
    # Convertir a JSON para JavaScript
    taxistas_js = json.dumps(taxi_taxista_map, ensure_ascii=False)
    rutas_js = json.dumps(rutas_taxis, ensure_ascii=False)
    
    # Ruta principal
    ruta_principal = [[p[0], p[1]] for p in config.RUTA_PRINCIPAL]
    ruta_principal_js = json.dumps(ruta_principal)
    
    # Centro del mapa
    centro = config.CENTRO_MADRID
    radio_busqueda = config.TAXI_CONFIG["RADIO_BUSQUEDA_KM"] * 1000  # Convertir a metros
    
    # Generar HTML
    html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>UNIETAXI - Mapa en Tiempo Real</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
        #map {{ position: absolute; top: 0; bottom: 0; width: 100%; }}
        .taxi-marker {{
            width: 35px;
            height: 35px;
            border: 3px solid black;
            border-radius: 50%;
            text-align: center;
            line-height: 29px;
            font-size: 20px;
        }}
        .controls {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            z-index: 1000;
            max-width: 320px;
            max-height: 90vh;
            overflow-y: auto;
        }}
        .controls h3 {{
            margin: 0 0 10px 0;
            font-size: 16px;
            color: #333;
        }}
        .controls label {{
            display: block;
            margin: 8px 0;
            cursor: pointer;
            font-size: 13px;
        }}
        .controls input {{
            margin-right: 8px;
        }}
        .btn {{
            margin-top: 10px;
            padding: 10px 15px;
            background: #27ae60;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
            font-size: 14px;
            font-weight: bold;
        }}
        .btn:hover {{
            background: #229954;
        }}
        .btn-reset {{
            background: #e74c3c;
            margin-top: 5px;
        }}
        .btn-reset:hover {{
            background: #c0392b;
        }}
        .taxista-info {{
            font-size: 11px;
            color: #666;
            margin-left: 28px;
            line-height: 1.4;
        }}
        .header {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            z-index: 1000;
        }}
        .header h2 {{
            margin: 0;
            font-size: 18px;
            color: #2c3e50;
        }}
        .header p {{
            margin: 5px 0 0 0;
            font-size: 12px;
            color: #7f8c8d;
        }}
        .stats {{
            position: absolute;
            bottom: 10px;
            left: 10px;
            background: white;
            padding: 10px 15px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            z-index: 1000;
            font-size: 12px;
        }}
        .stats strong {{
            color: #2c3e50;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    
    <div class="header">
        <h2>🚖 UNIETAXI - Sistema en Tiempo Real</h2>
        <p>Radio de búsqueda: {config.TAXI_CONFIG['RADIO_BUSQUEDA_KM']} km | {num_taxis} taxis activos</p>
    </div>
    
    <div class="stats" id="stats">
        <strong>📊 Estadísticas:</strong><br>
        Taxis activos: <span id="stat-activos">{num_taxis}</span><br>
        Taxis en movimiento: <span id="stat-movimiento">0</span>
    </div>
    
    <div class="controls">
        <h3>🚕 Control de Taxis</h3>
        <div id="taxi-controls"></div>
        <button class="btn" onclick="iniciarAnimacion()">▶️ Iniciar Animación</button>
        <button class="btn btn-reset" onclick="resetearAnimacion()">🔄 Reiniciar</button>
    </div>
    
    <script>
        // Datos de taxistas
        var taxistasData = {taxistas_js};
        
        // Rutas de taxis
        var rutasTaxis = {rutas_js};
        
        // Crear controles dinámicamente
        var controlsDiv = document.getElementById('taxi-controls');
        Object.keys(taxistasData).forEach(function(taxiId, index) {{
            var taxista = taxistasData[taxiId];
            var ruta = rutasTaxis[index];
            
            var label = document.createElement('label');
            var checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = taxiId;
            checkbox.checked = true;
            
            var emoji = ['🟠', '🟣', '🔴', '🟢', '⚫', '🔵', '🌸', '🟤'][index];
            var text = emoji + ' ' + ruta.nombre;
            
            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(text));
            
            var infoDiv = document.createElement('div');
            infoDiv.className = 'taxista-info';
            infoDiv.innerHTML = '👤 ' + taxista.nombre + '<br>🚗 ' + taxista.placa;
            if (taxista.calificacion) {{
                infoDiv.innerHTML += '<br>⭐ ' + taxista.calificacion.toFixed(1);
            }}
            label.appendChild(infoDiv);
            
            controlsDiv.appendChild(label);
        }});
        
        // Crear mapa
        var map = L.map('map').setView([{centro['lat']}, {centro['lng']}], 14);
        
        // Añadir capa de OpenStreetMap
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap | UNIETAXI Sistema v{config.VERSION}'
        }}).addTo(map);
        
        // Ruta principal (azul)
        var rutaPrincipal = {ruta_principal_js};
        L.polyline(rutaPrincipal, {{color: 'blue', weight: 5, opacity: 0.8}}).addTo(map);
        
        // Marcadores de ruta principal
        L.marker([{centro['lat']}, {centro['lng']}]).addTo(map)
            .bindPopup('<b>{centro['nombre']}</b><br>Punto de encuentro');
        
        // Círculo de radio de búsqueda
        L.circle([{centro['lat']}, {centro['lng']}], {{
            radius: {radio_busqueda},
            color: 'white',
            fillColor: 'white',
            fillOpacity: 0.1
        }}).addTo(map).bindPopup('Radio de búsqueda: {config.TAXI_CONFIG['RADIO_BUSQUEDA_KM']} km');
        
        // Dibujar las rutas de los taxis
        rutasTaxis.forEach(function(taxi, index) {{
            L.polyline(taxi.ruta, {{
                color: taxi.color,
                weight: 4,
                opacity: 0.6,
                dashArray: '5, 5'
            }}).addTo(map);
            
            // Marcador de inicio
            var taxista = taxistasData['taxi' + (index + 1)];
            var popupText = taxi.nombre + ' - Partida';
            if (taxista) {{
                popupText += '<br><b>Taxista:</b> ' + taxista.nombre;
                popupText += '<br><b>Placa:</b> ' + taxista.placa;
            }}
            L.marker(taxi.ruta[0]).addTo(map).bindPopup(popupText);
        }});
        
        // Variables globales para animación
        var taxiMarkers = [];
        var taxiStates = [];
        var animationRunning = false;
        
        // Inicializar marcadores
        rutasTaxis.forEach(function(taxi, i) {{
            var icon = L.divIcon({{
                className: 'taxi-marker',
                html: '<div style="background: ' + taxi.bg + '; width: 100%; height: 100%; border-radius: 50%; display: flex; align-items: center; justify-content: center;">🚕</div>',
                iconSize: [35, 35]
            }});
            
            var marker = L.marker(taxi.ruta[0], {{icon: icon}}).addTo(map);
            
            // Popup con información del taxista
            var taxista = taxistasData['taxi' + (i + 1)];
            var popupContent = '<b>' + taxi.nombre + '</b>';
            if (taxista) {{
                popupContent += '<br>👤 ' + taxista.nombre;
                popupContent += '<br>🚗 ' + taxista.placa;
                if (taxista.calificacion) {{
                    popupContent += '<br>⭐ ' + taxista.calificacion.toFixed(1);
                }}
                if (taxista.servicios) {{
                    popupContent += '<br>📊 ' + taxista.servicios + ' servicios';
                }}
            }}
            marker.bindPopup(popupContent);
            
            taxiMarkers.push(marker);
            taxiStates.push({{
                id: 'taxi' + (i + 1),
                index: 0,
                step: 0,
                totalSteps: 50,
                ruta: taxi.ruta,
                nombre: taxi.nombre,
                finished: false,
                activo: true
            }});
        }});
        
        // Función para iniciar la animación
        function iniciarAnimacion() {{
            // Leer qué taxis están seleccionados
            taxiStates.forEach(function(state) {{
                var checkbox = document.getElementById(state.id);
                state.activo = checkbox.checked;
            }});
            
            if (!animationRunning) {{
                animationRunning = true;
                animateAllTaxis();
            }}
        }}
        
        // Función para resetear
        function resetearAnimacion() {{
            animationRunning = false;
            taxiStates.forEach(function(state, i) {{
                state.finished = false;
                state.index = 0;
                state.step = 0;
                taxiMarkers[i].setLatLng(state.ruta[0]);
            }});
            actualizarEstadisticas();
        }}
        
        // Función de animación para todos los taxis
        function animateAllTaxis() {{
            var allFinished = true;
            var enMovimiento = 0;
            
            taxiStates.forEach(function(state, i) {{
                if (!state.activo) return;
                
                if (!state.finished && state.index < state.ruta.length - 1) {{
                    allFinished = false;
                    enMovimiento++;
                    state.step++;
                    
                    if (state.step > state.totalSteps) {{
                        state.step = 0;
                        state.index++;
                    }}
                    
                    if (state.index < state.ruta.length - 1) {{
                        var lat1 = state.ruta[state.index][0];
                        var lng1 = state.ruta[state.index][1];
                        var lat2 = state.ruta[state.index + 1][0];
                        var lng2 = state.ruta[state.index + 1][1];
                        
                        var fraction = state.step / state.totalSteps;
                        var currentLat = lat1 + (lat2 - lat1) * fraction;
                        var currentLng = lng1 + (lng2 - lng1) * fraction;
                        
                        taxiMarkers[i].setLatLng([currentLat, currentLng]);
                    }}
                }} else if (!state.finished) {{
                    // Taxi llegó a Sol
                    state.finished = true;
                    var taxista = taxistasData[state.id];
                    var arrivedMsg = '✅ ' + state.nombre + ' - ¡Llegó a {centro["nombre"]}!';
                    if (taxista) {{
                        arrivedMsg += '<br>Taxista: ' + taxista.nombre;
                    }}
                    taxiMarkers[i].bindPopup(arrivedMsg).openPopup();
                    setTimeout(function() {{ taxiMarkers[i].closePopup(); }}, 3000);
                }}
            }});
            
            // Actualizar estadísticas
            document.getElementById('stat-movimiento').textContent = enMovimiento;
            
            if (!allFinished) {{
                setTimeout(animateAllTaxis, 30);
            }} else {{
                animationRunning = false;
                console.log('Todos los taxis activos llegaron a {centro["nombre"]}');
            }}
        }}
        
        function actualizarEstadisticas() {{
            var activos = taxiStates.filter(s => s.activo).length;
            document.getElementById('stat-activos').textContent = activos;
        }}
    </script>
</body>
</html>
"""
    
    # Guardar el HTML
    with open(config.MAPA_HTML, "w", encoding="utf-8") as f:
        f.write(html_code)
    
    print(f"\n✅ Archivo '{config.MAPA_HTML}' creado con éxito")
    print(f"\n📋 INFORMACIÓN DE LOS TAXIS:")
    for taxi_id, taxista in taxi_taxista_map.items():
        print(f"\n   {taxi_id.upper()}:")
        print(f"   👤 Taxista: {taxista['nombre']}")
        print(f"   🚗 Placa: {taxista['placa']}")
        print(f"   📋 ID: {taxista['identificacion']}")
        if taxista.get('calificacion'):
            print(f"   ⭐ Calificación: {taxista['calificacion']:.1f}")
        if taxista.get('servicios'):
            print(f"   📊 Servicios: {taxista['servicios']}")
    
    print(f"\n🎮 CÓMO USAR:")
    print(f"   1. Abre {config.MAPA_HTML} en tu navegador")
    print(f"   2. Usa el panel de control para activar/desactivar taxis")
    print(f"   3. Haz clic en 'Iniciar Animación' para ver los taxis moverse")
    print(f"   4. Haz clic en los marcadores para ver información detallada")
    
    return config.MAPA_HTML


# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Función principal del generador de mapas"""
    print("="*60)
    print("UNIETAXI - Generador de Mapa Animado")
    print("="*60)
    
    # Cargar taxis
    taxistas = cargar_taxis_registrados()
    
    if not taxistas:
        print("\n❌ No hay taxis registrados.")
        print("💡 Ejecuta primero:")
        print("   1. python registro_unificado.py (para registrar taxis)")
        print("   2. python main.py (para ejecutar el sistema)")
        return
    
    # Generar mapa
    archivo_html = generar_mapa_html(taxistas)
    
    print("\n" + "="*60)
    print("✅ Mapa generado correctamente")
    print("="*60)


if __name__ == "__main__":
    main()


## start .\taxi_animado.html