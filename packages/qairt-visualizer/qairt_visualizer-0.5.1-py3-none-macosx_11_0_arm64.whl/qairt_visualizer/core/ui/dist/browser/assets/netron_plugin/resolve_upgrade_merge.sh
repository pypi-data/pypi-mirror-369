#!/bin/bash
for file in $(git diff --name-only --diff-filter=U); do
  if grep -q "QAIRT Netron" "$file" || grep -q "QDS" "$file" || [[ "$file" == qais/* ]]; then
    echo "Skipping $file"
  else
    git checkout --theirs "$file"
    git add "$file"
    echo "Accepted all incoming changes for $file"
  fi
done
