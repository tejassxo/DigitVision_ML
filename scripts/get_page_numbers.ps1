try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $docPath = "C:\Users\tejas\Desktop\ML_project\ML-Project Documentation.docx"
    # Open ReadOnly ($true)
    $doc = $word.Documents.Open($docPath, [ref]$false, [ref]$true)
    Write-Host "Successfully opened doc in background!"
    Write-Host "Page Count: $($doc.ComputeStatistics(2))" # 2 = wdStatisticPages
    $doc.Close([ref]$false)
    $word.Quit([ref]$false)
} catch {
    Write-Error $_
    if ($word) { $word.Quit([ref]$false) }
}
