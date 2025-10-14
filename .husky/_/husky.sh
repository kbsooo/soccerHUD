#!/bin/sh
if [ -z "$husky_skip_init" ]; then
  export husky_skip_init=1
  . "$(dirname "$0")/../node_modules/husky/lib/init.sh"
fi
