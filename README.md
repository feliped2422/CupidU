# Projeto Django + Supabase

Este projeto integra **Django REST Framework** com **Supabase** para autenticação e banco de dados.  
Ele permite que usuários façam login, obtenham tokens JWT do Supabase e consultem/inseram dados na tabela `profiles`.

---

## 🚀 Tecnologias utilizadas
- Python 3.x
- Django
- Django REST Framework
- Supabase (PostgreSQL + Auth)
- Insomnia (para testes de API)

---

## ⚙️ Configuração do ambiente

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-repo/projeto.git
   cd projeto

2. Crie e ative o ambiente virtual
   ```bash
   python -m venv venv
   
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows

3. Instale as dependências
   ```bash
   pip install -r requirements.tx

4. configure .env
  - crie um arquivo chamado .env na raiz do projeto
  - copie o conteúdo de .env.example e cole em .env
  - depois disso pode apagar o .env.example
  - agora preencha os campos que faltam em .env
  - todas as chaves são encontradas dentro do supabase
  - a DB_PASSWORD só é fornecida pelo dono do projeto no supabase

5. Rodando no servidor
   ```bash
   python manage.py runserver

## 🔑 Autenticação
O login gera um access_token JWT do supabase
esse token deve ser usado nos headers das requisições

No Insomnia ->

1. Crie uma requisição GET para `https://sgcoqululbosblwicmwz.supabase.co/rest/v1/profiles`
 - no lugar de `profiles` coloque oq deseja acessar
 - isso irá permitir ter acesso aos dados do banco
   
2. Adicione os headers
 - Content-Type: application/json
 - apikey: SUA_ANON_KEY
 - Authorization: Bearer SEU_ACCESS_TOKEN
   
 O indicio que funcionou é a resposta `200 OK`

 -para conseguir o SEU_ACCESS_TOKEN, rode na raiz do projeto
   ```bash
    python login.py
 
  
   
 



   
