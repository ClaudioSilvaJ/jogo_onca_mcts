````markdown
# Jogo da Onça – Bot com Monte Carlo

Implementação de um bot para o **Jogo da Onça**, utilizando um controlador em Python
(`controlador.py` / `tabuleiro.py`) inspirado nos controladores originais em C, com
comunicação via **Redis**.

---

## Participantes

- Claudio Honorio da Silva Junior  
- Mateus Heck Soares  
- Pedro Pivetta Barrotti  

---

## Visão Geral

Os arquivos **`tabuleiro.py`** e **`controlador.py`** foram implementados com base
nos controladores originais escritos em C, mantendo o mesmo protocolo de comunicação
e lógica de jogo, mas agora em Python.

O bot é iniciado pelos scripts:

- `start_bot_mct.py o` → joga com a **onça**  
- `start_bot_mct.py c` → joga com os **cães**

---

## Pré-requisitos

- Python 3.x
- Redis instalado e acessível no sistema

---

## Instalação das dependências

Na raiz do projeto, execute:

```bash
pip3 install -r requirements.txt
````

---

## Como executar

A execução padrão utiliza o **controlador em Python** e o **Redis**.

### 1. Iniciar o servidor Redis

Em um console:

```bash
redis-server redis.conf
```

> Certifique-se de que o arquivo `redis.conf` está acessível no diretório correto
> ou configurado no seu sistema.

### 2. Iniciar o controlador em Python

Em outro console:

```bash
python3 controlador.py o 50 0
```

Parâmetros:

* `o` → lado que inicia o jogo (onça)
* `50` → número máximo de jogadas na partida
* `0` → tempo limite em segundos para cada jogada (`0` = sem limite)

### 3. Iniciar o bot da onça

Em outro console:

```bash
python3 start_bot_mct.py o
```

### 4. Iniciar o bot dos cães

Em outro console:

```bash
python3 start_bot_mct.py c
```

---

## Usando o controlador original em C

O algoritmo também funciona caso o **controlador em C** esteja sendo executado.

Nesse cenário, basta garantir que:

* o **controlador C** esteja rodando, e
* o **servidor Redis** esteja ativo,

e então executar apenas o bot (por exemplo, para a onça):

```bash
python3 start_bot_mct.py o
```

---

## 📝 Observações

* Verifique se todas as instâncias (Redis, controlador e bots) estão usando o
  mesmo host e porta configurados no código.
* Caso utilize ambientes virtuais (virtualenv/venv), lembre-se de ativá-los
  antes de instalar as dependências e rodar os scripts.

```
```
