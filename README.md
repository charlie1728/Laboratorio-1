# VOID RUNNER 🚀
**Endless Runner Espacial — Laboratorio 1: Persistencia con Tabla Hash**

---

## Descripción del juego

VOID RUNNER es un *endless runner* espacial en perspectiva lateral donde el jugador
pilota una nave que esquiva asteroides viajando a velocidad creciente.

### Mecánicas principales
- **3 carriles** — la nave cambia de carril con ↑ / ↓
- **Velocidad creciente** — cada 5 segundos la velocidad aumenta
- **Powerups**: ⚡ Energía (+puntos) | 🛡 Escudo (invulnerabilidad 5 s) | ×2 Multiplicador de puntaje
- **Guardado automático** al terminar cada partida

---

## Estructura del proyecto

```
void_runner/
├── main.py                          # Entry point (Pygame + asyncio para Pygbag)
│
├── game/
│   ├── constants.py                 # Constantes globales, paleta de colores
│   ├── draw_utils.py                # Arte procedural (no hay assets externos)
│   ├── starfield.py                 # Fondo parallax
│   └── scenes/
│       ├── menu.py                  # Menú principal
│       ├── game_scene.py            # Escena de juego
│       ├── leaderboard.py           # Top 10 puntajes
│       ├── settings.py              # Configuración persistente
│       └── hash_viz.py              # Visualizador de tabla hash (bonus)
│
├── persistence/
│   ├── hash_entry.py                # Entrada de la tabla hash
│   ├── hash_table.py                # Tabla hash con chaining y rehash
│   ├── engine.py                    # Fachada: coordina tabla + archivos
│   ├── recovery.py                  # Reconstrucción de índice desde data.log
│   └── storage/
│       ├── record_store.py          # Gestión de data.log (append-only)
│       ├── index_store.py           # Serialización de index.bin
│       └── serializer.py            # Codificación JSON Lines
│
├── repositories/
│   ├── profile_repository.py        # Perfil del jugador
│   ├── leaderboard_repository.py    # Tabla de puntajes global
│   └── settings_repository.py      # Configuración del juego
│
├── benchmark.py                     # Experimentos de rendimiento
├── requirements.txt
└── README.md
```

---

## Instalación y ejecución

### Requisitos
```
Python 3.11+
pygame >= 2.5.0
pygbag >= 0.9.0   (solo para versión web)
```

### Instalación
```bash
pip install -r requirements.txt
```

### Ejecución local
```bash
cd void_runner
python main.py
```

### Ejecución en navegador (WebAssembly)
```bash
cd void_runner
pygbag .
# Abre http://localhost:8000
```

### Benchmarks de rendimiento
```bash
cd void_runner
python benchmark.py
```

---

## Controles

| Acción | Tecla |
|--------|-------|
| Mover carril arriba | ↑ / W |
| Mover carril abajo | ↓ / S |
| Seleccionar en menú | Enter / Space |
| Volver al menú | Escape |
| Reiniciar partida | R (en game over) |
| Abrir Hash Visualizer | F1 (desde cualquier escena) |

---

## Sistema de Persistencia

### Arquitectura

```
┌─────────────────────────────────────────┐
│           PersistenceEngine             │
│                                         │
│  ┌───────────────┐  ┌─────────────────┐ │
│  │  HashTable    │  │  RecordStore    │ │
│  │  (índice RAM) │  │  (data.log)     │ │
│  │               │  │  append-only    │ │
│  │  key → offset │  │  JSON Lines     │ │
│  └───────────────┘  └─────────────────┘ │
│         ↕                               │
│  ┌───────────────┐  ┌─────────────────┐ │
│  │  IndexStore   │  │  recovery.py    │ │
│  │  (index.bin)  │  │  reconstruye    │ │
│  │  JSON         │  │  si index.bin   │ │
│  │               │  │  se pierde      │ │
│  └───────────────┘  └─────────────────┘ │
└─────────────────────────────────────────┘
```

### Tabla Hash

- **Función hash**: djb2 adaptada — distribución uniforme para claves tipo `player:id`, `score:run_42`
- **Colisiones**: Encadenamiento (chaining) — cada bucket es una lista enlazada
- **Factor de carga**: `elementos / capacidad`; umbral configurable (default 0.7)
- **Rehash**: duplica capacidad y reinserta todos los elementos automáticamente
- **Estructuras prohibidas**: ❌ `dict`, `set`, `defaultdict`, `Counter`, `shelve`

### Archivos generados

| Archivo | Descripción |
|---------|-------------|
| `data.log` | Registros en formato JSON Lines, append-only |
| `index.bin` | Tabla hash serializada en JSON |
| `benchmark_results.json` | Resultados de benchmarks |

### Módulos persistentes (mínimo 3 ✓)

1. **Perfil del jugador** (`player:<id>`) — mejor puntaje, distancia total, partidas jugadas
2. **Leaderboard** (`leaderboard:global`) — top 10 ordenado por puntaje
3. **Configuración** (`config:global`) — nombre, volumen, dificultad, opciones visuales

---

## Requerimientos cumplidos

| Requerimiento | Estado |
|---------------|--------|
| Tabla hash manual (sin dict/set) | ✅ |
| Encadenamiento (chaining) | ✅ |
| Factor de carga + rehash automático | ✅ |
| Persistencia en data.log (JSON Lines) | ✅ |
| Índice en index.bin | ✅ |
| Reconstrucción del índice | ✅ |
| ≥ 3 módulos persistentes | ✅ (perfil, leaderboard, settings) |
| Menú principal | ✅ |
| Pantalla Leaderboard | ✅ |
| Pantalla Settings | ✅ |
| Guardado automático al terminar | ✅ |
| Benchmarks (1k, 5k, 20k) | ✅ |
| Compatible con Pygbag (web) | ✅ |
| Visualizador de tabla hash (bonus) | ✅ (F1 o desde menú) |

---

## Evaluación de rendimiento (resultados típicos)

| N | Insert (ms) | Search (ms) | Colisiones | Rehashes | LF final |
|---|-------------|-------------|------------|----------|----------|
| 1,000 | ~3 | ~2 | ~180 | 6 | ~0.49 |
| 5,000 | ~12 | ~8 | ~950 | 8 | ~0.61 |
| 20,000 | ~55 | ~35 | ~4100 | 10 | ~0.61 |

*Nota: valores en hardware moderno. El motor de disco es más lento por I/O.*

---

## Decisiones de diseño

### Función hash djb2
Elegida por su excelente distribución con strings cortos y velocidad. Alternativas como
FNV-1a o MurmurHash ofrecen resultados similares; djb2 es más legible para fines educativos.

### Chaining vs Open Addressing
El enunciado especifica chaining explícitamente. Con open addressing el factor de carga
tiene un límite real de ~0.7; con chaining puede superarse a costa de cadenas más largas.

### JSON Lines para data.log
Permite reconstrucción trivial del índice: cada línea es un registro auto-contenido.
El formato binario (pickle, msgpack) sería más rápido pero menos inspeccionable.

### Rehash con factor 2×
Duplicar la capacidad amortiza el costo de O(n) a O(1) por operación en promedio.
Un factor de 1.5× reduciría el pico de memoria pero incrementaría la frecuencia de rehashes.
