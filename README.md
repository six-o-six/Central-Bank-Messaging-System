# Central Bank Messaging System

Simulação simplificada do ecossistema PIX brasileiro, feita para a disciplina de Sistemas Paralelos e Distribuídos. Vários bancos publicam transações PIX em uma fila do RabbitMQ, e um serviço de auditoria consome essas mensagens e grava um log permanente em disco.

## Como funciona

O sistema tem três partes:

- **`produtor.py`** — simula vários bancos ao mesmo tempo (`BancoA` a `BancoE`), cada um rodando em sua própria thread. A cada 1-5 segundos, cada banco gera uma transação PIX aleatória (valor, conta de origem/destino, banco destinatário) e publica na fila `pix` do RabbitMQ.
- **RabbitMQ** — o message broker. Recebe as transações publicadas pelos produtores e as entrega ao consumidor. Roda em Docker via `docker-compose.yml`.
- **`consumidor.py`** — o serviço de Auditoria (Audit Logging Service). Fica escutando a fila `pix`, e para cada transação recebida grava uma linha no arquivo `audit.log`, no formato:

  ```
  [2026-06-01 10:15:30] TX123456 | BancoA | BancoB | 1500.50
  ```

  Cada mensagem só é confirmada (`ack`) ao broker depois de gravada com sucesso, então nenhuma transação é perdida se o consumidor cair no meio do processo.

Fluxo resumido:

```
BancoA ─┐
BancoB ─┼─► RabbitMQ (fila "pix") ─► consumidor.py ─► audit.log
BancoC ─┘
```

## Pré-requisitos

- Docker e Docker Compose
- Python 3.10+

## Como executar

**1. Suba o RabbitMQ:**

```bash
docker compose up -d
```

Isso deixa o broker disponível em `localhost:5672` (usado pelo `pika`) e o painel de administração em [http://localhost:15672](http://localhost:15672) (login `guest` / `guest`), onde dá para acompanhar a fila `pix` recebendo mensagens em tempo real.

**2. Instale as dependências Python:**

```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requisitos.txt
```

**3. Em um terminal, inicie o consumidor (serviço de auditoria):**

```bash
python consumidor.py
```

**4. Em outro terminal, inicie os produtores:**

```bash
python produtor.py
```

Isso já sobe os 5 bancos simulados publicando transações simultaneamente. Para parar tudo, `Ctrl+C` em cada terminal.

**5. Verifique o resultado:**

```bash
cat audit.log
```

Cada linha corresponde a uma transação processada pelo serviço de auditoria.

## Estrutura do projeto

```
.
├── docker-compose.yml    # sobe o RabbitMQ
├── produtor.py           # simula os bancos (produtores)
├── consumidor.py         # serviço de auditoria (consumidor)
├── requisitos.txt        # dependências (pika)
└── audit.log             # gerado em tempo de execução
```
