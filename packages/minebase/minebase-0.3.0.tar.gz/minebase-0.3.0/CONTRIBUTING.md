# Contributing Guidelines

The contributing guidelines and instructions on setting up this project mostly match those of mcproto. In the interest
of not having to rewrite the same instructions again, please follow the [mcproto
documentation](https://py-mine.github.io/mcproto/latest/contributing/guides/) for contributing guidelines.

## Extra things

Even though most of our workflows match those in mcproto, there are some differences. These will be explained here.

### Git Submodules (cloning the repo & updating)

When you'll be cloning this repository, you will want to use the `--recursive` flag, as we include the
[minecraft-data](https://github.com/PrismarineJS/minecraft-data) repository as a git submodule. This means when cloning
the repo, you'll want to use the following command:

```bash
git clone --recursive https://github.com/py-mine/minebase
```

If you already have a cloned repo without the `--recursive` flag, you can use:

```bash
git submodule update --init --recursive
```

#### Keeping the submodule up to date

We will often update the minecraft-data submodule to match the latest release, when we do this, you should also update
your local copy of the submodule, as git won't do this automatically for you on `git pull`. To do this, you can use:

```bash
git submodule update --init --recursive
```

#### Updating the submodule

If you find that the submodule is out of date compared to the upstream (there was a new release of minecraft-data), you
can update the submodule and push the update (open a PR). To do this with the following:

```bash
cd minebase/data
git fetch --tags
latest_tag=$(git tag --sort=-v:refname | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' | head -n 1)
git checkout "$latest_tag"
```

Now go back to the main project and commit the submodule change:

```bash
cd ../..
git add minebase/data
# You will also probably want to make a branch here, if you haven't yet
git commit -m "Update submodule to minecraft-data $latest_tag"
git push
```

### Slotscheck

Mcproto uses `slotscheck` tool to validate proper use of slots, we don't use this.
