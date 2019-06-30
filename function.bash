# Copy the function below to your bash settings file, e.g.
# add it to the end of `~/.bashrc`.
# Don't forget to set the path to `quickjump.py`.
# Then, open a new terminal and issue the command `qj`,
# which will actually call this function.

qj () {
  QJ="$HOME/Dropbox/python/quickjump/quickjump.py"
  if [[ -z "$1" ]]
  then
    $QJ
  else
    cd "`$QJ $1`"
  fi
}
