#!/bin/bash

TARGET="otp"
chmod +x "$TARGET"
DEST_DIR="$HOME/.local/bin"
PLATFORM="$(uname -s)"

# Check if the target script exists
if [ ! -f "$TARGET" ]; then
  echo "Error: $TARGET not found in the current directory."
  exit 1
fi

# Check if .local/bin exists, create if not
if [ ! -d "$DEST_DIR" ]; then
  mkdir -p "$DEST_DIR"
fi

# Make the script executable
chmod +x "$TARGET"

# Link the script
ln -sf "$(pwd)/$TARGET" "$DEST_DIR/$(basename "$TARGET")"

# Check if the platform is macOS and update PATH in shell config if needed
if [ "$PLATFORM" = "Darwin" ]; then
  SHELL_CONFIG="$HOME/.zshrc"
else
  SHELL_CONFIG="$HOME/.bashrc"
fi

if [[ ":$PATH:" != *":$DEST_DIR:"* ]]; then
  echo "export PATH=\"\$PATH:$DEST_DIR\"" >>"$SHELL_CONFIG"
  echo "Added $DEST_DIR to PATH in $SHELL_CONFIG. Restart your shell or run 'source $SHELL_CONFIG'."
else
  echo "$DEST_DIR is already in your PATH."
fi

echo "Successfully linked $TARGET to $DEST_DIR/"
