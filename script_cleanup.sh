#!/bin/bash

echo "🔵 Iniciando limpieza de Ollama y Docker..."


# =============================================
# 1. DETENER Y DESINSTALAR OLLAMA
# =============================================
if brew list --formula | grep -q ollama; then
    echo "🟡 Desinstalando Ollama..."

    if launchctl list | grep -q ollama; then
        echo "⏳ Deteniendo el servicio Ollama..."
        brew services stop ollama
        sleep 3
    fi
    
    brew uninstall ollama
    echo "✅ Ollama desinstalado."
    
    OLLAMA_MODELS_DIR="${HOME}/.ollama/models"
    if [ -d "$OLLAMA_MODELS_DIR" ]; then
        echo "🗑️ Eliminando modelos descargados de Ollama..."
        rm -rf "$OLLAMA_MODELS_DIR"
        echo "✅ Modelos eliminados."
    else
        echo "🟡 No se encontró el directorio de modelos de Ollama."
    fi
else
    echo "🟡 Ollama no está instalado via Homebrew."
fi

# =============================================
# 2. LIMPIAR CONTENEDORES Y VOLUMENES DE DOCKER 
# =============================================

if command -v docker-compose &> /dev/null || command -v docker compose &> /dev/null; then
    echo "🐳 Limpiando contenedores y volúmenes de Docker Compose..."
    
    COMPOSE_CMD="docker-compose"
    if ! command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker compose"
    fi
    
    $COMPOSE_CMD down --volumes --remove-orphans
    
    echo "✅ Contenedores y volúmenes de Docker Compose eliminados."
else
    echo "🟡 Docker Compose no está instalado."
fi


# =============================================
# 3. OPCIONAL: LIMPIAR TODAS LA IMAGENES DOCKER
# =============================================

# echo "🐳 Limpiando TODOS los contenedores, imágenes y volúmenes de Docker..."
# docker system prune -a --volumes -f

echo "✨ Limpieza completada."