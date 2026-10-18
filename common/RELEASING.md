# Releasing

Releases are automated. Merging to `main` is the only trigger.

## What happens on a merge to main

1. The `Release` workflow runs semantic-release over the commits since the last tag.
2. semantic-release derives the next version from the commit messages.
3. It creates the `vX.Y.Z` git tag and a GitHub Release with generated notes.
4. That release triggers the publish workflow, which stamps the released version into the package manifest, builds it, and publishes it to the registry.

## Commit messages decide the version

| Commit                                         | Release |
| ---------------------------------------------- | ------- |
| `fix: ...`                                     | patch   |
| `feat: ...`                                    | minor   |
| `feat!: ...` or a `BREAKING CHANGE:` footer    | major   |
| `chore:`, `docs:`, `ci:`, `test:`, `refactor:` | nothing |

A message that does not parse as [Conventional Commits](https://www.conventionalcommits.org/) is rejected by the `commit-msg` git hook. `npm install` installs that hook through the `prepare` script, so run it once after cloning.

## The manifest version is a placeholder

The version in the repository manifest is `0.0.0` on purpose. The git tag is the source of truth and the publish workflow stamps it in during the build. Nothing is ever committed back to `main`, so a release needs no exemption from branch protection and leaves no `[skip ci]` commits behind.

## Re-running a failed publish

Re-run the failed publish workflow from the Actions tab. It reads the version from the release tag that triggered it, so it does not need a new release or a new tag.

## Publishing credentials

Both publish workflows authenticate with OpenID Connect, so no long-lived registry token is stored in this repository. Register the publisher once, then delete the section that does not apply to this project.

For npm:

1. Open the package on npmjs.com, then Settings, then Trusted publishing.
2. Add a GitHub Actions publisher with the repository and the workflow filename `publish.yml`.
3. Make `package.json` `repository.url` match the GitHub repository exactly. npm rejects a mismatch, and a smoke test in `test/smoke.test.cjs` guards the shape of that field.

For PyPI:

1. Open the project on PyPI, then Publishing, then add a trusted publisher.
2. Set the owner, repository, workflow filename `publish.yml` and environment name `pypi`.
3. Create the `pypi` environment in the repository settings if a release should wait for approval.

The environment names (`npm`, `pypi`) in the workflow files only have to match if you set an environment on the registry side.
