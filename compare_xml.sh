#!/usr/bin/env bash
# The purpose of this script is to compare the xml files of two directories. It is expected that each xml file exists in both directories.

if ! [[ -d "$1" ]]; then
  echo "The first argument is not a directory: [$1]"
  exit 2
elif ! [[ -d "$2" ]]; then
  echo "The second argument is not a directory: [$2]"
  exit 2
fi

FIRST_DIR="${1%*/}"
SECOND_DIR="${2%*/}"
FILE_STATUS=()
ALL_IDENTICAL=true
for FILE in "$FIRST_DIR"/*.xml
do
  filename="${FILE##*/}"
  if ! [[ -f "$SECOND_DIR"/"$filename" ]]; then
    echo "File $filename exists in $FIRST_DIR but not in $SECOND_DIR"
    exit 2
  fi

  a="$FIRST_DIR/$filename"
  b="$SECOND_DIR/$filename"
  # From Jukka Matilainen's stackexchange answer: https://superuser.com/a/81036
  # Compares the flattened Canonical XML versions of both files. Will let user know whether they are identical or not.
  if ! diff -sw --brief --label "$a" --label "$b" <(xmllint --format "$a") <(xmllint --format "$b"); then
    ALL_IDENTICAL=false
    FILE_STATUS+=("\u2716")
  else
    FILE_STATUS+=("\u2713")
  fi
done

echo -e "${FILE_STATUS[@]}"
if $ALL_IDENTICAL; then
  echo "All files match!"
else
  echo "The files do not all match"
fi
