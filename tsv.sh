# installation:
# pip3 install opentimestamps-client
# brew install openssl    (plz set $PATH according to the instruction)

# ut=`date -j -f "%Y-%m-%d %H:%M:%S" "$2" +%s`

# ots generation
ots v $1.ots
ots i $1.ots

# RFC 3161
openssl ts -verify -CApath capath -in $1.freetsa.tsr -queryfile $1.tsq
openssl ts -verify -CApath capath -in $1.apple.tsr -queryfile $1.tsq
openssl ts -verify -CApath capath -in $1.sslcom.tsr -queryfile $1.tsq
openssl ts -verify -CApath capath -in $1.digicert.tsr -queryfile $1.tsq