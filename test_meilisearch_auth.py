#!/usr/bin/env python3
import requests
import os

url = 'http://meilisearch:7700'
key = '5b1af87b20feb96b826836db017363c4bc08c1e143c449cd148f52da72cf09fa'

# Teste 1: COM Bearer
headers_bearer = {
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

try:
    response = requests.get(f'{url}/indexes', headers=headers_bearer, timeout=5)
    print(f"[1] Bearer: {response.status_code}")
except Exception as e:
    print(f"[1] Bearer ERROR: {e}")

# Teste 2: SEM Bearer (só a chave)
headers_key = {
    'Authorization': key,
    'Content-Type': 'application/json'
}

try:
    response = requests.get(f'{url}/indexes', headers=headers_key, timeout=5)
    print(f"[2] Chave direta: {response.status_code}")
except Exception as e:
    print(f"[2] Chave direta ERROR: {e}")

# Teste 3: Verificar env
env_key = os.getenv('MEILISEARCH_KEY')
print(f"[3] Env MEILISEARCH_KEY: {env_key[:20] if env_key else 'NOT SET'}...")

# Teste 4: Com env
if env_key:
    headers_env = {
        'Authorization': f'Bearer {env_key}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.get(f'{url}/indexes', headers=headers_env, timeout=5)
        print(f"[4] Bearer (ENV): {response.status_code}")
    except Exception as e:
        print(f"[4] Bearer (ENV) ERROR: {e}")
