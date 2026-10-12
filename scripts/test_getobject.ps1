Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName Microsoft.VisualBasic

try {
    # Try GetObject with path to get the running document instance directly!
    $doc = [Microsoft.VisualBasic.Interaction]::GetObject("C:\Users\tejas\Desktop\ML_project\ML-Project Documentation.docx")
    Write-Host "SUCCESS! Connected directly to open document: $($doc.Name)"
    Write-Host "Tables count: $($doc.Tables.Count)"
    
    # Check Table of Contents table
    $t = $null
    for ($i = 1; $i -le $doc.Tables.Count; $i++) {
        $firstCell = $doc.Tables.Item($i).Cell(1,1).Range.Text.Trim()
        if ($firstCell -eq "Chapter") {
            $t = $doc.Tables.Item($i)
            Write-Host "Found TOC table at index $i!"
            break
        }
    }
    if ($t) {
        Write-Host "Row 6 (Intro): $($t.Cell(6,1).Range.Text.Trim()) | $($t.Cell(6,2).Range.Text.Trim()) | $($t.Cell(6,3).Range.Text.Trim())"
    }
} catch {
    Write-Error $_
}
