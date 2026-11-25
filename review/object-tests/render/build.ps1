# Generate the two anonymous, entirely synthetic review boards next to the brief.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$root = Split-Path $PSScriptRoot

function Fill($g,$color,$x,$y,$w,$h) {
    $brush = [Drawing.SolidBrush]::new([Drawing.ColorTranslator]::FromHtml($color))
    try { $g.FillRectangle($brush,$x,$y,$w,$h) } finally { $brush.Dispose() }
}
function Line($g,$color,$width,$x1,$y1,$x2,$y2,$opacity=255) {
    $ink = [Drawing.Color]::FromArgb($opacity,[Drawing.ColorTranslator]::FromHtml($color))
    $pen = [Drawing.Pen]::new($ink,$width)
    try { $g.DrawLine($pen,[single]$x1,[single]$y1,[single]$x2,[single]$y2) } finally { $pen.Dispose() }
}
function Label($g,$s,$size,$x,$y,$color='#252e35',$bold=$false) {
    $style = if ($bold) { [Drawing.FontStyle]::Bold } else { [Drawing.FontStyle]::Regular }
    $font = [Drawing.Font]::new('Segoe UI',$size,$style,[Drawing.GraphicsUnit]::Pixel)
    $brush = [Drawing.SolidBrush]::new([Drawing.ColorTranslator]::FromHtml($color))
    try { $g.DrawString($s,$font,$brush,[single]$x,[single]$y) } finally { $font.Dispose(); $brush.Dispose() }
}
function Map($g,$mode) {
    Fill $g '#6f7974' 0 0 360 240
    Fill $g '#555d58' 22 26 325 196
    Fill $g '#d6cba4' 17 20 325 196
    Fill $g '#e6ddba' 17 20 111 196
    Fill $g '#eae1c1' 237 20 105 196
    $g.SetClip([Drawing.Rectangle]::new(17,20,325,196))
    $rng = [Random]::new(237)
    for ($i=0;$i -lt 2200;$i++) {
        $x=$rng.Next(17,342); $y=$rng.Next(20,216)
        Line $g '#625b40' 0.65 $x $y ($x+$rng.Next(2,7)) ($y-1) ($rng.Next(12,40))
    }
    for ($y=45;$y -lt 216;$y+=32) { Line $g '#929578' 0.8 17 $y 342 ($y-9) 95 }
    for ($x=36;$x -lt 342;$x+=38) { Line $g '#929578' 0.8 $x 20 ($x+10) 216 95 }
    $river = @(@(14,132),@(50,126),@(86,143),@(109,143),@(141,159),@(177,160),@(209,176),@(257,168),@(302,190),@(346,192))
    $road = @(@(15,174),@(53,159),@(92,165),@(132,144),@(166,141),@(213,111),@(252,108),@(306,73),@(343,68))
    foreach ($route in @($river,$road)) {
        $isRiver=$route[0][1] -eq 132
        for ($i=1;$i -lt $route.Count;$i++) {
            $p=$route[$i-1]; $q=$route[$i]
            if ($isRiver) { Line $g '#6d9eac' 5 $p[0] $p[1] $q[0] $q[1] }
            else { Line $g '#a65d42' 2.8 $p[0] $p[1] $q[0] $q[1] }
        }
    }
    Label $g 'RIVER DISTRICT' 12 33 35 '#626b56' $true
    Label $g 'East fork' 11 252 175 '#456b74'
    for ($i=0;$i -lt 12;$i++) {
        Line $g '#68634e' 1 (128+$i) 20 (128+$i) 216 ([int](75*(1-$i/12)))
    }
    Line $g '#f8ecc8' 1.6 127 20 127 216
    Line $g '#b2a581' 2 236 20 236 216
    if ($mode -ne 'clean') {
        $rng=[Random]::new(402)
        for ($i=0;$i -lt 450;$i++) {
            $x=$rng.Next(0,81); $y=$rng.Next(0,39)
            $radius=[Math]::Pow(($x-40)/40,2)+[Math]::Pow(($y-19)/19,2)
            if ($radius -ge 1) { continue }
            $opacity=if($mode -eq 'source'){100}else{38}
            $alpha=[int]($opacity*(1-$radius))
            Line $g '#373735' 1.25 (116+$x) (66+$y) (121+$x) (69+$y) $alpha
        }
    }
    $g.ResetClip()
}
function Book($g,$mode) {
    Fill $g '#e2cfab' 0 0 360 240
    for ($i=-240;$i -lt 390;$i+=31) {
        Line $g '#b69376' 2 $i 0 ($i+240) 240
        Line $g '#eee1ca' 1 ($i+4) 0 ($i+244) 240
    }
    for ($i=0;$i -lt 360;$i+=42) { Line $g '#b8a888' 1 $i 0 $i 240 110 }
    $x=if ($mode -eq 'source'){82}else{103}
    for ($i=13;$i -ge 1;$i--) {
        $shade=[Drawing.SolidBrush]::new([Drawing.Color]::FromArgb(10,55,41,28))
        try { $g.FillRectangle($shade,($x+$i), (31+$i), 163,168) } finally { $shade.Dispose() }
    }
    if ($mode -eq 'residual') {
        Line $g '#485757' 1.65 82 45 82 180 108
        Line $g '#485757' 1.2 82 180 82 198 60
    }
    Fill $g '#294b4c' $x 31 163 168
    Fill $g '#d0bd96' ($x+6) 191 153 5
    Line $g '#918368' 1 ($x+6) 194 ($x+158) 194
    Fill $g '#618386' ($x+2) 31 159 160
    Fill $g '#547477' ($x+3) 31 12 160
    Line $g '#456468' 1 ($x+15) 31 ($x+15) 190
    for ($i=0;$i -lt 4;$i++) {
        Line $g '#aec1af' 1 ($x+27) (124+$i*4) ($x+134) (111+$i*4)
    }
    Label $g 'FIELD' 21 ($x+24) 54 '#f0e9d3' $true
    Label $g 'NOTES' 21 ($x+24) 76 '#f0e9d3' $true
}
function Board($name,$title,$task,$modes,$cx,$cy,$note) {
    $board=[Drawing.Bitmap]::new(1140,503)
    $g=[Drawing.Graphics]::FromImage($board)
    $g.Clear([Drawing.ColorTranslator]::FromHtml('#f9f8f4'))
    Label $g $title 23 13 5 '#252e35' $true
    Label $g $task 16 15 38
    Label $g 'Same native-pixel crop from each view' 14 15 335 '#42535a' $true
    $names=@('Reference (before edit)','A','B')
    for($i=0;$i -lt 3;$i++) {
        $x=16+$i*374
        Label $g $names[$i] 16 $x 63 '#263b44' $true
        $scene=[Drawing.Bitmap]::new(360,240); $sg=[Drawing.Graphics]::FromImage($scene)
        $sg.SmoothingMode=[Drawing.Drawing2D.SmoothingMode]::AntiAlias
        if($name -eq 'paper'){ Map $sg $modes[$i] }else{ Book $sg $modes[$i] }
        $sg.Dispose()
        $g.DrawImageUnscaled($scene,$x,89)
        $crop=$scene.Clone([Drawing.Rectangle]::new($cx,$cy,160,96),[Drawing.Imaging.PixelFormat]::Format32bppArgb)
        $g.DrawImageUnscaled($crop,$x,359)
        $crop.Dispose(); $scene.Dispose()
    }
    Label $g $note 14 15 466
    $board.Save((Join-Path $root "$name.png"),[Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $board.Dispose()
}
Board 'paper' 'Folded map' 'Remove the graphite rubbing beside the fold. Keep the paper fibers, printed grid, fold shadow and map markings.' @('source','residual','clean') 85 45 'Stage: delivered cleanup. The reference shows the marked map before cleanup. Inspect the center panel just to the right of the fold.'
Board 'book' 'Book on a patterned mat' 'Move the book 21 pixels right. Preserve the mat pattern, cover and page edges. Move its soft cast shadow with the book.' @('source','clean','residual') 51 108 'Stage: delivered repositioning edit. The reference shows the original placement. Inspect the exposed mat to the left and the shadow below the book.'
