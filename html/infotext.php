<?php
$f = fopen("./txt/info.txt", "r");
// Liest eine Zeile aus der Textdatei und gibt deren Inhalt aus
$text = fgets($f);
echo $text;

?>
