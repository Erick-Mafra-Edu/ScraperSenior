# Script para fazer deploy da correção do OpenAPI no servidor people-fy.com

$SERVER = "root@people-fy.com"
$REMOTE_PATH = "/root/ScraperSenior"
$LOCAL_COMPOSE = "C:\Users\Digisys\scrapyTest\docker-compose.yml"

Write-Host "🚀 Iniciando deploy da correção OpenAPI..." -ForegroundColor Cyan
Write-Host "=" * 70

# Step 1: Fazer backup do docker-compose.yml no servidor
Write-Host "`n1️⃣  Fazendo backup do docker-compose.yml no servidor..." -ForegroundColor Yellow
ssh $SERVER "cd $REMOTE_PATH && cp docker-compose.yml docker-compose.yml.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backup criado com sucesso"
} else {
    Write-Host "❌ Erro ao criar backup"
    exit 1
}

# Step 2: Copiar docker-compose.yml corrigido
Write-Host "`n2️⃣  Copiando docker-compose.yml corrigido..." -ForegroundColor Yellow
scp $LOCAL_COMPOSE "${SERVER}:${REMOTE_PATH}/docker-compose.yml"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Arquivo copiado com sucesso"
} else {
    Write-Host "❌ Erro ao copiar arquivo"
    exit 1
}

# Step 3: Parar containers antigos
Write-Host "`n3️⃣  Parando containers antigos..." -ForegroundColor Yellow
ssh $SERVER "cd $REMOTE_PATH && docker-compose down"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Containers parados com sucesso"
} else {
    Write-Host "⚠️  Erro ao parar containers (pode estar vazio)"
}

# Step 4: Iniciar novos containers
Write-Host "`n4️⃣  Iniciando novos containers..." -ForegroundColor Yellow
ssh $SERVER "cd $REMOTE_PATH && docker-compose up -d"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Containers iniciados com sucesso"
} else {
    Write-Host "❌ Erro ao iniciar containers"
    exit 1
}

# Step 5: Esperar containers ficarem prontos
Write-Host "`n5️⃣  Aguardando containers ficarem prontos (15 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Step 6: Verificar status dos containers
Write-Host "`n6️⃣  Verificando status dos containers..." -ForegroundColor Yellow
ssh $SERVER "cd $REMOTE_PATH && docker-compose ps"

# Step 7: Testar endpoint /openapi.json
Write-Host "`n7️⃣  Testando endpoint /openapi.json..." -ForegroundColor Yellow
$response = curl -s -w "`nHTTP_CODE:%{http_code}" http://people-fy.com:8000/openapi.json

Write-Host "Resposta do servidor:"
Write-Host $response

if ($response -match "HTTP_CODE:200") {
    Write-Host "`n✅ SUCESSO! OpenAPI Server está funcionando!" -ForegroundColor Green
    Write-Host "   Acesse: http://people-fy.com:8000/docs" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Ainda com problema. Verificar logs:" -ForegroundColor Yellow
    Write-Host "   docker-compose logs mcp-server" -ForegroundColor Yellow
}

Write-Host "`n" + "=" * 70
Write-Host "✅ Deploy concluído!" -ForegroundColor Green
