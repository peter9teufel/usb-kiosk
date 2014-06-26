<?php

$target = (isset($_REQUEST['T']))? $_REQUEST['T']:'NA';
$data = "";
switch($target){
    case 'PAGES':
        $data = pages();
    break;
    case 'IMG':
        $page = $_REQUEST['PAGE'];
        $data = images($page);
    break;
    case 'TXT':
        $page = $_REQUEST['PAGE'];
        $data = infotext($page);
    break;
}
echo $data;


function pages(){
    $dir="./pages";
    $files = array();
    $cnt = 0;
    $result = "";
    if ($dir_list = opendir($dir)){
        while(($filename = readdir($dir_list)) !== false){
            // check for '.' '..''.htaccess'
            if(!startsWith($filename, ".") && $filename != "." && $filename != ".." && $filename != ".htaccess"){
                if(is_dir($dir . '/' . $filename)){
                    if($cnt > 0){
                        $result .= ";";
                    }
                    $result .= $filename;
                    //array_push($files, $filename);
                    $cnt = $cnt + 1;
                }
            }
        }
    }
    return $result;
}

function images($folder){
    $dir="./pages/".$folder."/img";
    $files = array();
    $cnt = 0;
    $result = "";
    if ($dir_list = opendir($dir)){
        while(($filename = readdir($dir_list)) !== false){
            // check for '.' '..' '.htaccess'
            if(!startsWith($filename, ".") && $filename != "." && $filename != ".." && $filename != ".htaccess"){
                if(!is_dir($dir . '/' . $filename)){
                    if($cnt > 0){
                        $result .= ";";
                    }
                    $result .= $dir . '/' . $filename;
                    //array_push($files, $filename);
                    $cnt = $cnt + 1;
                }
            }
        }
    }
    return $result;
}


function infotext($folder){
    $f = fopen("./pages/".$folder."/txt/info.txt", "r");
    // Liest eine Zeile aus der Textdatei und gibt deren Inhalt aus
    $text = fgets($f);
    return $text;
}

function startsWith($haystack, $needle){
    return $needle === "" || strpos($haystack, $needle) === 0;
}

?>
