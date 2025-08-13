set -e

if [ -z "$1" ]; then
    echo "Error: Please provide a new version number (./publish.sh x.y.z)"
    exit 1
fi

NEW_VERSION=$1
PYPROJECT_FILE="pyproject.toml"

echo "Updating version in $PYPROJECT_FILE to $NEW_VERSION..."
sed -i '' -e "s/^version = \"[0-9.]*\"/version = \"$NEW_VERSION\"/" "$PYPROJECT_FILE"

echo "Cleaning previous build..."
rm -rf dist/*

echo "Building the package..."
python -m build

echo "Publishing the package to PyPI..."
twine upload dist/*

echo "Successfully published version $NEW_VERSION!"