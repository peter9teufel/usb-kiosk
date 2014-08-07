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

        // split the result and sort --> provides multiple images
        var images = imgList.split(";");
        images.sort();
        var img = images[0];

        // set new content
        headline.innerHTML =  pages[pageNr];
        textfield.innerHTML = infotext;
        // clear previous image and set new
        image.src = '';
        image.src = img;

        if(isHeadlineTwoLined(headline)){
            txtMaxH = '72%';
            imgMaxH = '57%';
            imgMaxHNoTxt = '72%';
        }else{
            txtMaxH = '81%';
            imgMaxH = '66%';
            imgMaxHNoTxt = '81%';
        }

        // set visibility of textfield
        if(infoJSON.length == 0 || (infoJSON.length == 1 && infotext.split(' ') == 1)){
            // no text to show
            textfield.style.display = 'none';
            image.style.maxWidth = '100%';
            image.style.maxHeight = imgMaxHNoTxt;
        }else{
            textfield.style.display = 'inline';
            textfield.style.maxHeight = txtMaxH;
            image.style.maxWidth = '48%'
            image.style.maxHeight = imgMaxH;
        }

        // auto size text to avoid overflow
        initTextSize()
        resize()

        // increment pageNr and set timeout for next page switch
        pageNr++;

        // calculate page duration --> get minimum duration needed for texts
        var duration = pageDuration(infoJSON);
        // split available duration for images
        var imgDuration = (duration / images.length) * 0.95;
        // each image should be visible at least for 5 seconds
        if(duration == 0 || imgDuration < 5000){
            imgDuration = 5000;
            // adjust complete duration --> duration for each image plus 1 sec loading time
            duration = (images.length * 6000);
        }
        // calculate duration for each text
        var txtDuration = (duration / infoJSON.length);

        // set timeouts for page switch, image change and text change
        setTimeout("switchPage()", duration);
        setTimeout(function(){
            changeImage(images, 1, imgDuration);
        }, imgDuration);
        setTimeout(function(){
            changeText(infoJSON, 1, txtDuration);
        }, txtDuration);
    }
}

function isHeadlineTwoLined(headline){
    var hHeight = headline.offsetHeight;
    var sHeight = screen.height;

    var pHeight = (hHeight / sHeight) * 100;
    return (pHeight > 12);
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

        // auto size text to avoid overflow
        initTextSize()
        resize()

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
        $(el).css("font-size", "65px")
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
