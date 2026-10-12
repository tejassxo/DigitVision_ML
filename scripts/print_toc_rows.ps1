Add-Type -AssemblyName Microsoft.VisualBasic

try {
    $doc = [Microsoft.VisualBasic.Interaction]::GetObject("C:\Users\tejas\Desktop\ML_project\ML-Project Documentation.docx")
    $t = $doc.Tables.Item(5)
    Write-Host "TOC Table Rows: $($t.Rows.Count)"
    for ($r = 1; $r -le $t.Rows.Count; $r++) {
        $c1 = ($t.Cell($r, 1).Range.Text -replace "[\r\n\a]", "").Trim()
        $c2 = ($t.Cell($r, 2).Range.Text -replace "[\r\n\a]", "").Trim()
        $c3 = ($t.Cell($r, 3).Range.Text -replace "[\r\n\a]", "").Trim()
        Write-Host "Row $r : '$c1' | '$c2' | '$c3'"
    }
} catch {
    Write-Error $_
}
