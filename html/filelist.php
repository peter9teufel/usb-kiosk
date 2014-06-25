<?php
$dir="./img";
$files = array();
$cnt = 0;
if ($dir_list = opendir($dir))
{
    while(($filename = readdir($dir_list)) !== false)
    {
        if(!startsWith($filename, ".") && $filename != "." && $filename != ".." && $filename != ".htaccess") // check for '.' '..' '.htaccess'
        {
            if(!is_dir($dir.$filename)){
                if($cnt > 0){
                    echo ";";
                }
                echo $dir . '/' . $filename;
                //array_push($files, $filename);
                $cnt = $cnt + 1;
            }
        }
    }
}
//echo json_encode($files);

function startsWith($haystack, $needle)
{
    return $needle === "" || strpos($haystack, $needle) === 0;
}

?>
