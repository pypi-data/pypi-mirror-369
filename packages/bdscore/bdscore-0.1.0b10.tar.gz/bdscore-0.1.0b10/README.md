## BDSCore

BDSCore é a biblioteca oficial da BDS DataSolution para integração com APIs de dados de mercado e dados proprietários.

### Principais recursos
- Autenticação via chave de API BDS
- Suporte a múltiplas URLs base para diferentes serviços (DataPack, DataManagement, DataFlex)
- Reutilização de sessão HTTP para eficiência e performance
- Métodos organizados por serviço: `bds.datapack.getFX()`, `bds.datamanagement.getEquitiesB3()`, entre outros
- Tratamento robusto de erros, incluindo mensagens detalhadas
- Documentação integrada via docstrings para fácil uso em IDEs

### Instalação

```bash
pip install bdscore
```

### Quick Start

```python
from bdscore import BDSCore

# Instanciar o BDSCore
bds = BDSCore(api_key="SUA_CHAVE_AQUI")

# Pegar TODAS as últimas cotações os dados do mercado de câmbio (Moedas) disponíves no mercado
fx = bds.datapack.getFX(Symbols=":all", InitialDate="last")

# Exibir os dados (padrão Dictionary)
print(fx.data)
# Exibir os dados em JSON
print(fx.data.to_json())
# Exibir os dados em DataFrame (pandas)
print(fx.data.to_df())
```

### Sobre

A **BDS DataSolution** é especialista em dados, informações e geradora de insights para o mercado financeiro. Utiliza as mais eficientes tecnologias de Inteligência Artificial para acelerar e potencializar decisões.

O propósito da biblioteca **BDSCore** é justamente conectar você, desenvolvedor ou empresa, a esse ecossistema de dados e inteligência da BDS. Com ela, você pode acessar de forma simples, segura e eficiente todos os dados, APIs e funcionalidades oferecidas pelo BDS DataPack e BDS DataManagement, integrando diretamente os recursos de Big Data, Analytics e IA ao seu sistema ou aplicação.