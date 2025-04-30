nbl export
nbl clean

git push

latest_version=$(git describe --tags $(git rev-list --tags --max-count=1))
echo "The latest published version of nblite is $latest_version"

version=$(sed -n 's/^version = "\([^"]*\)"/\1/p' pyproject.toml)
echo "The current version in pyproject.toml is $version"

read -p "Are you sure you want to push the new version ($version)? (y/n): " confirm
if [[ $confirm != [yY] ]]; then
    echo "Aborting the push of the new version."
    exit 1
fi

git tag -a v$version -m "Release v$version"
git push --tags

read -p "Do you want to update the changelog? (y/n): " update_changelog
if [[ $update_changelog == [yY] ]]; then
    git cliff -o CHANGELOG.md
    # git add CHANGELOG.md
    # git commit -m "Update CHANGELOG.md"
    # git push
fi

uv build

if [[ $1 == "--test" ]]; then
    twine upload -r testpypi dist/*
else
    twine upload -r pypi dist/*
fi