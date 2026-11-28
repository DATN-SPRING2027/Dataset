#!/usr/bin/env node
/**
 * Idempotent dev seeder for the synthetic Vietnamese 1-1 DM dataset (`continuum-dm-ai-dataset`).
 *
 * Safety invariants:
 * - Defaults to `--dry-run` (zero DB writes unless `--apply` is explicitly passed).
 * - Requires isolated development environment (`NODE_ENV=development` AND `DATN_DB_ENV=development`)
 *   plus validated MongoDB URI for `--apply`.
 * - Never prints credentials, MongoDB URIs, password hashes, or tokens.
 * - Upserts conversations by `(organizationId, directKey)` (reusing existing DM `_id` if present),
 *   members by `(conversationId, userId)`, and messages by deterministic `_id` so re-running never
 *   duplicates messages or destroys live user/AI messages.
 * - Strictly seeds human-to-human messages only (zero pre-seeded AI bot replies, zero gold eval answers).
 */

import { createHash } from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DATASET_PKG_ROOT = path.resolve(__dirname, '..');
const DATASET_REPO_ROOT = path.resolve(DATASET_PKG_ROOT, '..');
const WORKSPACE_ROOT = path.resolve(DATASET_REPO_ROOT, '..');

export const DEFAULT_FIXTURE_PATH = path.join(
  DATASET_PKG_ROOT,
  'seed',
  'dm_seed_fixture.json',
);
export const DEFAULT_TIMEZONE = 'Asia/Ho_Chi_Minh';
export const DEFAULT_UTC_OFFSET = '+07:00';
const DEVELOPMENT_ENVIRONMENT = 'development';
const ALLOWED_MONGODB_SCHEMES = new Set(['mongodb:', 'mongodb+srv:']);
const OBJECT_ID_RE = /^[a-f0-9]{24}$/i;
const UUID_V4_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const ISO_DATE_RE = /^(\d{4})-(\d{2})-(\d{2})$/;
const LOCAL_TIME_RE = /^(\d{2}):(\d{2}):(\d{2})$/;
const PRODUCTION_HOST_RE = /(^|[.-])(prod|production)([.-]|$)/i;

const FORBIDDEN_SEED_KEYS = new Set([
  'expectedAnswer',
  'goldAnswer',
  'goldAnswers',
  'requiredAnswerFacts',
  'requiredSourceMessageIds',
  'expectedStatus',
  'forbiddenSubstrings',
  'evalCases',
  'groundTruth',
  'password',
  'passwordHash',
]);

export function loadMongoDriver(beRoot = process.env.DATN_BE_ROOT || path.join(WORKSPACE_ROOT, 'DATN_BE')) {
  try {
    const bePkg = path.join(beRoot, 'package.json');
    const requireFromBe = createRequire(pathToFileURL(bePkg).href);
    return requireFromBe('mongodb');
  } catch {
    const requireLocal = createRequire(import.meta.url);
    return requireLocal('mongodb');
  }
}

export function stableObjectIdHex(...parts) {
  return createHash('sha256')
    .update(JSON.stringify(['continuum.dm-seed.v1', ...parts]))
    .digest('hex')
    .slice(0, 24);
}

export function formatTodayInTimezone(now = new Date(), timeZone = DEFAULT_TIMEZONE) {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(now);
}

export function resolveAnchorDate(anchorDateInput, now = new Date(), timeZone = DEFAULT_TIMEZONE) {
  const value = anchorDateInput ? String(anchorDateInput).trim() : formatTodayInTimezone(now, timeZone);
  const match = ISO_DATE_RE.exec(value);
  if (!match) {
    throw new Error(`Invalid --anchor-date "${value}". Expected YYYY-MM-DD.`);
  }
  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  const probe = new Date(Date.UTC(year, month - 1, day));
  if (
    probe.getUTCFullYear() !== year ||
    probe.getUTCMonth() !== month - 1 ||
    probe.getUTCDate() !== day
  ) {
    throw new Error(`Invalid calendar date for --anchor-date "${value}".`);
  }
  return value;
}

export function shiftIsoDate(anchorDate, dayOffset) {
  const match = ISO_DATE_RE.exec(anchorDate);
  if (!match) throw new Error(`Invalid anchorDate "${anchorDate}".`);
  if (!Number.isInteger(dayOffset)) {
    throw new Error(`dayOffset must be an integer, got ${dayOffset}.`);
  }
  const shifted = new Date(
    Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3]) + dayOffset),
  );
  const y = String(shifted.getUTCFullYear()).padStart(4, '0');
  const m = String(shifted.getUTCMonth() + 1).padStart(2, '0');
  const d = String(shifted.getUTCDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

export function computeMessageTimestamps(anchorDate, message, utcOffset = DEFAULT_UTC_OFFSET) {
  if (!LOCAL_TIME_RE.test(String(message.timeLocal ?? ''))) {
    throw new Error(`Invalid timeLocal "${message.timeLocal}" on message ${message.id}.`);
  }
  const localDate = shiftIsoDate(anchorDate, message.dayOffset);
  const createdAt = new Date(`${localDate}T${message.timeLocal}${utcOffset}`);
  if (!Number.isFinite(createdAt.valueOf())) {
    throw new Error(`Failed to compute createdAt for message ${message.id}.`);
  }

  let editedAt = null;
  if (message.editedOffsetMinutes !== null && message.editedOffsetMinutes !== undefined) {
    if (!Number.isInteger(message.editedOffsetMinutes) || message.editedOffsetMinutes <= 0) {
      throw new Error(`editedOffsetMinutes must be a positive integer on message ${message.id}.`);
    }
    editedAt = new Date(createdAt.valueOf() + message.editedOffsetMinutes * 60_000);
  }

  let deletedAt = null;
  if (message.deletedOffsetMinutes !== null && message.deletedOffsetMinutes !== undefined) {
    if (!Number.isInteger(message.deletedOffsetMinutes) || message.deletedOffsetMinutes <= 0) {
      throw new Error(`deletedOffsetMinutes must be a positive integer on message ${message.id}.`);
    }
    deletedAt = new Date(createdAt.valueOf() + message.deletedOffsetMinutes * 60_000);
  }

  const updatedAt = deletedAt ?? editedAt ?? createdAt;
  return { localDate, createdAt, editedAt, deletedAt, updatedAt };
}

export function buildDirectKey(organizationId, userIdA, userIdB) {
  const orgHex = String(organizationId).toLowerCase();
  const a = String(userIdA).toLowerCase();
  const b = String(userIdB).toLowerCase();
  if (!OBJECT_ID_RE.test(orgHex) || !OBJECT_ID_RE.test(a) || !OBJECT_ID_RE.test(b)) {
    throw new Error('buildDirectKey requires valid 24-hex ObjectId strings.');
  }
  if (a === b) {
    throw new Error('Direct conversation requires two distinct user IDs.');
  }
  const [first, second] = [a, b].sort();
  return `${orgHex}:${first}:${second}`;
}

export function extractChatLinks(content) {
  const links = [];
  for (const candidate of String(content ?? '').match(/https?:\/\/[^\s<>]+/giu) ?? []) {
    try {
      const url = new URL(candidate.replace(/[),.;!?]+$/u, ''));
      if (!url.username && !url.password) links.push(url.href);
    } catch {
      // Ignore malformed URLs and keep as plain text.
    }
  }
  return [...new Set(links)].slice(0, 50);
}

export function validateDevelopmentTarget(env, mongoUri) {
  if (
    env?.DATN_DB_ENV !== DEVELOPMENT_ENVIRONMENT ||
    env?.NODE_ENV !== DEVELOPMENT_ENVIRONMENT
  ) {
    throw new Error(
      'Safety guard: DATN_DB_ENV and NODE_ENV must both be exactly "development" for --apply.',
    );
  }
  if (!mongoUri || typeof mongoUri !== 'string') {
    throw new Error('Safety guard: MONGODB_URI (or CHAT_MONGODB_URI) is required.');
  }

  let parsed;
  try {
    parsed = new URL(mongoUri);
  } catch {
    throw new Error('Safety guard: MONGODB_URI must be a valid MongoDB URI.');
  }

  if (!ALLOWED_MONGODB_SCHEMES.has(parsed.protocol)) {
    throw new Error(
      'Safety guard: MONGODB_URI must use mongodb:// or mongodb+srv:// for development.',
    );
  }

  const authorityStart = mongoUri.indexOf('://') + 3;
  const authority = mongoUri.slice(authorityStart).split(/[/?#]/, 1)[0];
  const hosts = authority.slice(authority.lastIndexOf('@') + 1);
  if (!parsed.hostname || !hosts || hosts.includes(',')) {
    throw new Error('Safety guard: MONGODB_URI must identify exactly one development host.');
  }

  const hostname = parsed.hostname.replace(/^\[|\]$/g, '').toLowerCase();
  if (hostname === '0.0.0.0' || hostname === '::') {
    throw new Error('Safety guard: MONGODB_URI must not use an unspecified host address.');
  }

  if (PRODUCTION_HOST_RE.test(hostname)) {
    throw new Error(
      `Safety guard: refusing to write to production-like MongoDB hostname "${hostname}".`,
    );
  }

  if (!['', '/'].includes(parsed.pathname)) {
    throw new Error(
      'Safety guard: MONGODB_URI must not select a database in the path; service-owned DB names (continuum_iam / continuum_chat) are selected explicitly.',
    );
  }

  if (parsed.protocol === 'mongodb+srv:') {
    const labels = hostname.replace(/\.$/, '').split('.');
    if (
      parsed.port ||
      labels.length < 3 ||
      labels.some((label) => label.length === 0) ||
      !parsed.username ||
      !parsed.password
    ) {
      throw new Error(
        'Safety guard: Atlas development MONGODB_URI must use one DNS hostname and include database-user credentials.',
      );
    }
    const disablesTls = [...parsed.searchParams.entries()].some(
      ([name, value]) =>
        ['tls', 'ssl'].includes(name.toLowerCase()) &&
        ['false', '0', 'no'].includes(value.toLowerCase()),
    );
    if (disablesTls) {
      throw new Error('Safety guard: Atlas development MONGODB_URI must not disable TLS.');
    }
  }

  // Return strictly redacted metadata (never credentials or raw URI).
  return {
    protocol: parsed.protocol,
    hostname,
  };
}

export function assertFixtureIntegrity(fixture) {
  if (!fixture || typeof fixture !== 'object') {
    throw new Error('Seed fixture must be a JSON object.');
  }
  if (fixture.containsGoldAnswers !== false) {
    throw new Error('Seed fixture must explicitly set containsGoldAnswers: false.');
  }

  function scanForbiddenKeys(node, pathTrail = '$') {
    if (!node || typeof node !== 'object') return;
    if (Array.isArray(node)) {
      node.forEach((item, index) => scanForbiddenKeys(item, `${pathTrail}[${index}]`));
      return;
    }
    for (const [key, value] of Object.entries(node)) {
      if (FORBIDDEN_SEED_KEYS.has(key)) {
        throw new Error(`Forbidden gold/secret key "${key}" found in seed fixture at ${pathTrail}.`);
      }
      scanForbiddenKeys(value, `${pathTrail}.${key}`);
    }
  }
  scanForbiddenKeys(fixture);

  const actorKeys = new Set((fixture.actors ?? []).map((a) => a.key));
  const orgKeys = new Set((fixture.organizations ?? []).map((o) => o.key));
  const seenMsgIds = new Set();
  const seenClientIds = new Set();

  for (const conv of fixture.conversations ?? []) {
    if (conv.type !== 'DIRECT') {
      throw new Error(`Conversation ${conv.key} must have type DIRECT.`);
    }
    if (!orgKeys.has(conv.orgKey)) {
      throw new Error(`Conversation ${conv.key} references unknown orgKey ${conv.orgKey}.`);
    }
    if (!Array.isArray(conv.memberActorKeys) || conv.memberActorKeys.length !== 2) {
      throw new Error(`DIRECT conversation ${conv.key} must have exactly 2 memberActorKeys.`);
    }
    for (const memberKey of conv.memberActorKeys) {
      if (!actorKeys.has(memberKey)) {
        throw new Error(`Conversation ${conv.key} references unknown actor ${memberKey}.`);
      }
    }
    const convMsgIds = new Set();
    for (const msg of conv.messages ?? []) {
      if (!OBJECT_ID_RE.test(String(msg.id ?? ''))) {
        throw new Error(`Invalid ObjectId "${msg.id}" in ${conv.key}.`);
      }
      if (!UUID_V4_RE.test(String(msg.clientMessageId ?? ''))) {
        throw new Error(`Invalid UUIDv4 clientMessageId "${msg.clientMessageId}" on ${msg.id}.`);
      }
      if (seenMsgIds.has(msg.id)) {
        throw new Error(`Duplicate message id "${msg.id}".`);
      }
      if (seenClientIds.has(msg.clientMessageId)) {
        throw new Error(`Duplicate clientMessageId "${msg.clientMessageId}".`);
      }
      if (!conv.memberActorKeys.includes(msg.senderActorKey)) {
        throw new Error(
          `Message ${msg.id} sender "${msg.senderActorKey}" is not a member of ${conv.key}.`,
        );
      }
      if (msg.deletedOffsetMinutes && msg.content !== '') {
        throw new Error(`Pre-deleted message ${msg.id} must have empty content "".`);
      }
      if (msg.replyToMessageId && !convMsgIds.has(msg.replyToMessageId)) {
        throw new Error(
          `Message ${msg.id} replies to "${msg.replyToMessageId}" which is not an earlier message in ${conv.key}.`,
        );
      }
      seenMsgIds.add(msg.id);
      seenClientIds.add(msg.clientMessageId);
      convMsgIds.add(msg.id);
    }
  }
}

export function buildFallbackIdentities(fixture) {
  const orgsByKey = {};
  for (const org of fixture.organizations) {
    orgsByKey[org.key] = {
      id: org.fallbackId.toLowerCase(),
      name: org.name,
      slug: org.slug,
      source: 'fallback',
    };
  }
  const actorsByKey = {};
  for (const actor of fixture.actors) {
    actorsByKey[actor.key] = {
      id: actor.fallbackId.toLowerCase(),
      orgKey: actor.orgKey,
      organizationId: orgsByKey[actor.orgKey].id,
      email: actor.email,
      displayName: actor.fallbackDisplayName,
      avatarUrl: null,
      source: 'fallback',
    };
  }
  return { orgsByKey, actorsByKey };
}

export async function resolveIdentitiesFromIam(iamDb, fixture, { allowFallbackIam = false, org1Slug = null, org2Slug = null } = {}) {
  const fallback = buildFallbackIdentities(fixture);
  const usersCol = iamDb.collection('users');
  const orgsCol = iamDb.collection('organizations');
  const membershipsCol = iamDb.collection('organization_memberships');

  const org1Spec = fixture.organizations.find((o) => o.key === 'org1');
  const org2Spec = fixture.organizations.find((o) => o.key === 'org2');
  const org1Actors = fixture.actors.filter((a) => a.orgKey === 'org1');

  const resolvedActors = { ...fallback.actorsByKey };
  const resolvedOrgs = { ...fallback.orgsByKey };

  // 1) Resolve Org 1 actors by email (strict safe projection: zero passwordHash/secrets).
  const org1Emails = org1Actors.map((a) => a.email.toLowerCase());
  const foundUsers = await usersCol
    .find(
      { email: { $in: org1Emails }, status: 'ACTIVE' },
      { projection: { _id: 1, email: 1, fullName: 1, avatarUrl: 1, status: 1 } },
    )
    .toArray();
  const userByEmail = new Map(foundUsers.map((u) => [String(u.email).toLowerCase(), u]));

  const missingOrg1Emails = org1Emails.filter((email) => !userByEmail.has(email));
  if (missingOrg1Emails.length > 0 && !allowFallbackIam) {
    throw new Error(
      `Missing active Org 1 dev users in continuum_iam.users: ${missingOrg1Emails.join(', ')}. ` +
        'Ensure dev IAM seed is present or pass --allow-fallback-iam for isolated sandbox seeding.',
    );
  }

  let resolvedOrg1Doc = null;
  if (org1Slug) {
    resolvedOrg1Doc = await orgsCol.findOne(
      { slug: org1Slug.toLowerCase() },
      { projection: { _id: 1, name: 1, slug: 1 } },
    );
  }
  if (!resolvedOrg1Doc && userByEmail.has('member1@continuum.ai')) {
    const memberA = userByEmail.get('member1@continuum.ai');
    const memberships = await membershipsCol
      .find(
        { userId: memberA._id, status: 'ACTIVE' },
        { projection: { organizationId: 1 } },
      )
      .toArray();
    if (memberships.length > 0) {
      const orgIds = memberships.map((m) => m.organizationId);
      const orgDocs = await orgsCol
        .find(
          { _id: { $in: orgIds } },
          { projection: { _id: 1, name: 1, slug: 1 } },
        )
        .toArray();
      resolvedOrg1Doc =
        orgDocs.find((o) => o.slug === org1Spec.slug) ??
        orgDocs[0] ??
        null;
    }
  }

  if (resolvedOrg1Doc) {
    resolvedOrgs.org1 = {
      id: String(resolvedOrg1Doc._id).toLowerCase(),
      name: resolvedOrg1Doc.name,
      slug: resolvedOrg1Doc.slug,
      source: 'continuum_iam',
    };
  } else if (!allowFallbackIam) {
    throw new Error(
      'Could not resolve Org 1 organization in continuum_iam.organizations for member1@continuum.ai.',
    );
  }

  for (const actor of org1Actors) {
    const doc = userByEmail.get(actor.email.toLowerCase());
    if (doc) {
      resolvedActors[actor.key] = {
        id: String(doc._id).toLowerCase(),
        orgKey: 'org1',
        organizationId: resolvedOrgs.org1.id,
        email: doc.email,
        displayName: doc.fullName || actor.fallbackDisplayName,
        avatarUrl: doc.avatarUrl ?? null,
        source: 'continuum_iam',
      };
    }
  }

  // 2) Resolve Org 2: prefer existing distinct organization with >= 2 active users; otherwise fallback deterministic IDs (chat-only).
  const candidateSlugs = org2Slug
    ? [org2Slug.toLowerCase()]
    : (org2Spec?.preferredExistingSlugs ?? []).map((s) => s.toLowerCase());

  let resolvedOrg2Doc = null;
  let org2Users = [];

  for (const slug of candidateSlugs) {
    const candidateOrg = await orgsCol.findOne(
      { slug },
      { projection: { _id: 1, name: 1, slug: 1 } },
    );
    if (!candidateOrg || String(candidateOrg._id).toLowerCase() === resolvedOrgs.org1.id) {
      continue;
    }
    const candidateMemberships = await membershipsCol
      .find(
        { organizationId: candidateOrg._id, status: 'ACTIVE' },
        { projection: { userId: 1 } },
      )
      .toArray();
    const candidateUserIds = candidateMemberships.map((m) => m.userId);
    if (candidateUserIds.length < 2) continue;

    const org1UserIdSet = new Set(
      org1Actors.map((a) => resolvedActors[a.key].id),
    );
    const activeUsers = (
      await usersCol
        .find(
          { _id: { $in: candidateUserIds }, status: 'ACTIVE' },
          { projection: { _id: 1, email: 1, fullName: 1, avatarUrl: 1, status: 1 } },
        )
        .toArray()
    )
      .filter((u) => !org1UserIdSet.has(String(u._id).toLowerCase()))
      .sort((a, b) => String(a.email).localeCompare(String(b.email)));

    if (activeUsers.length >= 2) {
      resolvedOrg2Doc = candidateOrg;
      org2Users = activeUsers.slice(0, 2);
      break;
    }
  }

  if (resolvedOrg2Doc && org2Users.length >= 2) {
    resolvedOrgs.org2 = {
      id: String(resolvedOrg2Doc._id).toLowerCase(),
      name: resolvedOrg2Doc.name,
      slug: resolvedOrg2Doc.slug,
      source: 'continuum_iam',
    };
    const [uX, uY] = org2Users;
    resolvedActors.org2_user_x = {
      id: String(uX._id).toLowerCase(),
      orgKey: 'org2',
      organizationId: resolvedOrgs.org2.id,
      email: uX.email,
      displayName: uX.fullName || fallback.actorsByKey.org2_user_x.displayName,
      avatarUrl: uX.avatarUrl ?? null,
      source: 'continuum_iam',
    };
    resolvedActors.org2_user_y = {
      id: String(uY._id).toLowerCase(),
      orgKey: 'org2',
      organizationId: resolvedOrgs.org2.id,
      email: uY.email,
      displayName: uY.fullName || fallback.actorsByKey.org2_user_y.displayName,
      avatarUrl: uY.avatarUrl ?? null,
      source: 'continuum_iam',
    };
  }

  if (resolvedOrgs.org1.id === resolvedOrgs.org2.id) {
    throw new Error('Safety guard: Org 1 and Org 2 must resolve to distinct organizationIds.');
  }

  return { orgsByKey: resolvedOrgs, actorsByKey: resolvedActors };
}

export function buildSeedPlan(fixture, identities, anchorDate) {
  assertFixtureIntegrity(fixture);
  const utcOffset = fixture.utcOffset || DEFAULT_UTC_OFFSET;
  const resolvedAnchor = resolveAnchorDate(anchorDate);

  const conversations = fixture.conversations.map((conv) => {
    const org = identities.orgsByKey[conv.orgKey];
    const [memberKeyA, memberKeyB] = conv.memberActorKeys;
    const actorA = identities.actorsByKey[memberKeyA];
    const actorB = identities.actorsByKey[memberKeyB];
    const ownerActor = identities.actorsByKey[conv.ownerActorKey];

    const directKey = buildDirectKey(org.id, actorA.id, actorB.id);

    let prevTimestampMs = -Infinity;
    const messages = conv.messages.map((msg) => {
      const sender = identities.actorsByKey[msg.senderActorKey];
      const ts = computeMessageTimestamps(resolvedAnchor, msg, utcOffset);
      if (ts.createdAt.valueOf() <= prevTimestampMs) {
        throw new Error(
          `Non-ascending timestamp in ${conv.key} at message ${msg.id} (${ts.createdAt.toISOString()}).`,
        );
      }
      prevTimestampMs = ts.createdAt.valueOf();
      const isDeleted = ts.deletedAt !== null;
      const content = isDeleted ? '' : msg.content;
      const mentionUserIds = isDeleted
        ? []
        : (msg.mentionActorKeys ?? []).map((key) => identities.actorsByKey[key].id);

      return {
        id: msg.id.toLowerCase(),
        clientMessageId: msg.clientMessageId.toLowerCase(),
        organizationId: org.id,
        senderId: sender.id,
        senderName: sender.displayName,
        senderAvatarUrl: sender.avatarUrl ?? null,
        content,
        mentionUserIds,
        links: isDeleted ? [] : extractChatLinks(content),
        isPinned: isDeleted ? false : Boolean(msg.isPinned),
        editedAt: ts.editedAt,
        deletedAt: ts.deletedAt,
        reactions: [],
        replyToMessageId: msg.replyToMessageId ? msg.replyToMessageId.toLowerCase() : null,
        attachments: [],
        createdAt: ts.createdAt,
        updatedAt: ts.updatedAt,
        localDate: ts.localDate,
        dayOffset: msg.dayOffset,
        tags: msg.tags ?? [],
      };
    });

    const firstMsg = messages[0];
    const lastMsg = messages[messages.length - 1];
    const members = [actorA, actorB].map((actor) => {
      const peer = actor.id === actorA.id ? actorB : actorA;
      return {
        id: stableObjectIdHex('member', conv.key, org.id, actor.id),
        organizationId: org.id,
        userId: actor.id,
        displayName: actor.displayName,
        searchLabel: peer.displayName,
        avatarUrl: actor.avatarUrl ?? null,
        role: actor.id === ownerActor.id ? 'OWNER' : 'MEMBER',
        status: 'ACTIVE',
        joinedAt: firstMsg.createdAt,
      };
    });

    const verifiedNonMembers = (conv.verifiedNonMemberActorKeys ?? []).map((key) => ({
      actorKey: key,
      userId: identities.actorsByKey[key].id,
      email: identities.actorsByKey[key].email,
    }));

    return {
      key: conv.key,
      fallbackConversationId: conv.id.toLowerCase(),
      orgKey: conv.orgKey,
      organizationId: org.id,
      organizationSlug: org.slug,
      organizationSource: org.source,
      type: 'DIRECT',
      directKey,
      createdBy: ownerActor.id,
      firstMessageAt: firstMsg.createdAt,
      lastMessage: {
        id: lastMsg.id,
        createdAt: lastMsg.createdAt,
        preview: lastMsg.deletedAt ? 'Message deleted' : lastMsg.content.slice(0, 180),
        senderId: lastMsg.senderId,
      },
      members,
      verifiedNonMembers,
      messages,
      offPageCount: Math.max(
        0,
        messages.length - (fixture.uiInitialPageSizeReference ?? 50),
      ),
    };
  });

  return {
    datasetId: fixture.datasetId,
    anchorDate: resolvedAnchor,
    timezone: fixture.defaultTimezone || DEFAULT_TIMEZONE,
    conversations,
    totals: {
      organizations: Object.keys(identities.orgsByKey).length,
      conversations: conversations.length,
      members: conversations.reduce((acc, c) => acc + c.members.length, 0),
      messages: conversations.reduce((acc, c) => acc + c.messages.length, 0),
      preEditedMessages: conversations.reduce(
        (acc, c) => acc + c.messages.filter((m) => m.editedAt !== null).length,
        0,
      ),
      preDeletedMessages: conversations.reduce(
        (acc, c) => acc + c.messages.filter((m) => m.deletedAt !== null).length,
        0,
      ),
    },
  };
}

export async function applySeedPlan(chatDb, plan, toObjectId) {
  const convCol = chatDb.collection('chat_conversations');
  const membersCol = chatDb.collection('chat_members');
  const msgsCol = chatDb.collection('chat_conversation_messages');

  const summaryConversations = [];

  for (const conv of plan.conversations) {
    const orgOid = toObjectId(conv.organizationId);
    const fallbackConvOid = toObjectId(conv.fallbackConversationId);

    // 1) Upsert conversation by (organizationId, directKey), reusing existing _id if present!
    let existingConv = await convCol.findOne(
      { organizationId: orgOid, directKey: conv.directKey },
      { projection: { _id: 1, lastMessageAt: 1 } },
    );
    let conversationAction = 'REUSED_EXISTING_DIRECT_KEY';
    if (!existingConv) {
      await convCol.updateOne(
        { organizationId: orgOid, directKey: conv.directKey },
        {
          $setOnInsert: {
            _id: fallbackConvOid,
            organizationId: orgOid,
            type: 'DIRECT',
            directKey: conv.directKey,
            title: null,
            createdBy: conv.createdBy,
            lastMessageAt: null,
            lastMessageId: null,
            lastMessagePreview: '',
            lastMessageSenderId: null,
            membershipVersion: 0,
            status: 'ACTIVE',
            createdAt: conv.firstMessageAt,
            updatedAt: conv.firstMessageAt,
          },
        },
        { upsert: true },
      );
      existingConv = await convCol.findOne(
        { organizationId: orgOid, directKey: conv.directKey },
        { projection: { _id: 1, lastMessageAt: 1 } },
      );
      conversationAction = 'UPSERTED';
    }
    const resolvedConvOid = existingConv._id;

    // 2) Upsert the 2 conversation members by (conversationId, userId).
    let membersUpserted = 0;
    let membersMatched = 0;
    for (const member of conv.members) {
      const res = await membersCol.updateOne(
        { conversationId: resolvedConvOid, userId: member.userId },
        {
          $set: {
            organizationId: orgOid,
            displayName: member.displayName,
            searchLabel: member.searchLabel,
            avatarUrl: member.avatarUrl,
            status: 'ACTIVE',
            updatedAt: conv.lastMessage.createdAt,
          },
          $setOnInsert: {
            _id: toObjectId(member.id),
            conversationId: resolvedConvOid,
            userId: member.userId,
            role: member.role,
            lastReadMessageId: null,
            lastReadAt: null,
            readRecordedAt: null,
            lastDeliveredMessageId: null,
            lastDeliveredAt: null,
            deliveredRecordedAt: null,
            notificationMode: 'ALL',
            isPinned: false,
            isArchived: false,
            markedUnread: false,
            draft: '',
            draftMentionUserIds: [],
            draftUpdatedAt: null,
            joinedAt: member.joinedAt,
            createdAt: member.joinedAt,
          },
        },
        { upsert: true },
      );
      if (res.upsertedCount > 0) membersUpserted += 1;
      else membersMatched += 1;
    }

    // 3) Verify required non-members (e.g. C and Manager in dm_org1_ab) are NOT active members!
    const nonMemberUserIds = conv.verifiedNonMembers.map((nm) => nm.userId);
    if (nonMemberUserIds.length > 0) {
      const unexpectedMembers = await membersCol
        .find(
          {
            conversationId: resolvedConvOid,
            userId: { $in: nonMemberUserIds },
            status: 'ACTIVE',
          },
          { projection: { userId: 1 } },
        )
        .toArray();
      if (unexpectedMembers.length > 0) {
        const offending = unexpectedMembers.map((m) => m.userId).join(', ');
        throw new Error(
          `ACL invariant violated: unexpected non-member user(s) [${offending}] found active in ${conv.key} (${resolvedConvOid}).`,
        );
      }
    }

    // 4) Idempotently upsert every human message by deterministic _id (never touches live/non-seed messages!).
    let messagesUpserted = 0;
    let messagesMatched = 0;
    for (const msg of conv.messages) {
      const msgOid = toObjectId(msg.id);
      const replyOid = msg.replyToMessageId ? toObjectId(msg.replyToMessageId) : null;
      const res = await msgsCol.updateOne(
        { _id: msgOid },
        {
          $set: {
            organizationId: orgOid,
            conversationId: resolvedConvOid,
            senderId: msg.senderId,
            senderName: msg.senderName,
            senderAvatarUrl: msg.senderAvatarUrl,
            clientMessageId: msg.clientMessageId,
            content: msg.content,
            mentionUserIds: msg.mentionUserIds,
            links: msg.links,
            isPinned: msg.isPinned,
            editedAt: msg.editedAt,
            deletedAt: msg.deletedAt,
            reactions: msg.reactions,
            replyToMessageId: replyOid,
            attachments: msg.attachments,
            createdAt: msg.createdAt,
            updatedAt: msg.updatedAt,
          },
        },
        { upsert: true },
      );
      if (res.upsertedCount > 0) messagesUpserted += 1;
      else messagesMatched += 1;
    }

    // 5) Advance lastMessage* only if conversation has no newer live messages!
    const lastMsgOid = toObjectId(conv.lastMessage.id);
    await convCol.updateOne(
      {
        _id: resolvedConvOid,
        organizationId: orgOid,
        $or: [
          { lastMessageAt: null },
          { lastMessageAt: { $lte: conv.lastMessage.createdAt } },
        ],
      },
      {
        $set: {
          lastMessageAt: conv.lastMessage.createdAt,
          lastMessageId: lastMsgOid,
          lastMessagePreview: conv.lastMessage.preview,
          lastMessageSenderId: conv.lastMessage.senderId,
          updatedAt: conv.lastMessage.createdAt,
        },
      },
    );

    summaryConversations.push({
      key: conv.key,
      conversationId: String(resolvedConvOid),
      organizationId: conv.organizationId,
      organizationSlug: conv.organizationSlug,
      organizationSource: conv.organizationSource,
      directKey: conv.directKey,
      action: conversationAction,
      membersUpserted,
      membersMatched,
      messagesUpserted,
      messagesMatched,
      totalSeedMessages: conv.messages.length,
      offPageMessages: conv.offPageCount,
      verifiedNonMembersAbsent: conv.verifiedNonMembers.map((nm) => nm.actorKey),
    });
  }

  return {
    mode: 'apply',
    datasetId: plan.datasetId,
    anchorDate: plan.anchorDate,
    timezone: plan.timezone,
    totals: plan.totals,
    conversations: summaryConversations,
  };
}

export async function verifySeededData(chatDb, plan, toObjectId) {
  const convCol = chatDb.collection('chat_conversations');
  const membersCol = chatDb.collection('chat_members');
  const msgsCol = chatDb.collection('chat_conversation_messages');

  const checks = [];
  for (const conv of plan.conversations) {
    const orgOid = toObjectId(conv.organizationId);
    const convDoc = await convCol.findOne(
      { organizationId: orgOid, directKey: conv.directKey },
      { projection: { _id: 1, type: 1, status: 1 } },
    );
    if (!convDoc) {
      throw new Error(`Verify failed: missing conversation ${conv.key} (${conv.directKey}).`);
    }

    const activeMembers = await membersCol
      .find(
        { conversationId: convDoc._id, status: 'ACTIVE' },
        { projection: { userId: 1 } },
      )
      .toArray();
    const activeIds = new Set(activeMembers.map((m) => String(m.userId).toLowerCase()));
    for (const expectedMember of conv.members) {
      if (!activeIds.has(expectedMember.userId.toLowerCase())) {
        throw new Error(
          `Verify failed: missing active member ${expectedMember.userId} in ${conv.key}.`,
        );
      }
    }
    for (const nonMember of conv.verifiedNonMembers) {
      if (activeIds.has(nonMember.userId.toLowerCase())) {
        throw new Error(
          `Verify failed: forbidden non-member ${nonMember.actorKey} is active in ${conv.key}.`,
        );
      }
    }

    const expectedMsgIds = conv.messages.map((m) => toObjectId(m.id));
    const foundCount = await msgsCol.countDocuments({
      _id: { $in: expectedMsgIds },
      conversationId: convDoc._id,
      organizationId: orgOid,
    });
    if (foundCount !== conv.messages.length) {
      throw new Error(
        `Verify failed: ${conv.key} expected ${conv.messages.length} seeded messages, found ${foundCount}.`,
      );
    }

    checks.push({
      key: conv.key,
      conversationId: String(convDoc._id),
      activeMembersCount: activeMembers.length,
      seededMessagesVerified: foundCount,
      nonMembersVerifiedAbsent: conv.verifiedNonMembers.map((nm) => nm.actorKey),
    });
  }

  return {
    mode: 'verify',
    verified: true,
    anchorDate: plan.anchorDate,
    checks,
  };
}

export function parseCliArgs(argv) {
  const options = {
    mode: 'dry-run',
    anchorDate: null,
    fixturePath: DEFAULT_FIXTURE_PATH,
    org1Slug: null,
    org2Slug: null,
    allowFallbackIam: false,
    envFile: null,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--apply') options.mode = 'apply';
    else if (arg === '--dry-run') options.mode = 'dry-run';
    else if (arg === '--verify') options.mode = 'verify';
    else if (arg === '--allow-fallback-iam') options.allowFallbackIam = true;
    else if (arg === '--anchor-date') options.anchorDate = argv[++i];
    else if (arg === '--fixture') options.fixturePath = path.resolve(argv[++i]);
    else if (arg === '--org1-slug') options.org1Slug = argv[++i];
    else if (arg === '--org2-slug') options.org2Slug = argv[++i];
    else if (arg === '--env-file') options.envFile = path.resolve(argv[++i]);
    else if (arg === '--help' || arg === '-h') options.help = true;
    else throw new Error(`Unknown argument: ${arg}`);
  }
  return options;
}

function parseSimpleDotenv(text) {
  const result = {};
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith('#')) continue;
    const eq = line.indexOf('=');
    if (eq <= 0) continue;
    const key = line.slice(0, eq).trim();
    let value = line.slice(eq + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    result[key] = value;
  }
  return result;
}

async function main() {
  const options = parseCliArgs(process.argv.slice(2));
  if (options.help) {
    console.log(
      [
        'Usage: node seed_dm_chat_dev.mjs [--dry-run | --apply | --verify] [options]',
        'Options:',
        '  --anchor-date YYYY-MM-DD   Anchor date in Asia/Ho_Chi_Minh (default: today)',
        '  --fixture <path>           Path to dm_seed_fixture.json',
        '  --org1-slug <slug>         Override Org 1 slug lookup in continuum_iam',
        '  --org2-slug <slug>         Override Org 2 slug lookup in continuum_iam',
        '  --allow-fallback-iam       Allow fallback deterministic IDs if IAM users are absent',
        '  --env-file <path>          Optional .env file to load MONGODB_URI from (never logged)',
      ].join('\n'),
    );
    return;
  }

  const rawFixture = await fs.readFile(options.fixturePath, 'utf8');
  const fixture = JSON.parse(rawFixture);
  assertFixtureIntegrity(fixture);

  const mergedEnv = { ...process.env };
  if (options.envFile) {
    const dotenvText = await fs.readFile(options.envFile, 'utf8');
    for (const [k, v] of Object.entries(parseSimpleDotenv(dotenvText))) {
      if (!(k in mergedEnv)) mergedEnv[k] = v;
    }
  }

  const mongoUri = mergedEnv.CHAT_MONGODB_URI || mergedEnv.MONGODB_URI || null;
  const anchorDate = resolveAnchorDate(options.anchorDate);

  if (options.mode === 'dry-run' && !mongoUri) {
    const fallbackIds = buildFallbackIdentities(fixture);
    const plan = buildSeedPlan(fixture, fallbackIds, anchorDate);
    console.log(
      JSON.stringify(
        {
          mode: 'dry-run-offline',
          datasetId: plan.datasetId,
          anchorDate: plan.anchorDate,
          timezone: plan.timezone,
          totals: plan.totals,
          conversations: plan.conversations.map((c) => ({
            key: c.key,
            organizationId: c.organizationId,
            organizationSlug: c.organizationSlug,
            organizationSource: c.organizationSource,
            directKey: c.directKey,
            messageCount: c.messages.length,
            offPageMessages: c.offPageCount,
            firstMessageAt: c.firstMessageAt.toISOString(),
            lastMessageAt: c.lastMessage.createdAt.toISOString(),
            verifiedNonMembers: c.verifiedNonMembers.map((nm) => nm.actorKey),
          })),
        },
        null,
        2,
      ),
    );
    return;
  }

  let redactedTarget = null;
  if (options.mode === 'apply') {
    redactedTarget = validateDevelopmentTarget(mergedEnv, mongoUri);
  } else if (mongoUri) {
    // Still parse safely to emit only redacted host metadata.
    const parsed = new URL(mongoUri);
    redactedTarget = {
      protocol: parsed.protocol,
      hostname: parsed.hostname.replace(/^\[|\]$/g, '').toLowerCase(),
    };
  }

  const { MongoClient, ObjectId } = loadMongoDriver();
  const toObjectId = (hex) => new ObjectId(hex);
  const client = new MongoClient(mongoUri, { serverSelectionTimeoutMS: 10_000 });
  await client.connect();

  try {
    const iamDb = client.db(mergedEnv.IAM_DB_NAME || 'continuum_iam');
    const chatDb = client.db(mergedEnv.CHAT_DB_NAME || 'continuum_chat');

    const identities = await resolveIdentitiesFromIam(iamDb, fixture, {
      allowFallbackIam: options.allowFallbackIam || options.mode === 'dry-run',
      org1Slug: options.org1Slug,
      org2Slug: options.org2Slug,
    });
    const plan = buildSeedPlan(fixture, identities, anchorDate);

    if (options.mode === 'dry-run') {
      console.log(
        JSON.stringify(
          {
            mode: 'dry-run-connected',
            target: {
              ...redactedTarget,
              iamDb: iamDb.databaseName,
              chatDb: chatDb.databaseName,
            },
            datasetId: plan.datasetId,
            anchorDate: plan.anchorDate,
            timezone: plan.timezone,
            totals: plan.totals,
            conversations: plan.conversations.map((c) => ({
              key: c.key,
              organizationId: c.organizationId,
              organizationSlug: c.organizationSlug,
              organizationSource: c.organizationSource,
              directKey: c.directKey,
              messageCount: c.messages.length,
              offPageMessages: c.offPageCount,
              verifiedNonMembers: c.verifiedNonMembers.map((nm) => nm.actorKey),
            })),
          },
          null,
          2,
        ),
      );
      return;
    }

    if (options.mode === 'verify') {
      const report = await verifySeededData(chatDb, plan, toObjectId);
      console.log(
        JSON.stringify(
          {
            ...report,
            target: {
              ...redactedTarget,
              iamDb: iamDb.databaseName,
              chatDb: chatDb.databaseName,
            },
          },
          null,
          2,
        ),
      );
      return;
    }

    const report = await applySeedPlan(chatDb, plan, toObjectId);
    console.log(
      JSON.stringify(
        {
          ...report,
          target: {
            ...redactedTarget,
            iamDb: iamDb.databaseName,
            chatDb: chatDb.databaseName,
          },
        },
        null,
        2,
      ),
    );
  } finally {
    await client.close();
  }
}

const isDirectExecution =
  process.argv[1] && path.resolve(process.argv[1]) === path.resolve(__filename);
if (isDirectExecution) {
  main().catch((err) => {
    // Emit only the error message (never dump process.env or raw URIs).
    console.error('[seed_dm_chat_dev] ERROR:', err.message);
    process.exitCode = 1;
  });
}
