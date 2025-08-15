# $pier_6 = @{
#     0 = 'EDC original scope'
#     1 = 'Entire project'
#     2 = 'Landscape only'
# }
# for (($i = 0);  ($i -lt $pier_6.Count);, ($i++)){
#     $value = $pier_6[$i]
#     New-Setup "Pier 6" "$value\Page {0} Pathfinder.txt" $value $i;
# 





function ReadPier6 {
    # $Folder_Name = "Pathfinder_Data"
    $pier_6 = @{
        0 = 'EDC original scope'
        1 = 'Entire project'
        2 = 'Landscape only'
        3 = 'Landscape only - no reuse'
        4 = 'Landscape only - no woodland'

    }
    for (($i = 0); ($i -lt $pier_6.Count); , ($i++)) {
        $value = $pier_6[$i]
        New-Setup "Pier 6" "$value\Page {0} Pathfinder.txt" $value $i;
      
    }


    # New-Setup "Pier 6" "$Folder_Name\OPT 1-reuse of soil\pg{0}.txt" $pier_6[0] 0;
    # New-Setup "Pier 6" "$Folder_Name\OPT 2-importing soil-subregional distance\pg{0}.txt" $pier_6[1] 1
    # New-Setup "Pier 6" "$Folder_Name\OPT3-importing soil-long distance\pg{0}.txt" $pier_6[2] 2
    uv run "$SRC_PATH\extract\extract.py" "pier_6"
}



function ReadSaginaw {
    $Folder_Name = "Pathfinder_Data"
    $saginaw = @{
        0 = 'reuse'
        1 = 'import'
        2 = 'import_long'
    }
    New-Setup "Saginaw" "$Folder_Name\OPT 1-reuse of soil\pg{0}.txt" $saginaw[0] 0;
    New-Setup "Saginaw" "$Folder_Name\OPT 2-importing soil-subregional distance\pg{0}.txt" $saginaw[1] 1
    New-Setup "Saginaw" "$Folder_Name\OPT3-importing soil-long distance\pg{0}.txt" $saginaw[2] 2
    uv run "$SRC_PATH\extract\extract.py" "saginaw"
}


function ReadNewtownCreek {
    $Folder_Name = "250722_Study"
    $newtown_creek = @{
        0 = 'baseline'
        1 = 'depth_reduction'
        2 = 'area_reduction'
        3 = 'depth_area_reduction'
    }
    New-Setup "Newtown Creek" "Newtown-Creek-page_{0}.txt" $newtown_creek[0] 0;
    New-Setup "Newtown Creek" "$Folder_Name\Newtown-Pave-Study 1- Depth-Reduction-page_{0}.txt" $newtown_creek[1] 1;
    New-Setup "Newtown Creek" "$Folder_Name\Newtown-Pave-Study-2-Area-Reduction-page_{0}.txt" $newtown_creek[2] 2;
    New-Setup "Newtown Creek" "$Folder_Name\Newtown-Pave-Study-3-Depth+Area-Reduction-page_{0}.txt" $newtown_creek[3] 3;
    uv run "$SRC_PATH\extract\extract.py" "newtown_creek"

    
}


#### ----------------- MAIN --------------------
. .\setup.ps1
$SRC_PATH = "C:\Users\juliet.intern\_SCAPECode\path_extract\src\path_extract"
# ReadNewtownCreek
# ReadSaginaw
ReadPier6


