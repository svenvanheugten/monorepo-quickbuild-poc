# mrpbuild-poc

This is a proof-of-concept for a (near-)zero-configuration Docker-and-.NET-aware monorepo build tool. There's currently a lot of sharp edges and strong assumptions about the project structure.

## Installation
Install:

```bash
python3 setup.py install
```

In the root of your repository, create a file called `mrpbuild.yaml` of the following form:

```yaml
imagePrefix: [container registry]/[namespace]/[repository]
```

Next, add the following to your repository's `.gitignore`:

```
image-tag
```

## Building images
Run `mrpbuild` anywhere in the repository. For every project directory containing a `Dockerfile`, it will generate an `image-tag` file containing the tag of the built image.

## Deploying the built images
To actually deploy the projects to a cluster, you'll need to use other tooling that reads these `image-tag` files and updates the resource definitions in the cluster. To make this easier, `mrpbuild` has the command `mrpbuild deploy`, which will run all `deploy.sh`-files found in the repository once the build completes.

## How does it work?
It hashes all dependencies of a project directory by looking at the non-ignored files in that directory (and, for .NET projects, all projects referenced through `ProjectReference`s). That hash will become the image tag and will be written to the `image-tag` file in the same directory.

If an image with that tag already exists (either locally or remotely), it skips the build. Otherwise, it will build the image and push it. The net result will be that any projects that have been built somewhere before (either on your own machine, another machine or in CI/CD) will be skipped, and you'll be provided with a reference to a pre-existing image instead.

## Future ideas
* Speed up builds by building all changed .NET projects in the repository in one go, and then use `dotnet publish --no-build --no-restore` to create the images.
* Tag images differently based on the machine that they were built, and only ever use images that were built either in CI/CD or on your own machine.
