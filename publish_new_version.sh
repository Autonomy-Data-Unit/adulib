
nbdev_export
nbdev_clean

if ! git diff-index --quiet HEAD --; then
    echo "You have uncommitted changes. Please commit or stash them before proceeding."
    exit 1
fi

if ! git fetch origin; then
    echo "Failed to fetch from origin. Please check your network connection."
    exit 1
fi

if ! git diff --quiet origin/main; then
    echo "Your local repository is not in sync with the origin. Please pull the latest changes before proceeding."
    exit 1
fi

git push

read -p "Do you want to update the changelog? (y/n): " update_changelog
if [[ $update_changelog == [yY] ]]; then
    git cliff -o CHANGELOG.md
    git add CHANGELOG.md
    git commit -m "Update CHANGELOG.md"
    git push
fi

latest_version=$(python -c "import importlib.metadata; print(importlib.metadata.version('adulib'))")
echo "The latest version of adulib is $latest_version"

read -p "Enter the new version: " version
git tag -a v$version -m "Release v$version"
git push --tags

read -p "Are you sure you want to push the new version? (y/n): " confirm
if [[ $confirm != [yY] ]]; then
    echo "Aborting the push of the new version."
    exit 1
fi

uv build

if [[ $1 == "--test" ]]; then
    twine upload -r testpypi dist/*
else
    twine upload -r pypi dist/*
fi