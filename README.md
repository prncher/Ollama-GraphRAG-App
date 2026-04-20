# Ollama-GraphRAG-App
Use neo4j graph db to implement a RAG with knowledge graph along with Ollama inference engine and a local llm

## 🧰 Getting Started

### 1. Install Ollama
Download and install **Ollama 0.12.3** from the official site:  
👉 [https://ollama.com/download/windows](https://ollama.com/download/windows)

### 2. Pull the Model
After installing Ollama, pull the required model:

```bash
ollama pull Llama3.1:8b
```


### 3. Install Python Dependencies
Install [**uv**](https://github.com/astral-sh/uv) (a fast Python package installer):

```bash
pip install uv
```

### 4. Create and Activate a Virtual Environment

#### 🪟 **Windows**
```bash
uv venv
.venv\Scripts\activate
```

#### 🍎 **macOS / 🐧 Linux**
```bash
uv venv
source .venv/bin/activate
```

### 5. Install the Project in Editable Mode
This installs dependencies and links the local project for development:

```bash
uv pip install -e .
```

> 📝 **VS Code Tip**: You may need to manually select the `.venv` Python interpreter to resolve imports.

### 6. Run the RAG Application
Start the RAG Application to query which are not supported by Llama3.1:

```bash
uv run src\app.py
```
