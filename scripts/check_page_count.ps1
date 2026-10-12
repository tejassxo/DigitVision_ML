$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open('C:\Users\tejas\Desktop\ML_project\docs\DigitVision_AI_Micro_Project_Report_Final.docx')
    $pages = $doc.ComputeStatistics(2)
    Write-Host "EXACT_WORD_PAGE_COUNT: $pages"
    $doc.Close([ref]$false)
} finally {
    $word.Quit()
}
