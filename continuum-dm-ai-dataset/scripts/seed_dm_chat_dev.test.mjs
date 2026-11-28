import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import test from 'node:test';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';

import {
  DEFAULT_FIXTURE_PATH,
  applySeedPlan,
  assertApprovedDevOrganizations,
  assertApprovedDevTarget,
  assertFixtureIntegrity,
  buildDirectKey,
  buildFallbackIdentities,
  buildSeedPlan,
  computeMessageTimestamps,
  extractChatLinks,
  parseCliArgs,
  resolveAnchorDate,
  validateDevelopmentTarget,
  verifySeededData,
} from './seed_dm_chat_dev.mjs';

const execFileAsync = promisify(execFile);
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = path.join(__dirname, 'seed_dm_chat_dev.mjs');

class FakeObjectId {
  constructor(hex) {
    this.hex = String(hex).toLowerCase();
  }
  toString() {
    return this.hex;
  }
  toJSON() {
    return this.hex;
  }
}

function normalizeVal(v) {
  if (v instanceof FakeObjectId) return v.hex;
  if (v instanceof Date) return v.valueOf();
  return v;
}

function matchesFilter(doc, filter) {
  for (const [key, expected] of Object.entries(filter ?? {})) {
    if (key === '$or') {
      if (!expected.some((branch) => matchesFilter(doc, branch))) return false;
      continue;
    }
    const actual = doc[key];
    if (
      expected &&
      typeof expected === 'object' &&
      !(expected instanceof Date) &&
      !(expected instanceof FakeObjectId)
    ) {
      if ('$in' in expected) {
        const set = new Set(expected.$in.map(normalizeVal));
        if (!set.has(normalizeVal(actual))) return false;
        continue;
      }
      if ('$lte' in expected) {
        if (actual === null || actual === undefined) return false;
        if (normalizeVal(actual) > normalizeVal(expected.$lte)) return false;
        continue;
      }
      if ('$lt' in expected) {
        if (actual === null || actual === undefined) return false;
        if (normalizeVal(actual) >= normalizeVal(expected.$lt)) return false;
        continue;
      }
    }
    if (normalizeVal(actual) !== normalizeVal(expected)) return false;
  }
  return true;
}

class FakeCollection {
  constructor(name) {
    this.name = name;
    this.docs = [];
  }

  async findOne(filter) {
    return this.docs.find((doc) => matchesFilter(doc, filter)) ?? null;
  }

  find(filter) {
    const matched = this.docs.filter((doc) => matchesFilter(doc, filter));
    return {
      async toArray() {
        return matched;
      },
    };
  }

  async countDocuments(filter) {
    return this.docs.filter((doc) => matchesFilter(doc, filter)).length;
  }

  async updateOne(filter, update, options = {}) {
    const idx = this.docs.findIndex((doc) => matchesFilter(doc, filter));
    if (idx >= 0) {
      const target = { ...this.docs[idx] };
      let modified = 0;
      if (update.$set) {
        Object.assign(target, update.$set);
        modified = 1;
      }
      if (update.$unset) {
        for (const key of Object.keys(update.$unset)) {
          delete target[key];
        }
        modified = 1;
      }
      this.docs[idx] = target;
      return { matchedCount: 1, modifiedCount: modified, upsertedCount: 0 };
    }
    if (options.upsert) {
      const created = {};
      for (const [k, v] of Object.entries(filter)) {
        if (
          !k.startsWith('$') &&
          (typeof v !== 'object' || v instanceof FakeObjectId || v instanceof Date)
        ) {
          created[k] = v;
        }
      }
      if (update.$setOnInsert) Object.assign(created, update.$setOnInsert);
      if (update.$set) Object.assign(created, update.$set);
      this.docs.push(created);
      return { matchedCount: 0, modifiedCount: 0, upsertedCount: 1 };
    }
    return { matchedCount: 0, modifiedCount: 0, upsertedCount: 0 };
  }
}

class FakeDb {
  constructor() {
    this.collections = new Map();
  }
  collection(name) {
    if (!this.collections.has(name)) {
      this.collections.set(name, new FakeCollection(name));
    }
    return this.collections.get(name);
  }
}

test('assertApprovedDevTarget enforces strict loopback + remote allowlist, DB allowlist, and credential redaction', async () => {
  assert.equal(validateDevelopmentTarget, assertApprovedDevTarget);
  const devEnv = { NODE_ENV: 'development', DATN_DB_ENV: 'development' };

  // Loopback hosts allowed with default continuum_chat / continuum_iam DBs
  for (const [uri, expectedHost] of [
    ['mongodb://127.0.0.1:27017', '127.0.0.1'],
    ['mongodb://localhost:27017', 'localhost'],
    ['mongodb://[::1]:27017', '::1'],
  ]) {
    const ok = assertApprovedDevTarget(devEnv, uri);
    assert.deepEqual(ok, {
      protocol: 'mongodb:',
      hostname: expectedHost,
      targetClass: 'loopback',
      iamDb: 'continuum_iam',
      chatDb: 'continuum_chat',
    });
  }

  // Remote dev cluster requires explicit allowlist match (--approved-cluster-host or DATN_SEED_APPROVED_CLUSTER_HOST)
  assert.throws(
    () =>
      assertApprovedDevTarget(
        devEnv,
        'mongodb+srv://devuser:example-pass@cluster-dev.example.mongodb.net/?retryWrites=true',
        { allowSharedDatabase: true },
      ),
    /not in the approved dev cluster allowlist/,
  );

  const atlasOk = assertApprovedDevTarget(
    devEnv,
    'mongodb+srv://devuser:example-placeholder-val@cluster-dev.example.mongodb.net/?retryWrites=true',
    { approvedClusterHost: 'cluster-dev.example.mongodb.net' },
  );
  assert.deepEqual(atlasOk, {
    protocol: 'mongodb+srv:',
    hostname: 'cluster-dev.example.mongodb.net',
    targetClass: 'approved-remote-dev',
    iamDb: 'continuum_iam',
    chatDb: 'continuum_chat',
  });
  assert.equal(JSON.stringify(atlasOk).includes('example-placeholder-val'), false);

  // Also works via DATN_SEED_APPROVED_CLUSTER_HOST env var
  const atlasEnvOk = assertApprovedDevTarget(
    {
      ...devEnv,
      DATN_SEED_APPROVED_CLUSTER_HOST: 'cluster-dev.example.mongodb.net',
    },
    'mongodb+srv://devuser:example-placeholder-val@cluster-dev.example.mongodb.net/',
  );
  assert.equal(atlasEnvOk.targetClass, 'approved-remote-dev');

  // Arbitrary unapproved remote hosts MUST be rejected even with NODE_ENV=development, DATN_DB_ENV=development, AND --allow-shared-database!
  for (const badUri of [
    'mongodb+srv://u:p@evil-or-prod.mongodb.net/',
    'mongodb://staging.example.com:27017',
    'mongodb+srv://u:p@staging.example.com/',
    'mongodb+srv://u:p@random-cluster.example.mongodb.net/',
  ]) {
    assert.throws(
      () => assertApprovedDevTarget(devEnv, badUri, { allowSharedDatabase: true }),
      /Safety guard:/,
    );
  }

  // Even if someone explicitly passes a prod/staging/non-dev host to --approved-cluster-host, it is STILL rejected!
  assert.throws(
    () =>
      assertApprovedDevTarget(devEnv, 'mongodb+srv://u:p@evil-or-prod.mongodb.net/', {
        approvedClusterHost: 'evil-or-prod.mongodb.net',
        allowSharedDatabase: true,
      }),
    /non-dev \/ production-like/,
  );
  assert.throws(
    () =>
      assertApprovedDevTarget(devEnv, 'mongodb://staging.example.com:27017', {
        approvedClusterHost: 'staging.example.com',
        allowSharedDatabase: true,
      }),
    /non-dev \/ production-like/,
  );
  assert.throws(
    () =>
      assertApprovedDevTarget(devEnv, 'mongodb+srv://u:p@unlabeled.example.mongodb.net/', {
        approvedClusterHost: 'unlabeled.example.mongodb.net',
      }),
    /dev\/sandbox host naming pattern/,
  );
  assert.throws(
    () =>
      assertApprovedDevTarget(devEnv, 'mongodb+srv://u:p@cluster-dev.example.mongodb.net/', {
        approvedClusterHost: '*.mongodb.net',
      }),
    /invalid --approved-cluster-host/,
  );

  // Reject wrong DB names
  assert.throws(
    () =>
      assertApprovedDevTarget(
        { ...devEnv, CHAT_DB_NAME: 'continuum_chat_prod' },
        'mongodb://127.0.0.1:27017',
      ),
    /CHAT_DB_NAME must be exactly "continuum_chat"/,
  );
  assert.throws(
    () =>
      assertApprovedDevTarget(
        { ...devEnv, IAM_DB_NAME: 'other_iam' },
        'mongodb://127.0.0.1:27017',
      ),
    /IAM_DB_NAME must be exactly "continuum_iam"/,
  );

  // Reject non-development env
  assert.throws(
    () =>
      assertApprovedDevTarget(
        { NODE_ENV: 'production', DATN_DB_ENV: 'development' },
        'mongodb://127.0.0.1:27017',
      ),
    /DATN_DB_ENV and NODE_ENV/,
  );
  assert.throws(
    () =>
      assertApprovedDevTarget(
        { NODE_ENV: 'development', DATN_DB_ENV: 'staging' },
        'mongodb://127.0.0.1:27017',
      ),
    /DATN_DB_ENV and NODE_ENV/,
  );

  // Reject Atlas with TLS disabled
  assert.throws(
    () =>
      assertApprovedDevTarget(
        devEnv,
        'mongodb+srv://u:p@cluster-dev.example.mongodb.net/?tls=false',
        { approvedClusterHost: 'cluster-dev.example.mongodb.net' },
      ),
    /disable TLS/,
  );

  // Reject URI with explicit database path
  assert.throws(
    () => assertApprovedDevTarget(devEnv, 'mongodb://127.0.0.1:27017/continuum_chat'),
    /must not select a database/,
  );

  // Reject unspecified host
  assert.throws(
    () => assertApprovedDevTarget(devEnv, 'mongodb://0.0.0.0:27017'),
    /unspecified host/,
  );

  // CLI subprocess proof: unapproved remote hosts fail closed before connecting even with dev env + --allow-shared-database
  for (const remoteUri of [
    'mongodb+srv://u:p@evil-or-prod.mongodb.net/',
    'mongodb://staging.example.com:27017',
  ]) {
    await assert.rejects(
      () =>
        execFileAsync(
          process.execPath,
          [SCRIPT_PATH, '--apply', '--allow-shared-database', '--anchor-date', '2026-11-28'],
          {
            env: {
              PATH: process.env.PATH,
              NODE_ENV: 'development',
              DATN_DB_ENV: 'development',
              MONGODB_URI: remoteUri,
            },
          },
        ),
      (err) => {
        assert.equal(err.code, 1);
        assert.match(err.stderr, /Safety guard:/);
        return true;
      },
    );
  }
});

test('assertApprovedDevOrganizations fails closed on unapproved IAM orgs, remote fallback orgs, or pinned ID mismatch', async () => {
  const fixture = JSON.parse(await fs.readFile(DEFAULT_FIXTURE_PATH, 'utf8'));
  const validRemoteIds = {
    orgsByKey: {
      org1: { id: '6ad88b71ed7cd148fcd0e619', slug: 'continuum-ai-labs', source: 'continuum_iam' },
      org2: { id: '6ad88b71ed7cd148fcd0e620', slug: 'datn-dev', source: 'continuum_iam' },
    },
  };

  const ok = assertApprovedDevOrganizations(validRemoteIds, fixture, {
    targetClass: 'approved-remote-dev',
    approvedOrg1Id: '6ad88b71ed7cd148fcd0e619',
    approvedOrg2Id: '6ad88b71ed7cd148fcd0e620',
  });
  assert.equal(ok.org1.slug, 'continuum-ai-labs');
  assert.equal(ok.org2.slug, 'datn-dev');

  // Unapproved IAM org1 slug rejected
  assert.throws(
    () =>
      assertApprovedDevOrganizations(
        {
          orgsByKey: {
            org1: { id: '6ad88b71ed7cd148fcd0e619', slug: 'customer-prod', source: 'continuum_iam' },
            org2: validRemoteIds.orgsByKey.org2,
          },
        },
        fixture,
        { targetClass: 'approved-remote-dev' },
      ),
    /Org 1 slug "customer-prod" in continuum_iam is not in the approved dev org allowlist/,
  );

  // Unapproved IAM org2 slug rejected
  assert.throws(
    () =>
      assertApprovedDevOrganizations(
        {
          orgsByKey: {
            org1: validRemoteIds.orgsByKey.org1,
            org2: { id: '6ad88b71ed7cd148fcd0e620', slug: 'nova-solutions', source: 'continuum_iam' },
          },
        },
        fixture,
        { targetClass: 'approved-remote-dev' },
      ),
    /Org 2 slug "nova-solutions" in continuum_iam is not in the approved dev org allowlist/,
  );

  // Remote cluster rejects fallback org identities
  const fallbackIds = buildFallbackIdentities(fixture);
  assert.throws(
    () =>
      assertApprovedDevOrganizations(fallbackIds, fixture, {
        targetClass: 'approved-remote-dev',
        allowFallbackIam: true,
      }),
    /Org 1 must resolve to an approved dev organization/,
  );

  // Pinned org ID mismatch fails closed
  assert.throws(
    () =>
      assertApprovedDevOrganizations(validRemoteIds, fixture, {
        targetClass: 'approved-remote-dev',
        approvedOrg1Id: '6ad88b71ed7cd148fcd0e999',
      }),
    /does not match pinned --approved-org1-id/,
  );
});

test('parseCliArgs validates flag combinations and supports --flag=value syntax', () => {
  const parsed = parseCliArgs([
    '--apply',
    '--reset-fixture',
    '--approved-cluster-host=cluster-dev.example.mongodb.net',
    '--approved-org1-id=6ad88b71ed7cd148fcd0e619',
    '--anchor-date=2026-11-28',
  ]);
  assert.equal(parsed.mode, 'apply');
  assert.equal(parsed.resetFixture, true);
  assert.equal(parsed.approvedClusterHost, 'cluster-dev.example.mongodb.net');
  assert.equal(parsed.approvedOrg1Id, '6ad88b71ed7cd148fcd0e619');
  assert.equal(parsed.anchorDate, '2026-11-28');

  assert.throws(() => parseCliArgs(['--reset-fixture']), /--reset-fixture requires --apply/);
  assert.throws(
    () => parseCliArgs(['--dry-run', '--reset-fixture']),
    /--reset-fixture requires --apply/,
  );
  assert.throws(
    () => parseCliArgs(['--apply', '--allow-e2e-mutations']),
    /--allow-e2e-mutations is only valid with --verify/,
  );
});

test('anchor date and Asia/Ho_Chi_Minh (+07:00) relative timestamp math handle month/leap-year rollovers', () => {
  assert.equal(resolveAnchorDate('2026-11-28'), '2026-11-28');
  assert.throws(() => resolveAnchorDate('2026-02-30'), /Invalid calendar date/);
  assert.throws(() => resolveAnchorDate('28-11-2026'), /Expected YYYY-MM-DD/);

  const leapYesterday = computeMessageTimestamps('2028-03-01', {
    id: '6928d1000000000000000001',
    dayOffset: -1,
    timeLocal: '09:05:00',
    editedOffsetMinutes: 15,
    deletedOffsetMinutes: null,
  });
  assert.equal(leapYesterday.localDate, '2028-02-29');
  assert.equal(leapYesterday.createdAt.toISOString(), '2028-02-29T02:05:00.000Z');
  assert.equal(leapYesterday.editedAt.toISOString(), '2028-02-29T02:20:00.000Z');
  assert.equal(leapYesterday.deletedAt, null);
});

test('buildDirectKey matches DATN_BE sorted organizationId:userId1:userId2 contract', () => {
  const org = '6ad88b71ed7cd148fcd0e619';
  const a = '6ad88b6fed7cd148fcd0e616';
  const b = '6ad88b70ed7cd148fcd0e617';
  assert.equal(buildDirectKey(org, b, a), `${org}:${a}:${b}`);
  assert.equal(buildDirectKey(org, a, b), `${org}:${a}:${b}`);
  assert.throws(() => buildDirectKey(org, a, a), /two distinct user IDs/);
});

test('extractChatLinks strips trailing punctuation and excludes credentialed URLs', () => {
  assert.deepEqual(
    extractChatLinks(
      'URL mới là https://staging-chat-02.continuum-dev.internal), bỏ https://user:pass@secret.test',
    ),
    ['https://staging-chat-02.continuum-dev.internal/'],
  );
});

test('assertFixtureIntegrity rejects accidental gold answer or password keys inside seed fixture', () => {
  assert.throws(
    () =>
      assertFixtureIntegrity({
        containsGoldAnswers: false,
        organizations: [],
        actors: [],
        conversations: [{ key: 'x', type: 'DIRECT', expectedAnswer: 'leaked' }],
      }),
    /Forbidden gold\/secret key/,
  );
});

test('default --apply is insert-only (preserves live E2E edits/deletions & revoked members), while --reset-fixture restores fixture baseline', async () => {
  const fixture = JSON.parse(await fs.readFile(DEFAULT_FIXTURE_PATH, 'utf8'));
  const identities = buildFallbackIdentities(fixture);
  const plan = buildSeedPlan(fixture, identities, '2026-11-28');

  const fakeChatDb = new FakeDb();
  const toOid = (hex) => new FakeObjectId(hex);

  // Pre-seed an existing A-C conversation with a different _id (mirrors real dev state)
  const acPlan = plan.conversations.find((c) => c.key === 'dm_org1_ac');
  const preexistingAcId = toOid('6adb1ee0ed7cd148fcd0fa37');
  await fakeChatDb.collection('chat_conversations').updateOne(
    { organizationId: toOid(acPlan.organizationId), directKey: acPlan.directKey },
    {
      $setOnInsert: {
        _id: preexistingAcId,
        organizationId: toOid(acPlan.organizationId),
        type: 'DIRECT',
        directKey: acPlan.directKey,
        lastMessageAt: null,
      },
    },
    { upsert: true },
  );

  // First apply: inserts all 3 conversations, 6 members, 82 messages
  const run1 = await applySeedPlan(fakeChatDb, plan, toOid);
  assert.equal(run1.mode, 'apply');
  assert.equal(fakeChatDb.collection('chat_conversations').docs.length, 3);
  assert.equal(fakeChatDb.collection('chat_members').docs.length, 6);
  assert.equal(fakeChatDb.collection('chat_conversation_messages').docs.length, 82);

  const acSummary1 = run1.conversations.find((c) => c.key === 'dm_org1_ac');
  assert.equal(acSummary1.conversationId, '6adb1ee0ed7cd148fcd0fa37');
  assert.equal(acSummary1.action, 'REUSED_EXISTING_DIRECT_KEY');

  // Simulate live E2E mutations:
  // 1) Live runtime user/AI message appended after seed
  const abSummary1 = run1.conversations.find((c) => c.key === 'dm_org1_ab');
  const liveMessageTime = new Date('2026-11-28T05:00:00.000Z');
  const liveMessageId = toOid('6928ffff0000000000000001');
  await fakeChatDb.collection('chat_conversation_messages').updateOne(
    { _id: liveMessageId },
    {
      $set: {
        _id: liveMessageId,
        organizationId: toOid(abSummary1.organizationId),
        conversationId: toOid(abSummary1.conversationId),
        senderId: 'assistant:continuum_ai',
        authorType: 'ASSISTANT',
        content: 'Live runtime AI reply after seed',
        createdAt: liveMessageTime,
      },
    },
    { upsert: true },
  );
  await fakeChatDb.collection('chat_conversations').updateOne(
    { _id: toOid(abSummary1.conversationId) },
    {
      $set: {
        lastMessageAt: liveMessageTime,
        lastMessageId: liveMessageId,
        lastMessagePreview: 'Live runtime AI reply after seed',
      },
    },
  );

  // 2) Live edit on candidate #59
  const msg59Id = toOid('6928d1000000000000000059');
  const editedTime = new Date('2026-11-28T05:10:00.000Z');
  await fakeChatDb.collection('chat_conversation_messages').updateOne(
    { _id: msg59Id },
    {
      $set: {
        content: 'Ghi chú bổ sung cho hạng mục E2E-EDIT-401: hạn mức đã nâng lên 8.000.000 VNĐ/giao dịch.',
        editedAt: editedTime,
        contentVersion: 1,
      },
    },
  );

  // 3) Live delete on candidate #60
  const msg60Id = toOid('6928d1000000000000000060');
  const deletedTime = new Date('2026-11-28T05:12:00.000Z');
  await fakeChatDb.collection('chat_conversation_messages').updateOne(
    { _id: msg60Id },
    {
      $set: {
        content: '',
        deletedAt: deletedTime,
        contentVersion: 1,
      },
    },
  );

  // 4) Member B revoked / left dm_org1_ab
  await fakeChatDb.collection('chat_members').updateOne(
    {
      conversationId: toOid(abSummary1.conversationId),
      userId: identities.actorsByKey.org1_user_b.id,
    },
    { $set: { status: 'REMOVED' } },
  );

  // Re-run default --apply (insert-only): MUST NOT overwrite edited #59, deleted #60, revoked member B, or live AI message!
  const run2 = await applySeedPlan(fakeChatDb, plan, toOid);
  assert.equal(fakeChatDb.collection('chat_conversations').docs.length, 3);
  assert.equal(fakeChatDb.collection('chat_members').docs.length, 6);
  assert.equal(fakeChatDb.collection('chat_conversation_messages').docs.length, 83); // 82 seed + 1 live
  for (const conv of run2.conversations) {
    assert.equal(conv.messagesUpserted, 0);
    assert.equal(conv.messagesReset, 0);
    assert.equal(conv.messagesMatched, conv.totalSeedMessages);
    assert.equal(conv.membersReset, 0);
  }

  const msg59AfterDefaultApply = await fakeChatDb
    .collection('chat_conversation_messages')
    .findOne({ _id: msg59Id });
  assert.match(msg59AfterDefaultApply.content, /8\.000\.000 VNĐ/);
  assert.equal(msg59AfterDefaultApply.contentVersion, 1);
  assert.equal(msg59AfterDefaultApply.editedAt.valueOf(), editedTime.valueOf());

  const msg60AfterDefaultApply = await fakeChatDb
    .collection('chat_conversation_messages')
    .findOne({ _id: msg60Id });
  assert.equal(msg60AfterDefaultApply.content, '');
  assert.equal(msg60AfterDefaultApply.deletedAt.valueOf(), deletedTime.valueOf());

  const memberBAfterDefaultApply = await fakeChatDb.collection('chat_members').findOne({
    conversationId: toOid(abSummary1.conversationId),
    userId: identities.actorsByKey.org1_user_b.id,
  });
  assert.equal(memberBAfterDefaultApply.status, 'REMOVED');

  const abConvAfterRun2 = await fakeChatDb.collection('chat_conversations').findOne({
    _id: toOid(abSummary1.conversationId),
  });
  assert.equal(abConvAfterRun2.lastMessagePreview, 'Live runtime AI reply after seed');

  // Now run explicit --apply --reset-fixture: restores ONLY fixture-owned messages & members, preserving live AI message!
  const resetRun = await applySeedPlan(fakeChatDb, plan, toOid, { resetFixture: true });
  assert.equal(resetRun.mode, 'apply-reset-fixture');
  assert.equal(resetRun.resetFixture, true);
  assert.equal(fakeChatDb.collection('chat_conversation_messages').docs.length, 83); // live AI message preserved!

  const msg59AfterReset = await fakeChatDb
    .collection('chat_conversation_messages')
    .findOne({ _id: msg59Id });
  assert.match(msg59AfterReset.content, /5\.000\.000 VNĐ/);
  assert.equal(msg59AfterReset.editedAt, null);
  assert.equal('contentVersion' in msg59AfterReset, false);

  const msg60AfterReset = await fakeChatDb
    .collection('chat_conversation_messages')
    .findOne({ _id: msg60Id });
  assert.match(msg60AfterReset.content, /23:15 giờ Việt Nam/);
  assert.equal(msg60AfterReset.deletedAt, null);

  const memberBAfterReset = await fakeChatDb.collection('chat_members').findOne({
    conversationId: toOid(abSummary1.conversationId),
    userId: identities.actorsByKey.org1_user_b.id,
  });
  assert.equal(memberBAfterReset.status, 'ACTIVE');

  const liveMsgStillPresent = await fakeChatDb
    .collection('chat_conversation_messages')
    .findOne({ _id: liveMessageId });
  assert.equal(liveMsgStillPresent.content, 'Live runtime AI reply after seed');

  // Strict verify passes cleanly after reset
  const verifyReport = await verifySeededData(fakeChatDb, plan, toOid);
  assert.equal(verifyReport.verified, true);
  assert.equal(verifyReport.checks.length, 3);
  for (const check of verifyReport.checks) {
    assert.equal(check.exactMemberSetMatch, true);
    assert.deepEqual(check.mutatedFixtureMessages, []);
  }
});

test('applySeedPlan fails closed on cross-conversation or cross-org fixture _id collisions', async () => {
  const fixture = JSON.parse(await fs.readFile(DEFAULT_FIXTURE_PATH, 'utf8'));
  const identities = buildFallbackIdentities(fixture);
  const plan = buildSeedPlan(fixture, identities, '2026-11-28');
  const toOid = (hex) => new FakeObjectId(hex);

  // 1) Message _id collision belonging to a different conversation
  const dbWithMsgCollision = new FakeDb();
  const collidingMsgId = toOid('6928d1000000000000000001');
  const foreignConvId = toOid('aaaaaaaaaaaaaaaaaaaaaaaa');
  await dbWithMsgCollision.collection('chat_conversation_messages').updateOne(
    { _id: collidingMsgId },
    {
      $setOnInsert: {
        _id: collidingMsgId,
        organizationId: toOid(identities.orgsByKey.org1.id),
        conversationId: foreignConvId,
        senderId: 'other-user',
        content: 'Unrelated foreign conversation message',
      },
    },
    { upsert: true },
  );

  await assert.rejects(
    () => applySeedPlan(dbWithMsgCollision, plan, toOid),
    /Message ID collision/,
  );
  await assert.rejects(
    () => applySeedPlan(dbWithMsgCollision, plan, toOid, { resetFixture: true }),
    /Message ID collision/,
  );
  // Colliding document MUST remain untouched!
  const untouched = await dbWithMsgCollision
    .collection('chat_conversation_messages')
    .findOne({ _id: collidingMsgId });
  assert.equal(untouched.content, 'Unrelated foreign conversation message');
  assert.equal(String(untouched.conversationId), 'aaaaaaaaaaaaaaaaaaaaaaaa');

  // 2) Member _id collision belonging to a different conversation
  const dbWithMemberCollision = new FakeDb();
  const abFirstMember = plan.conversations.find((c) => c.key === 'dm_org1_ab').members[0];
  await dbWithMemberCollision.collection('chat_members').updateOne(
    { _id: toOid(abFirstMember.id) },
    {
      $setOnInsert: {
        _id: toOid(abFirstMember.id),
        organizationId: toOid(identities.orgsByKey.org1.id),
        conversationId: foreignConvId,
        userId: 'unrelated-user',
        status: 'ACTIVE',
      },
    },
    { upsert: true },
  );
  await assert.rejects(
    () => applySeedPlan(dbWithMemberCollision, plan, toOid),
    /Member ID collision/,
  );
});

test('verifySeededData rejects extra 3rd ACTIVE member, corrupted message fields, and enforces strict vs --allow-e2e-mutations', async () => {
  const fixture = JSON.parse(await fs.readFile(DEFAULT_FIXTURE_PATH, 'utf8'));
  const identities = buildFallbackIdentities(fixture);
  const plan = buildSeedPlan(fixture, identities, '2026-11-28');
  const toOid = (hex) => new FakeObjectId(hex);

  const fakeChatDb = new FakeDb();
  const applied = await applySeedPlan(fakeChatDb, plan, toOid);
  const abSummary = applied.conversations.find((c) => c.key === 'dm_org1_ab');
  const abConvOid = toOid(abSummary.conversationId);

  // 1) Extra unexpected 3rd ACTIVE member (NOT in verifiedNonMembers denylist!) MUST fail verification AND apply!
  const strayThirdUserId = '6928dead0000000000000099';
  await fakeChatDb.collection('chat_members').updateOne(
    { conversationId: abConvOid, userId: strayThirdUserId },
    {
      $set: {
        organizationId: toOid(abSummary.organizationId),
        conversationId: abConvOid,
        userId: strayThirdUserId,
        status: 'ACTIVE',
      },
    },
    { upsert: true },
  );

  const extraMemberReport = await verifySeededData(fakeChatDb, plan, toOid, {
    throwOnFailure: false,
  });
  assert.equal(extraMemberReport.verified, false);
  const abCheckExtra = extraMemberReport.checks.find((c) => c.key === 'dm_org1_ab');
  assert.equal(abCheckExtra.exactMemberSetMatch, false);
  assert.deepEqual(abCheckExtra.unexpectedActiveMemberIds, [strayThirdUserId]);

  await assert.rejects(
    () => verifySeededData(fakeChatDb, plan, toOid),
    /unexpected active member\(s\): \[6928dead0000000000000099\]/,
  );
  await assert.rejects(
    () => applySeedPlan(fakeChatDb, plan, toOid),
    /ACL invariant violated/,
  );

  // Remove the 3rd member; also verify known forbidden non-member org1_manager fails with clear reason
  fakeChatDb.collection('chat_members').docs = fakeChatDb
    .collection('chat_members')
    .docs.filter((d) => d.userId !== strayThirdUserId);
  await fakeChatDb.collection('chat_members').updateOne(
    { conversationId: abConvOid, userId: identities.actorsByKey.org1_manager.id },
    { $set: { status: 'ACTIVE' } },
    { upsert: true },
  );
  await assert.rejects(
    () => verifySeededData(fakeChatDb, plan, toOid),
    /forbidden non-member org1_manager/,
  );
  fakeChatDb.collection('chat_members').docs = fakeChatDb
    .collection('chat_members')
    .docs.filter((d) => d.userId !== identities.actorsByKey.org1_manager.id);

  // 2) Mutating a designated E2E candidate (#59) fails strict default verify, passes ONLY with allowE2eMutations: true
  const msg59Id = toOid('6928d1000000000000000059');
  const orig59 = {
    ...(await fakeChatDb.collection('chat_conversation_messages').findOne({ _id: msg59Id })),
  };
  await fakeChatDb.collection('chat_conversation_messages').updateOne(
    { _id: msg59Id },
    { $set: { content: 'Edited 8.000.000 VNĐ', editedAt: new Date('2026-11-28T06:00:00.000Z') } },
  );

  const strictReport59 = await verifySeededData(fakeChatDb, plan, toOid, {
    throwOnFailure: false,
  });
  assert.equal(strictReport59.verified, false);
  const abStrict59 = strictReport59.checks.find((c) => c.key === 'dm_org1_ab');
  assert.equal(abStrict59.mutatedFixtureMessages.length, 1);
  assert.equal(abStrict59.mutatedFixtureMessages[0].messageId, '6928d1000000000000000059');

  const allowedReport59 = await verifySeededData(fakeChatDb, plan, toOid, {
    allowE2eMutations: true,
    throwOnFailure: false,
  });
  assert.equal(allowedReport59.verified, true);
  assert.equal(
    allowedReport59.checks.find((c) => c.key === 'dm_org1_ab').allowedE2eMutations[0].messageId,
    '6928d1000000000000000059',
  );

  // Even with allowE2eMutations: true, authorType: 'ASSISTANT' on #59 MUST fail!
  await fakeChatDb.collection('chat_conversation_messages').updateOne(
    { _id: msg59Id },
    { $set: { authorType: 'ASSISTANT' } },
  );
  const assistantReport = await verifySeededData(fakeChatDb, plan, toOid, {
    allowE2eMutations: true,
    throwOnFailure: false,
  });
  assert.equal(assistantReport.verified, false);
  assert.match(
    assistantReport.checks
      .find((c) => c.key === 'dm_org1_ab')
      .mutatedFixtureMessages[0].reasons.join(','),
    /forbidden_authorType/,
  );

  // Restore #59
  await fakeChatDb.collection('chat_conversation_messages').updateOne(
    { _id: msg59Id },
    { $set: orig59, $unset: { authorType: '' } },
  );

  // 3) Corrupted fields on a non-candidate fixture message (#10: content, senderId, organizationId) MUST fail even with allowE2eMutations: true!
  const msg10Id = toOid('6928d1000000000000000010');
  await fakeChatDb.collection('chat_conversation_messages').updateOne(
    { _id: msg10Id },
    {
      $set: {
        content: 'Tampered content on #10',
        senderId: identities.actorsByKey.org1_user_b.id,
        organizationId: toOid(identities.orgsByKey.org2.id),
      },
    },
  );
  const corruptedReport = await verifySeededData(fakeChatDb, plan, toOid, {
    allowE2eMutations: true,
    throwOnFailure: false,
  });
  assert.equal(corruptedReport.verified, false);
  const corruptedItem = corruptedReport.checks
    .find((c) => c.key === 'dm_org1_ab')
    .mutatedFixtureMessages.find((m) => m.messageId === '6928d1000000000000000010');
  assert.ok(corruptedItem);
  assert.ok(corruptedItem.reasons.some((r) => r.startsWith('organizationId_mismatch')));
  assert.ok(corruptedItem.reasons.some((r) => r.startsWith('senderId_mismatch')));
  assert.ok(corruptedItem.reasons.includes('content_mismatch'));

  await assert.rejects(
    () => verifySeededData(fakeChatDb, plan, toOid, { allowE2eMutations: true }),
    /corrupted\/mutated fixture message/,
  );
});

test('CLI offline --dry-run runs cleanly and prints accurate deterministic counts', async () => {
  const { stdout } = await execFileAsync(
    process.execPath,
    [SCRIPT_PATH, '--dry-run', '--anchor-date', '2026-11-28'],
    {
      env: { PATH: process.env.PATH }, // No MONGODB_URI => offline dry-run
    },
  );
  const parsed = JSON.parse(stdout);
  assert.equal(parsed.mode, 'dry-run-offline');
  assert.equal(parsed.anchorDate, '2026-11-28');
  assert.equal(parsed.totals.conversations, 3);
  assert.equal(parsed.totals.messages, 82);
  const ab = parsed.conversations.find((c) => c.key === 'dm_org1_ab');
  assert.equal(ab.messageCount, 68);
  assert.equal(ab.offPageMessages, 18);
});
