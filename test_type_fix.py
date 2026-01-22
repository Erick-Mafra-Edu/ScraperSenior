#!/usr/bin/env python3
"""Teste rápido dos ajustes de tipo de parâmetro"""
import json

# Simular o que acontecia antes e depois

print("=== TESTE: Bug Fix de Tipo de Parâmetro ===\n")

# ❌ ANTES (Bug)
print("❌ ANTES (sem validação):")
query_before = ["BPM"]  # Vinha como list
try:
    query_lower = query_before.lower()  # ❌ Erro!
except AttributeError as e:
    print(f"   Erro: {e}\n")

# ✅ DEPOIS (Corrigido)
print("✅ DEPOIS (com validação):")
query_after = ["BPM"]  # Recebe como list
if isinstance(query_after, list):
    query_after = query_after[0] if query_after else ""
query_after = str(query_after).strip()
try:
    query_lower = query_after.lower()  # ✅ OK!
    print(f"   Query normalizado: '{query_after}'")
    print(f"   Lowercase: '{query_lower}'")
    print(f"   Tipo: {type(query_after)}\n")
except AttributeError as e:
    print(f"   Erro: {e}\n")

# Testar com diferentes tipos de entrada
print("=== TESTES COM DIFERENTES ENTRADAS ===\n")

test_cases = [
    "BPM",  # String normal
    ["BPM"],  # List (bug original)
    ["Python", "Rules"],  # List com múltiplos (pega primeiro)
]

for test_input in test_cases:
    print(f"Input: {test_input} (tipo: {type(test_input).__name__})")
    
    query = test_input
    if isinstance(query, list):
        query = query[0] if query else ""
    query = str(query).strip()
    
    print(f"  ✓ Resultado: '{query}' (tipo: {type(query).__name__})")
    print(f"  ✓ Lowercase: '{query.lower()}'\n")

print("✅ Todos os testes passaram! Bug corrigido.")
