#!/usr/bin/env sh
set -e

ZIP_NAME="digital-products-ecommerce.zip"

# Exclude common build artifacts and node_modules
zip -r "$ZIP_NAME" . \
  -x "*.git*" \
  -x "backend/static/*" \
  -x "frontend/node_modules/*" \
  -x "*.venv/*" \
  -x "*.pytest_cache/*" \
  -x "__pycache__/*"

echo "Created $ZIP_NAME"