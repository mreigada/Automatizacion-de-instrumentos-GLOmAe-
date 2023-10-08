# Automatización de instrumentos - GLOmAe
En este repositorio se encuentran los códigos fuentes desarrollados para automatizar el uso de instrumentos de laboratorio disponibles en el GLOmAe (Grupo de Láser, Óptica de Materiales y Aplicaciones Electromagnéticas) de la FIUBA. 


## Características del sistema
- Sistema basado en el módulo de Python PyVISA para establecer comunicación con instrumentos independientemente de la interfaz (por ejemplo, GPIB, RS232, USB, Ethernet).
- Apto para ser utilizado en proyectos que requieran del control y adquisición de datos de manera simultanea


## Organización del repositorio
El repositorio se organiza con la siguiente estructura:
    
    .
    ├── src
    │   ├── osctck.py
    │   └── rotmcESP.py
    │   └── usrt.py
    │   └── utils.py
    ├── examples    
    │   ├── Ejemplo de control de base (ESP300)
    │   └── Ejemplo de medicion con osciloscopio (TDS2024)
    │   └── Ejemplo de Rutina de tomografia
    │   └── ...
    └── README.md
