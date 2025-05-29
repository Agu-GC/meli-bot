#!/bin/bash
set -e

MODELS=(
  "llama3:8b-instruct-q4_K_M"
  "llama3:8b-instruct-q5_K_M"
  "mistral:7b-instruct-v0.2-q4_K_M"
  "mistral:7b-instruct-v0.2-q5_K_M"
  "deepseek-coder:6.7b-instruct-q4_K_M"
  "deepseek-llm:7b-chat-q4_K_M"
  "phi3:3.8b-mini-128k-instruct-q5_K_M"
  "phi3:14b-medium-128k-instruct-q4_K_M"
  "gemma3:4b-it-q4_K_M"
  "gemma3:1b-it-q4_K_M"
  "gemma3:1b-it-q8_0"
)
PROMPTS_FORMAT=(
  "<|start_header_id|>system<|end_header_id|><|start_header_id|>user<|end_header_id|>\\n{prompt}\\n<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
  "<|start_header_id|>system<|end_header_id|><|start_header_id|>user<|end_header_id|>\\n{prompt}\\n<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
  "[INST]\\n{prompt}\\n[/INST]"
  "[INST]\\n{prompt}\\n[/INST]"
  "User:{prompt}Assistant:"
  "User:{prompt}Assistant:"
  "<|system|><|end|><|user|>\\n{prompt}<|end|><|assistant|>"
  "<|system|><|end|><|user|>\\n{prompt}<|end|><|assistant|>"
  "<start_of_turn>user\\n{prompt}<end_of_turn><start_of_turn>model"
  "<start_of_turn>user\\n{prompt}<end_of_turn><start_of_turn>model"
  "<start_of_turn>user\\n{prompt}<end_of_turn><start_of_turn>model"
)




# =============================================
# 1. VERIFICACIÓN E INSTALACIÓN DE OLLAMA
# =============================================
echo "🔍 Verificando instalación de Ollama..."

if [[ ! -f "/usr/local/bin/ollama" && ! -f "/Applications/Ollama.app/Contents/Resources/ollama" ]]; then
    echo "⚙️ Ollama no está instalado. Instalando..."
    brew install ollama || {
        echo "❌ Error: No se pudo instalar Ollama con Homebrew. Por favor, instálalo manualmente."
        exit 1
    }
    echo "✅ Ollama instalado correctamente"
fi

# =============================================
# 2. INICIO DEL SERVICIO
# =============================================
echo "🚀 Iniciando servicio Ollama..."
export OLLAMA_USE_METAL=1
export OLLAMA_FLASH_ATTENTION=1

if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "🔌 Iniciando Ollama en segundo plano..."
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    
    timeout=30
    while [ $timeout -gt 0 ]; do
        if curl -s http://localhost:11434/api/tags &> /dev/null; then
            break
        fi
        sleep 1
        ((timeout--))
    done
    
    if [ $timeout -eq 0 ]; then
        echo "❌ Error: Timeout al iniciar Ollama. Ver logs en /tmp/ollama.log"
        echo "ℹ️ Intenta iniciar Ollama manualmente: ollama serve"
        exit 1
    fi
else
    echo "✅ Ollama ya está en ejecución"
fi

# =============================================
# 3. DESCARGAR MODELOS 
# =============================================
echo ""
echo "🔽 Descargando modelos..."
for MODEL in "${MODELS[@]}"; do
  echo "➡️  ollama pull $MODEL"
  ollama pull "$MODEL"
done

# =============================================
# 4. INICIAR BENCHMARK
# =============================================
echo ""
echo "🧪 Benchmark iniciado..."
BENCH_FILE="benchmark_results.txt"
echo "Fecha: $(date)" > "$BENCH_FILE"
echo "Prompt: $PROMPT" >> "$BENCH_FILE"
echo "" >> "$BENCH_FILE"

# Recorrer usando índice numérico
for (( i=0; i<${#MODELS[@]}; i++ )); do
  MODEL=${MODELS[$i]}
  PROMPT=${PROMPTS_FORMAT[$i]}
  
  export OLLAMA_MODEL="$MODEL"
  export OLLAMA_PROMPT="$PROMPT_FORMAT"
  docker-compose up --build -d

  echo "⏳ Esperando que la API esté lista..."
  
  timeout=30
  while ! curl -s http://localhost:8001/health > /dev/null; do
    sleep 1
    ((timeout--))
    if [ $timeout -eq 0 ]; then
      echo "❌ Timeout esperando el servicio en http://localhost:8001"
      exit 1
    fi
  done
  
  echo "✅ API disponible. Ejecutando prueba..."


  START=$(date +%s)
  RESPONSE=$(curl --location 'http://0.0.0.0:8001/api/v1/chat' --header 'Content-Type: application/json' --data '{"user_id": "miguel","message": "¿que es Oauth2?"}')
  END=$(date +%s)
  DURATION=$(( (END - START) * 1000 ))

  echo "=== $MODEL ===" >> "$BENCH_FILE"
  echo "⏱️ Tiempo de respuesta: ${DURATION} ms" >> "$BENCH_FILE"
  echo "📥 Respuesta (primeras líneas):" >> "$BENCH_FILE"
  echo "$RESPONSE" | head -n 10 >> "$BENCH_FILE"
  echo "" >> "$BENCH_FILE"

  echo "✅ Modelo $MODEL completado en ${DURATION} ms"
  echo "----------------------------------------"
  
  docker-compose down
done

echo "✅ Benchmark completado. Resultados guardados en $BENCH_FILE"
