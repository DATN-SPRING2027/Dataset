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
  assertFixtureIntegrity,
  buildDirectKey,
  buildFallbackIdentities,
  buildSeedPlan,
  computeMessageTimestamps,
  extractChatLinks,
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
    if (expected && typeof expected === 'object' && !(expected instanceof Date) && !(expected instanceof FakeObjectId)) {
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
      if (update.$set) Object.assign(target, update.$set);
      this.docs[idx] = target;
      return { matchedCount: 1, modifiedCount: 1, upsertedCount: 0 };
    }
    if (options.upsert) {
      const created = {};
      for (const [k, v] of Object.entries(filter)) {
        if (!k.startsWith('$') && (typeof v !== 'object' || v instanceof FakeObjectId || v instanceof Date)) {
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

test('validateDevelopmentTarget enforces strict isolated development guards and redacts credentials', () => {
  const devEnv = { NODE_ENV: 'development', DATN_DB_ENV: 'development' };

  const localOk = validateDevelopmentTarget(devEnv, 'mongodb://127.0.0.1:27017');
  assert.deepEqual(localOk, { protocol: 'mongodb:', hostname: '127.0.0.1' });

  const atlasOk = validateDevelopmentTarget(
    devEnv,
    'mongodb+srv://devuser:super-secret-value@cluster-dev.example.mongodb.net/?retryWrites=true',
  );
  assert.deepEqual(atlasOk, {
    protocol: 'mongodb+srv:',
    hostname: 'cluster-dev.example.mongodb.net',
  });
  assert.equal(JSON.stringify(atlasOk).includes('super-secret-value'), false);

  // Reject non-development env
  assert.throws(
    () => validateDevelopmentTarget({ NODE_ENV: 'production', DATN_DB_ENV: 'development' }, 'mongodb://127.0.0.1:27017'),
    /DATN_DB_ENV and NODE_ENV/,
  );
  assert.throws(
    () => validateDevelopmentTarget({ NODE_ENV: 'development', DATN_DB_ENV: 'staging' }, 'mongodb://127.0.0.1:27017'),
    /DATN_DB_ENV and NODE_ENV/,
  );

  // Reject production-like hostname
  assert.throws(
    () => validateDevelopmentTarget(devEnv, 'mongodb+srv://u:p@cluster-prod.example.mongodb.net/'),
    /production-like/,
  );

  // Reject Atlas with TLS disabled
  assert.throws(
    () => validateDevelopmentTarget(devEnv, 'mongodb+srv://u:p@cluster-dev.example.mongodb.net/?tls=false'),
    /disable TLS/,
  );

  // Reject URI with explicit database path
  assert.throws(
    () => validateDevelopmentTarget(devEnv, 'mongodb://127.0.0.1:27017/continuum_chat'),
    /must not select a database/,
  );

  // Reject unspecified host
  assert.throws(
    () => validateDevelopmentTarget(devEnv, 'mongodb://0.0.0.0:27017'),
    /unspecified host/,
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
    extractChatLinks('URL mới là https://staging-chat-02.continuum-dev.internal), bỏ https://user:pass@secret.test'),
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

test('applySeedPlan is 100% idempotent across reruns, reuses existing directKey, and preserves newer live messages', async () => {
  const fixture = JSON.parse(await fs.readFile(DEFAULT_FIXTURE_PATH, 'utf8'));
  const identities = buildFallbackIdentities(fixture);
  const plan1 = buildSeedPlan(fixture, identities, '2026-11-28');

  const fakeChatDb = new FakeDb();
  const toOid = (hex) => new FakeObjectId(hex);

  // Pre-seed an existing A-C conversation with a different _id (mirrors real dev Atlas state!)
  const acPlan = plan1.conversations.find((c) => c.key === 'dm_org1_ac');
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

  // First apply
  const run1 = await applySeedPlan(fakeChatDb, plan1, toOid);
  assert.equal(fakeChatDb.collection('chat_conversations').docs.length, 3);
  assert.equal(fakeChatDb.collection('chat_members').docs.length, 6);
  assert.equal(fakeChatDb.collection('chat_conversation_messages').docs.length, 82);

  const acSummary1 = run1.conversations.find((c) => c.key === 'dm_org1_ac');
  assert.equal(acSummary1.conversationId, '6adb1ee0ed7cd148fcd0fa37');
  assert.equal(acSummary1.action, 'REUSED_EXISTING_DIRECT_KEY');

  // Simulate a live user/AI message appended AFTER seeding in dm_org1_ab
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
        senderId: identities.actorsByKey.org1_user_a.id,
        content: 'Live runtime message after seed',
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
        lastMessagePreview: 'Live runtime message after seed',
      },
    },
  );

  // Second apply (same anchor date): zero duplicate docs, live message untouched, lastMessagePreview NOT regressed!
  const run2 = await applySeedPlan(fakeChatDb, plan1, toOid);
  assert.equal(fakeChatDb.collection('chat_conversations').docs.length, 3);
  assert.equal(fakeChatDb.collection('chat_members').docs.length, 6);
  assert.equal(fakeChatDb.collection('chat_conversation_messages').docs.length, 83); // 82 seed + 1 live
  for (const conv of run2.conversations) {
    assert.equal(conv.messagesUpserted, 0);
    assert.equal(conv.messagesMatched, conv.totalSeedMessages);
  }
  const abConvAfterRun2 = await fakeChatDb.collection('chat_conversations').findOne({
    _id: toOid(abSummary1.conversationId),
  });
  assert.equal(abConvAfterRun2.lastMessagePreview, 'Live runtime message after seed');

  // Verify passes cleanly
  const verifyReport = await verifySeededData(fakeChatDb, plan1, toOid);
  assert.equal(verifyReport.verified, true);
  assert.equal(verifyReport.checks.length, 3);

  // Tampering test: if org1_manager is accidentally added to dm_org1_ab, applySeedPlan & verifySeededData MUST fail!
  await fakeChatDb.collection('chat_members').updateOne(
    { conversationId: toOid(abSummary1.conversationId), userId: identities.actorsByKey.org1_manager.id },
    { $set: { status: 'ACTIVE' } },
    { upsert: true },
  );
  await assert.rejects(
    () => verifySeededData(fakeChatDb, plan1, toOid),
    /forbidden non-member org1_manager/,
  );
  await assert.rejects(
    () => applySeedPlan(fakeChatDb, plan1, toOid),
    /ACL invariant violated/,
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
