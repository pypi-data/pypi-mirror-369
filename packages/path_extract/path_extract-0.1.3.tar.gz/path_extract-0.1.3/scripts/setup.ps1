$SOURCE_FOLDER_ROOT = 'r:\00-WORKSTREAMS\CLMT\CLMT Pilot Projects'
$CLMT_PILOT_FOLDER_INPUTS = 'C:\Users\juliet.intern\_SCAPECode\path_extract\inputs\250701_CLMT_Pilot_Sprint'
$INFO_JSON = 'info.json'
$TEXT_FOLDER = 'text'
$HTML_FOLDER = 'html'

# "R:\00-WORKSTREAMS\CLMT\CLMT Pilot Projects\Analysis"

function New-Setup {

    param (
        [Parameter(Mandatory)]
        [ValidateSet('BPCR','Newtown Creek','Pier 6', 'Saginaw', 'SDSS')]
        [string] $SourceName,
        
        [Parameter(Mandatory)]
        [ValidateScript({
            if (($_).Contains("{0}")) {
                $True
            } else {
                Throw "$_ does not contain {0}, needed for string interpolation!"
            }
        })]
        [string] $SourceFilePath,

        [Parameter(Mandatory)]
        [string] $ExpName,
        

        [Parameter(Mandatory)]
        [int] $ExpNumber,

        [string] $DestFolder = $CLMT_PILOT_FOLDER_INPUTS
    )

    # declare names     
    $ProjectName = $SourceName.Replace(" ", "_").ToLower()
    $ExpFolder = "exp_$ExpNumber"
    
    
    # declare all new paths 
    $ProjectPath = Join-Path $DestFolder $ProjectName
    $ExpPath = Join-Path $ProjectPath $ExpFolder # TODO this shoild be created...
    $JSONPath = Join-Path $ExpPath $INFO_JSON
    $TextPath = Join-Path $ExpPath $TEXT_FOLDER
    $HTMLPath = Join-Path $ExpPath $HTML_FOLDER


    # # create directories if they dont exist 
    New-Item $ProjectPath -ItemType Directory -Force 
    New-Item $ExpPath -ItemType Directory -Force

    New-Item $TextPath -ItemType Directory -Force
    New-Item $HTMLPath -ItemType Directory -Force




    $SourcePath = Join-Path $SOURCE_FOLDER_ROOT $SourceName

    for (($i = 1);  ($i -lt 3);, ($i++)){
        # TODO 
        $InterpolatedFileName = [String]::Format($SourceFilePath, $i)
        $CurrSourcePath = Join-Path $SourcePath $InterpolatedFileName
        Write-Output $InterpolatedFileName
        if (-not (Test-Path $CurrSourcePath)){
            Throw "$CurrSourcePath does not exist!"
        }
        $TextDestPath = Join-Path $TextPath "_$i.txt"
        $HTMLDestPath = Join-Path $HTMLPath "_$i.html"
        Copy-Item $CurrSourcePath $TextDestPath
        Copy-Item $TextDestPath $HTMLDestPath
    }



    # make a info.json in experiment folder
    $Info = @{
        project= $SourceName;
        experiment= $ExpName;
        index= $ExpNumber
    } 
    $JSONInfo =  $Info | ConvertTo-Json
    New-Item $JSONPath -ItemType File -Value $JSONInfo -Force

}

