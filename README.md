# ANS Processor (Python Ver.)

## 📖 Sumário

- [Visão Geral](#-visão-geral)
  - [Objetivo](#objetivo)
  - [Tecnologias Utilizadas](#tecnologias-utilizadas)
  - [Principais Recursos](#principais-recursos)
  - [Tratamento de Erros](#tratamento-de-erros)
- [Execução do Projeto](#-execução-do-projeto)
- [Estrutura de Arquivos](#-estrutura-de-arquivos)
- [Saída Esperada](#-saída-esperada)

## 🔎 Visão Geral

### Objetivo
Automatizar a extração, processamento e compactação dos dados do Anexo I (Rol de Procedimentos) do portal da Agência Nacional de Saúde Suplementar (ANS), garantindo qualidade de dados.

### Tecnologias Utilizadas

| Tecnologia        | Finalidade                         |
|------------------|--------------------------------|
| Python       | Linguagem principal             |
| BeautifulSoup| Extração de URLs e parsing HTML |
| Tabula-py    | Extração de tabelas de PDF      |
| Pandas       | Manipulação e limpeza de dados  |
| Requests     | Download de arquivos            |
| Zipfile      | Compactação de arquivos         |

### Principais Recursos

| Feature                     | Benefício                                 |
| --------------------------- | ----------------------------------------- |
| Normalização de texto       | Dados consistentes e limpos               |
| Tratamento de erros robusto | Continuidade mesmo com problemas parciais |
| Logging detalhado           | Facilita diagnóstico de problemas         |
| Compactação automática      | Arquivo final pronto para envio           |
| Validação de dados          | Garante qualidade da saída                |

### Tratamento de Erros

O sistema possui um tratamento orientado para:

- **Falhas de conexão** com o portal.
- **Estrutura inesperada** de PDF.
- **Dados corrompidos ou incompletos**.
- **Problemas de escrita em disco**.

 **📌 Todos os erros são registrados no arquivo `ans_processor.log` com detalhes para diagnóstico.**

## ⚙️ Execução do Projeto

#### 1. Faça um clone [do repositório](https://github.com/anaperinii/web-scraper-ans-py.git) em sua máquina:

* Crie uma pasta em seu computador para esse programa
* Abra o `git bash` ou `terminal` dentro da respectiva pasta
* Copie a [URL](https://github.com/anaperinii/web-scraper-ans-py.git) do repositório
* Digite `git clone <URL copiada>` e pressione `enter`
* Instale as dependências necessárias com `pip install`

#### 2. Execute o processador principal:

```bash
python processador_anss.py
```

## 📂 Estrutura de Arquivos

```
.
├── downloads/          # Arquivos baixados temporariamente (PDF)
├── output/             # Resultados processados
│   ├── Rol_Procedimentos.csv
│   └── Teste_[NOME].zip
├── ans_processor.log   # Log de execução
└── ans_processor.py    # Código principal
```

## 📊 Saída Esperada

```
2023-11-20 10:00:00 - INFO - URL do Anexo I encontrada: https://www.gov.br/.../Anexo_I.pdf
2023-11-20 10:00:05 - INFO - Arquivo baixado: downloads/Anexo_I.pdf
2023-11-20 10:00:10 - INFO - Extraídas 3392 linhas
2023-11-20 10:00:15 - INFO - Dados limpos e formatados
2023-11-20 10:00:20 - INFO - CSV formatado salvo em: output/Rol_Procedimentos.csv
2023-11-20 10:00:25 - INFO - Arquivo ZIP criado: output/Teste_Ana_Perini.zip
```


