# Repository Size Reduction Instructions

This document explains how to completely remove large files from the Git history to reduce repository size.

## Current Situation

The repository was initially very large (~5.4GB) due to:
- Original dataset: `House_Rent_10M_balanced_40cities.csv` (1.2GB)
- Processed data: `output/enhanced_rental_data_with_external_factors.csv` (4.2GB)

These files have been moved to a temporary location and are no longer needed for the core functionality.

## To Completely Remove Large Files from Git History

If you want to completely remove these files from Git history (which is recommended for a clean repository), follow these steps:

### 1. Remove the files from Git history using filter-branch:

```bash
# From the repository root
cd '/Users/sittminthar/Downloads/Properties/10 Million House Rent Data of 40 cities'

# Remove the large files from Git history
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch House_Rent_10M_balanced_40cities.csv' \
--prune-empty --tag-name-filter cat -- --all

git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch output/enhanced_rental_data_with_external_factors.csv' \
--prune-empty --tag-name-filter cat -- --all
```

### 2. Clean up the refs and garbage collect:

```bash
# Clean up references
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin

# Garbage collect and compress
git reflog expire --expire=now --all
git gc --prune=now

# Double-check the size
git count-objects -vH
```

### 3. Update the .gitignore file:

The .gitignore file has already been updated to prevent these files from being added again:

```
# Data files (too large for Git)
*.csv
!*.csv # Except those tracked by Git LFS

# Large raw data files that should not be in Git
House_Rent_10M_balanced_40cities.csv
output/
data/
dataset/
datasets/
```

### 4. Force push the changes (if working with a remote repository):

⚠️ **Warning**: This will permanently change the Git history. Only do this if you're sure and coordinate with your team.

```bash
git push origin --force --all
git push origin --force --tags
```

## What's Preserved

After removing the large files, the repository still contains:

- All trained model files (`.pkl` files) - these are essential for the API
- All API server code - this is what frontend developers need
- All model serving code
- All documentation
- All evaluation scripts
- All configuration files

## Verification

To verify the repository size reduction:

```bash
du -sh .
```

The repository should now be significantly smaller (under 100MB) while maintaining all functionality.

## Alternative: BFG Repo-Cleaner

For a more efficient alternative to git filter-branch, you can use the BFG Repo-Cleaner tool:

1. Download BFG from https://rtyley.github.io/bfg-repo-cleaner/
2. Create a backup of your repository
3. Run: `java -jar bfg.jar --delete-files House_Rent_10M_balanced_40cities.csv your-repo.git`
4. Run: `java -jar bfg.jar --delete-folders output your-repo.git`
5. Follow the same cleanup steps as above