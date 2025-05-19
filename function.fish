# Copy this file to the folder `~/.config/fish/functions`
# and rename it to `qj.fish`
# Don't forget to set the path to `quickjump.py`.
# Then, open a new terminal and issue the command `qj`,
# which will actually call this function.

function qj -d "QuickJump script"
    set -l QJ "$DROPBOX/python/quickjump/quickjump.py"
    if test -z $argv[1]
        $QJ
    else
        cd ($QJ $argv[1])
    end
end
