# Native Windows source contract: docs/p0-design/windows-command-contract.md
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][ValidateSet('inspect','install','migrate','test','app-check')][string]$Phase,
    [Parameter(Mandatory=$true)][string]$Python,
    [Parameter(Mandatory=$true)][string]$Venv
)
$ErrorActionPreference = 'Stop'
try {
    if (-not [IO.Path]::IsPathRooted($Python) -or -not [IO.Path]::IsPathRooted($Venv)) {
        throw 'Absolute interpreter and venv paths required.'
    }
    if ($env:PYTHONOPTIMIZE) { throw 'Optimized Python refused.' }
    $repoRoot = Split-Path -Parent $PSScriptRoot
    $venvPython = Join-Path $Venv 'Scripts/python.exe'
    Write-Output ('shell_version=' + $PSVersionTable.PSVersion.ToString())
    if ($Phase -eq 'install') {
        & $Python -X utf8 -c "import sys; sys.exit(0 if sys.platform == 'win32' and sys.version_info[:3] == (3,12,14) and sys.flags.optimize == 0 else 1)"
        $nativeExit = $LASTEXITCODE
        if ($nativeExit -ne 0) { exit $nativeExit }
        if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
            # Capture native creation errors, which can contain private paths.
            $creationOutput = & $Python -X utf8 -m venv $Venv 2>&1
            $nativeExit = $LASTEXITCODE
            if ($nativeExit -ne 0) { Write-Error 'Venv preparation failed; diagnostics suppressed.' -ErrorAction Continue; exit $nativeExit }
        }
    }
    if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) { throw 'Existing venv interpreter required; run install explicitly.' }
    Push-Location $repoRoot
    try {
        & $venvPython -X utf8 (Join-Path $PSScriptRoot 'milestone_a_runner.py') $Phase --native-windows
        $nativeExit = $LASTEXITCODE
    } finally { Pop-Location }
    exit $nativeExit
} catch {
    Write-Error 'MILESTONE_A_RESULT=ERROR; phase launcher failed; diagnostics suppressed.' -ErrorAction Continue
    exit 1
}
