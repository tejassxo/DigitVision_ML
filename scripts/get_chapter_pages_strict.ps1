$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $docPath = "C:\Users\tejas\Desktop\ML_project\ML-Project Documentation.docx"
    $doc = $word.Documents.Open($docPath, [ref]$false, [ref]$true)

    $chapterKeys = @(
        "CHAPTER 1",
        "CHAPTER 2",
        "CHAPTER 3",
        "CHAPTER 4",
        "CHAPTER 5",
        "CHAPTER 6",
        "CHAPTER 7",
        "CHAPTER 8",
        "CHAPTER 9",
        "REFERENCES",
        "APPENDIX A",
        "APPENDIX B",
        "APPENDIX C"
    )

    Write-Host "Scanning paragraphs for exact Chapter headers with Page >= 12..."
    $foundPages = @{}

    foreach ($p in $doc.Paragraphs) {
        $txt = $p.Range.Text.Trim()
        foreach ($k in $chapterKeys) {
            if ($foundPages[$k] -eq $null) {
                if ($txt -eq $k -or $txt.StartsWith($k)) {
                    $page = $p.Range.Information(3)
                    if ($page -ge 12) {
                        $foundPages[$k] = $page
                        Write-Host "$k -> Page $page (Full text: $txt)"
                    }
                }
            }
        }
    }

    Write-Host ""
    Write-Host "=== EXACT DETECTED PAGE NUMBERS ==="
    foreach ($k in $chapterKeys) {
        $pNum = $foundPages[$k]
        Write-Host "$k : Page $pNum"
    }

    $doc.Close([ref]$false)
    $word.Quit([ref]$false)
} catch {
    Write-Error $_
    if ($doc) { $doc.Close([ref]$false) }
    if ($word) { $word.Quit([ref]$false) }
}
