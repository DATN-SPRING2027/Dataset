import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {
  assertApprovedDevTarget,
  buildDirectKey,
  computeMessageTimestamps,
  DEFAULT_CHAT_FIXTURE_PATH,
  DEFAULT_WORKSPACE_FIXTURE_PATH,
  EXPECTED_ORG_ID,
  parseApprovedClusterHosts,
  resolveAnchorDate,
  shiftIsoDate,
  stableFixtureMemberIdHex,
  validateSeedFixtures,
} from './seed_wdp301_dev.mjs';

const DEV_ENV = {
  NODE_ENV: 'development',
  DATN_DB_ENV: 'development',
};

test('resolveAnchorDate & shiftIsoDate handle Vietnam calendar dates and leap years', () => {
  assert.equal(resolveAnchorDate('2026-11-28'), '2026-11-28');
  assert.equal(shiftIsoDate('2026-11-28', -1), '2026-11-27');
  assert.equal(shiftIsoDate('2026-11-28', -7), '2026-11-21');
  assert.equal(shiftIsoDate('2026-03-01', -1), '2026-02-28');
  assert.throws(() => resolveAnchorDate('2026-02-30'), /Invalid calendar date/);
});

test('computeMessageTimestamps respects +07:00 midnight boundary accurately', () => {
  const beforeMidnight = computeMessageTimestamps('2026-11-28', {
    id: '6f3012070000000000000009',
    dayOffset: -1,
    timeLocal: '23:48:00',
  });
  const afterMidnight = computeMessageTimestamps('2026-11-28', {
    id: '6f3012070000000000000010',
    dayOffset: 0,
    timeLocal: '00:12:00',
  });
  // 23:48 +07:00 on Nov 27 -> 16:48 UTC Nov 27; 00:12 +07:00 on Nov 28 -> 17:12 UTC Nov 27 (24 min apart!)
  assert.equal(afterMidnight.createdAt.valueOf() - beforeMidnight.createdAt.valueOf(), 24 * 60_000);
  assert.equal(beforeMidnight.createdAt.toISOString(), '2026-11-27T16:48:00.000Z');
  assert.equal(afterMidnight.createdAt.toISOString(), '2026-11-27T17:12:00.000Z');
});

test('buildDirectKey sorts user IDs deterministically and rejects same user', () => {
  const k1 = buildDirectKey(
    EXPECTED_ORG_ID,
    '6ad6bc44a331093723e438fd',
    '6acbab2449b08a24945ccb6e',
  );
  const k2 = buildDirectKey(
    EXPECTED_ORG_ID,
    '6acbab2449b08a24945ccb6e',
    '6ad6bc44a331093723e438fd',
  );
  assert.equal(k1, k2);
  assert.equal(
    k1,
    '6ad76c7d938f3bf53df7335e:6acbab2449b08a24945ccb6e:6ad6bc44a331093723e438fd',
  );
  assert.throws(
    () => buildDirectKey(EXPECTED_ORG_ID, '6acbab2449b08a24945ccb6e', '6acbab2449b08a24945ccb6e'),
    /two distinct user IDs/,
  );
});

test('stableFixtureMemberIdHex uses deterministic 6f3019 prefix', () => {
  const idA = stableFixtureMemberIdHex('6f3011000000000000000005', '6acbab2449b08a24945ccb6e');
  const idB = stableFixtureMemberIdHex('6f3011000000000000000005', '6acbab2449b08a24945ccb6e');
  assert.equal(idA, idB);
  assert.match(idA, /^6f3019[0-9a-f]{18}$/);
});

test('assertApprovedDevTarget fails closed on non-dev env, wrong org, prod hosts, missing allowlist, weak TLS, or missing auth', () => {
  // Missing development env
  assert.throws(
    () =>
      assertApprovedDevTarget(
        { NODE_ENV: 'production', DATN_DB_ENV: 'development' },
        'mongodb://127.0.0.1:27017',
        { expectedOrgId: EXPECTED_ORG_ID },
      ),
    /NODE_ENV and DATN_DB_ENV/,
  );

  // Missing or wrong expectedOrgId
  assert.throws(
    () =>
      assertApprovedDevTarget(DEV_ENV, 'mongodb://127.0.0.1:27017', {
        expectedOrgId: '000000000000000000000000',
      }),
    /--expected-org-id/,
  );

  // Loopback allowed cleanly when env + org match
  const loop = assertApprovedDevTarget(DEV_ENV, 'mongodb://127.0.0.1:27017', {
    expectedOrgId: EXPECTED_ORG_ID,
  });
  assert.equal(loop.isLoopback, true);

  // Production-like remote host rejected even if passed in allowlist
  assert.throws(
    () =>
      assertApprovedDevTarget(
        DEV_ENV,
        'mongodb+srv://user:pass@cluster-prod.example.invalid/?retryWrites=true',
        { expectedOrgId: EXPECTED_ORG_ID, approvedClusterHost: 'cluster-prod.example.invalid' },
      ),
    /production\/staging-like/,
  );

  // Remote host rejected without exact allowlist
  assert.throws(
    () =>
      assertApprovedDevTarget(
        DEV_ENV,
        'mongodb+srv://user:pass@sandbox.example.invalid/?retryWrites=true',
        { expectedOrgId: EXPECTED_ORG_ID },
      ),
    /not allowlisted/,
  );

  // Wildcards in allowlist rejected
  assert.throws(() => parseApprovedClusterHosts('*.example.invalid'), /invalid --approved-cluster-host/);

  // Remote host with tls=false rejected
  assert.throws(
    () =>
      assertApprovedDevTarget(
        DEV_ENV,
        'mongodb+srv://user:pass@sandbox.example.invalid/?tls=false',
        { expectedOrgId: EXPECTED_ORG_ID, approvedClusterHost: 'sandbox.example.invalid' },
      ),
    /enforce TLS/,
  );

  // Remote host with tlsAllowInvalidCertificates=true rejected
  assert.throws(
    () =>
      assertApprovedDevTarget(
        DEV_ENV,
        'mongodb+srv://user:pass@sandbox.example.invalid/?tlsAllowInvalidCertificates=true',
        { expectedOrgId: EXPECTED_ORG_ID, approvedClusterHost: 'sandbox.example.invalid' },
      ),
    /weakening TLS/,
  );

  // Remote host without credentials rejected
  assert.throws(
    () =>
      assertApprovedDevTarget(
        DEV_ENV,
        'mongodb+srv://sandbox.example.invalid/?retryWrites=true',
        { expectedOrgId: EXPECTED_ORG_ID, approvedClusterHost: 'sandbox.example.invalid' },
      ),
    /username and password/,
  );

  // Remote host with exact allowlist + SRV TLS + credentials passes
  const ok = assertApprovedDevTarget(
    DEV_ENV,
    'mongodb+srv://devuser:devpass@sandbox.example.invalid/?retryWrites=true',
    { expectedOrgId: EXPECTED_ORG_ID, approvedClusterHost: 'sandbox.example.invalid' },
  );
  assert.equal(ok.isLoopback, false);
  assert.equal(ok.hostname, 'sandbox.example.invalid');
});

test('validateSeedFixtures accepts real generated WDP301 fixtures and rejects gold/AI contamination', async () => {
  const chatFixture = JSON.parse(await fs.readFile(DEFAULT_CHAT_FIXTURE_PATH, 'utf8'));
  const workspaceFixture = JSON.parse(await fs.readFile(DEFAULT_WORKSPACE_FIXTURE_PATH, 'utf8'));
  assert.doesNotThrow(() => validateSeedFixtures(chatFixture, workspaceFixture));

  const poisoned = structuredClone(chatFixture);
  poisoned.conversations[0].messages[0].authorType = 'ASSISTANT';
  assert.throws(
    () => validateSeedFixtures(poisoned, workspaceFixture),
    /Human-only seed violation/,
  );

  const goldPoisoned = structuredClone(workspaceFixture);
  goldPoisoned.taskComments[0].goldAnswer = 'leaked';
  assert.throws(
    () => validateSeedFixtures(chatFixture, goldPoisoned),
    /Forbidden gold\/secret key/,
  );
});
