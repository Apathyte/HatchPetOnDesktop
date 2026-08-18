Add-Type -AssemblyName System.Drawing

$assetDir = Join-Path $PSScriptRoot "..\assets\dex-concept"
$w = 184
$h = 128

$movingPrefixes = @("trot", "happy", "patrol", "zoom")
$transparent = [System.Drawing.Color]::FromArgb(0, 0, 0, 0)

function Blend-Color($pixel, $targetR, $targetG, $targetB, $amount) {
    $r = [int]($pixel.R * (1 - $amount) + $targetR * $amount)
    $g = [int]($pixel.G * (1 - $amount) + $targetG * $amount)
    $b = [int]($pixel.B * (1 - $amount) + $targetB * $amount)
    return [System.Drawing.Color]::FromArgb($pixel.A, $r, $g, $b)
}

function Is-PaleArtifact($pixel) {
    if ($pixel.A -le 20) {
        return $false
    }
    $avg = ($pixel.R + $pixel.G + $pixel.B) / 3
    $spread = [Math]::Max($pixel.R, [Math]::Max($pixel.G, $pixel.B)) - [Math]::Min($pixel.R, [Math]::Min($pixel.G, $pixel.B))
    return $avg -gt 150 -and $spread -lt 65
}

function Is-GreyEdgeArtifact($pixel) {
    if ($pixel.A -le 20) {
        return $false
    }
    $avg = ($pixel.R + $pixel.G + $pixel.B) / 3
    $spread = [Math]::Max($pixel.R, [Math]::Max($pixel.G, $pixel.B)) - [Math]::Min($pixel.R, [Math]::Min($pixel.G, $pixel.B))
    return $avg -gt 78 -and $avg -lt 210 -and $spread -lt 80
}

function Is-MovingFrame($name) {
    foreach ($prefix in $movingPrefixes) {
        if ($name -like "$prefix`_*.png") {
            return $true
        }
    }
    return $false
}

function Mirror-Zone($zone) {
    return @{
        x0 = $w - 1 - $zone.x1
        x1 = $w - 1 - $zone.x0
        y0 = $zone.y0
        y1 = $zone.y1
    }
}

function Tone-Zone($bitmap, $zone) {
    $changed = 0
    for ($y = $zone.y0; $y -le $zone.y1; $y++) {
        for ($x = $zone.x0; $x -le $zone.x1; $x++) {
            $pixel = $bitmap.GetPixel($x, $y)
            if (Is-PaleArtifact $pixel) {
                $bitmap.SetPixel($x, $y, (Blend-Color $pixel 42 38 34 0.78))
                $changed++
            }
        }
    }
    return $changed
}

function Clear-Zone($bitmap, $zone) {
    $changed = 0
    for ($y = $zone.y0; $y -le $zone.y1; $y++) {
        for ($x = $zone.x0; $x -le $zone.x1; $x++) {
            $pixel = $bitmap.GetPixel($x, $y)
            if (Is-GreyEdgeArtifact $pixel) {
                $bitmap.SetPixel($x, $y, $transparent)
                $changed++
            }
        }
    }
    return $changed
}

$rightBelly = @{ x0 = 96; x1 = 150; y0 = 76; y1 = 98 }
$rightFarRear = @{ x0 = 166; x1 = 183; y0 = 78; y1 = 100 }
$rightSitLower = @{ x0 = 134; x1 = 183; y0 = 100; y1 = 127 }

$totalFiles = 0

Get-ChildItem -Path $assetDir -Filter *.png | ForEach-Object {
    $name = $_.Name
    $path = $_.FullName
    $shouldClean = (Is-MovingFrame $name) -or ($name -like "sit_0*.png")
    if (-not $shouldClean) {
        return
    }

    $bitmap = [System.Drawing.Bitmap]::new($path)
    try {
        $isLeft = $name -like "*_left.png"
        $belly = if ($isLeft) { Mirror-Zone $rightBelly } else { $rightBelly }
        $farRear = if ($isLeft) { Mirror-Zone $rightFarRear } else { $rightFarRear }
        $sitLower = if ($isLeft) { Mirror-Zone $rightSitLower } else { $rightSitLower }

        $changed = 0
        $changed += Tone-Zone $bitmap $belly

        if (Is-MovingFrame $name) {
            $changed += Clear-Zone $bitmap $farRear
        }

        if ($name -like "sit_0*.png") {
            $changed += Clear-Zone $bitmap $sitLower
        }

        if ($changed -gt 0) {
            $tempPath = "$path.tmp.png"
            $bitmap.Save($tempPath, [System.Drawing.Imaging.ImageFormat]::Png)
            $bitmap.Dispose()
            $bitmap = $null
            Move-Item -LiteralPath $tempPath -Destination $path -Force
            Write-Output "${name}: cleaned $changed pixels"
            $script:totalFiles++
            return
        }
    }
    finally {
        if ($null -ne $bitmap) {
            $bitmap.Dispose()
        }
    }
}

Write-Output "Updated $totalFiles sprite files."
