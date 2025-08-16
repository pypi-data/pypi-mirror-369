#!/bin/bash

COPYRIGHT="# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com"
LICENSE_NOTICE="# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/."

HEADER="$COPYRIGHT\n$LICENSE_NOTICE"

# File extensions you want to apply the header to
EXTENSIONS=("py")

for ext in "${EXTENSIONS[@]}"; do
  find . \
    -path ./node_modules -prune -o \
    -path ./dist -prune -o \
    -path ./build -prune -o \
    -path ./.venv -prune -o \
    -path ./test -prune -o \
    -path ./.idea -prune -o \
    -type f -name "*.${ext}" -typer.echo | while read file; do
      if ! grep -q "Mozilla Public License" "$file"; then
        echo "Adding license to $file"
        (echo -e "$HEADER"; echo ""; cat "$file") > "$file.tmp" && mv "$file.tmp" "$file"
      fi
  done
done
