# Relatório Financeiro

Aplicativo web desenvolvido em Python/Streamlit que transforma o relatório financeiro exportado de um sistema jurídico em um relatório Excel completo e formatado automaticamente.

## O que o programa faz

O usuário faz upload do arquivo `.xlsx` exportado do sistemas de gestão e o sistema gera um relatório profissional com as seguintes análises:

- **DRE Operacional:** Demonstrativo de Resultado do Exercício completo
- **Movimento Não Contábil:** Distribuição de lucros e resultado de investimentos
- **Conciliação:** Receitas fixas, variáveis e não contábeis detalhadas
- **Despesas:** Todas as despesas detalhadas por categoria
- **Bancos:** Saldo inicial, entradas, saídas e saldo final por conta
- **Ranking de Clientes:** Receita por cliente com participação percentual
- **Centro de Custos:** Receita, despesa e resultado por área do escritório

## Acesse o sistema

🔗 [relatoriofinanceiro.onrender.com](https://relatoriofinanceiro.onrender.com)

> **Obs:** na primeira abertura pode demorar até 30 segundos para carregar (servidor em modo de espera no plano gratuito).

## Como rodar localmente

**Pré-requisitos:** Python 3.9+

```bash
# Clone o repositório
git clone https://github.com/Bomjardimraquel/RelatorioFinanceiro.git
cd RelatorioFinanceiro

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Rode o app
streamlit run app.py
```

## Estrutura do projeto

```
├── app.py           # Interface Streamlit e fluxo principal
├── relatorios.py    # Cálculos financeiros e geração das tabelas
├── estilos.py       # Formatação visual do Excel
├── funcoes.py       # Funções auxiliares de soma
├── requirements.txt # Dependências do projeto
```

## Dependências

```
pandas
xlsxwriter
openpyxl
streamlit
```

## Formato do arquivo de entrada

O arquivo deve ser exportado diretamente do **Astrea** em formato `.xlsx`, contendo as colunas:

`Data`, `Conta Financeira`, `Descricao`, `Categoria`, `Centro de custo`, `Pago para / Recebido de`, `Cliente`, `Valor`, `Tipo`, `Status`

## Segurança

Nenhum dado é armazenado. O arquivo é processado em memória no servidor e descartado após o download do relatório.

---

Desenvolvido por **Raquel Bomjardim** • 2026
