#!/usr/bin/env python3
"""
Script para corregir errores de sintaxis en main.py
"""

import re

def corregir_main_py():
    """Corrige los errores de sintaxis en main.py"""
    print("🔧 Corrigiendo errores de sintaxis en main.py...")
    
    with open('main.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Eliminar líneas problemáticas
    patrones_eliminar = [
        r'^        :\.2f\} ms"\)$\n',
        r'^        \}\)"$\n',
        r'^        \}\)"$\n',
    ]
    
    for patron in patrones_eliminar:
        contenido = re.sub(patron, '', contenido, flags=re.MULTILINE)
    
    # Limpiar líneas vacías múltiples
    contenido = re.sub(r'\n\s*\n\s*\n', '\n\n', contenido)
    
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("✅ Errores de sintaxis corregidos")

if __name__ == "__main__":
    corregir_main_py()
