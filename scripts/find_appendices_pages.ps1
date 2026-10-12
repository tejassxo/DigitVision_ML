$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $docPath = "C:\Users\tejas\Desktop\ML_project\ML-Project Documentation.docx"
    $doc = $word.Documents.Open($docPath, [ref]$false, [ref]$true)

    Write-Host "Looking for actual Appendix sections after page 48..."
    foreach ($p in $doc.Paragraphs) {
        $page = $p.Range.Information(3) # wdActiveEndAdjustedPageNumber
        if ($page -ge 48) {
            $text = $p.Range.Text.Trim()
            if ($text -match "^Appendix\s+[A-G]" -or $text -match "^APPENDIX\s+[A-G]" -or $text -eq "REFERENCES" -or $text -match "^References") {
                Write-Host "Page $page : $text"
            }
        }
    }

    $doc.Close([ref]$false)
    $word.Quit([ref]$false)
} catch {
    Write-Error $_
    if ($doc) { $doc.Close([ref]$false) }
    if ($word) { $word.Quit([ref]$false) }
}
