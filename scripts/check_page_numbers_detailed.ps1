$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open("C:\Users\tejas\Desktop\ML_project\ML-Project Documentation.docx", [ref]$false, [ref]$true)

    $sec1 = $doc.Sections.Item(1)
    $sec2 = $doc.Sections.Item(2)

    Write-Host "Sec 1 PageSetup RestartNumbering: $($sec1.Headers.Item(1).PageNumbers.RestartNumberingAtSection)"
    Write-Host "Sec 1 StartingNumber: $($sec1.Headers.Item(1).PageNumbers.StartingNumber)"
    Write-Host "Sec 2 PageSetup RestartNumbering: $($sec2.Headers.Item(1).PageNumbers.RestartNumberingAtSection)"
    Write-Host "Sec 2 StartingNumber: $($sec2.Headers.Item(1).PageNumbers.StartingNumber)"

    # Check first paragraph of Sec 2
    Write-Host "Sec 2 first para text: '$($sec2.Range.Paragraphs.Item(1).Range.Text.Trim())'"

    # For each Chapter heading, check its section and page number
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

    foreach ($p in $doc.Paragraphs) {
        $txt = $p.Range.Text.Trim()
        foreach ($k in $chapterKeys) {
            if ($txt -eq $k -or ($txt.StartsWith($k) -and $txt.Length -lt 80)) {
                # wdActiveEndAdjustedPageNumber = 3, wdActiveEndPageNumber = 1
                $adjPage = $p.Range.Information(3)
                $physPage = $p.Range.Information(1)
                $secNum = $p.Range.Information(2) # wdActiveEndSectionNumber
                Write-Host "$k -> AdjustedPage: $adjPage, PhysicalPage: $physPage, Section: $secNum (Text: '$txt')"
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
