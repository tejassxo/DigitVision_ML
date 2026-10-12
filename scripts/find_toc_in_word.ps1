Add-Type -AssemblyName Microsoft.VisualBasic

try {
    $doc = [Microsoft.VisualBasic.Interaction]::GetObject("C:\Users\tejas\Desktop\ML_project\ML-Project Documentation.docx")
    for ($i = 1; $i -le 10; $i++) {
        $t = $doc.Tables.Item($i)
        $r1 = ""
        try {
            $r1 = $t.Cell(1,1).Range.Text.Trim() + " | " + $t.Cell(1,2).Range.Text.Trim()
        } catch {}
        Write-Host "Table $i : $r1 (Rows: $($t.Rows.Count), Cols: $($t.Columns.Count))"
        if ($r1 -match "Chapter" -or $r1 -match "Title") {
            Write-Host "=== TOC TABLE FOUND AT INDEX $i ==="
            for ($r = 1; $r -le $t.Rows.Count; $r++) {
                $c1 = $t.Cell($r, 1).Range.Text.Trim().Replace([char]7, "")
                $c2 = $t.Cell($r, 2).Range.Text.Trim().Replace([char]7, "")
                $c3 = $t.Cell($r, 3).Range.Text.Trim().Replace([char]7, "")
                Write-Host "Row $r : '$c1' | '$c2' | '$c3'"
            }
        }
    }
} catch {
    Write-Error $_
}
