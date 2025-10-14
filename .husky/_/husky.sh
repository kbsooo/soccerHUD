#!/bin/sh
# Husky placeholder to allow lint-staged execution without installation.
if [ -z "$husky_skip_init" ]; then
  husky_skip_init=1
  if [ "$HUSKY_DEBUG" = "1" ]; then
    set -x
  fi
  export husky_skip_init
fi
