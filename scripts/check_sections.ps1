$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open("C:\Users\tejas\Desktop\ML_project\ML-Project Documentation.docx", [ref]$false, [ref]$true)
    Write-Host "Total sections: $($doc.Sections.Count)"
    $i = 1
    foreach ($sec in $doc.Sections) {
        $startPage = $sec.Range.Information(1)
        $footerText = $sec.Footers.Item(1).Range.Text.Trim()
        Write-Host "Section $i -> Start Page: $startPage, Footer: '$footerText'"
        $i++
    }
    $doc.Close([ref]$false)
    $word.Quit([ref]$false)
} catch {
    Write-Error $_
    if ($doc) { $doc.Close([ref]$false) }
    if ($word) { $word.Quit([ref]$false) }
}
