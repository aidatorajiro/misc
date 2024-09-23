Packet capturing is a perfect solution for archive websites with TCP cryptographic proof! Just run these commands, and timestamp both the `keylog` file and the `capture.pcapng` file together using tools like OpenTimestamp. To not expose your IP address, access the website via VPN is recommended.

via VPN
```bash
SSLKEYLOGFILE="$PWD/keylog" google-chrome-stable --incognito &
tshark -w capture.pcapng -i tun0
tshark -r capture.pcapng -q -z io,phs,tls -o "tls.keylog_file:$PWD/keylog" -q
tshark -r capture.pcapng -q -o tls.keylog_file:keylog --export-objects http,dest
```

via wifi
```bash
SSLKEYLOGFILE="$PWD/keylog" google-chrome-stable --incognito &
tshark -w capture.pcapng -i wlo1
tshark -r capture.pcapng -q -z io,phs,tls -o "tls.keylog_file:$PWD/keylog" -q
tshark -r capture.pcapng -q -o tls.keylog_file:keylog --export-objects http,dest
```

Please note that once `previous packet not captured` error occurs, Wireshark cannot parse http2 packets afterwards (for http/1.1 over TLS there's no such problem i guess?). Therefore, if that error happens, you should restart the browser and access to the website again. The problem is that CUI tshark cannot tell you about TCP errors. Only the GUI Wireshark can (just set the filter to `tcp.analysis.lost_segment`). so yeah packet capturing is difficult.


