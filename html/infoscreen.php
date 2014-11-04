<?php

$target = (isset($_REQUEST['T']))? $_REQUEST['T']:'NA';
$data = "";
switch($target){
    case 'PAGES':
        $data = pages();
    break;
    case 'STYLE':
        $page = $_REQUEST['PAGE'];
        $data = style($page);
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
    $pages = array();
    $headlines = "";
    $styles = array();
    $images = array();
    $texts = array();
    $folders = array();
    $pagedirs = array();
    if ($dir_list = opendir($dir)){
        while(($filename = readdir($dir_list)) !== false){
            // check for '.' '..''.htaccess'
            if(!startsWith($filename, ".") && $filename != "." && $filename != ".." && $filename != ".htaccess"){
                if(is_dir($dir . '/' . $filename)){
                    // page directory --> store page dir path
                    $pagedirs[] = $dir . '/' . $filename;
                    $folders[] = $filename;
                }
            }
        }
    }
    // sort page directory paths
    natsort($pagedirs);
    // build result data
    $cnt=0;
    foreach($pagedirs as $pagedir){
        $text = file_get_contents($pagedir . "/txt/headline.txt");
                    if($cnt > 0){
                        $headlines .= ";";
                    }
                    $headlines .= $text;
                    $styles[$cnt] = style($folders[$cnt]);
                    array_push($images, images($folders[$cnt]));
                    // $images[$cnt] = images($folders[$cnt]);
                    $texts[$cnt] = infotext($folders[$cnt]);
                    $cnt = $cnt + 1;
    }
    $pages['page_headlines'] = $headlines;
    $pages['page_styles'] = $styles;
    $pages['page_images'] = $images;
    $pages['page_texts'] = $texts;

    $data = json_encode($pages);
    return $data;
}

function style($folder){
    $dir="./pages/".$folder;
    $result = file_get_contents($dir . "/style.txt");
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
                if(!is_dir($dir . '/' . $filename) && $filename != "headline.txt" &&  endsWith($filename, ".txt")){
                    // $filename points to a txt file in txt dir
                    $text = file_get_contents($dir . "/" . $filename);
                    $lines = explode(PHP_EOL, $text);
                    $result = '';
                    foreach ($lines as $line) {
                        $result .= $line;
                        $result .= '<br>';
                    }
                    $txts[$filename] = $result;
                    $cnt = $cnt + 1;
                }
            }
        }
    }
    ksort($txts);
    $returnArray = array();
    foreach($txts as $txt){
        array_push($returnArray, $txt);
    }
    $data = json_encode($returnArray);
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
