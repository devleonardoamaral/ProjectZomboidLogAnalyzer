## Changelog

### 0.0.3 Pre-alpha - Refatoração para implementar SQLAlchemy ORM
- **Refatoração Completa**: Reestruturado o código para melhorar a legibilidade e manutenção.
- **Suporte a ORM**: Adicionado suporte ao SQLAlchemy ORM, facilitando a interação com o banco de dados.
- **Segurança Aprimorada**: Implementado um sistema de segurança que garante a integridade das operações, mesmo em caso de interrupção por KeyboardInterrupt.
- **Configurações Específicas**: Introduzidas configurações de regex específicas para cada tipo de log através do arquivo de configuração `config.ini`, permitindo maior flexibilidade na filtragem de logs.
- **Correções de Bugs**: Resolução de diversos bugs resultantes da reestruturação significativa do código, melhorando a estabilidade da aplicação.

### 0.0.2 Pre-alpha - Correções de Problemas
- **Correção**: Resolvido o problema de softlock infinito que ocorria quando nenhum dos padrões regex correspondia à linha atual.
- **Atualização**: Alterado o padrão regex padrão para aceitar logs que não terminam com um ponto final.

### 0.0.1 Pre-alpha - Compromisso Inicial
- **Funcionalidade**: Adicionada a hierarquia de logs para melhor organização das mensagens.
- **Funcionalidade**: Introduzido um singleton `Config` para gerenciar configurações globais da aplicação.
- **Funcionalidade**: Implementada a leitura de logs do **Project Zomboid**, permitindo o processamento sequencial de novas entradas.
- **Funcionalidade**: Adicionado filtro regex personalizável para capturar eventos específicos de log, como interações de jogadores e mudanças de estado.
- **Funcionalidade**: Integrado o armazenamento em banco de dados SQLite para os dados filtrados dos logs, facilitando consultas e análises.
- **Funcionalidade**: Implementada atualização dinâmica para rastrear a posição de leitura dos logs, garantindo que apenas novas entradas sejam processadas.
- **Informação**: A aplicação é de código aberto, promovendo colaboração e contribuições da comunidade. 
