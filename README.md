# 🤖 `meli-chatbot`
# Chatbot de Seguridad con RAG y Ollama

**`meli-bot`** es una Prueba de Concepto (POC) de un chatbot conversacional diseñado para responder preguntas sobre documentación de seguridad del equipo de seguridad. Utiliza Recuperación Aumentada por Generación (RAG), almacenamiento semántico vectorial con **ChromaDB**, modelos LLM locales administrados por **Ollama**, y sigue principios de **Clean Architecture** para facilitar su mantenibilidad y escalabilidad.

<br/>
---


## 📌 Propósito

El chatbot tiene como objetivo asistir en consultas frecuentes del equipo de seguridad sobre temas como autenticación, autorización y normativas internas. La documentación se almacena en archivos locales y es embebida al iniciar la aplicación, permitiendo búsquedas semánticas rápidas y respuestas contextualizadas.

<br/>
---


## 🧩 Componentes principales

| Componente                | Rol en el sistema                                                                                                                       |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **FastAPI REST API**      | Expone un único endpoint `/chat`, que recibe mensajes del usuario y entrega respuestas. Al iniciar, también carga documentos embebidos. |
| **Redis**                 | Almacena las últimas 10 interacciones por `user_id` para mantener el contexto de la conversación.                                       |
| **ChromaDB**              | Base de datos vectorial donde se almacenan los embeddings de los documentos cargados dinámicamente desde la carpeta `./documents`.      |
| **LLM con Ollama**        | Permite utilizar cualquier modelo compatible con Ollama.                          |
| **Sentence Transformers** | Se usa en tiempo real para codificar la consulta del usuario y los documentos.                                                          |
| **Docker Compose**        | Orquesta los servicios de API, Redis y Chroma. La configuración se maneja vía variables de entorno.                                     |

<br/>
---


## ⚙️ Flujo de ejecución

### 🔄 Al iniciar la API:

1. Escanea la carpeta `./documents`.
2. Valida qué archivos aún no han sido embebidos en Chroma.
3. Divide cada nuevo documento en fragmentos.
4. Genera los embeddings con `sentence-transformers`.
5. Guarda los vectores en Chroma.

### 💬 Al recibir un mensaje:

1. Recupera las últimas 10 interacciones del usuario desde Redis.
2. Codifica la consulta del usuario.
3. Busca los documentos más similares en Chroma.
4. Construye un prompt con: historial + resultados de búsqueda + consulta del usuario.
5. Llama al modelo a través del `LLMService` que se comunica con `ollama`.
6. Guarda la interacción en Redis y devuelve la respuesta.

<br/>
---


## 🧱 Estructura del proyecto (Clean Architecture)

```
meli-bot/
│
└───api
│   ├── domain/                     # Entidades principales del sistema
│   │   └── entities.py
│   │
│   ├── application/
│   │   ├── services/               # Lógica de negocio principal
│   │   └── interfaces/             # Interfaces de entrada/salida
│   │
│   ├── infrastructure/
│   │   ├── repositories/           # Acceso a Redis y Chroma
│   │   ├── services/               # Embeddings, LLM (Ollama)
│   │   └── web/                    # Endpoints de FastAPI
│   └── main.py                     # Punto de entrada
│
├── documents/                  # Documentos que se embeben en Chroma
├── Dockerfile                  # Creación de imagen de la API REST
├── docker-compose.yml          # Orquestación de servicios
├── script_benchmark.sh         # Script para comparacion de modelos
├── script_cleanup.sh           # Script para limpiar el host
├── script_stratup.sh           # Script para iniciar el Chatbot
└── .env                        # Configuración del entorno
```


---


## 📦 Cómo ejecutar

### 1. Requisitos

* Docker + Docker Compose
* Brew instalado localmente

### 2. Configurar variables en `.env` (ejemplo)

```env
OLLAMA_MODEL="gemma3:1b-it-q8_0"
OLLAMA_MODEL_PROMPT_FORMAT="<start_of_turn>user\\n{prompt}<end_of_turn><start_of_turn>model"
```

### 3. Levantar servicios

```bash
sh script_startup.sh
```

1. Validara que se tenga `ollama` instalado
2. Iniciara `ollama serve`
2. Descargará el modelo necesario
3. Correrá `docker compose up --build` construyendo la imagen de la API y descargando las demás. Levantando *REDIS*, *CHROMA* y el *API REST*

### 4. Probar el endpoint

```bash
curl --location 'http://0.0.0.0:8001/api/v1/chat' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "jose",
    "message": "que es oauth"
  }'
```

#### Algunas Pruebas


```bash
curl --location 'http://0.0.0.0:8001/api/v1/chat' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "jose",
    "message": "What is OAuth2?"
  }'
```

```json
{
       "response": "OAuth2 is an authorization framework that allows third-party applications to access resources on an user's behalf without requiring the user to share their credentials. It provides secure and standardized methods for obtaining access tokens, which can be used to make API requests on the user's behalf."
}
```


```bash
curl --location 'http://0.0.0.0:8001/api/v1/chat' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "jose",
    "message": "Who create it?"
  }'
```

```json
{
    "response": "OAuth2 was developed by a group of industry experts and was approved as a standard by IETF (Internet Engineering Task Force) in August 2012. It is an update to the original OAuth protocol, providing improved security features and more flexible authorization capabilities."
}
```


```bash
curl --location 'http://0.0.0.0:8001/api/v1/chat' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "miguel",
    "message": "¿puedes responder en espanol?"
  }'
```

```json
{
    "response": "Sí, soy un asistente capaz de responder preguntas basadas en el contexto proporcionado. El proceso de reconciliación implica que eventos se desencadenan y se procesan según políticas definidas. La política de administración de usuarios es importante para determinar quién debe tener acceso a qué sistemas y qué tipos de permisos y privilegios tienen. El mecanismo Challenge-Response es una forma de comprobar la identidad, donde el solicitudante de acceso se desafía por parte del proveedor de acceso y debe responder según lo esperado. Por ejemplo, preguntas secretas o certificados digitales. El catalogo de permisos es una base de datos de permisos y sus metadatos.\n\nNo entiendo la pregunta sobre el español específicamente en este contexto. Si está relacionada con idiomas, por favor, clarifique la pregunta."
}
```

### 5. Limpiar ambiente

```bash
sh script_cleanup.sh
```

<br/>
---


## 📚 Benchmark

Se realizaron pruebas con los principales modelos ligeros recomendados para host con M1 (como lo son nuestras PCs)  
A traves del script `script_benchmark.sh` se analizaron:  
- "llama3:8b-instruct-q4_K_M"
- "llama3:8b-instruct-q5_K_M"
- "mistral:7b-instruct-v0.2-q4_K_M"
- "mistral:7b-instruct-v0.2-q5_K_M"
- "deepseek-coder:6.7b-instruct-q4_K_M"
- "deepseek-llm:7b-chat-q4_K_M"
- "phi3:3.8b-mini-128k-instruct-q5_K_M"
- "phi3:14b-medium-128k-instruct-q4_K_M"
- "gemma3:4b-it-q4_K_M"
- "gemma3:1b-it-q4_K_M"
- "gemma3:1b-it-q8_0"
Los resultados fueron almacenados en el file `benchmark_results.txt`.  
En caso de querer analizar otros modelos solo se debe incluir la version del modelo en la variable MODELS y el template del prompt esperado en PROMPTS_FORMAT del script

<br/>
---


## 📘 Decisiones técnicas

* **RAG sobre almacenamiento local:** permite respuesta contextual sin necesidad de modelos muy grandes ni APIs externas. Evita el reentrenamiento del modelo. Y es mas facil de expandir.
* **LLM local:** se eligió Ollama para poder probar múltiples modelos como LLaMA3, Mistral, Phi-3, DeepSeek sin depender de terceros. Se intento levantar Ollama como contenedor pero no mostró buena performance, agergaba mucha latencia a las consultas.
* **Ollama:** modelos intercambiables. Flexibilidad para experimentar
* **Embeddings en tiempo real:** otorga máxima flexibilidad y evita preprocesamiento manual.
* **Clean Architecture:** asegura una estructura sólida y desacoplada, ideal para iteraciones futuras o escalar a producción.
* **Vector DB - ChromaDB:** Fácil integración, ligero y Open Source.
* **Almacenamiento Historial - Redis:** Baja latencia para acceso conversacional

<br/>
---


## 📈 Mejoras pendientes

* 🔐 Autenticación de los requests
* 🗃️ Testing


---