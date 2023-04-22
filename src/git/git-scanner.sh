repoUrl=$1
repoName=$2
companyName=$3
provider=$4


mkdir -p "./data"

baseDirectory="./data/$companyName/"
repoDirectory="$baseDirectory/repos"
resultsDirectory="$baseDirectory/results"


mkdir -p "$baseDirectory"
mkdir -p "$repoDirectory"
mkdir -p "$resultsDirectory"


specificRepoDir="$repoDirectory/$repoName"

# delete if already exists
rm -rf "$specificRepoDir"

# really bad solution, we could just pass the repo url to the command instead
# so we wouldnt have to download it :) 
git clone ${repoUrl} ${specificRepoDir}
cd "$specificRepoDir"

resultName=${companyName}_${provider}_${repoName}.txt

gitleaks detect -v > $resultName

# only add to results, if the file has contents
if test -s "./$resultName"; then
    mv $resultName "../../results"
fi

cd ..
rm -rf "$repoName"


