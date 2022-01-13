MYDIR=`pwd`/$1

if [ -d $MYDIR ]; then
    echo "ERROR: path already exists!!"
else
    mkdir -p $MYDIR
    cd /Users/$USER/Library/Containers/
    zip $MYDIR/com.apple.Notes.zip -ry ./com.apple.Notes
    cd /Users/$USER/Library/Group\ Containers/
    zip $MYDIR/group.com.apple.notes.zip -ry ./group.com.apple.notes
fi
