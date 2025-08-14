nbl export
nbl clean

sh ./update_docs.sh

git push

latest_version=$(git describe --tags $(git rev-list --tags --max-count=1))
echo "The latest published version is $latest_version"

version=$(sed -n 's/^version = "\([^"]*\)"/\1/p' pyproject.toml)
echo "The current version in pyproject.toml is $version"

read -p "What new version do you want to publish? " new_version
version=$new_version

sed -i '' "s/^version = \".*\"/version = \"$version\"/" pyproject.toml

git add pyproject.toml
git commit -m "chore: Update version in pyproject.toml"
git push

git tag -a v$version -m "Release v$version"
git push --tags

read -p "Do you want to update the changelog? (y/n): " update_changelog
if [[ -z $update_changelog || $update_changelog == [yY] ]]; then
    git cliff -o CHANGELOG.md
    git add CHANGELOG.md
    git commit -m "chore: Update CHANGELOG.md"
    git push
fi

uv build

if [[ $1 == "--test" ]]; then
    twine upload -r testpypi dist/*
else
    twine upload -r pypi dist/*
fi