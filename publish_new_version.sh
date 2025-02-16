nbdev_export
nbdev_clean

git push

read -p "Do you want to update the changelog? (y/n): " update_changelog
if [[ $update_changelog == [yY] ]]; then
    git cliff -o CHANGELOG.md
    git add CHANGELOG.md
    git commit -m "Update CHANGELOG.md"
    git push
fi

latest_version=$(git describe --tags $(git rev-list --tags --max-count=1))
echo "The latest version of adulib is $latest_version"

read -p "Enter the new version: " version

read -p "Are you sure you want to push the new version? (y/n): " confirm
if [[ $confirm != [yY] ]]; then
    echo "Aborting the push of the new version."
    exit 1
fi

git tag -a v$version -m "Release v$version"
git push --tags

uv build

if [[ $1 == "--test" ]]; then
    twine upload -r testpypi dist/*
else
    twine upload -r pypi dist/*
fi