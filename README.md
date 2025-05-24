# Financeiro Dashboard

![Streamlit](https://img.shields.io/badge/Deploy-Streamlit-blue)

## 📊 Descrição

O **Financeiro Dashboard** é um aplicativo web desenvolvido em **Streamlit**, voltado para o acompanhamento e análise de suas finanças pessoais. A partir de documentos bancários (extratos de conta, cartão de crédito, investimentos, empréstimos, etc.) em formatos CSV, Excel ou PDF, o dashboard gera:

* **KPIs** principais (saldo, despesas, investimentos, dívidas)
* **Séries temporais** de receitas e despesas
* **Gráficos interativos** por categoria
* **Tabelas detalhadas** dos registros
* **Insights automáticos** via OpenAI (opcional)

Este projeto está organizado para ser fácil de usar, estender e conectar a outras ferramentas (por exemplo, APIs para automação de insights).

---

## 🚀 Recursos

* Visualização de dados em tempo real
* Filtros de data e categoria
* Gráficos interativos com Plotly
* Extração de tabelas de PDFs com `tabula-py` ou `camelot`
* Integração opcional com a API OpenAI para geração de insights
* Deploy simples no **Streamlit Community Cloud** ou outras plataformas

---

## 📂 Estrutura do Projeto

```
financeiro-dashboard/
├── data/                   # Pasta para inserir CSVs, XLSX e PDFs
│   ├── extratos_conta.csv
│   ├── cartao_credito.csv
│   ├── investimentos.csv
│   └── emprestimos.csv
├── dashboard.py            # Aplicativo Streamlit principal
├── requirements.txt        # Dependências do projeto
└── .gitignore              # Arquivos e pastas ignoradas pelo Git
```

---

## 💻 Pré-requisitos

* Python 3.8 ou superior
* [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) instalado no sistema (caso queira extrair tabelas de PDFs ou usar OCR em imagens).

---

## 🔧 Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/NetoVNG/financeiro-dashboard.git
   cd financeiro-dashboard
   ```
2. Crie e ative um ambiente virtual:

   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Execução

Para iniciar o dashboard localmente:

```bash
streamlit run dashboard.py
```

Em seguida, abra o navegador em `http://localhost:8501` para visualizar o painel.

---

## ☁️ Deploy no Streamlit Cloud

1. Acesse [Streamlit Community Cloud](https://streamlit.io/cloud) e faça login.
2. Clique em **"New app"** e conecte seu repositório `financeiro-dashboard` do GitHub.
3. Configure a branch `main` e o arquivo `dashboard.py` como script de inicialização.
4. Clique em **"Deploy"**. Seu dashboard estará online em poucos segundos.

---

## 🤝 Contribuição

Pull requests e sugestões são bem-vindas! Sinta-se à vontade para abrir issues e discutir melhorias.

---

## 📜 Licença

Este projeto está licenciado sob a [MIT License](https://opensource.org/licenses/MIT).
