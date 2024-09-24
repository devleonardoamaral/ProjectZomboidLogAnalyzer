# Project Zomboid Log Analyzer

**Project Zomboid Log Analyzer** é uma script Python open-source desenvolvido para coletar, processar e analisar logs gerados pelo jogo Project Zomboid, voltada tanto para jogadores quanto para administradores de servidores. Seu principal objetivo é simplificar a extração de informações relevantes dos logs, transformando dados brutos em insights valiosos para a administração e acompanhamento de eventos no jogo.

### Funcionalidades

- **Coleta e Processamento de Logs:** Captura logs gerados durante a execução do jogo ou do servidor.
- **Análise Baseada em Regex:** Utiliza expressões regulares (regex) para filtrar e identificar eventos importantes, como mortes, conexões de jogadores, erros de servidor, entre outros.
- **Exportação de Dados:** Transforma os dados extraídos em formatos como texto ou JSON, possibilitando a integração com outras ferramentas ou sistemas de análise.
- **Armazenamento em SQLite:** Os dados processados são armazenados em um banco de dados SQLite, permitindo consultas rápidas e integrando-se facilmente a outros processos ou sistemas.

### Como funciona

- **Coleta de Logs**: O script verifica todos os logs disponíveis no diretório `Zomboid/Logs`, identificando e filtrando os tipos de log repetidos, selecionando apenas os mais recentes com base no timestamp no nome do arquivo. Após determinar o arquivo atual, é gerado um cache com informações sobre esse arquivo. A cada ciclo de leitura, o script sincroniza esses dados com o banco de dados SQLite. As informações sobre cada tipo de arquivo são registradas na tabela `log_files`.

- **Processamento com Regex**: Durante a leitura dos logs, expressões regulares são aplicadas para filtrar e extrair informações relevantes, como eventos de jogador ou erros críticos. Essas informações são convertidas para um formato JSON e salvas na tabela `logs` no banco de dados SQLite.

- **Gerenciamento de Memória**: A cada iteração, o script filtra as entradas da tabela `logs` do SQLite e remove logs que estejam "expirados", conforme o tempo de expiração configurado no sistema, otimizando o uso de recursos e garantindo que apenas dados relevantes sejam mantidos.

### Requisitos

#### Python 3.12.X ou mais recente
Faça o download do instalador do Python 3.12.x através da [**Página de Download do Python**](https://www.python.org/downloads/) ou da [**Microsoft Store**](https://www.microsoft.com/store/productId/9NCVDN91XZQP?ocid=pdpshare).

#### Bibliotecas Python necessárias
##### SQLAlchemy 2.0.35
```bash
pip install SQLAlchemy==2.0.35
```

### Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests com melhorias, correções ou novas funcionalidades.

### Licença

Este projeto é licenciado sob a [GNU GENERAL PUBLIC LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt).

## Como utilizar

### Passos para Instalação

#### Abra o terminal (Prompt de Comando no Windows ou Terminal no Linux)
Navegue até o diretório raiz do script onde se encontra o arquivo `main.py`.

#### Crie e configure um ambiente virtual
_Certifique-se de que as variáveis de ambiente do Python estejam configuradas corretamente em sua máquina._
```bash
python3 -m venv venv
```

##### Ative o ambiente virtual
###### Windows:
```bash
.\venv\Scripts\activate
```
###### Linux:
```sh
source venv/bin/activate
```

##### Instale as dependências no ambiente virtual
###### Windows e Linux:
```bash
pip install -r requirements.txt
```

### Como Executar o Script

#### Execute o script

Após a primeira execução do script, será gerado automaticamente um arquivo de configuração chamado `config.ini` no mesmo diretório onde o arquivo `main.py` está localizado. 

Antes de continuar utilizando a ferramenta, é necessário configurar esse arquivo. O `config.ini` oferece diversas opções que permitem customizar e ajustar a execução do script, como:

- Diretório de logs
- Filtros de eventos específicos
- Frequência de leitura dos logs
- Tempo de expiração dos logs armazenados
- Configurações de conexão com o banco de dados SQLite

Edite o `config.ini` conforme suas necessidades, e, em seguida, execute o script para começar a coletar e processar os logs de **Project Zomboid** de acordo com as configurações ajustadas.

##### Windows:
```bash
.\venv\Scripts\python -m main.py
```
##### Linux:
```bash
venv/bin/python -m main.py
```

### Criando um Script para Automatizar a Execução

Para simplificar a execução do seu script, você pode criar um script que automatiza o processo de ativação do ambiente virtual e execução do script. 

#### Windows

Crie um arquivo chamado `run.bat`no diretório raiz do seu script com o seguinte conteúdo:

```bat
@echo off
call .\venv\Scripts\activate
python -m main.py
pause
```

O comando `pause` é opcional, mas ele permite que você veja a saída do script antes de fechar o terminal.

#### Linux

Crie um arquivo chamado `run.sh` no diretório raiz do seu script com o seguinte conteúdo:

```bash
#!/bin/bash
source venv/bin/activate
python -m main.py
```

### Observações

**Desativar o ambiente virtual**: Após terminar a execução do script, você pode desativar o ambiente virtual utilizando o comando:
```bash
deactivate
```

**Certifique-se de que o Python está adicionado ao PATH** no Windows para que os comandos funcionem corretamente.

### Recursos Adicionais

Para entender melhor como criar expressões regulares em Python, consulte os seguintes links:

- [W3Schools: Python Regex](https://www.w3schools.com/python/python_regex.asp)
- [Documentação Python: re](https://docs.python.org/3/library/re.html)
- [Documentação Python: Howto Regex](https://docs.python.org/3/howto/regex.html)

Ferramentas externas:
- [SQLite: A Lightweight Database:](https://www.sqlite.org/index.html) Site oficial da tecnologia SQLite, lá você encontra documentação e mais informações sobre.
- [SQLiteStudio:](https://sqlitestudio.pl/) Permite criar, editar e visualizar arquivos do SQLite.
