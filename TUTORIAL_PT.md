# LFT AI - Tutorial Completo
## GUI, CLI, Visualizacao e Acesso aos Dados

**Versao:** 1.0 | **Data:** Marco 2026 | **Mantenedor:** Profissa - UnB

---

## Sumario

1. [Pre-requisitos](#1-pre-requisitos)
2. [Modo GUI (`lft-gui`)](#2-modo-gui)
   - [Aba AI Generator](#21-aba-ai-generator)
   - [Aba Topology Builder](#22-aba-topology-builder)
   - [Aba Experiments](#23-aba-experiments)
   - [Aba Results](#24-aba-results)
   - [Aba Monitoring](#25-aba-monitoring)
3. [Modo CLI / Standalone (`lft-ai`)](#3-modo-cli--standalone)
   - [Gerar Topologias](#31-gerar-topologias)
   - [Modo Interativo](#32-modo-interativo)
   - [Ver Exemplos](#33-ver-exemplos)
   - [Script Standalone](#34-script-standalone)
4. [Visualizacao](#4-visualizacao)
   - [Monitoramento em Tempo Real](#41-monitoramento-em-tempo-real)
   - [Visualizacao Estatica (A Partir de Arquivo)](#42-visualizacao-estatica)
   - [Visualizacao Programatica](#43-visualizacao-programatica)
5. [Acessando os Dados da Simulacao](#5-acessando-os-dados-da-simulacao)
   - [Resultados de Experimentos (JSON)](#51-resultados-de-experimentos-json)
   - [Dados de Telemetria (CSV/JSON)](#52-dados-de-telemetria)
   - [Analisando Resultados](#53-analisando-resultados)
6. [API Python Programatica](#6-api-python-programatica)
7. [Guia de Selecao de Modelos](#7-guia-de-selecao-de-modelos)
8. [Solucao de Problemas](#8-solucao-de-problemas)

---

## 1. Pre-requisitos

```bash
# 1. Python 3.9+ necessario
python3 --version

# 2. Instalar o LFT
pip3 install profissa_lft

# 3. Docker (ou Podman) deve estar em execucao
sudo systemctl start docker

# 4. Para funcionalidades de IA, instalar dependencias dos modelos
pip3 install torch transformers accelerate

# 5. Para funcionalidades de visualizacao
pip3 install matplotlib networkx docker

# 6. (Opcional) Token da API Hugging Face para inferencia remota
export HF_TOKEN="seu_token_aqui"
```

---

## 2. Modo GUI

Inicie a interface grafica:

```bash
lft-gui
# ou diretamente:
python3 lft_gui.py
```

A GUI abre uma janela com cinco abas e um painel de saida do console compartilhado na parte inferior.

### 2.1 Aba AI Generator

Esta aba permite descrever uma rede em linguagem natural e ter um modelo de IA gerando o codigo Python do LFT.

**Passo a passo:**

1. **Escreva uma descricao** na area de texto a esquerda. Seja especifico:
   ```
   Create a simple SDN topology with 2 hosts connected to a switch
   ```

2. **Escolha um modelo** no menu suspenso "Model". O padrao e o DeepSeek-R1 (melhor qualidade). Para resultados mais rapidos, selecione Phi-3 Mini ou Stable Code 3B.

3. **Configure as opcoes de API** (opcional):
   - Marque "Use Hugging Face API" para usar inferencia remota (requer token HF)
   - Deixe desmarcado para usar um modelo baixado localmente

4. **Clique em "Generate Topology"**. O rotulo de status mostra o progresso. A geracao leva de 30 a 60 segundos dependendo do modelo.

5. **Revise e edite** o codigo gerado no editor do lado direito. O editor e totalmente editavel -- voce pode corrigir ou personalizar qualquer coisa antes de executar.

6. **Execute, salve ou copie** o codigo:
   - **"Run Generated Code"**: Executa o codigo imediatamente (cria containers Docker). A saida aparece no Console na parte inferior.
   - **"Save to File"**: Salva o codigo como um arquivo `.py`.
   - **"Copy All"** / **"Undo"** / **"Clear"**: Acoes da barra de ferramentas do editor.

**Usando topologias de exemplo:**

Em vez de gerar do zero, clique em qualquer um dos seis botoes de exemplo pre-verificados na parte inferior do painel esquerdo:

- **Simple SDN Topology** -- 2 hosts + 1 switch
- **4G Wireless Network** -- 2 UEs + eNodeB + EPC
- **Multi-Switch SDN** -- 3 switches + 1 controlador + 4 hosts
- **Fog Computing Network** -- 3 nos de borda + 2 nos de nevoa + nuvem
- **Enterprise Network** -- gateway + 2 switches departamentais + 4 hosts
- **IoT Network** -- 3 sensores + gateway + servidor na nuvem

Clicar em um exemplo carrega tanto o prompt quanto o codigo verificado, pronto para executar.

### 2.2 Aba Topology Builder

Construa topologias manualmente sem IA, usando controles de apontar e clicar.

**Criar um no:**
1. Selecione um **Tipo** (Host, Switch, Controller, UE, EnB, EPC, Perfsonar)
2. Digite um **Nome** (ex.: `h1`)
3. A **Imagem Docker** e preenchida automaticamente com base no tipo (editavel)
4. Opcionalmente defina **Memoria** (ex.: `512m`) e **CPUs** (ex.: `1.0`)
5. Clique em **"Create Node"**

**Conectar dois nos:**
1. Selecione **Node 1** e **Node 2** nos menus suspensos (preenchidos automaticamente a partir dos containers em execucao)
2. Digite os nomes das interfaces (ex.: `h1s1` e `s1h1`)
3. Clique em **"Connect"**

**Configurar IP:**
1. Selecione um **Node** e uma **Interface**
2. Digite o endereco **IP** e a **Mascara** (ex.: `10.0.0.1` / `24`)
3. Clique em **"Set IP"**

**Executar um script:** Navegue ate qualquer arquivo de topologia `.py` e clique em "Run".

O painel direito mostra todos os **Containers Docker Ativos** com nome, tipo, imagem e status. Use "Refresh", "Delete Selected" ou "Delete All Containers" para gerencia-los.

### 2.3 Aba Experiments

Execute experimentos de desempenho de rede na sua topologia em execucao.

**Teste personalizado:**
1. Selecione o **Tipo de Teste**: Throughput, RTT ou Latency
2. Digite um **Nome do Teste** (usado para o nome do arquivo de saida)
3. Digite o **IP de Origem** e o **IP de Destino** dos nos na sua topologia
4. Clique em **"Run Experiment"**

Os resultados sao salvos como arquivos JSON em `results/data/` e a saida aparece no painel direito.

**Scripts predefinidos:** Clique em qualquer um dos botoes de experimento pre-configurados:
- Emu-Emu Wired / Emu-Phy Wired
- Emu-Emu Wireless / Emu-Phy Wireless
- Deploy LFT Benchmark
- Simple SDN Topology

### 2.4 Aba Results

Navegue e inspecione os arquivos de resultado dos experimentos.

1. Use o menu suspenso **Filter** para mostrar apenas arquivos de Throughput, RTT, Latency, CSV ou Todos
2. Clique em um arquivo na lista a esquerda para ver seu conteudo (JSON ou CSV) no painel direito
3. Clique em **"Plot Results"** para executar o `analyzeResults.py`, que gera graficos comparativos
4. Clique em **"Export Selected"** para salvar uma copia de qualquer arquivo de resultado

### 2.5 Aba Monitoring

Telemetria em tempo real e visualizacao dos containers em execucao.

**Iniciar o Visualizador em Tempo Real:**
1. Defina o intervalo de atualizacao em milissegundos (padrao: 1000)
2. Clique em **"Start Real-Time Visualizer"** -- abre uma janela matplotlib mostrando:
   - Grafo da topologia de rede (nos coloridos por tipo)
   - Grafico de uso de CPU
   - Grafico de uso de memoria
   - Grafico de trafego de rede
   - Grafico de latencia

**Coletar Snapshot de Telemetria:** Clique para obter uma leitura unica de CPU, memoria e estatisticas de rede de todos os containers em execucao.

**Exportar Dados de Telemetria:** Salve a telemetria coletada como CSV ou JSON para analise externa.

---

## 3. Modo CLI / Standalone

### 3.1 Gerar Topologias

```bash
# Geracao basica (usa o modelo DeepSeek-R1 padrao, inferencia local)
lft-ai generate "Create an SDN topology with 2 hosts connected to a switch" -o minha_topologia.py

# Usar um modelo especifico
lft-ai generate "Create a 4G network with 2 UEs" --model phi3-mini -o wireless.py

# Usar a API do Hugging Face ao inves de modelo local
lft-ai generate "Create a datacenter topology" --token SEU_TOKEN_HF -o datacenter.py

# Gerar com validacao
lft-ai generate "Create a fog computing network" -o fog.py --validate

# Saida detalhada (mostra progresso do carregamento do modelo, detalhes da geracao)
lft-ai generate "Create a simple network" -o simples.py -v
```

**Aliases de modelos disponiveis:** `deepseek-r1`, `deepseek-r1-8b`, `phi3-mini`, `stable-code-3b`, `qwen2-7b`, `gemma2-9b`, `code-llama-7b`, `deepseek-coder-7b`

Apos gerar, execute sua topologia:
```bash
sudo python3 minha_topologia.py
```

### 3.2 Modo Interativo

```bash
lft-ai interactive
# ou com um modelo especifico:
lft-ai interactive --model phi3-mini
```

O modo interativo abre um REPL onde voce digita descricoes e recebe o codigo de volta imediatamente:

```
LFT AI Interactive Mode
Type a topology description and press Enter.
Commands: quit, help, clear

>>> Create a simple network with 2 hosts and 1 switch
[Generating...]

# O codigo gerado aparece aqui
from profissa_lft.host import Host
from profissa_lft.switch import Switch
...

>>> quit
```

### 3.3 Ver Exemplos

```bash
lft-ai examples
```

Imprime descricoes de topologias de exemplo e suas saidas esperadas para ajudar voce a aprender o formato dos prompts.

### 3.4 Script Standalone

O script standalone agrupa toda a funcionalidade do LFT AI em um unico arquivo (sem necessidade de instalacao de pacote):

```bash
# Gerar topologia
python3 lft_ai_standalone.py generate "Create an SDN topology with 2 hosts" -o topologia.py

# Modo interativo
python3 lft_ai_standalone.py interactive

# Visualizacao em tempo real (monitora containers em execucao)
python3 lft_ai_standalone.py visualize

# Visualizacao estatica a partir de um arquivo de topologia
python3 lft_ai_standalone.py visualize --file topologia.py

# Intervalo de atualizacao personalizado
python3 lft_ai_standalone.py visualize --interval 2000

# Exportar telemetria
python3 lft_ai_standalone.py visualize --export-csv metricas.csv
python3 lft_ai_standalone.py visualize --export-json metricas.json

# Mostrar exemplos
python3 lft_ai_standalone.py examples
```

---

## 4. Visualizacao

### 4.1 Monitoramento em Tempo Real

Monitore containers Docker em execucao em tempo real com um dashboard interativo matplotlib.

**Pela GUI:**
Va ate a aba Monitoring e clique em "Start Real-Time Visualizer".

**Pela CLI:**
```bash
python3 lft_ai_standalone.py visualize
```

**O que ele mostra:**
- **Grafo da Topologia**: Nos como circulos coloridos (verde=Host, azul=Switch, laranja=Controller, roxo=UE, vermelho=EPC, rosa=eNodeB), com linhas para conexoes
- **Uso de CPU**: % em tempo real por container (ultimas 100 amostras)
- **Uso de Memoria**: MB consumidos por container
- **Trafego de Rede**: Throughput em KB/s (RX+TX combinados)
- **Latencia**: RTT entre pares de nos

**Exemplo de fluxo de trabalho:**
```bash
# Terminal 1: Inicie sua topologia
sudo python3 minha_topologia.py

# Terminal 2: Inicie o visualizador
python3 lft_ai_standalone.py visualize
```

O visualizador descobre automaticamente todos os containers em execucao. Feche a janela do matplotlib para parar.

### 4.2 Visualizacao Estatica

Renderize um grafo de topologia a partir de um arquivo `.py` sem executar nenhum container:

```bash
python3 lft_ai_standalone.py visualize --file topologia_gerada.py
```

Isso analisa o arquivo Python, extrai instanciacoes de nos e chamadas `.connect()`, e renderiza um grafo de rede estatico. Util para pre-visualizar uma topologia antes da implantacao.

### 4.3 Visualizacao Programatica

```python
from profissa_lft.visualizer import NetworkVisualizer

# Uso basico
visualizer = NetworkVisualizer(update_interval=1000)
visualizer.start()  # Bloqueia ate a janela ser fechada

# Em uma thread em segundo plano (para integracao com outro codigo)
import threading
visualizer = NetworkVisualizer()
viz_thread = threading.Thread(target=visualizer.start)
viz_thread.daemon = True
viz_thread.start()

# ... sua topologia continua em execucao ...
input("Pressione Enter para parar...\n")
```

---

## 5. Acessando os Dados da Simulacao

### 5.1 Resultados de Experimentos (JSON)

Os experimentos produzem arquivos JSON em `results/data/`. Existem tres tipos:

**Throughput (iperf3):**
```bash
# Executar um teste de throughput
lft-ai generate "..." -o topo.py && sudo python3 topo.py
# Depois em outro terminal, ou pela aba Experiments da GUI:
python3 -c "
from experiment.experiment import runThroughput
runThroughput('meu_teste', '10.0.0.1', '10.0.0.2')
"
```

Arquivo de saida: `results/data/meu_teste_throughput_1.json`

Campos principais no JSON:
```json
{
  "intervals": [
    {
      "sum": {
        "bits_per_second": 943215600.0,
        "bytes": 117901950
      }
    }
  ],
  "end": {
    "sum_sent": { "bits_per_second": 943718400.0 },
    "sum_received": { "bits_per_second": 943214300.0 }
  }
}
```

**RTT (ping):**
```python
from experiment.experiment import runRTT
runRTT('meu_teste', '10.0.0.1', '10.0.0.2')
```

Arquivo de saida: `results/data/meu_teste_rtt_1.json`

Campos principais:
```json
{
  "result": {
    "roundtrips": [
      {
        "seq": 1,
        "length": 64,
        "ip": "10.0.0.2",
        "rtt": "PT0.000234S"
      }
    ]
  }
}
```
Os valores de RTT usam o formato de duracao ISO 8601 (ex.: `PT0.000234S` = 0.234 ms).

**Latencia (OWAMP unidirecional):**
```python
from experiment.experiment import runLatency
runLatency('meu_teste', '10.0.0.1', '10.0.0.2')
```

Arquivo de saida: `results/data/meu_teste_latency_1.json`

Campos principais:
```json
{
  "result": {
    "succeeded": true,
    "packets-sent": 100,
    "packets-received": 100,
    "packets-lost": 0
  }
}
```

### 5.2 Dados de Telemetria

O sistema de telemetria coleta metricas de containers Docker em tempo real.

**Pela GUI:** Use a aba Monitoring para coletar snapshots ou exportar dados.

**Programaticamente:**
```python
from profissa_lft.telemetry import TelemetryStore, TelemetryCollector

# Criar store e coletor
store = TelemetryStore()
collector = TelemetryCollector(store)

# Descobrir automaticamente containers em execucao
collector.auto_discover()

# Coletar metricas
collector.collect_all()

# Obter um dicionario resumido
summary = collector.summary()
for node, metrics in summary.items():
    print(f"\n{node}:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value}")

# Exportar para arquivo
store.export_csv("dados_telemetria.csv")
store.export_json("dados_telemetria.json")
```

**Pela CLI:**
```bash
# Exportar durante a visualizacao
python3 lft_ai_standalone.py visualize --export-csv metricas.csv
python3 lft_ai_standalone.py visualize --export-json metricas.json
```

### 5.3 Analisando Resultados

O script `results/analyzeResults.py` processa os arquivos JSON dos experimentos e gera graficos:

```bash
cd /caminho/para/lft_ai
python3 results/analyzeResults.py
```

Isso produz:
- Graficos de barras comparativos de throughput (LFT vs Mininet-WiFi)
- Box plots de RTT
- Distribuicoes de latencia
- Comparacoes de tempo de implantacao (a partir de benchmarks CSV)
- Intervalos de confianca de 99% com remocao de outliers

**Pela GUI:** Va ate a aba Results e clique em "Plot Results (analyzeResults.py)".

**Localizacao dos arquivos de resultado:**
```
lft_ai/
  results/
    data/
      wired_emu_emu_throughput_1.json    # Resultados de throughput
      wired_emu_emu_rtt_1.json           # Resultados de RTT
      wired_emu_emu_latency_1.json       # Resultados de latencia
      deployLftTime.csv                  # Benchmarks de implantacao
      deployLftMem.csv                   # Benchmarks de memoria
    analyzeResults.py                    # Script de analise/graficos
```

---

## 6. API Python Programatica

Use o LFT AI a partir dos seus proprios scripts Python:

```python
from profissa_lft import ModernAITopologyGenerator

# Inicializar (carrega o modelo, leva 30-60s)
gen = ModernAITopologyGenerator(model_name="deepseek-r1")

# Gerar codigo a partir de descricao
code = gen.generate_topology("""
Create a network with:
- 3 hosts: h1 (10.0.0.1/24), h2 (10.0.0.2/24), h3 (10.0.0.3/24)
- 1 switch: s1
- Connect all hosts to switch
- Instantiate all nodes
""")

# Validar o codigo gerado
if gen.validate_generated_code(code):
    print("Codigo valido!")

# Salvar em arquivo
with open('minha_topologia.py', 'w') as f:
    f.write(code)

# Ou gerar diretamente para um arquivo
gen.generate_topology("Create a simple SDN topology", output_file="topologia.py")
```

**Dica:** Para melhores resultados, inclua detalhes especificos na sua descricao: quantidade de nos, enderecos IP, padroes de conexao e quais componentes do LFT utilizar.

---

## 7. Guia de Selecao de Modelos

| Modelo | Alias | Velocidade | Qualidade | Melhor Para |
|--------|-------|------------|-----------|-------------|
| DeepSeek-R1-0528 | `deepseek-r1` | Lento (~60s init) | Melhor | Topologias complexas |
| DeepSeek-R1-8B | `deepseek-r1-8b` | Medio | Muito Bom | Uso equilibrado |
| Phi-3 Mini | `phi3-mini` | Rapido (~15s init) | Bom | Prototipagem rapida |
| Stable Code 3B | `stable-code-3b` | Muito Rapido | Bom | Codigo limpo e simples |
| Qwen2-7B | `qwen2-7b` | Medio | Bom | Tarefas focadas em codigo |
| Gemma2-9B | `gemma2-9b` | Medio | Bom | Uso geral |
| Code Llama 7B | `code-llama-7b` | Medio | Bom | Geracao de codigo |
| DeepSeek Coder 7B | `deepseek-coder-7b` | Medio | Bom | Geracao de codigo |

**Requisitos de memoria:**
- Modelos 3B: ~4 GB RAM/VRAM
- Modelos 7-8B: ~8 GB RAM/VRAM
- DeepSeek-R1 completo: ~16+ GB RAM/VRAM (use `load_in_4bit=True` para reduzir)

---

## 8. Solucao de Problemas

### A GUI nao inicia
```bash
# Certifique-se de que o tkinter esta instalado
sudo apt install python3-tk   # Debian/Ubuntu
```

### "No network detected" no visualizador
Certifique-se de que os containers estao em execucao: `sudo docker ps`. O visualizador so detecta containers Docker em execucao.

### Carregamento do modelo lento ou falha
```bash
# Use um modelo menor para inicializacao mais rapida
lft-ai generate "..." --model phi3-mini -o topologia.py

# Ou use quantizacao em Python
gen = ModernAITopologyGenerator(load_in_4bit=True)
```

### Falta de memoria durante a geracao com IA
Use um modelo menor (`phi3-mini` ou `stable-code-3b`) ou ative a quantizacao de 4 bits.

### Permissao negada do Docker
```bash
sudo usermod -aG docker $USER
# Depois faca logout e login novamente, ou:
newgrp docker
```

### Usando Podman ao inves de Docker
```bash
# Iniciar o socket do Podman
systemctl --user start podman.socket

# Definir o socket compativel com Docker
export DOCKER_HOST=unix:///run/user/$(id -u)/podman/podman.sock

# Configurar registro de imagens
mkdir -p ~/.config/containers
echo 'unqualified-search-registries = ["docker.io"]' > ~/.config/containers/registries.conf
```

### O codigo gerado nao funciona
- Seja mais especifico na sua descricao (inclua nomes dos nos, IPs, conexoes)
- Use os exemplos da GUI como templates -- eles contem codigo verificado e funcional
- Edite o codigo gerado no editor da GUI antes de executar

---

## Cartao de Referencia Rapida

| Tarefa | GUI | CLI |
|--------|-----|-----|
| Gerar topologia | Aba AI Generator | `lft-ai generate "..." -o arquivo.py` |
| Geracao interativa | -- | `lft-ai interactive` |
| Executar topologia | Botao "Run Generated Code" | `sudo python3 topologia.py` |
| Visualizacao em tempo real | Aba Monitoring > "Start Visualizer" | `python3 lft_ai_standalone.py visualize` |
| Visualizacao estatica | -- | `python3 lft_ai_standalone.py visualize --file topologia.py` |
| Executar experimento | Aba Experiments | `python3 -c "from experiment.experiment import runThroughput; ..."` |
| Ver resultados | Aba Results | Abrir `results/data/*.json` |
| Plotar resultados | Aba Results > "Plot Results" | `python3 results/analyzeResults.py` |
| Exportar telemetria | Aba Monitoring > "Export CSV/JSON" | `python3 lft_ai_standalone.py visualize --export-csv arquivo.csv` |
| Coletar telemetria | Aba Monitoring > "Collect Snapshot" | Programatico via `TelemetryCollector` |
| Ver exemplos | Aba AI Generator > botoes de exemplo | `lft-ai examples` |

---

**Licenca:** GNU General Public License v3.0
**Mantenedor:** Profissa - UnB
