# toolforge jobs framework -- command line interface

This is the source code of command line interface part of the Toolforge Jobs Framework.

The TJF creates an abstraction layer over kubernetes Jobs, CronJobs and Deployments to allow
operating a Kubernetes installation as if it were a Grid (like GridEngine).

This was created for [Wikimedia Toolforge](https://toolforge.org).

## Usage

The help message:

```console
$ toolforge jobs --help
usage: toolforge jobs [-h] [--debug] {images,run,show,logs,list,delete,flush,load,restart,quota} ...

Toolforge Jobs Framework, command line interface

positional arguments:
  {images,run,show,logs,list,delete,flush,load,restart,quota}
                        possible operations (pass -h to know usage of each)
    images              list information on available container image types for Toolforge jobs
    run                 run a new job of your own in Toolforge
    show                show details of a job of your own in Toolforge
    logs                show output from a running job
    list                list all running jobs of your own in Toolforge
    delete              delete a running job of your own in Toolforge
    flush               delete all running jobs of your own in Toolforge
    load                flush all jobs and load a YAML file with job definitions and run them
    restart             restarts a running job
    quota               display quota information

options:
  -h, --help            show this help message and exit
  --debug               activate debug mode
```

More information at [Wikitech](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Running_jobs) and in the man page.

## Installation

We currently deploy this code into Toolforge using a debian package that is built from this very
source tree.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Development

You need a local kubernetes cluster with a fake Toolforge installed to it. There are several ways
of doing that. The author of this README recommends the lima-kilo project.

Follow docs at https://gitlab.wikimedia.org/cloud/toolforge/lima-kilo

### Testing with tox on debian

Clone the repo (instructions here https://gitlab.wikimedia.org/repos/cloud/toolforge/jobs-cli).

Install tox (this is the only debian-specific part):
```
~:$ apt install tox
```

Move to the directory where you cloned the repo, and run tox:
```
/path/to/repo/jobs-cli:$ tox
```

That will run the tests and create a virtualenv that you can use to manually debug anything you need, to enter it:
```
/path/to/repo/jobs-cli:$ source .tox/py3-tests/bin/activate
```

## Building the debian packages

The process will be:
* Create new branch
* Bump the version
* Build and deploy the package
* Upload the package to the toolforge repositories
* Merge PR and Create a release

Let's get started!

### Create new branch
To get started, create a new branch from main:
```
~:$ git checkout -b <new-branch-name>
```

### Bump the version
#### Update the changelog and pyproject.toml
1. To do so, you can run the script:
    ```
    ~:$ utils/bump_version.sh
    ```

    That will:

    * create an entry in `debian/changelog` from the git log since the last `debian/*` tag
    * bump the version in `pyproject.toml` too
    * create the required commit and tag.

2. Once this is done, you should push the new commit and tag for review:
    ```
    git push -u origin <new-branch-name>
    git push origin debian/<new_version>
    ```
    You can find out the value of the newly created tag by looking at your terminal output or running `git tags --list`

#### Create a patch and get it reviewed

On gitlab you should create a patch based on the above PR, then Review the `changelog` and the `pyproject.toml` changes to make sure it's what you want (it uses your name, email, etc.), and ask
for reviews.

### Build and deploy the package
#### Build and deploy with cookbook (Recommended)

> **NOTE**: Currently the PR created above needs to be open before you can use this cookbook. If you choose to use the more complicated alternatives below, keeping the PR open is not mandatory.

1. Building and deploying the package has been greatly simplified using the cookbook. To do this simply run:
    ```
    ~:$ cookbook wmcs.toolforge.component.deploy --cluster-name toolsbeta --component jobs-cli --git-branch bump_version
    ```
    The above builds the package, uploads it to the toolsbeta package repository, and installs it on all the toolsbeta bastions. To do the same for tools use `--cluster-name tools`.

    See https://wikitech.wikimedia.org/wiki/Spicerack/Cookbooks for details on cookbooks.

#### Build and deploy with containers
> **NOTE**: This will not allow you to sign your package, so if you need that try using the manual process.

1. You can build the package with:
    ```
    ~:$ utils/build_deb.sh
    ```
    The first time it might take a bit more time as it will build the core image to build packages, downloading many
    dependencies. The next run it will not need to download all those dependencies, so it will be way faster.

    > **NOTE**: If it failed when installing packages, try passing `--no-cache` to force rebuilding the cached layers.

2. After building, you'll need to upload the built package to toolforge package repository. See [`Uploading to the toolforge repository`](#uploading-to-the-toolforge-repository) for more details.

3. Once you are done uploading, you also need to login to the various bastions on both tools and toolsbeta to manually install the package there.
    For example to install on toolsbeta bastion 6:
    ```
    ~:$ ssh toolsbeta-bastion-6.toolsbeta.eqiad1.wikimedia.cloud
    ~:$ sudo apt-get update && sudo apt-get install toolforge-jobs-cli
    ```
    It is important to check how many bastions we have for both tools and toolsbeta and do this for all. You can ask the toolforge team if you don't have this information.




#### Build and deploy with wmcs-package-build script
1. Another alternative is using the wmcs-package-build.py script that you can find in
the operations/puppet repo at modules/toolforge/files

    ```
    $ ./wmcs-package-build.py --git-repo https://gitlab.wikimedia.org/repos/cloud/toolforge/jobs-cli -a buster-toolsbeta -a bullseye-toolsbeta --git-branch main --build-dist=bullseye --backports --toolforge-repo=tools
    ```

    The script will SSH into a build server, build the package there, and publish it
    to two repos: `buster-toolsbeta` and `bullseye-tooslbeta`.

    The additional params `--backports, --toolforge-repo=tools
    --build-dist=bullseye` are necessary because the build requires Poetry and other
    build tools not available in the buster repos.

2. If that command is successful, you should then copy the package from the
"toolsbeta" to the "tools" distribution. See [`Uploading to the toolforge repository`](#uploading-to-the-toolforge-repository) for more details.

3. Once you are done uploading, you also need to login to the various bastions on both tools and toolsbeta to manually install the package there.
    For example to install on toolsbeta bastion 6:
    ```
    ~:$ ssh toolsbeta-bastion-6.toolsbeta.eqiad1.wikimedia.cloud
    ~:$ sudo apt-get update && sudo apt-get install toolforge-jobs-cli
    ```
    It is important to check how many bastions we have for both tools and toolsbeta and do this for all. You can ask the toolforge team if you don't have this information.

Additional documentation on the wmcs-package-build script is available at
https://wikitech.wikimedia.org/wiki/Portal:Toolforge/Admin/Packaging#wmcs-package-build

#### Manual process (only on debian)
1. For this you'll need debuild installed:
    ```
    ~:$ sudo apt install debuild
    ```

    Install the build dependencies, this requires devscripts and equivs:
    ```
    ~:$ sudo apt install devscripts equivs
    ...
    /path/to/repo/jobs-cli:$ sudo mk-build-deps --install debian/control
    ```

    Or just manually check the `debian/control` file `Build-Dependencies` and install them manually.

    > **Note**: that it will build a debian package right there, and install it, you can remove it to clean up the dependencies any time.


2. Now for the actuall build:
    ```
    /path/to/repo/jobs-cli:$ debuild -uc -us
    ```

    That will end up creating an unsigned package under `../toolforge-jobs-cli.*.deb`.
    If you want to sign it, you will have to do something like:
    ```
    /path/to/repo/jobs-cli:$ debuild -kmy@key.org
    ```

### Uploading to the toolforge repository

If you built the package using any of the manual methods, you can uploade it following:
https://wikitech.wikimedia.org/wiki/Portal:Toolforge/Admin/Packaging#Uploading_a_package

### Merge PR and Create a release
Depending on the deployment method you chose, the PR might still be open. If that's the case remember to merge the PR and create a new Gitlab release.

## License
[GPLv3](https://choosealicense.com/licenses/gpl-3.0/)
