from supabase import create_client
import os

url = "https://sgcoqululbosblwicmwz.supabase.co"  # Project URL
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNnY29xdWx1bGJvc2Jsd2ljbXd6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTE1NTc5NjIsImV4cCI6MjEwNzEzMzk2Mn0.I_NC9NrgL-JvYXlAtVLKrp-mFZNRZaxukV0Gu87Syeg"  # pegue no painel do Supabase (Project Settings → API → anon key)
supabase = create_client(url, key)

#usuario um que criei para teste - siga essa mesma estrutura se quiser criar outro
user = supabase.auth.sign_in_with_password({
    "email": "usuario@gmail.com",
    "password": "teste123"
})

print("Access token:", user.session.access_token)
