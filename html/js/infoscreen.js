var SITE_ROOT = "http://localhost/usb-kiosk/";
var TICKER_INTERVAL = 15; // ms
var init_load = true;
var pageNr=0;
var pageData = [];
var cachedImgs = [];
var numPages = 0;
var pages = [];
var timeout;
var second = false;
var tickerPos=1850;
var tickerW = -1;
var ticker_text = "";
var ticker_moving = true;
var ticker_enabled = true;
var background = "";
var duration_offset = 0;

function load(){
    loadPages();
    // set initial ticker position
    var tWidth = $("#ticker").width()
    tickerPos = tWidth;
    switchPage();
    moveText();
}

function switchPage(){
    if(duration_offset == 0){
        if(init_load || !ticker_moving || tickerOffScreen()){
            if(numPages > 0 && pages[0] != ""){
                if(pageNr == numPages){
                    pageNr = 0;
                }

                var headline = document.getElementById("txt_headline");

                var infotexts = pageData['page_texts'][pageNr];

                var styleStr = pageData['page_styles'][pageNr];
                var styleJSON = JSON.parse(styleStr);
                var style = 'style' in styleJSON ? parseInt(styleJSON['style']) : 0;
                var imageMode = 'img_mode' in styleJSON ? styleJSON['img_mode'] : 'image_fit';
                var ticker_txt = 'ticker_text' in styleJSON ? styleJSON['ticker_text'] : null;
                var enable_ticker = 'ticker_enabled' in styleJSON ? styleJSON['ticker_enabled'] == "1" : true;
                var ticker_mov = 'ticker_moving' in styleJSON ? styleJSON['ticker_moving'] == 1 : null;
                var fontFam = 'font_family' in styleJSON ? styleJSON['font_family'] : null;
                var customBg = 'custom_bg' in styleJSON ? styleJSON['custom_bg'] == "1" : false;
                updateBackground(customBg);
                updateTicker(ticker_txt, ticker_mov, enable_ticker);

                var infoJSON = JSON.parse(infotexts);

                var infotext = infoJSON[0];

                // split the result and sort --> provides multiple images
                var images = cachedImgs[pageNr];
                images.sort();
                var img = images[0];

                var ids = new Array()
                switch(style){
                    case 0: // HL, Ticker, IMG left, TXT right
                        ids = setupDefaultPage();
                        break;
                    case 1:
                        ids = setupDefaultPageFlipped();
                        break;
                    case 2:
                        ids = setupDoubleImagePage();
                        break;
                    case 3:
                        ids = setupTextOnlyPage();
                        break;
                    case 4:
                        ids = setupImageOnlyPage();
                        break;
                    case 5:
                        ids = setupFullscreenImagePage();
                        break;
                }

                var textfield = document.getElementById(ids['txt']);

                // set new content
                headline.innerHTML =  pages[pageNr];
                textfield.innerHTML = infotext;

                if(style == 2){
                    var image1 = document.getElementById(ids['img'][0]);
                    var image2 = document.getElementById(ids['img'][1]);
                    image1.src = images[0];
                    image2.src = images[1];

                    image1.onload = function(e){
                        sizeImage(ids['img'][0], ids['img_container'][0], imageMode)
                    }
                    image2.onload = function(e){
                        sizeImage(ids['img'][1], ids['img_container'][1], imageMode)
                    }
                }else{
                    var image = document.getElementById(ids['img']);
                    image.src = img;
                    image.onload = function(e){
                        sizeImage(ids['img'], ids['img_container'], imageMode);
                    }
                }

                // auto size text to avoid overflow
                initTextSize();
                resize();

                // increment pageNr and set timeout for next page switch
                pageNr++;

                // calculate page duration --> get minimum duration needed for texts
                var duration = pageDuration(infoJSON);
                // split available duration for images
                var imgDuration = (duration / images.length) * 0.95;
                if(style == 2){
                    // two images at once
                    imgDuration *= 2;
                }
                // each image should be visible at least for 5 seconds
                if(duration == 0 || imgDuration < 8000){
                    imgDuration = 8000;
                    // adjust complete duration --> duration for each image plus some loading time
                    duration = (images.length * 8700);
                    if(style == 2){
                        imgDuration = 11000;
                        duration = (images.length / 2) * 11700
                    }else if(style == 5){
        		duration = 11700;
        		imgDuration = 11000;
        	    }
                }
                // calculate duration for each text
                var txtDuration = (duration / infoJSON.length);

                // set timeouts for page switch, image change and text change
                setTimeout("switchPage()", duration);
                setTimeout(function(){
                    changeImage(images, 1, imgDuration, ids['img'], ids['img_container'], style, imageMode);
                }, imgDuration);
                setTimeout(function(){
                    changeText(infoJSON, 1, txtDuration, ids['txt']);
                }, txtDuration);
            } else {
                // no pages on player show demo page with description
                headline = document.getElementById("txt_headline");
                textfield = document.getElementById("txt_text");
                image = document.getElementById("info_img");
                image.style.display = 'none';
                noImg = true;
                textfield.style.width = '96.5%';
                textfield.style.height = '62%';

                var title = "Welcome to your USB-Kiosk!";
                var msg = "How to get started:<br>";
                msg += " - Open the \"Kiosk Editor\" desktop application to setup your kiosk pages, background, logo and background music.<br>";
                msg += " - Kiosk Editor allows you to save your kiosk configuration in one single file to share it or edit it again.<br>";
                msg += " - Once you have all your pages setup, click on \"File - Create Kiosk USB-Stick\"<br>";
                msg += " - You will be prompted to connect a USB Stick and your pages will be copied as soon as you do so.<br>";
                msg += " - Connect the prepared USB Stick to the Kiosk player and power it on.<br>";
                msg += "<br>";
                msg += "THAT'S IT! Your data is copied to the player and the player starts the kiosk mode.<br>";
                msg += "<br>";
                msg += "For more information checkout the ReadMe at http://bit.do/usb-kiosk-readme";

                headline.innerHTML = title
                textfield.innerHTML = msg

                // auto size text to avoid overflow
                initTextSize()
                resize()
            }
            if(init_load){
                init_load = false;
            }
        }else{
            // wait for ticker to go offscreen before switching page
            var delay = timeUntilTickerOffScreen();
            setTimeout("switchPage()", delay/4);
        }
    }else{
        // page duration has offset due to waiting for ticker for image changes, wait that offset before changing and reset offset
        setTimeout("switchPage()", duration_offset);
        duration_offset = 0;
    }
}

function setupDefaultPage(){
    var headline = document.getElementById("txt_headline");
    var textfield = document.getElementById("txt_text");
    var image = document.getElementById("info_img");
    var image_container = document.getElementById("img_container");
    var textfield_2 = document.getElementById("txt_text_2");
    var image_2 = document.getElementById("info_img_2");
    var image_2_container = document.getElementById("img_container_2");
    var image_fullscreen = document.getElementById("info_img_fullscreen");
    var image_fullscreen_container = document.getElementById("img_container_fullscreen");
    var logo = document.getElementById("logo_div");

    // hide unused elements
    image_fullscreen_container.style.display = 'none';
    textfield_2.style.display = 'none';
    image_2_container.style.display = 'none';

    // show page elements
    headline.style.display = 'inline';
    textfield.style.display = 'inline';
    textfield.style.width = '48%';
    image_container.style.display = 'inline';
    image_container.style.width = '48%';
    logo.style.display = 'inline';

    ids = new Array()
    ids['txt'] = "txt_text";
    ids['img'] = "info_img";
    ids['img_container'] = "img_container";
    return ids;
}

function setupDefaultPageFlipped(){
    var headline = document.getElementById("txt_headline");
    var textfield = document.getElementById("txt_text");
    var image = document.getElementById("info_img");
    var textfield_2 = document.getElementById("txt_text_2");
    var image_2 = document.getElementById("info_img_2");
    var image_container = document.getElementById("img_container");
    var image_2_container = document.getElementById("img_container_2");
    var image_fullscreen = document.getElementById("info_img_fullscreen");
    var image_fullscreen_container = document.getElementById("img_container_fullscreen");
    var logo = document.getElementById("logo_div");

    // hide unused elements
    image_fullscreen_container.style.display = 'none';
    textfield.style.display = 'none';
    image_container.style.display = 'none';

    // show page elements
    headline.style.display = 'inline';
    textfield_2.style.display = 'inline';
    textfield_2.style.width = '48%';
    image_2_container.style.display = 'inline';
    image_2_container.style.width = '48%';
    logo.style.display = 'inline';

    ids = new Array()
    ids['txt'] = "txt_text_2";
    ids['img'] = "info_img_2";
    ids['img_container'] = "img_container_2";
    return ids;
}

function setupTextOnlyPage(){
    var headline = document.getElementById("txt_headline");
    var textfield = document.getElementById("txt_text");
    var image = document.getElementById("info_img");
    var textfield_2 = document.getElementById("txt_text_2");
    var image_2 = document.getElementById("info_img_2");
    var image_container = document.getElementById("img_container");
    var image_2_container = document.getElementById("img_container_2");
    var image_fullscreen = document.getElementById("info_img_fullscreen");
    var image_fullscreen_container = document.getElementById("img_container_fullscreen");
    var logo = document.getElementById("logo_div");

    // hide unused elements
    image_fullscreen_container.style.display = 'none';
    image_2_container.style.display = 'none';
    image_container.style.display = 'none';
    textfield_2.style.display = 'none';

    // show page elements
    headline.style.display = 'inline';
    textfield.style.display = 'inline';
    textfield.style.width = '98%';
    logo.style.display = 'inline';

    ids = new Array()
    ids['txt'] = "txt_text";
    ids['img'] = "info_img";
    ids['img_container'] = "img_container";
    return ids;
}

function setupImageOnlyPage(){
    var headline = document.getElementById("txt_headline");
    var textfield = document.getElementById("txt_text");
    var image = document.getElementById("info_img");
    var textfield_2 = document.getElementById("txt_text_2");
    var image_2 = document.getElementById("info_img_2");
    var image_container = document.getElementById("img_container");
    var image_2_container = document.getElementById("img_container_2");
    var image_fullscreen = document.getElementById("info_img_fullscreen");
    var image_fullscreen_container = document.getElementById("img_container_fullscreen");
    var logo = document.getElementById("logo_div");

    // hide unused elements
    image_fullscreen_container.style.display = 'none';
    image_container.style.display = 'none';
    textfield.style.display = 'none';
    textfield_2.style.display = 'none';
    logo.style.display = 'inline';

    // show page elements
    headline.style.display = 'inline';
    image_2_container.style.display = 'inline';
    image_2_container.style.width = '98%';
    
    ids = new Array()
    ids['txt'] = "txt_text";
    ids['img'] = "info_img_2";
    ids['img_container'] = "img_container_2";
    return ids;
}

function setupDoubleImagePage(){
    var headline = document.getElementById("txt_headline");
    var textfield = document.getElementById("txt_text");
    var image = document.getElementById("info_img");
    var textfield_2 = document.getElementById("txt_text_2");
    var image_2 = document.getElementById("info_img_2");
    var image_container = document.getElementById("img_container");
    var image_2_container = document.getElementById("img_container_2");
    var image_fullscreen = document.getElementById("info_img_fullscreen");
    var image_fullscreen_container = document.getElementById("img_container_fullscreen");
    var logo = document.getElementById("logo_div");

    // hide unused elements
    image_fullscreen_container.style.display = 'none';
    textfield.style.display = 'none';
    textfield_2.style.display = 'none';

    // show page elements
    headline.style.display = 'inline';
    image_container.style.display = 'inline';
    image_container.style.width = '48%';
    image_2_container.style.display = 'inline';
    image_2_container.style.width = '48%';
    logo.style.display = 'inline';

    // info_img is right and info_img_2 left --> fix order with order of IDs
    ids = new Array()
    ids['txt'] = "txt_text";
    ids['img'] = ["info_img_2", "info_img"];
    ids['img_container'] = ["img_container_2", "img_container"];
    return ids;
}

function setupFullscreenImagePage(){
    var headline = document.getElementById("txt_headline");
    var textfield = document.getElementById("txt_text");
    var image = document.getElementById("info_img");
    var textfield_2 = document.getElementById("txt_text_2");
    var image_2 = document.getElementById("info_img_2");
    var image_container = document.getElementById("img_container");
    var image_2_container = document.getElementById("img_container_2");
    var image_fullscreen = document.getElementById("info_img_fullscreen");
    var image_fullscreen_container = document.getElementById("img_container_fullscreen");
    var logo = document.getElementById("logo_div");

    // hide unused elements
    image_2_container.style.display = 'none';
    image_container.style.display = 'none';
    textfield.style.display = 'none';
    textfield_2.style.display = 'none';
    headline.style.display = 'none';
    logo.style.display = 'none';

    // show page elements
    image_fullscreen_container.style.display = 'inline';

    ids = new Array()
    ids['txt'] = "txt_text";
    ids['img'] = "info_img_fullscreen";
    ids['img_container'] = "img_container_fullscreen";
    return ids;
}

function pageDuration(pageTxts){
    var duration = 0;
    for(var i = 0; i < pageTxts.length; i++){
        txt = pageTxts[i];
        var numWords = txt.split(' ').length;
        duration += (numWords / 1.5) * 1000;
    }
    return duration;
}

function changeImage(images, index, duration, targetID, targetContainer, style, imageMode){
    if(!ticker_moving || tickerOffScreen()){
        if(style == 2){
            var image1 = document.getElementById(targetID[0]);
            var image1Container = document.getElementById(targetContainer[0]);
            var image2 = document.getElementById(targetID[1]);
            var image2Container = document.getElementById(targetContainer[1]);
            var targetIndex = index * 2;
            if(targetIndex < images.length-1){
                var img1 = images[targetIndex];
                var img2 = images[targetIndex+1];
                index++;

                image1.src = img1;
                image2.src = img2;

                image1.onload = function(e){
                    sizeImage(targetID[0], targetContainer[0], imageMode);
                }

                image2.onload = function(e){
                    sizeImage(targetID[1], targetContainer[1], imageMode);
                }

                // only set timeout if two more images are left to show
                var newTargetIndex = index * 2;
                if(newTargetIndex < images.length-1){
                    setTimeout(function(){
                        changeImage(images, index, duration, targetID, targetContainer, style, imageMode)
                    }, duration);
                }
            }
        }else{
            if(index < images.length){
                var img = images[index];
                var image = document.getElementById(targetID);
                index++;

                image.src = img;

                image.onload = function(e){
                    sizeImage(targetID, targetContainer, imageMode);
                }

                // only set timeout for image change if further images to show
                if(index < images.length){
                    setTimeout(function(){
                        changeImage(images, index, duration, targetID, targetContainer, style, imageMode);
                    }, duration);
                }
            }
        }
    } else {
        var delay = timeUntilTickerOffScreen();
        duration_offset += delay/4;
        // wait time to let ticker go off screen before changing images
        setTimeout(function(){
            changeImage(images, index, duration, targetID, targetContainer, style, imageMode);
        }, delay/4);
    }
}

function sizeImage(targetID, targetContainer, mode){
    // default image sizing mode is fit if not set
    //mode = mode || 'image_crop';
    mode = 'image_crop';
    var image = document.getElementById(targetID);
    // reset margin and size properties
    image.style.marginTop = '0px';
    image.style.marginLeft = '0px';
    image.style.height = "100%";
    image.style.width = "auto";

    // get size and ratio of image and container
    var w = $( "#"+String(targetID) ).width();
    var h = $( "#"+String(targetID) ).height();
    var cW = $( "#"+String(targetContainer) ).width();
    var cH = $( "#"+String(targetContainer) ).height();

    var imgRatio = w/h;
    var conRatio = cW/cH;

    if(mode == "image_fit"){
        // fit image in container preserving aspect ratio
        if(imgRatio < conRatio){
            image.style.height = "100%";
            image.style.width = "auto";
        }else{
            image.style.width = "100%";
            image.style.height = "auto";
            // center image vertically in container
            h = $( "#"+String(targetID) ).height();
            image.style.height = h + 'px';
            var offset = (cH - h) / 2;
            image.style.marginTop = offset + 'px';
        }
    }else{ // image crop
        // fill image container cropping and centering image preserving aspect ratio
        if(imgRatio < conRatio){
            image.style.width = "100%";
            image.style.height = "auto";
            // center image vertically in container
            h = $( "#"+String(targetID) ).height();
            image.style.height = h + 'px';
            var offset = (h - cH) / 2;
            image.style.marginTop = '-' + offset + 'px';
        }else{
            image.style.height = "100%";
            image.style.width = "auto";
        }
    }
}

function changeText(texts, index, duration, targetID){
    if(index < texts.length){
        var txt = texts[index];
        var txt_div = document.getElementById(targetID);
        txt_div.innerHTML = txt;
        index++;

        // auto size text to avoid overflow
        initTextSize()
        resize()

        // only set timeout for text change if further texts to show
        if(index < texts.length){
            setTimeout(function(){
                changeText(texts, index, duration, targetID);
            }, duration);
        }
    }
}

function initTextSize(){
    elements = $('.text');
    elements.push($('.text_2'));
    if (elements.length < 0) {
        return;
    }
    _results = [];
    for (_i = 0, _len = elements.length; _i < _len; _i++) {
        el = elements[_i];
        $(el).css("font-size", "60px")
    }

    elements = $('.headline');
    if (elements.length < 0) {
        return;
    }
    _results = [];
    for (_i = 0, _len = elements.length; _i < _len; _i++) {
        el = elements[_i];
        $(el).css("font-size", "4em")
    }
}

function resize(){
    var elements;
    elements = $('.headline');
    resizeElements(elements);
    elements = $('.text');
    resizeElements(elements);
    elements = $('.text_2');
    resizeElements(elements);
    return true;
}

function resizeElements(elements){
    var el, _i, _len, _results;
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
    var data = httpGet('infoscreen.php?T=PAGES');
    pageData = JSON.parse(data)
    pages = pageData['page_headlines'].split(";");
    numPages = pages.length;
    for(var i = 0; i < pageData['page_images'].length; i++){
        var curList = pageData['page_images'][i];
        var curImgs = curList.split(";");
        var pageImgs = new Array();
        for(var j = 0; j < curImgs.length; j++){
            // preload images
            var cImg = new Image();
            cImg.src = curImgs[j];
            pageImgs[j] = cImg.src;
        }
        cachedImgs[i] = pageImgs;
    }
}

function updateBackground(customBG){
    if(customBG){
        var pageNrStr = "";
        var curNum = pageNr + 1;
        if(curNum < 10){
            pageNrStr = "000" + String(curNum);
        }else if(curNum < 100){
            pageNrStr = "00" + String(curNum);
        }else if(curNum < 1000){
            pageNrStr = "0" + String(curNum);
        }else{
            pageNrStr = String(curNum);
        }
        background = SITE_ROOT + 'pages/page' + String(pageNrStr) + '/custom_bg.jpg'
    }else{
        background = SITE_ROOT + 'bg.jpg'
    }
    var bgImg = document.getElementById("bg_img");
    bgImg.src = background;    
}

function updateTicker(ticker_txt, ticker_mov, enable_ticker){
    ticker_enabled = enable_ticker
    if(enable_ticker){
        document.getElementById("ticker").style.display = 'inline'
        document.getElementById("logo_div").style.display = 'inline'
        if(ticker_txt != null && ticker_text != ticker_txt){
            // message changed
            ticker_text = ticker_txt;
            var ticker = document.getElementById("ticker_txt");
            ticker.innerHTML = ticker_text;
        }

        if(ticker_mov != null){
            var move = (!ticker_moving && ticker_mov);
            ticker_moving = ticker_mov;
            if(move){
                // reset ticker position and trigger movement
                tWidth = $("#ticker").width()
                tickerPos = tWidth;
                moveText();
            }
        }
    }else{
        document.getElementById("logo_div").style.display = 'none'
        document.getElementById("ticker").style.display = 'none'
    }
}

function moveText(){
    // document.getElementById("ticker_txt").style.visibility="visible";
    var ticker = document.getElementById("ticker_txt");
    ticker.innerHTML = ticker_text;
    var tickerStyle = ticker.style;

    tickerW = $( "#ticker_txt").width();

    if(tickerPos > (tickerW * -1) - 10){
        tickerPos-=1;
    } else {
        // reset ticker position to right
        tWidth = $("#ticker").width()
        tickerPos = tWidth;
    }
    tickerStyle.left = tickerPos+'px';
    tickerLoop();
}

function tickerOffScreen(){
    var tickerW = $( "#ticker_txt").width();
    return (tickerPos < (tickerW * -1));
}

function timeUntilTickerOffScreen(){
    var tickerW = $( "#ticker_txt").width();
    var diff = tickerPos + tickerW;
    var time = diff * TICKER_INTERVAL; // interval time for each pixel
    return time;
}

function moveTextOutOfScreen(){
    // document.getElementById("ticker_txt").style.visibility="visible";
    var ticker = document.getElementById("ticker_txt");
    ticker.innerHTML = ticker_text;
    var tickerStyle = ticker.style;

    tickerW = $( "#ticker_txt").width();

    if(tickerPos > (tickerW * -1)){
        tickerPos-=1;
    } else {
        // reset ticker position to right
        tWidth = $("#ticker").width()
        tickerPos = tWidth;
    }
    tickerStyle.left = tickerPos+'px';
}

function tickerLoop() {
    if(ticker_moving){
        tickerInt = setTimeout("moveText()",TICKER_INTERVAL);
    }else{
        // stop ticker
        tickerPos = 20;
        document.getElementById("ticker_txt").style.left = tickerPos+'px';
    }

}
