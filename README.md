# repo-template

Release automation for new projects: Conventional Commits in, a versioned GitHub Release and a registry publish out. Most projects using it are JavaScript or TypeScript; a Python profile covers the rest.

The pipeline is deliberately language-agnostic. `common/` holds everything that is identical in every project. A profile holds only what genuinely differs: runtime setup, test command, package manifest, and publish target.

## How it works

```text
push to main
  └── Release workflow (common/)
        semantic-release reads the commits since the last tag
        computes the next version, creates the vX.Y.Z tag and a GitHub Release
              └── release: published
                    └── Publish workflow (profile)
                          stamps the tag version into the manifest, builds, publishes
```

Two properties follow from that shape:

1. The version lives in the git tag. The manifest keeps a placeholder version on purpose, so nothing is committed back to `main`, no `[skip ci]` commits appear, and branch protection needs no exemption for the release job.
2. Publishing is its own workflow, keyed off the release. A failed publish is re-run from the Actions tab without a new tag, and the publish target is the only file pair you swap per language.

## Layout

| Path               | Copied to the project root | Purpose                         |
| ------------------ | -------------------------- | ------------------------------- |
| `common/`          | yes                        | Everything language-independent |
| `profiles/node/`   | yes, layered on `common/`  | Node, TypeScript, npm           |
| `profiles/python/` | yes, layered on `common/`  | Python, uv, PyPI                |
| `README.md`        | no                         | This file                       |

Three placeholders are used throughout, and nothing else needs editing to get a green pipeline:

| Placeholder         | Replace with                                                   |
| ------------------- | -------------------------------------------------------------- |
| `your-github-owner` | the GitHub user or organisation that owns the repository       |
| `your-project-name` | the repository, npm and PyPI package name (lowercase, hyphens) |
| `your_project_name` | the Python import name (the project name with underscores)     |

## Using the template

1. Create a repository from this template and clone it.

2. Copy the shared files, then exactly one profile:

   ```bash
   cd /path/to/cloned
   cp -R common/. .
   cp -R profiles/node/. .        # or: cp -R profiles/python/. .
   ```

   The two sets never collide, so the order does not matter. `common/` carries the release config, the release workflow, and the repository hygiene files; the profile carries the manifest, the git hooks, `ci.yml`, `publish.yml`, and the dependabot config.

3. Replace the placeholders:

   ```bash
   grep -rl --exclude-dir=.git -e your-github-owner -e your-project-name -e your_project_name . |
     xargs perl -pi -e '
       s/your-github-owner/acme/g;
       s/your-project-name/acme-widget/g;
       s/your_project_name/acme_widget/g;
     '
   ```

4. Delete the template scaffolding that is still lying around, then commit:

   ```bash
   rm -rf common profiles
   git add -A
   git commit -m "chore: bootstrap the release pipeline"
   ```

   Keep `RELEASING.md`, which was copied out of `common/`. Replace this `README.md` with one for your project.

5. Install the toolchain and generate the lockfile:

   | Profile | Command                                                                        |
   | ------- | ------------------------------------------------------------------------------ |
   | Node    | `npm install`                                                                  |
   | Python  | `npm install` for the release toolchain, then `uv lock` to pin the Python deps |

   Both profiles ship a `package-lock.json`, because the release workflow installs the release toolchain with `npm ci`.

6. Delete or replace the placeholder smoke tests, `test/smoke.test.cjs` and `tests/test_smoke.py`.

7. Make the profile-specific edits:

   1. Node: point `files` in `package.json` at the build output. It is the allowlist of what the tarball contains, so a path that does not exist publishes a near-empty package. Run `npm publish --dry-run` to see the file list before the first release.
   2. Python: add `readme = "README.md"` to the `[project]` table once the project has a README. It is left out so that a build does not fail on a missing file.
   3. Python: rename the import directory if the default name does not fit, then update `[tool.hatch.build.targets.wheel].packages`, `[tool.ruff].src` and `tests/test_smoke.py` to match. The distribution name and the import name differ spelling, so both placeholders exist.

8. Protect `main`: require the `CI` workflow as a status check and require a pull request before merging. The release workflow trusts what is on `main`, so CI on the pull request is the gate.

9. Register the registry publisher, following the section in `RELEASING.md`. The workflows use OpenID Connect, so there is no token to add as a secret. Without this step the first publish fails.

10. Push to `main` with a `feat:` or `fix:` commit and watch the first release run.

## What the profiles pin

Verified on 2026-10-18.

| Profile   | Runtime                                                          | Toolchain                                          |
| --------- | ---------------------------------------------------------------- | -------------------------------------------------- |
| `common/` | Node 24 (`.nvmrc`)                                               | semantic-release 25                                |
| Node      | `actions/checkout@v7`, `actions/setup-node@v7`                   | commitlint 21, husky 9, lint-staged 17, prettier 3 |
| Python    | `actions/checkout@v7`, `astral-sh/setup-uv@v10.3.0`, Python 3.12 | uv, hatchling, pytest 9, ruff 0.17                 |

`astral-sh/setup-uv` publishes no floating major tag, so it is pinned exactly and Dependabot updates it through the `github-actions` ecosystem. Everything else uses a floating major tag, which is why Dependabot is part of the template.

This repository is not itself a project, so nothing updates the pins above automatically. Before relying on the template after a long gap, check the pins and the two profiles by assembling them somewhere temporary:

```bash
cd "$(mktemp -d)"
git clone <this repo> template && cd template
for profile in node python; do
  mkdir -p "/tmp/check-$profile"
  cp -R common/. "/tmp/check-$profile/"
  cp -R "profiles/$profile/." "/tmp/check-$profile/"
done
```

Then in each assembled directory run `npm ci && npm run lint && npm test`, and for the Python profile `uv sync --all-extras && uv run pytest && uv run ruff check .`.

## Extending

Both of the following are opt-in, and both move work back into the release workflow that the default design keeps separate. Do not add them without a reason.

### Committing a CHANGELOG.md back to the repository

semantic-release's own documentation advises against committing during a release, which is why the default relies on the GitHub Release notes. If the project still needs a changelog in the tree, add `@semantic-release/changelog` and `@semantic-release/git` to `devDependencies` and insert them into `.releaserc.cjs` before `@semantic-release/github`:

```js
[
  "@semantic-release/changelog",
  { changelogFile: "CHANGELOG.md" },
],
[
  "@semantic-release/git",
  {
    assets: ["CHANGELOG.md", "package.json", "package-lock.json"],
    message: "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}",
  },
],
```

The release workflow then has to push to `main`: drop `persist-credentials: false` from `release.yml`, and either allow `GITHUB_TOKEN` to bypass branch protection or provide a token with push access.

### Publishing from semantic-release instead of the publish workflow

This removes the separate publish step, and with it the ability to re-run a failed publish without a new tag. Add the plugin for the profile to `.releaserc.cjs`:

1. Node: `["@semantic-release/npm", { npmPublish: true }]`.
2. Python: `["@semantic-release/exec", { prepareCmd: "uv version ${nextRelease.version} --frozen", publishCmd: "uv build && uv publish" }]`. `--frozen` keeps `uv` from rewriting the lockfile during the release, which means `uv.lock` has to be committed first.

The Python form needs `uv` on the runner, which means a setup step in `release.yml` that the default design does not have.
