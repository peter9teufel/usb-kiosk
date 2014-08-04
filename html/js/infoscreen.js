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

        // auto size text to avoid overflow
        initTextSize()
        resize()

        // increment pageNr and set timeout for next page switch
        pageNr++;
        duration = pageDuration(infotext);
        setTimeout("switchPage()", duration);
    }
}

function pageDuration(pageTxt){
    numWords = pageTxt.split(' ').length;
    return (numWords / 2) * 1000;
}

function initTextSize(){
    elements = $('.text');
    console.log(elements);
    if (elements.length < 0) {
        return;
    }
    _results = [];
    for (_i = 0, _len = elements.length; _i < _len; _i++) {
        el = elements[_i];
        $(el).css("font-size", "30px")
    }
}

function resize(){
    var el, elements, _i, _len, _results;
    elements = $('.text');
    console.log(elements);
    if (elements.length < 0) {
        return;
    }
    _results = [];
    for (_i = 0, _len = elements.length; _i < _len; _i++) {
        el = elements[_i];
        _results.push((function(el) {
            var resizeText, _results1;
            resizeText = function() {
                var elNewFontSize;
                elNewFontSize = (parseInt($(el).css('font-size').slice(0, -2)) - 1) + 'px';
                return $(el).css('font-size', elNewFontSize);
            };
            _results1 = [];
            while (el.scrollHeight > el.offsetHeight) {
                _results1.push(resizeText());
            }
            return _results1;
        })(el));
    }
    return _results;
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
    pages.sort();
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
