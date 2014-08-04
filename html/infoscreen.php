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
    // check for available txt files in page directory
    $dir = "./pages/".$folder."/txt";
    $txts = array();
    $cnt = 0;
    if($dir_list = opendir($dir)){
        while(($filename = readdir($dir_list)) !== false){
            // check for '.' '..' and '.htaccess'
            if(!startsWith($filename, ".") && $filename != "." && $filename != ".." && $filename != ".htaccess"){
                if(!is_dir($dir . '/' . $filename) && endsWith($filename, ".txt")){
                    // $filename points to a txt file in txt dir
                    $text = file_get_contents($dir . "/" . $filename);
                    $lines = explode(PHP_EOL, $text);
                    $result = '';
                    foreach ($lines as $line) {
                        $result .= $line;
                        $result .= '<br>';
                    }
                    array_push($txts, $result);
                    $cnt = $cnt + 1;
                }
            }
        }
    }
    $data = json_encode($txts);
    return $data;
}

function startsWith($haystack, $needle){
    return $needle === "" || strpos($haystack, $needle) === 0;
}

function endsWith($haystack, $needle)
{
    return $needle === "" || substr($haystack, -strlen($needle)) === $needle;
}

?>
