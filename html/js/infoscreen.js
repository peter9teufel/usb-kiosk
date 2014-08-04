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

        var infotexts = httpGet('infoscreen.php?T=TXT&PAGE='+pages[pageNr]);
        var infoJSON = JSON.parse(infotexts);

        var infotext = infoJSON[0];
        var imgList = httpGet('infoscreen.php?T=IMG&PAGE='+pages[pageNr]);
        // split the result --> future version could provide functionality for multiple images
        var images = imgList.split(";");
        // by now we only show the first image if multiple images are returned for a page
        var img = images[0];

        // set new content
        headline.innerHTML =  pages[pageNr];
        textfield.innerHTML = infotext;
        image.src = img;

        // auto size text to avoid overflow
        initTextSize()
        resize()

        // increment pageNr and set timeout for next page switch
        pageNr++;
        var duration = pageDuration(infoJSON);
        setTimeout("switchPage()", duration);

        // calculate duration for each image and set timeout to start image change
        var imgDuration = (duration / images.length) * 0.95;
        setTimeout(function(){
            changeImage(images, 1, imgDuration);
        }, imgDuration);

        // calculate duration for each text and set timeout to start text change
        var txtDuration = (duration / infoJSON.length);
        setTimeout(function(){
            changeText(infoJSON, 1, txtDuration);
        }, txtDuration);
    }
}

function pageDuration(pageTxts){
    var duration = 0;
    for(var i = 0; i < pageTxts.length; i++){
        txt = pageTxts[i];
        var numWords = txt.split(' ').length;
        duration += (numWords / 2) * 1000;
    }
    return duration;
}

function changeImage(images, index, duration){
    if(index < images.length){
        var img = images[index];
        var image_div = document.getElementById("info_img");
        image_div.src = img;
        index++;

        // only set timeout for image change if further images to show
        if(index < images.length){
            setTimeout(function(){
                changeImage(images, index, duration);
            }, duration);
        }
    }
}

function changeText(texts, index, duration){
    if(index < texts.length){
        var txt = texts[index];
        var txt_div = document.getElementById("txt_text");
        txt_div.innerHTML = txt;
        index++;

        // only set timeout for text change if further texts to show
        if(index < texts.length){
            setTimeout(function(){
                changeText(texts, index, duration);
            }, duration);
        }
    }
}

function initTextSize(){
    elements = $('.text');
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
