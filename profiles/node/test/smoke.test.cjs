const assert = require("node:assert/strict");
const { test } = require("node:test");

const pkg = require("../package.json");

// Guards the manifest invariants that npm publish and the npm trusted
// publisher both rely on. Replace it with tests for real behaviour.
test("package manifest is publishable", () => {
  assert.match(pkg.name, /^[a-z0-9][a-z0-9._-]*$/);
  assert.match(pkg.repository.url, /^git\+https:\/\/github\.com\/.+\/.+\.git$/);
});
