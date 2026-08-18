param(
    [string]$AssetDir = "assets\dex-concept",
    [string]$OutputPath = "assets\previews\v12-sprite-defect-diagnostics-contact-sheet.png"
)

Add-Type -AssemblyName System.Drawing

$ErrorActionPreference = "Stop"

$assetRoot = (Resolve-Path $AssetDir).Path
$outputFullPath = Join-Path (Get-Location) $OutputPath
$outputDir = Split-Path $outputFullPath -Parent
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

function Load-Bitmap($name) {
    $path = Join-Path $assetRoot $name
    return [System.Drawing.Bitmap]::new($path)
}

function Draw-Label($graphics, $text, $x, $y) {
    $font = [System.Drawing.Font]::new("Consolas", 10, [System.Drawing.FontStyle]::Bold)
    $brush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(245, 245, 245))
    $graphics.DrawString($text, $font, $brush, $x, $y)
    $brush.Dispose()
    $font.Dispose()
}

function Draw-Crop($graphics, $bitmap, $sourceRect, $x, $y, $scale, $label) {
    $destRect = [System.Drawing.Rectangle]::new($x, $y, $sourceRect.Width * $scale, $sourceRect.Height * $scale)
    $graphics.DrawImage($bitmap, $destRect, $sourceRect, [System.Drawing.GraphicsUnit]::Pixel)
    $pen = [System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(220, 220, 220), 1)
    $graphics.DrawRectangle($pen, $destRect)
    $pen.Dispose()
    Draw-Label $graphics $label $x ($y - 18)
}

function Draw-White-Hotspots($graphics, $bitmap, $sourceRect, $x, $y, $scale) {
    $brush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(230, 255, 40, 40))
    for ($py = $sourceRect.Y; $py -lt ($sourceRect.Y + $sourceRect.Height); $py++) {
        for ($px = $sourceRect.X; $px -lt ($sourceRect.X + $sourceRect.Width); $px++) {
            $color = $bitmap.GetPixel($px, $py)
            if ($color.A -gt 0 -and $color.R -gt 190 -and $color.G -gt 190 -and $color.B -gt 190) {
                $graphics.FillRectangle($brush, $x + (($px - $sourceRect.X) * $scale), $y + (($py - $sourceRect.Y) * $scale), $scale, $scale)
            }
        }
    }
    $brush.Dispose()
}

function Get-White-Count($bitmap, $sourceRect) {
    $count = 0
    for ($py = $sourceRect.Y; $py -lt ($sourceRect.Y + $sourceRect.Height); $py++) {
        for ($px = $sourceRect.X; $px -lt ($sourceRect.X + $sourceRect.Width); $px++) {
            $color = $bitmap.GetPixel($px, $py)
            if ($color.A -gt 0 -and $color.R -gt 190 -and $color.G -gt 190 -and $color.B -gt 190) {
                $count++
            }
        }
    }
    return $count
}

$sheet = [System.Drawing.Bitmap]::new(1600, 980)
$graphics = [System.Drawing.Graphics]::FromImage($sheet)
$graphics.Clear([System.Drawing.Color]::FromArgb(28, 28, 28))
$graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::None

Draw-Label $graphics "Dex v12 sprite defect diagnostics - no sprite edits in this pass" 24 18
Draw-Label $graphics "Red overlay marks opaque near-white pixels in the reviewed crop. Lower/right crops are for blobbage and one-frame artifact review." 24 38

$sit = Load-Bitmap "sit_0.png"
$sitLeft = Load-Bitmap "sit_0_left.png"
$patrolFrames = @("patrol_0.png", "patrol_1.png", "patrol_2.png", "patrol_3.png")
$trotFrames = @("trot_0.png", "trot_1.png", "trot_2.png", "trot_3.png")

$full = [System.Drawing.Rectangle]::new(0, 0, 184, 128)
$sitHead = [System.Drawing.Rectangle]::new(74, 0, 76, 54)
$patrolHead = [System.Drawing.Rectangle]::new(0, 0, 82, 54)
$legs = [System.Drawing.Rectangle]::new(38, 70, 106, 54)
$rightEdge = [System.Drawing.Rectangle]::new(132, 24, 48, 76)

Draw-Crop $graphics $sit $full 24 88 2 "sit_0 full"
Draw-Crop $graphics $sit $sitHead 420 88 5 "sit_0 head/white-pixel crop"
Draw-White-Hotspots $graphics $sit $sitHead 420 88 5
Draw-Crop $graphics $sitLeft $sitHead 840 88 5 "sit_0_left head/white-pixel crop"
Draw-White-Hotspots $graphics $sitLeft $sitHead 840 88 5

$x = 24
foreach ($name in $patrolFrames) {
    $bmp = Load-Bitmap $name
    Draw-Crop $graphics $bmp $legs $x 420 3 "$name lower-body crop"
    $x += 330
    $bmp.Dispose()
}

$x = 24
foreach ($name in $trotFrames) {
    $bmp = Load-Bitmap $name
    Draw-Crop $graphics $bmp $legs $x 620 3 "$name lower-body crop"
    $x += 330
    $bmp.Dispose()
}

$x = 24
foreach ($name in $patrolFrames) {
    $bmp = Load-Bitmap $name
    Draw-Crop $graphics $bmp $patrolHead $x 820 3 "$name ear/eye crop"
    Draw-White-Hotspots $graphics $bmp $patrolHead $x 820 3
    $x += 250
    $bmp.Dispose()
}

$x = 1050
foreach ($name in $patrolFrames) {
    $bmp = Load-Bitmap $name
    Draw-Crop $graphics $bmp $rightEdge $x 820 2 "$($name -replace '\.png$', '') right"
    $x += 110
    $bmp.Dispose()
}

$diagnosticText = @()
foreach ($name in @("sit_0.png", "sit_0_left.png") + $patrolFrames + $trotFrames) {
    $bmp = Load-Bitmap $name
    $headRect = if ($name -like "sit_*") { $sitHead } else { $patrolHead }
    $diagnosticText += "$name head white pixels: $(Get-White-Count $bmp $headRect)"
    $diagnosticText += "$name lower white pixels: $(Get-White-Count $bmp $legs)"
    $bmp.Dispose()
}

$sheet.Save($outputFullPath, [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$sheet.Dispose()
$sit.Dispose()
$sitLeft.Dispose()

$diagnosticText | Set-Content -Path ($outputFullPath -replace "\.png$", ".txt")
Write-Output "Wrote $outputFullPath"
Write-Output "Wrote $($outputFullPath -replace '\.png$', '.txt')"
