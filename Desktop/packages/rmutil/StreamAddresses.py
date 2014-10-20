# -*- coding: utf-8 -*-
streams = (
    ("Hitradio Ö3", "http://mp3stream7.apasf.apa.at:8000/;stream.nsv"),
    ("FM4", "http://mp3stream1.apasf.apa.at:8000/;stream.nsv"),
    ("Radio Arabella", "http://stream10.arabella-at.vss.kapper.net:8000/listen.pls"),
    ("Radio Wien", "http://mp3stream2.apasf.apa.at:8000/;stream.nsv"),
    ("Radio Niederösterreich", "http://mp3stream8.apasf.apa.at:8000/;stream.nsv"),
    ("Radio Oberösterreich", "http://orfradio.liwest.at/liveHQ.m3u"),
    ("Radio Salzburg", "http://194.232.200.147:8000/listen.pls"),
    ("Radio Tirol", "http://mp3stream10.apasf.apa.at:8000/;stream.nsv"),
    ("Radio Vorarlberg", "http://194.232.200.149:8000/listen.pls"),
    ("Radio Kärnten", "http://194.232.200.145:8000/listen.pls"),
    ("Radio Steiermark", "http://mp3stream9.apasf.apa.at:8000/;stream.nsv"),
    ("Radio Burgenland", "http://194.232.200.146:8000/listen.pls"),
    ("Radio Ö1", "http://mp3stream3.apasf.apa.at:8000/;stream.nsv"),
    ("Radio 88.6", "http://ber.radiostream.de:36889/listen.pls"),
    ("Kronehit", "http://onair-ha1.krone.at/kronehit-hd.mp3.m3u"),
    ("Antenne Bayern", "http://www.antenne.de/webradio/antenne-aac.pls"),
    ("Rockantenne Bayern", "http://www.rockantenne.de/webradio/rockantenne.m3u"),
    ("Antenne Bayern Oldies but Goldies", "http://www.antenne.de/webradio/channels/oldies-but-goldies.aac.pls"),
    ("Antenne Bayern Schlager", "http://www.antenne.de/webradio/channels/das-schlager-karussell.aac.pls"),
    ("Antenne Bayern 80er Kult Hits", "http://www.antenne.de/webradio/channels/80er-kulthits.aac.pls")
)

def GetStreamNames():
    names = []
    for stream in streams:
        names.append(stream[0].decode('utf-8'))
    return names

def GetStreamAddresses():
    addr = []
    for stream in streams:
        addr.append(stream[1])
    return addr

def GetAddrForStream(index):
    return streams[index][1]

def GetNameForAddr(addr):
    for stream in streams:
        if stream[1] == addr:
            return stream[0].decode('utf-8')
    return ""
