$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $docPath = "C:\Users\tejas\Desktop\ML_project\ML-Project Documentation.docx"
    $doc = $word.Documents.Open($docPath, [ref]$false, [ref]$true)

    $headings = @(
        "Introduction",
        "Literature Survey",
        "Dataset Description",
        "Data Preprocessing and Feature Engineering",
        "Methodology and Model Design",
        "Model Training and Convergence Analysis",
        "Evaluation and Results",
        "Responsible AI: Societal, Environmental and Ethical Considerations",
        "Conclusion and Future Scope",
        "References",
        "Appendix A",
        "Appendix B",
        "Appendix C",
        "Appendix D",
        "Appendix E",
        "Appendix F",
        "Appendix G"
    )

    Write-Host "Scanning paragraphs for headings and their exact Word page numbers..."
    $results = @{}

    # Also iterate over all paragraphs and find matches
    foreach ($p in $doc.Paragraphs) {
        $text = $p.Range.Text.Trim()
        if ($text.Length -gt 0 -and $text.Length -lt 150) {
            foreach ($h in $headings) {
                if ($results[$h] -eq $null) {
                    # Check if paragraph starts with Chapter X: $h or is the heading
                    $isMatch = $false
                    if ($text -eq $h) { $isMatch = $true }
                    elseif ($text -match "^Chapter\s+\d+[:\.\s]+$h") { $isMatch = $true }
                    elseif ($text -match "^1[\.\s]+$h" -and $h -eq "Introduction") { $isMatch = $true }
                    elseif ($text -match "^2[\.\s]+$h" -and $h -eq "Literature Survey") { $isMatch = $true }
                    elseif ($text -match "^3[\.\s]+$h" -and $h -eq "Dataset Description") { $isMatch = $true }
                    elseif ($text -match "^4[\.\s]+$h" -and $h -match "Data Preprocessing") { $isMatch = $true }
                    elseif ($text -match "^5[\.\s]+$h" -and $h -match "Methodology") { $isMatch = $true }
                    elseif ($text -match "^6[\.\s]+$h" -and $h -match "Model Training") { $isMatch = $true }
                    elseif ($text -match "^7[\.\s]+$h" -and $h -match "Evaluation") { $isMatch = $true }
                    elseif ($text -match "^8[\.\s]+$h" -and $h -match "Responsible AI") { $isMatch = $true }
                    elseif ($text -match "^9[\.\s]+$h" -and $h -match "Conclusion") { $isMatch = $true }
                    elseif ($h -match "^Appendix" -and $text -like "$h*") { $isMatch = $true }

                    if ($isMatch) {
                        # wdActiveEndAdjustedPageNumber = 3, wdActiveEndPageNumber = 1
                        $page = $p.Range.Information(3)
                        $results[$h] = @{
                            Text = $text
                            Page = $page
                        }
                        Write-Host "FOUND: '$h' -> Page $page (Heading: '$text')"
                    }
                }
            }
        }
    }

    Write-Host "`nSummary of Detected Page Numbers:"
    foreach ($h in $headings) {
        if ($results[$h]) {
            Write-Host "$h : Page $($results[$h].Page)"
        } else {
            Write-Host "$h : NOT FOUND DIRECTLY"
        }
    }

    $doc.Close([ref]$false)
    $word.Quit([ref]$false)
} catch {
    Write-Error $_
    if ($doc) { $doc.Close([ref]$false) }
    if ($word) { $word.Quit([ref]$false) }
}
