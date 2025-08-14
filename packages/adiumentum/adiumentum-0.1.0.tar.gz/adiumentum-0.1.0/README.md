# adiumentum

Running this project requires `copier`, `git`, `uv`, and `flake`. Install `nix` and
install the others by running `nix-shell -p uv python3 git`. You can now copy the project and run the toy CLI provided out-of-the-box:

```sh
copier copy --trust \
    /home/isaac/repos/dev-envs/python-uv-nix /tmp/hello-world \
    --data-file /home/isaac/repos/dev-envs/python-uv-nix/example-data-uv.yml

nix run /tmp/hello-world
```

You can also enter a development environment with all dependencies installed:

```sh
nix develop
```

Once in this dev shell, you have a number of development utils you can try out (via just):

```sh
✔just
✔just format
✔just check
✔just fix
✔just typecheck
✔just lint
✔just deal
✔just vulture
✔just pydeps-full
✔just pydeps
✔just pydeps-simple
✔just view-deps
✔just snakefood
✔just deply
✔just bandit
✔just bandit-html
✔just bandit-view
✔just pyflame
✔just flamegraph
✔just perf-flamegraph
✔just check-structure
✔just check-imports
✔just smoke
✔just unit
✔just test
✔just test-cov
✔just docs
✔just scalene
✔just view-cov
✔just view-docs
✔just view-flamegraphs
✔just sbom

lefthook validate
lefthook run all
```

## Roadmap

00. ✔ Sync package lists in uv.nix.jinja and README.md

01. ✔ Parametrize each package for copier and update copier.yml

02. ✔ Clean up copier.yml and example-data.yml

03. ✔ Get impure environment working -> draw from buildFHSUserEnv approach in consilium and other projects

04. ✔ Write working version of scripts and test them on datethyme

05. ✔ create reference project (revised from datethyme)

06. ✔ use copier to re-create it (make a datethyme answers file)

08. ✔ find good CLI tools for diffing an entire folder

09. ✔ iteratively modify template until copier perfectly re-creates the reference project

10. ✔ package mdformat with mdformat-mkdocs (via nix)

11. ✔ remove super-linter, but look over it and steal any good ideas

12. ✔ add [commitizen](https://github.com/commitizen-tools/commitizen) and [commitmsgfmt](https://gitlab.com/mkjeldsen/commitmsgfmt) ✔

13. ✔ Modify nix to support any python version via [nixpkgs-python](https://github.com/cachix/nixpkgs-python) and [tox](https://tox.wiki/en/4.27.0/index.html)

14. ✔ Read through [jinja2-ansible-filters](https://gitlab.com/dreamer-labs/libraries/)

15. Go through https://www.youtube.com/results?search_query=nix+and+python and any relevant NixCon talks

16. ✔ restructure nix code

17. ✔ add poetry support (selectable via copier)

18. re-make datethyme package using template, iteratively polishing the template

19. add copier switch to include a CLI or not

### Later

Note: first get working the way it is for datathyme.

0. [conventional-changelog](https://github.com/conventional-changelog/conventional-changelog)

1. Package all docs packages via nix, since they run independently of the other Python packages.

2. Do the same for testing dependencies, if possible.

3. Add different types of git hooks

- Client-Side Hooks

  - **Pre-commit hooks** run before a commit is created and are ideal for code quality checks. They're perfect for running linters, formatters, static analysis tools, or tests to catch issues before they enter the repository. If the hook exits with a non-zero status, the commit is aborted

  - **Prepare-commit-msg hooks** execute after the default commit message is created but before the editor opens. These work well for automatically adding ticket numbers, branch names, or standardized formatting to commit messages based on branch patterns or other context

  - **Commit-msg hooks** run after you've written your commit message and are excellent for enforcing commit message conventions. They can validate that messages follow specific formats, contain required information like issue references, or meet length requirements

  - **Post-commit hooks** trigger after a commit completes successfully. Since they can't affect the commit outcome, they're useful for notifications, triggering builds, updating external systems, or logging commit information

  - **Pre-rebase hooks** run before rebasing and help prevent rebasing published commits or branches that shouldn't be rebased. They're particularly valuable for protecting main branches or enforcing workflow policies

  - **Post-checkout and post-merge hooks** execute after checking out branches or completing merges. These are ideal for environment setup tasks like updating dependencies, clearing caches, generating files, or syncing external resources that depend on the current branch state

- Server-Side Hooks

  - **Pre-receive hooks** run before any references are updated when receiving a push. They're powerful for enforcing repository-wide policies like preventing force pushes to protected branches, validating that all commits meet standards, or checking permissions before allowing updates

  - **Update hooks** execute once per branch being updated and are perfect for branch-specific policies. They can enforce different rules for different branches, validate individual commits, or check that updates follow branching strategies

  - **Post-receive hooks** run after all references are successfully updated and are ideal for deployment triggers, sending notifications, updating issue trackers, or kicking off CI/CD pipelines. Since they run after the push succeeds, they're commonly used for automation that depends on the repository being in its new state

## Dependency Classes

## Dependency Classes

TODO: look at jj-fzf, lazyjj, gg-jj look at luxuries

- dependency resolution (should already be installed)

  - [uv](https://github.com/astral-sh/uv) ✔

- miscellaneous (semver via Python)

  - [semver](https://github.com/python-semver/python-semver) ✔

- task running / hooks (installable via Python or Nix; Nix preferred)

  - [just](https://just.systems/man/en/) ✔
  - [lefthook](https://lefthook.dev/) ✔

- interactive programming (installable via Python or Nix; Nix preferred)

  - [ipython](https://ipython.org/) ✔

- static type checking (installable via Python or Nix; Nix preferred)

  - [mypy](https://mypy.readthedocs.io/en/stable/) ✔
  - [ty](https://github.com/astral-sh/ty) ✔

- source code visualization (graphviz and pydeps via Nix, the rest via Python)

  - [pydeps](https://github.com/thebjorn/pydeps) ✔
  - [graphviz](https://graphviz.org/) ✔
  - [deply](https://vashkatsi.github.io/deply/) ✔
  - [snakefood3](https://furius.ca/snakefood/) ✔
  - [grimp](https://grimp.readthedocs.io/en/stable/usage.html) ✔

- performance profiling (flamegraph and scalene via Nix, pyflame via Python)

  - [pyflame](https://pyflame.readthedocs.io/en/latest/) ✔
  - [scalene](https://github.com/plasma-umass/scalene) ✔
  - [flamegraph-rs](https://github.com/flamegraph-rs/flamegraph)
    (cargo-flamegraph in nix) ✔

- software supply chain, security (installable via Python, but Nix preferred)

  - [cyclonedx-python](https://github.com/CycloneDX/cyclonedx-python) ✔
  - [bandit](https://bandit.readthedocs.io/en/latest/) ✔

- testing (installed via Python for now)

  - [pytest](https://docs.pytest.org/en/stable/) ✔
  - pytest plugins: --> look at [these](https://github.com/man-group/pytest-plugins)
    - [mock](https://pytest-mock.readthedocs.io/en/latest/) ✔
    - [testmon](https://testmon.org/) ✔
    - [cov](https://pytest-cov.readthedocs.io/en/latest/) ✔
    - [loguru](https://github.com/mcarans/pytest-loguru) ✔
    - [profiling](https://github.com/man-group/pytest-plugins/tree/master/pytest-profiling) [video](https://www.youtube.com/watch?v=OexWnUTsQGU) ✔
  - [coverage](https://coverage.readthedocs.io/en/7.8.2/) ✔
  - [hypothesis](https://hypothesis.readthedocs.io/en/latest/) ✔
  - [tox](https://tox.wiki/en/4.26.0/) ✔

- docs (installed via Python for now)

  - [mkdocs](https://www.mkdocs.org/) ✔
  - [mkdocstrings](https://mkdocstrings.github.io/) ✔
  - [mkdocstrings-python](https://mkdocstrings.github.io/python/) ✔
  - [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) ✔
  - [pygments](https://pygments.org/) ✔

- formatters / linters

  - installable via Python or Nix:
    - [ruff](https://astral.sh/ruff) ✔
    - [mdformat](https://github.com/hukkin/mdformat) + [mdformat-mkdocs](https://github.com/KyleKing/mdformat-mkdocs) TODO
    - [yamlfmt](https://github.com/google/yamlfmt)
      OR [yamllint](https://github.com/adrienverge/yamllint) ✔
    - [pyprojectsort](https://github.com/kieran-ryan/pyprojectsort)
    - [toml-sort](https://github.com/pappasam/toml-sort) ✔
  - installable only via Nix or other package manager:
    - [treefmt](https://treefmt.com/latest/) + [treefmt-nix](https://github.com/numtide/treefmt-nix) ✔
    - [alejandra](https://github.com/kamadorueda/alejandra) ✔
    - [super-linter](https://github.com/super-linter/super-linter) TODO
    - [markdown-code-runner](https://github.com/drupol/markdown-code-runner)
      OR [mdsf](https://github.com/hougesen/mdsf) ✔
    - [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2)
      OR [markdownlint-cli](https://github.com/DavidAnson/markdownlint-cli) TODO
    - [just-formatter](https://github.com/eli-yip/just-formatter) ✔

## To Look at for Later

- [pystackflame](https://pypi.org/project/pystackflame/)
