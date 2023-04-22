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

git clone ${repoUrl} ${specificRepoDir}

resultName=${companyName}_${provider}_${repoName}.txt

# Seems to only work locally(by cloning repos)
gitleaks detect -v --config ./gitleaks.toml --source $specificRepoDir > $resultName
# gitleaks detect -v --config "/Users/kenertkaru/Documents/personal-projects/Wabadus-Hackathon/src/git/gitleaks.toml" > $resultName
# gitleaks detect -v "$repoUrl" --config "/Users/kenertkaru/Documents/personal-projects/Wabadus-Hackathon/src/git/gitleaks.toml" > $resultName

# only add to results, if the file has contents
if test -s "./$resultName"; then
    mv $resultName $resultsDirectory
else
    rm $resultName 
fi


rm -rf "$specificRepoDir"


