
<html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kiosk</title>
        <link rel="stylesheet" type="text/css" href="css/infoscreen.css">
        <link rel="stylesheet" type="text/css" href="css/fonts.css">
        <script type="text/javascript" src="js/infoscreen.js" ></script>
        <script type="text/javascript" src="js/jquery-2.1.1.min.js"></script>
    </head>

    <body>
        <div id="main">
            <img id="bg_img" src="bg.jpg" />

            <!-- HEADLINE of page -->
            <div class="headline" id="txt_headline"></div>

            <!-- START OF CONTENT OF PAGE -->
            <div class="content_wrapper">

                <!-- CONTENT TEXT of page -->
                <div class="text" id="txt_text"></div>

                <!-- IMAGE
                <div class="img_div">
                    <img id="info_img"/>
                </div>

                -->

                <img class="img_div" id="info_img"/>

            </div>
            <!-- LOGO of customer -->
            <div id="logo_div">
                <img id="logo" src="logo.png" />
            </div>
        </div>

        <?php
            $name = (isset($_REQUEST['NAME']))? $_REQUEST['NAME']:'NA';
            $txts = (isset($_REQUEST['TXTS']))? $_REQUEST['TXTS']:'';
            $img = (isset($_REQUEST['IMG']))? $_REQUEST['IMG']:0;
        ?>

        <input type="hidden" name="hl_hidden" id="headline_hidden" value="<?php echo $name ?>" >
        <input type="hidden" name="info_hidden" id="infotexts_hidden" value="<?php echo $txts ?>" >
        <input type="hidden" name="img_hidden" id="image_hidden" value="<?php echo $img ?>" >

        <script>
            setTimeout('load()', 100);
        </script>

    </body>
</html>
