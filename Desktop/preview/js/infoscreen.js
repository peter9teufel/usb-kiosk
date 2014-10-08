var pageNr=0;
var numPages = 0;
var pages = [];
var timeout;
var second = false;

function load(){
    windowResize()
    showPage()
}

function windowResize() {
   var contentWidth = document.getElementById("main").offsetWidth;
   var contentHeight = document.getElementById("main").offsetHeight;
   window.resizeTo(contentWidth,contentHeight);
}

function showPage(){


    var headline = document.getElementById("txt_headline");
    var textfield = document.getElementById("txt_text");
    var headline_h = document.getElementById("headline_hidden");
    var textfield_h = document.getElementById("infotexts_hidden");
    var image = document.getElementById("info_img");

    var pageHeadline = headline_h.value;
    headline.innerHTML =  pageHeadline;
    // var infotexts = textfield_h.innerHTML;
    var txts = textfield_h.value;
    var infoJSON = txts.split(";")
    var infotext = infoJSON[0];
    infotext = replaceAll("%22", "\"",infotext)
    // set new content
    headline.innerHTML =  pageHeadline;
    textfield.innerHTML = infotext;

    if(isHeadlineTwoLined(headline)){
        if(screen.height < 1000){
            txtMaxH = '69%';
            imgMaxH = '54%';
            imgMaxHNoTxt = '69%';
        }else{
            txtMaxH = '72%';
            imgMaxH = '57%';
            imgMaxHNoTxt = '72%';
        }
    }else{
        if(screen.height < 1000){
            txtMaxH = '74%';
            imgMaxH = '64%';
            imgMaxHNoTxt = '74%';
        }else{
            txtMaxH = '74%';
            imgMaxH = '64%';
            imgMaxHNoTxt = '74%';
        }
    }

    // set visibility of textfield
    if(infoJSON.length == 0 || (infoJSON.length == 1 && infotext.length == 0)){
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

    // calculate page duration --> get minimum duration needed for texts
    var duration = pageDuration(infoJSON);
    // split available duration for images
    var imgDuration = (duration / 2) * 0.95;
    // each image should be visible at least for 5 seconds
    if(duration == 0 || imgDuration < 5000){
        imgDuration = 5000;
        // adjust complete duration --> duration for each image plus 1 sec loading time
        duration = (12000);
    }
    var txtDuration = (duration / infoJSON.length);
    setTimeout(function(){
        changeImage();
    }, imgDuration);
    setTimeout(function(){
        changeText(infoJSON, 1, txtDuration);
    }, txtDuration);
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

function changeImage(){
    var image_div = document.getElementById("info_img");
    image_div.src = "sample_img2.jpg";
}

function changeText(texts, index, duration){
    if(index < texts.length){
        var txt = texts[index];
        txt = replaceAll("%22", "\"", txt)
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

function replaceAll(find, replace, str) {
  return str.replace(new RegExp(find, 'g'), replace);
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
