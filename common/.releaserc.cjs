// Language-agnostic release config. It only reads Conventional Commits and
// turns them into a tag plus a GitHub Release; stamping the version into the
// language manifest and publishing to a registry happen in the publish
// workflow, keyed off that tag. See RELEASING.md.
module.exports = {
  branches: ["main"],
  tagFormat: "v${version}",
  plugins: [
    ["@semantic-release/commit-analyzer", { preset: "conventionalcommits" }],
    [
      "@semantic-release/release-notes-generator",
      { preset: "conventionalcommits" },
    ],
    "@semantic-release/github",
  ],
};
