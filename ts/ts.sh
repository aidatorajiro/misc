# installation:
# pip3 install opentimestamps-client
# brew install openssl    (plz set $PATH according to the instruction)

# ots generation
ots s $1

# RFC 3161
openssl ts -query -cert -data $1 -out $1.tsq
curl -H 'Content-Type: application/timestamp-query' --data-binary @$1.tsq -o $1.freetsa.tsr https://freetsa.org/tsr
curl -H 'Content-Type: application/timestamp-query' --data-binary @$1.tsq -o $1.apple.tsr http://timestamp.apple.com/ts01
curl -H 'Content-Type: application/timestamp-query' --data-binary @$1.tsq -o $1.sslcom.tsr http://ts.ssl.com
curl -H 'Content-Type: application/timestamp-query' --data-binary @$1.tsq -o $1.digicert.tsr http://timestamp.digicert.com
