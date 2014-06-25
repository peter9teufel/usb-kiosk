var i=0;
var numFiles = 0;
var files = [];
var timeout;
var second = false;

function httpGet(theUrl)
{
    var xmlHttp = null;

    xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", theUrl, false );
    xmlHttp.send( null );
    return xmlHttp.responseText;
}

function loadInfoText(){
    var text = httpGet('infotext.php');
    var txtElem = document.getElementById("info_line");
    txtElem.innerHTML = text;
}

function readFilelist(){
    var list = httpGet('filelist.php');
    files = list.split(";");
    numFiles = files.length;
}
function change_image()
{
    readFilelist();
    // ease_out();
    change()
}

function ease_out(){
    var img_elem = document.getElementById("bg_img");
    img_elem.style.opacity = 0;
    img_elem.style.filter = 'alpha(opacity=0)'; // IE fallback
    timeout = setTimeout("change()", 1000);
}
function change(){
    if(i==numFiles)
    {
        i=0;
    }

    var img=files[i];
    var img_elem = document.getElementById("bg_img");
    img_elem.src=img;
    i++;
    //setTimeout("ease_in()",1000);
    setTimeout("change()", 15000);
}

function ease_in(){
    var img_elem = document.getElementById("bg_img");
    img_elem.style.opacity = 100;
    img_elem.style.filter = 'alpha(opacity=100)'; // IE fallback
    timeout = setTimeout("change_image()", 15000);
}
