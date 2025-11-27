# Create a worktree for docs branch in a temp folder
random_dir="/tmp/dir_$(openssl rand -hex 8)"
echo "Starting worktree in $random_dir"

# Remove existing worktree for docs branch if it exists
existing_dir=$(git worktree list | awk '/\[docs\]/ {print $1}')
if [ -n "$existing_dir" ]; then
  echo "Removing existing worktree at $existing_dir"
  git worktree remove --force "$existing_dir"
fi

# Create a new worktree for the docs branch
git worktree add "$random_dir" docs

# Generate docs into the temp folder
nbl render-docs -o "$random_dir"

# # Commit and push to docs 
cd "$random_dir"
git add --all
NBL_DISABLE_PC=true git commit -m "Update docs"
git push origin docs

# # Remove the worktree (and delete the temp folder)
cd -
git worktree remove "$random_dir"
rm -rf "$random_dir"