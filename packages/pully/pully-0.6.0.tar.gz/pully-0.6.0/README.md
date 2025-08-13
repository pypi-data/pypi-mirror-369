# pully

<!-- BADGIE TIME -->

[![pipeline status](https://img.shields.io/gitlab/pipeline-status/saferatday0/sandbox/pully?branch=main)](https://gitlab.com/saferatday0/sandbox/pully/-/commits/main)
[![coverage report](https://img.shields.io/gitlab/pipeline-coverage/saferatday0/sandbox/pully?branch=main)](https://gitlab.com/saferatday0/sandbox/pully/-/commits/main)
[![latest release](https://img.shields.io/gitlab/v/release/saferatday0/sandbox/pully)](https://gitlab.com/saferatday0/sandbox/pully/-/releases)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![cici enabled](https://img.shields.io/badge/%E2%9A%A1_cici-enabled-c0ff33)](https://gitlab.com/saferatday0/cici)
[![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg)](https://github.com/prettier/prettier)

<!-- END BADGIE TIME -->

`pully` is a tool for managing a large number of Git repository checkouts
effectively.

## Why `pully`

`pully` was created to make managing and automating changes to multiple projects
easier. There are two general use cases `pully` is designed to address. First, a
mass action where a a set of projects is cloned and the same action is run on
each project. Second, managing a local workspace for a set of projects.

### Large scale changes

`pully` helps solve problems where you need to make the same
action across multiple projects.

- Update the copyright date in the license file of all projects.
- Update pre-commit versions in all projects.
- Add [`badgie`](https://gitlab.com/saferatday0/badgie) to all projects.

The recommended workflow in this case is to use `pully` to clone workspaces for
mass actions not regular development. Avoid using the same project workspaces
for both regular development and automated actions. Different branches, new
files, and unknown state that are common in work in progress are likely to
interfere with scripted changes.

### Manage local workspaces

`pully` can be used to manage project checkouts for regular development. This
makes onboarding new developers or setting up new environments easier. Common
tasks like pulling the latest changes or pruning remote branches are easy to do.
Beware of scripting changes to multiple projects since the status of each
project may different and cause unexpected results.

### With great power comes great responsibility

We recommend tremendous caution when automating repository changes. Some tips:

- Avoid making and committing changes in a single command

- Ensure that a human is reviewing all changes before committing

- Automate the creation of branches and merge requests as a minimally privileged
  user

We expect some of these workflows to become `pully` features in the future.

## Installation

```sh
python3 -m pip install pully
```

## Quickstart

```sh
# add projects for pully to track
pully add -G saferatday0/library

# clone/fetch all projects
pully

# run commands in checked out projects
pully run touch .gitkeep
```

## Usage

### Initialize a project workspace

Run `pully init` to create a project workspace.

```sh
pully init
```

A `.pully.json` will be created in the current directory that will be used to
track project checkouts.

### Add projects for tracking

Track any project by path:

```sh
pully add -P saferatday0/badgie
```

```console
$ pully add -P saferatday0/badgie
searching for group id by full path saferatday0
searching for project id by full path
found project ids: [70752539]
found pully file at /home/user/projects/.pully.json
adding saferatday0/badgie
```

Track any group by path (subgroups are supported):

```sh
pully add -G saferatday0/library
```

```console
$ pully add -G saferatday0/library
searching for group id by full path saferatday0/library
found group ids: [108399662]
creating new pullyfile at /home/user/projects
adding saferatday0/library/ansible
adding saferatday0/library/asciidoctor
...
adding saferatday0/library/verible
adding saferatday0/library/zola
```

Only newly added projects will be printed.

### Clone/fetch all repositories

Call `pully` to clone or pull the project to your local filesystem:

```sh
pully
```

```console
$ pully
found pully file at /home/user/projects/.pully.json
cloning saferatday0/library/ansible (70326944)
cloning saferatday0/library/asciidoctor (70588591)
...
cloning saferatday0/library/zola (70432884)
cloning saferatday0/badgie (70752539)
```

This is the same as calling `pully pull`:

```sh
pully pull
```

### Running commands on repositories

The `pully run` command can be used to run a command in each repository.

Commands can be run in one of two ways:

- As arguments

- Using `-c`/`--command`

#### As arguments

When run this way, commands are run directly, a shell is not instantiated, and
executable paths are fully resolved:

```sh
pully run git status
```

Command line options can be passed using `--`:

```sh
pully run -- ls -l
```

#### Using `-c`/`--command`

When run this way, a shell is launched, so shell features like indirection and
pipes can be used

```sh
pully run -c 'echo "$(pwd) $(git branch)"'
```

`["/bin/sh", "-euc"]` is the default entrypoint. A different entrypoint can be
specified with `-e`/`--entrypoint`:

```sh
pully run -e '["python3", "-c"]' -c 'fp = open(".gitignore", "a"); fp.write("*.pdf\n");'
```

```console
$ pully run -e '["python3", "-c"]' -c 'fp = open(".gitignore", "a"); fp.write("*.pdf\n");'
found pully file at /home/user/projects/.pully.json
running saferatday0/library/ansible --------------------------------------------
running saferatday0/library/asciidoctor ----------------------------------------
...
$ cd saferatday0/badgie/
$ git diff
diff --git a/.gitignore b/.gitignore
index c84b6c9..e56720a 100644
--- a/.gitignore
+++ b/.gitignore
@@ -15,3 +15,4 @@ build/
 env.sh

 node_modules/
+*.pdf
```

### Cleanup

Reverting changes is easy:

```sh
pully run git checkout .
```

```console
$ pully run git checkout .
found pully file at /home/bweir/blah/.pully.json
running saferatday0/library/ansible --------------------------------------------
Updated 1 path from the index
running saferatday0/library/asciidoctor ----------------------------------------
Updated 1 path from the index
```

### Private repositories

`pully` can clone private repositories by setting the `GITLAB_PRIVATE_TOKEN`
environment variable:

```sh
export GITLAB_PRIVATE_TOKEN="XXXXXX"
pully add -G private/namespace
pully
```

## License

Copyright 2025 UL Research Institutes.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
