ACCCODE="SELECT ZICCLOUDSYNCINGOBJECT.ZIDENTIFIER FROM ZICCLOUDSYNCINGOBJECT WHERE ZICCLOUDSYNCINGOBJECT.ZNAME IS NOT NULL;"

cd $1/
unzip group.com.apple.notes.zip

cd group.com.apple.notes
ACCID=`echo | sqlite3 NoteStore.sqlite -cmd "$ACCCODE"`
echo $ACCID

mkdir -p ./Accounts/$ACCID/
cd ./Accounts/$ACCID
ln -s ../../Media ./Media

cd ../../../../apple_cloud_notes_parser
bundle exec ruby notes_cloud_ripper.rb -m ../$1/group.com.apple.notes
