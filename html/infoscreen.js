var pageNr=0;
var numPages = 0;
var pages = [];
var timeout;
var second = false;

function load(){
    loadPages();
    switchPage();
}

function switchPage(){
    if(numPages > 0){
        if(pageNr == numPages){
            pageNr = 0;
        }

        var headline = document.getElementById("txt_headline");
        var textfield = document.getElementById("txt_text");
        var image = document.getElementById("info_img");

        var infotext = httpGet('infoscreen.php?T=TXT&PAGE='+pages[pageNr]);
        var imgList = httpGet('infoscreen.php?T=IMG&PAGE='+pages[pageNr]);
        // split the result --> future version could provide functionality for multiple images
        var images = imgList.split(";");
        // by now we only show the first image if multiple images are returned for a page
        img = images[0];

        // set new content
        headline.innerHTML =  pages[pageNr];
        textfield.innerHTML = infotext;
        image.src = img;

        // increment pageNr and set timeout for next page switch
        pageNr++;
        setTimeout("switchPage()", 20000);
}
}

function httpGet(theUrl)
{
    var xmlHttp = null;

    xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", theUrl, false );
    xmlHttp.send( null );
    return xmlHttp.responseText;
}

function loadPages(){
    var list = httpGet('infoscreen.php?T=PAGES');
    pages = list.split(";");
    numPages = pages.length;
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
