param(
    [Parameter(Mandatory=$true)][string]$Server,
    [Parameter(Mandatory=$true)][string]$Catalog,
    [string]$ClientLibrary = "$env:ProgramFiles\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll",
    [string]$OutputPath
)
# Read-only DAX checks against the user's already open Desktop housing model.
# No credentials, engine writes, publication, or report modifications.
$ErrorActionPreference = 'Stop'
if ($Server -notmatch '^localhost:\d+$') { throw 'Use the local Desktop engine only.' }
[void][System.Reflection.Assembly]::LoadFrom($ClientLibrary)
$housingConnection = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=$Server;Initial Catalog=$Catalog")
function Read-HousingQuery([string]$Query) {
    $housingCommand = $housingConnection.CreateCommand()
    $housingCommand.CommandText = $Query
    $housingReader = $housingCommand.ExecuteReader()
    try {
        while ($housingReader.Read()) {
            $housingRow = [ordered]@{}
            for ($i = 0; $i -lt $housingReader.FieldCount; $i++) {
                $housingRow[$housingReader.GetName($i)] = if ($housingReader.IsDBNull($i)) { $null } else { $housingReader.GetValue($i) }
            }
            [pscustomobject]$housingRow
        }
    } finally { $housingReader.Close(); $housingCommand.Dispose() }
}
$housingConnection.Open()
try {
    $latest = @(Read-HousingQuery @'
EVALUATE SUMMARIZECOLUMNS(Indicator[MetricID], TREATAS({"47"}, 'Area picker'[AreaID]), "value", [Selected area latest], "date", [Latest date], "coverage", [TA coverage], "formatted", [Selected area display], "national", [National display])
'@)
    $expected = @{
        register = @(663.0, '2026-04-01', 65, '663')
        rent = @(595.0, '2025-11-01', 64, '$595')
        consents = @(19.4023, '2026-03-01', 67, '19.4')
        'rent-burden' = @(0.426, '2023-01-01', 67, '42.6%')
        'rent-index' = @(1.2654, '2025-12-31', 66, '1.2654')
    }
    if ($latest.Count -ne 5) { throw 'Expected five exact indicator results.' }
    foreach ($row in $latest) {
        $reference = $expected[$row.'Indicator[MetricID]']
        if (!$reference -or [Math]::Abs($row.'[value]' - $reference[0]) -gt 0.0000001 -or
            $row.'[date]'.ToString('yyyy-MM-dd') -ne $reference[1] -or
            $row.'[coverage]' -ne $reference[2] -or $row.'[formatted]' -ne $reference[3]) {
            throw "Latest value/date/unit/coverage mismatch: $($row.'Indicator[MetricID]')"
        }
    }
    $guards = @(Read-HousingQuery @'
EVALUATE ROW("rows", COUNTROWS(Observation), "duplicates", COUNTROWS(Observation) - COUNTROWS(SUMMARIZE(Observation, Observation[MetricID], Observation[AreaID], Observation[Date])), "mixed_units", [Observed value], "missing_rent", CALCULATE([Selected area latest], TREATAS({"rent"}, Indicator[MetricID]), TREATAS({"67"}, 'Area picker'[AreaID])))
'@)
    if ($guards[0].'[rows]' -ne 13685 -or $guards[0].'[duplicates]' -ne 0 -or
        $null -ne $guards[0].'[mixed_units]' -or $null -ne $guards[0].'[missing_rent]') {
        throw 'Row count, uniqueness, mixed-unit, or missing-data guard failed.'
    }
    $evidence = [ordered]@{ status='Passed read-only live Desktop DAX checks'; latest=$latest; guards=$guards }
    $json = $evidence | ConvertTo-Json -Depth 8
    if ($OutputPath) { [IO.File]::WriteAllText($OutputPath, $json + "`n", [Text.UTF8Encoding]::new($false)) }
    Write-Output $json
} finally { $housingConnection.Close(); $housingConnection.Dispose() }
