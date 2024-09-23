# Project Zomboid Log Analyzer

A aplicação é uma ferramenta open-source desenvolvida para coletar e processar logs gerados pelo jogo **Project Zomboid**, permitindo que jogadores e administradores analisem eventos significativos registrados durante as sessões de jogo. Utilizando expressões regulares (regex), a aplicação filtra entradas de log para extrair informações relevantes, transformando dados brutos em insights úteis.

### Principais Funcionalidades:

- **Leitura de Logs**: A aplicação acessa arquivos de log gerados pelo Project Zomboid, permitindo a leitura sequencial e o processamento de novas entradas à medida que são adicionadas.

- **Filtragem por Regex**: Implementa um sistema de regex personalizável que permite aos usuários definir padrões específicos para capturar informações desejadas, como eventos de morte, interações de jogadores e mudanças de estado do jogo.

- **Armazenamento em Banco de Dados SQLite**: Dados filtrados são armazenados em um banco de dados SQLite, facilitando consultas e análises subsequentes. O uso do SQLite garante que a aplicação seja leve e fácil de configurar, sem a necessidade de servidores complexos.

- **Atualizações Dinâmicas**: A aplicação rastreia a posição de leitura dos logs, garantindo que apenas novas entradas sejam processadas, melhorando a eficiência e reduzindo a sobrecarga.

Claro! Aqui está uma versão aprimorada da seção de instalação e uma adição sobre como criar um script para automatizar a execução da aplicação.

## Como instalar e executar

### Pré-requisitos

1. **Instale o Python 3.12.X ou mais recente**: 
   - Faça o download do instalador em [**Python Source Releases**](https://www.python.org/downloads/source/) ou diretamente da [página oficial do Python](https://www.python.org/downloads/).

### Passos para Instalação

2. **Abra o terminal** (Prompt de Comando no Windows ou Terminal no Linux) e navegue até o diretório raiz do aplicativo onde se encontra o arquivo `main.py`.

3. **Crie um ambiente virtual:**
   - Windows e Linux:
   ```bash
   python3 -m venv venv
   ```

4. **Ative o ambiente virtual:**
   - Windows:
   ```bash
   .\venv\Scripts\activate
   ```
   - Linux:
   ```sh
   source venv/bin/activate
   ```

5. **Instale as dependências no ambiente virtual:**
   - Windows e Linux:
   ```bash
   pip install -r requirements.txt
   ```

### Como Executar o Aplicativo

6. **Execute o aplicativo:**
   - Windows:
   ```bash
   .\venv\Scripts\python -m main.py
   ```
   - Linux:
   ```bash
   venv/bin/python -m main.py
   ```

### Criando um Script para Automatizar a Execução

Para simplificar a execução do seu aplicativo, você pode criar um script que automatiza o processo de ativação do ambiente virtual e execução do aplicativo. 

#### Windows

1. **Crie um arquivo chamado `run.bat`** no diretório raiz do seu aplicativo com o seguinte conteúdo:

   ```bat
   @echo off
   call .\venv\Scripts\activate
   python -m main.py
   pause
   ```

   - O comando `pause` é opcional, mas ele permite que você veja a saída do aplicativo antes de fechar o terminal.

#### Linux

1. **Crie um arquivo chamado `run.sh`** no diretório raiz do seu aplicativo com o seguinte conteúdo:

   ```bash
   #!/bin/bash
   source venv/bin/activate
   python -m main.py
   ```

2. **Torne o script executável** com o seguinte comando:

   ```bash
   chmod +x run.sh
   ```

### Executando o Script

- Para executar o script no Windows, basta dar um duplo clique no arquivo `run.bat`.
- Para executar o script no Linux, no terminal, execute:

   ```bash
   ./run.sh
   ```

### Observações Adicionais

- **Desativar o ambiente virtual**: Após terminar a execução do aplicativo, você pode desativar o ambiente virtual utilizando o comando:
   ```bash
   deactivate
   ```

- **Certifique-se de que o Python está adicionado ao PATH** no Windows para que os comandos funcionem corretamente.

## Como configurar o `config.ini`

### Estrutura do Arquivo `config.ini`

O arquivo `config.ini` é dividido em seções que definem caminhos, configurações de aplicativo e padrões de regex para captura de logs.

### [path]

A seção `[path]` define os caminhos relevantes para o diretório do Project Zomboid e para o banco de dados.

#### Campos

- **zomboid**: 
  - **Descrição**: Define o caminho para o diretório do Project Zomboid.
  - **Exemplo**: 
    ```ini
    zomboid=C:/Users/{user}/Zomboid
    ```
  - **Observação**: `{user}` será substituído pelo nome do usuário logado no sistema operacional. Por exemplo, se o usuário logado for 'joao', o caminho resultante será `C:/Users/joao/Zomboid`.

- **database**: 
  - **Descrição**: Define o caminho e o nome do arquivo do banco de dados.
  - **Exemplo**:
    ```ini
    database={app_path}/database.db
    ```
  - **Observação**: `{app_path}` representa o diretório onde o arquivo da aplicação está sendo executado. O arquivo do banco de dados será nomeado como `database.db`.

### [app]

A seção `[app]` contém configurações específicas do aplicativo.

#### Campos

- **reading_frequency**: 
  - **Descrição**: Frequência de leitura dos logs em segundos.
  - **Exemplo**:
    ```ini
    reading_frequency=1
    ```
  - **Observação**: ⚠️ **Atenção**: Definir `reading_frequency` como 0 pode levar a um uso excessivo de recursos.

- **expiration_time**: 
  - **Descrição**: Tempo de expiração para logs em segundos.
  - **Exemplo**:
    ```ini
    expiration_time=10
    ```
  - **Observação**: ⚠️ **Atenção**: Definir `expiration_time` como 0 ou menor desativará a expiração automática dos logs.

### [default]

A seção `[default]` define um padrão de regex para correspondência de logs.

#### Campos

- **pattern**: 
  - **Descrição**: Padrão de regex para capturar mensagens de log padrão.
  - **Exemplo**:
    ```ini
    pattern=^\[(?P<datetime>\d{2}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\](?P<message>.+)$
    ```

### [patterns]

A seção `[patterns]` é opcional e permite definir padrões de regex para logs específicos.

#### Sintaxe

A sintaxe para definir padrões é a seguinte:

```ini
<nome_do_arquivo_de_log>__<nome_da_chave_do_dicionário>=<regex_no_formato_python>
```

- **Observação**: É obrigatório nomear os grupos de captura, pois o resultado JSON do banco de dados será um dicionário utilizando essas capturas nomeadas. Todas as capturas não nomeadas serão ignoradas no JSON resultante.

#### Exemplos

- **Padrão para logs de conexão de usuários**:
  ```ini
  user__fully connected=^\[(?P<datetime>\d{2}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\] (?P<steamid>\d{17}) "([\w\s]+)" fully connected \((?P<coordx>\d+),(?P<coordy>\d+),(?P<coordz>\d+)\)\.$
  ```

- **Padrão para logs de desconexão de usuários**:
  ```ini
  user__disconnected player=^\[(?P<datetime>\d{2}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\] (?P<steamid>\d{17}) "([\w\s]+)" disconnected player \((?P<coordx>\d+),(?P<coordy>\d+),(?P<coordz>\d+)\)\.$
  ```

### Recursos Adicionais

Para entender melhor como criar expressões regulares em Python, consulte os seguintes links:

- [W3Schools: Python Regex](https://www.w3schools.com/python/python_regex.asp)
- [Documentação Python: re](https://docs.python.org/3/library/re.html)
- [Documentação Python: Howto Regex](https://docs.python.org/3/howto/regex.html)
- [SQLite: A Lightweight Database](https://www.sqlite.org/index.html)
