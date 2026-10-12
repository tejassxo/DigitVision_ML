$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $docPath = "C:\Users\tejas\Desktop\ML_project\ML-Project Documentation.docx"
    $doc = $word.Documents.Open($docPath, [ref]$false, [ref]$true)

    # We want page numbers for headings
    $targets = @(
        @{ Key = "Introduction"; Query = "INTRODUCTION" },
        @{ Key = "Literature Survey"; Query = "LITERATURE SURVEY" },
        @{ Key = "Dataset Description"; Query = "DATASET DESCRIPTION" },
        @{ Key = "Data Preprocessing"; Query = "DATA PREPROCESSING AND FEATURE ENGINEERING" },
        @{ Key = "Methodology"; Query = "METHODOLOGY AND MODEL DESIGN" },
        @{ Key = "Model Training"; Query = "MODEL TRAINING AND CONVERGENCE ANALYSIS" },
        @{ Key = "Evaluation"; Query = "EVALUATION AND RESULTS" },
        @{ Key = "Responsible AI"; Query = "RESPONSIBLE AI" },
        @{ Key = "Conclusion"; Query = "CONCLUSION AND FUTURE SCOPE" },
        @{ Key = "References"; Query = "REFERENCES" },
        @{ Key = "Appendix A"; Query = "APPENDIX A" },
        @{ Key = "Appendix B"; Query = "APPENDIX B" },
        @{ Key = "Appendix C"; Query = "APPENDIX C" },
        @{ Key = "Appendix D"; Query = "APPENDIX D" },
        @{ Key = "Appendix E"; Query = "APPENDIX E" },
        @{ Key = "Appendix F"; Query = "APPENDIX F" },
        @{ Key = "Appendix G"; Query = "APPENDIX G" }
    )

    Write-Host "Searching headings in document..."
    foreach ($t in $targets) {
        $find = $doc.Content.Find
        $find.ClearFormatting()
        $find.Text = $t.Query
        $find.MatchCase = $false
        $find.MatchWholeWord = $false
        
        # Execute find
        $found = $find.Execute()
        if ($found) {
            # Check page number of found range
            # Note: make sure it's after Table of Contents (page > 6)
            $rng = $find.Parent
            $page = $rng.Information(3) # wdActiveEndAdjustedPageNumber
            while ($page -le 6 -and $find.Execute()) {
                $rng = $find.Parent
                $page = $rng.Information(3)
            }
            Write-Host "$($t.Key) : Page $page (Matched: '$($rng.Text)')"
        } else {
            Write-Host "$($t.Key) : NOT FOUND"
        }
    }

    $doc.Close([ref]$false)
    $word.Quit([ref]$false)
} catch {
    Write-Error $_
    if ($doc) { $doc.Close([ref]$false) }
    if ($word) { $word.Quit([ref]$false) }
}
