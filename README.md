# Projeto Django + Supabase

Este projeto integra **Django REST Framework** com **Supabase** para autenticação e banco de dados.  
Ele permite que usuários façam login, obtenham tokens JWT do Supabase e consultem/inseram dados na tabela `profiles`.

---

## 🚀 Tecnologias utilizadas
- Python 3.x
- Django
- Django REST Framework
- Supabase (PostgreSQL + Auth)
- Brevo (envio de OTP)
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
   ```bash
   - crie um arquivo chamado .env na raiz do projeto
   - copie o conteúdo de .env.example e cole em .env
   - agora preencha os campos que faltam em .env
   - todas as chaves são encontradas dentro do supabase
   - a DB_PASSWORD só é fornecida pelo dono do projeto no supabase

5. Rodando no servidor
   ```bash
   Descubra seu IPv4 usando:
   ipconfig
   ```

   Copie o endereço IPv4 e execute:

   ```bash
   python manage.py runserver SEU_IP:8000
   ```

   Exemplo:

   ```bash
   python manage.py runserver xxx.xxx.x.xx:8000
   ```   
   Com ele rodando, 
   ```bash
   adicione /api/ após a porta 
   exemplo: xxx.xxx.x.xx:8000/api/

   assim terá acesso a toda as rotas da api após essa
   ```
  
   
 



   
