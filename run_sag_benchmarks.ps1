param([string]$RetrievalCIManifest)
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
$env:PYTHONUTF8 = '1'
if (-not $env:SAG_BENCHMARK_USER_ID -or -not $env:SAG_BENCHMARK_ORGANIZATION_ID) {
    throw 'Set the existing SAG account and organization before running.'
}
if ($RetrievalCIManifest) {
    throw 'E2E benchmark requires fresh ingestion; reusing a manifest is not supported.'
}
$env:SAG_BENCHMARK_SCHEMA = 'sag'
$python = Join-Path $PSScriptRoot '../sag-laya-integration/SAG/apps/api/.venv/Scripts/python.exe'
$batch = Join-Path $PSScriptRoot ('reports/quality-latency-' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ'))
New-Item -ItemType Directory -Path $batch | Out-Null
Write-Output "BATCH=$batch"
$scopeNames = @('RUN_ID','PROJECT_ID','SOURCE_ID','SOURCE_CONFIG_ID','OUTPUT_DIR')
foreach ($scopeName in $scopeNames) { Remove-Item -LiteralPath "Env:SAG_BENCHMARK_$scopeName" -ErrorAction SilentlyContinue }
$ciArguments = @((Join-Path $PSScriptRoot 'RetrievalCI_Bench_v0_2026/scripts/run_bench_v0_sag.py'))
$ciLog = Join-Path $batch 'retrievalci.log'
& $python -u @ciArguments *> $ciLog
$ciExit = $LASTEXITCODE
Write-Output "RetrievalCI exit=$ciExit log=$ciLog"
foreach ($scopeName in $scopeNames) { Remove-Item -LiteralPath "Env:SAG_BENCHMARK_$scopeName" -ErrorAction SilentlyContinue }
$vnLog = Join-Path $batch 'vn_mteb.log'
& $python -u (Join-Path $PSScriptRoot 'VN_MTEB_RAG_Bench_2026/scripts/run_vn_mteb_sag.py') *> $vnLog
$vnExit = $LASTEXITCODE
Write-Output "VN-MTEB exit=$vnExit log=$vnLog"
if ($ciExit -eq 0 -and $vnExit -eq 0) {
    $ciId = (Select-String -LiteralPath $ciLog -Pattern '^RUN_ID=(\S+)').Matches[0].Groups[1].Value
    $vnId = (Select-String -LiteralPath $vnLog -Pattern '^RUN_ID=(\S+)').Matches[0].Groups[1].Value
    & $python -u (Join-Path $PSScriptRoot 'summarize_benchmark_runs.py') $ciId $vnId *> (Join-Path $batch 'verification.log')
    exit $LASTEXITCODE
}
exit 1
