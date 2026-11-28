#!/usr/bin/env node
/**
 * Safe dev seeder for the synthetic Vietnamese 1-1 DM dataset (`continuum-dm-ai-dataset`).
 *
 * Safety invariants:
 * - Defaults to `--dry-run` (zero DB writes unless `--apply` is explicitly passed).
 * - Requires isolated development environment (`NODE_ENV=development` AND `DATN_DB_ENV=development`),
 *   exact service-owned databases (`continuum_iam` & `continuum_chat`), explicit approved dev target
 *   allowlist (loopback OR explicitly allowlisted non-prod cluster host), and approved dev
 *   organizations (`continuum-ai-labs` & `datn-dev`) before `--apply`.
 * - Never prints credentials, MongoDB URIs, password hashes, or tokens.
 * - Default `--apply` is strictly insert-only (`$setOnInsert`) for conversations, members, and
 *   messages with fail-closed cross-conversation/org `_id` collision detection so live E2E edits,
 *   deletions, and revoked members are never overwritten.
 * - Explicit `--apply --reset-fixture` restores ONLY fixture-owned member & message records back to
 *   their clean baseline while preserving non-fixture live/AI messages.
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
export const APPROVED_CHAT_DB_NAME = 'continuum_chat';
export const APPROVED_IAM_DB_NAME = 'continuum_iam';
export const LOOPBACK_HOSTS = new Set(['127.0.0.1', 'localhost', '::1']);
export const APPROVED_DEV_ORG_SLUGS = Object.freeze({
  org1: Object.freeze(['continuum-ai-labs']),
  org2: Object.freeze(['datn-dev']),
});
const DEVELOPMENT_ENVIRONMENT = 'development';
const ALLOWED_MONGODB_SCHEMES = new Set(['mongodb:', 'mongodb+srv:']);
const OBJECT_ID_RE = /^[a-f0-9]{24}$/i;
const UUID_V4_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const ISO_DATE_RE = /^(\d{4})-(\d{2})-(\d{2})$/;
const LOCAL_TIME_RE = /^(\d{2}):(\d{2}):(\d{2})$/;
const FORBIDDEN_REMOTE_HOST_RE =
  /(^|[.-])(prod|production|prd|live|staging|stage|stg|uat|preprod)([.-]|$)/i;
const APPROVED_DEV_REMOTE_HOST_RE =
  /(^|[.-])(dev|development|sandbox|local|test)([.-]|$)/i;
const SAFE_HOSTNAME_RE = /^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/i;

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

export function parseApprovedClusterHosts(rawAllowlist) {
  const entries = Array.isArray(rawAllowlist)
    ? rawAllowlist
    : String(rawAllowlist ?? '')
        .split(',')
        .map((item) => item.trim());
  const hosts = new Set();
  for (const raw of entries) {
    const entry = String(raw ?? '').trim().toLowerCase().replace(/\.$/, '');
    if (!entry) continue;
    if (
      entry.includes('*') ||
      entry.includes('://') ||
      entry.includes('/') ||
      entry.includes('@') ||
      /\s/.test(entry) ||
      !SAFE_HOSTNAME_RE.test(entry)
    ) {
      throw new Error(
        `Safety guard: invalid --approved-cluster-host / DATN_SEED_APPROVED_CLUSTER_HOST entry "${entry}". Expected exact DNS hostname(s) with no wildcards or credentials.`,
      );
    }
    hosts.add(entry);
  }
  return hosts;
}

export function assertApprovedDevTarget(env, mongoUri, options = {}) {
  if (
    env?.DATN_DB_ENV !== DEVELOPMENT_ENVIRONMENT ||
    env?.NODE_ENV !== DEVELOPMENT_ENVIRONMENT
  ) {
    throw new Error(
      'Safety guard: DATN_DB_ENV and NODE_ENV must both be exactly "development" for --apply.',
    );
  }

  const chatDb = String(
    options.chatDbName ?? env?.CHAT_DB_NAME ?? APPROVED_CHAT_DB_NAME,
  ).trim();
  const iamDb = String(
    options.iamDbName ?? env?.IAM_DB_NAME ?? APPROVED_IAM_DB_NAME,
  ).trim();
  if (chatDb !== APPROVED_CHAT_DB_NAME) {
    throw new Error(
      `Safety guard: CHAT_DB_NAME must be exactly "${APPROVED_CHAT_DB_NAME}" for --apply (got "${chatDb}").`,
    );
  }
  if (iamDb !== APPROVED_IAM_DB_NAME) {
    throw new Error(
      `Safety guard: IAM_DB_NAME must be exactly "${APPROVED_IAM_DB_NAME}" for --apply (got "${iamDb}").`,
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

  const hostname = parsed.hostname
    .replace(/^\[|\]$/g, '')
    .toLowerCase()
    .replace(/\.$/, '');
  if (hostname === '0.0.0.0' || hostname === '::') {
    throw new Error('Safety guard: MONGODB_URI must not use an unspecified host address.');
  }

  if (!['', '/'].includes(parsed.pathname)) {
    throw new Error(
      'Safety guard: MONGODB_URI must not select a database in the path; service-owned DB names (continuum_iam / continuum_chat) are selected explicitly.',
    );
  }

  const isLoopback = LOOPBACK_HOSTS.has(hostname) && parsed.protocol === 'mongodb:';
  if (!isLoopback) {
    if (FORBIDDEN_REMOTE_HOST_RE.test(hostname)) {
      throw new Error(
        `Safety guard: refusing non-dev / production-like MongoDB hostname "${hostname}".`,
      );
    }

    if (!APPROVED_DEV_REMOTE_HOST_RE.test(hostname)) {
      throw new Error(
        `Safety guard: remote MongoDB hostname "${hostname}" does not match an approved dev/sandbox host naming pattern.`,
      );
    }

    const rawAllowlist =
      options.approvedClusterHost ?? env?.DATN_SEED_APPROVED_CLUSTER_HOST ?? '';
    const approvedHosts = parseApprovedClusterHosts(rawAllowlist);
    if (!approvedHosts.has(hostname)) {
      throw new Error(
        `Safety guard: remote MongoDB host "${hostname}" is not in the approved dev cluster allowlist. ` +
          `Explicitly pass --approved-cluster-host=${hostname} or set DATN_SEED_APPROVED_CLUSTER_HOST ` +
          '(passing --allow-shared-database never bypasses the approved cluster allowlist).',
      );
    }

    const disablesTls = [...parsed.searchParams.entries()].some(
      ([name, value]) =>
        ['tls', 'ssl'].includes(name.toLowerCase()) &&
        ['false', '0', 'no'].includes(value.toLowerCase()),
    );
    if (disablesTls) {
      throw new Error(
        'Safety guard: remote development MONGODB_URI must not disable TLS.',
      );
    }

    if (parsed.protocol === 'mongodb+srv:') {
      const labels = hostname.split('.');
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
    }
  }

  // Return strictly redacted metadata (never credentials or raw URI).
  return {
    protocol: parsed.protocol,
    hostname,
    targetClass: isLoopback ? 'loopback' : 'approved-remote-dev',
    iamDb,
    chatDb,
  };
}

export const validateDevelopmentTarget = assertApprovedDevTarget;

export function assertApprovedDevOrganizations(identities, fixture, options = {}) {
  const {
    targetClass = 'loopback',
    allowFallbackIam = false,
    approvedOrg1Id = null,
    approvedOrg2Id = null,
  } = options;

  const org1 = identities?.orgsByKey?.org1;
  const org2 = identities?.orgsByKey?.org2;
  if (!org1 || !org2) {
    throw new Error('Safety guard: resolved identities must contain both org1 and org2.');
  }
  if (!OBJECT_ID_RE.test(String(org1.id ?? '')) || !OBJECT_ID_RE.test(String(org2.id ?? ''))) {
    throw new Error('Safety guard: resolved organization IDs must be valid 24-hex ObjectIds.');
  }
  if (org1.id.toLowerCase() === org2.id.toLowerCase()) {
    throw new Error('Safety guard: Org 1 and Org 2 must resolve to distinct organizationIds.');
  }

  const org1Spec = fixture?.organizations?.find((o) => o.key === 'org1');
  const org2Spec = fixture?.organizations?.find((o) => o.key === 'org2');
  const org1Slug = String(org1.slug ?? '').toLowerCase();
  const org2Slug = String(org2.slug ?? '').toLowerCase();
  const isRemote = targetClass !== 'loopback';

  if (org1.source === 'continuum_iam') {
    if (!APPROVED_DEV_ORG_SLUGS.org1.includes(org1Slug)) {
      throw new Error(
        `Safety guard: resolved Org 1 slug "${org1Slug}" in continuum_iam is not in the approved dev org allowlist [${APPROVED_DEV_ORG_SLUGS.org1.join(', ')}].`,
      );
    }
  } else {
    if (isRemote || !allowFallbackIam) {
      throw new Error(
        'Safety guard: Org 1 must resolve to an approved dev organization ("continuum-ai-labs") in continuum_iam.',
      );
    }
    if (
      org1Slug !== String(org1Spec?.slug ?? '').toLowerCase() ||
      org1.id.toLowerCase() !== String(org1Spec?.fallbackId ?? '').toLowerCase()
    ) {
      throw new Error(
        `Safety guard: Org 1 fallback identity (${org1Slug}/${org1.id}) does not match fixture baseline.`,
      );
    }
  }

  if (org2.source === 'continuum_iam') {
    if (!APPROVED_DEV_ORG_SLUGS.org2.includes(org2Slug)) {
      throw new Error(
        `Safety guard: resolved Org 2 slug "${org2Slug}" in continuum_iam is not in the approved dev org allowlist [${APPROVED_DEV_ORG_SLUGS.org2.join(', ')}].`,
      );
    }
  } else {
    if (isRemote) {
      throw new Error(
        `Safety guard: remote target requires Org 2 to resolve to an approved dev organization [${APPROVED_DEV_ORG_SLUGS.org2.join(', ')}] in continuum_iam (fallback identities are blocked on remote clusters).`,
      );
    }
    if (
      org2Slug !== String(org2Spec?.slug ?? '').toLowerCase() ||
      org2.id.toLowerCase() !== String(org2Spec?.fallbackId ?? '').toLowerCase()
    ) {
      throw new Error(
        `Safety guard: Org 2 fallback identity (${org2Slug}/${org2.id}) does not match fixture baseline.`,
      );
    }
  }

  if (approvedOrg1Id) {
    const pinned1 = String(approvedOrg1Id).trim().toLowerCase();
    if (!OBJECT_ID_RE.test(pinned1)) {
      throw new Error(`Safety guard: invalid --approved-org1-id "${approvedOrg1Id}".`);
    }
    if (org1.id.toLowerCase() !== pinned1) {
      throw new Error(
        `Safety guard: resolved Org 1 ID "${org1.id}" does not match pinned --approved-org1-id "${pinned1}".`,
      );
    }
  }

  if (approvedOrg2Id) {
    const pinned2 = String(approvedOrg2Id).trim().toLowerCase();
    if (!OBJECT_ID_RE.test(pinned2)) {
      throw new Error(`Safety guard: invalid --approved-org2-id "${approvedOrg2Id}".`);
    }
    if (org2.id.toLowerCase() !== pinned2) {
      throw new Error(
        `Safety guard: resolved Org 2 ID "${org2.id}" does not match pinned --approved-org2-id "${pinned2}".`,
      );
    }
  }

  return {
    org1: { id: org1.id, slug: org1Slug, source: org1.source },
    org2: { id: org2.id, slug: org2Slug, source: org2.source },
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
        orgDocs.find((o) => String(o.slug ?? '').toLowerCase() === org1Spec.slug.toLowerCase()) ??
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

    const liveE2eCandidateIds = Object.values(conv.liveE2eCandidates ?? {})
      .map((cand) => String(cand?.messageId ?? '').toLowerCase())
      .filter((id) => OBJECT_ID_RE.test(id));

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
      liveE2eCandidateIds,
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

export async function applySeedPlan(
  chatDb,
  plan,
  toObjectId,
  { resetFixture = false } = {},
) {
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
      const collidingConv = await convCol.findOne(
        { _id: fallbackConvOid },
        { projection: { _id: 1, organizationId: 1, directKey: 1 } },
      );
      if (
        collidingConv &&
        (String(collidingConv.organizationId ?? '').toLowerCase() !== conv.organizationId ||
          collidingConv.directKey !== conv.directKey)
      ) {
        throw new Error(
          `Conversation ID collision: fixture conversation _id ${conv.fallbackConversationId} already belongs to ` +
            `(organizationId=${collidingConv.organizationId}, directKey=${collidingConv.directKey}).`,
        );
      }

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
    const resolvedConvIdHex = String(resolvedConvOid).toLowerCase();

    // 2) Insert-only default for conversation members ($setOnInsert); explicit --reset-fixture restores fixture-owned members.
    let membersUpserted = 0;
    let membersMatched = 0;
    let membersReset = 0;
    for (const member of conv.members) {
      const memberOid = toObjectId(member.id);
      const existingById = await membersCol.findOne(
        { _id: memberOid },
        { projection: { _id: 1, organizationId: 1, conversationId: 1, userId: 1 } },
      );
      if (
        existingById &&
        (String(existingById.organizationId ?? '').toLowerCase() !== conv.organizationId ||
          String(existingById.conversationId ?? '').toLowerCase() !== resolvedConvIdHex ||
          String(existingById.userId ?? '').toLowerCase() !== member.userId.toLowerCase())
      ) {
        throw new Error(
          `Member ID collision: fixture member _id ${member.id} already belongs to another scope ` +
            `(existing org=${existingById.organizationId}, conv=${existingById.conversationId}, user=${existingById.userId}; ` +
            `expected org=${conv.organizationId}, conv=${resolvedConvIdHex}, user=${member.userId}).`,
        );
      }

      const existingByPair = await membersCol.findOne(
        { conversationId: resolvedConvOid, userId: member.userId },
        { projection: { _id: 1, organizationId: 1, status: 1 } },
      );
      if (
        existingByPair &&
        existingByPair.organizationId !== undefined &&
        existingByPair.organizationId !== null &&
        String(existingByPair.organizationId).toLowerCase() !== conv.organizationId
      ) {
        throw new Error(
          `Member scope collision: existing member (${resolvedConvIdHex}, ${member.userId}) belongs to ` +
            `organizationId=${existingByPair.organizationId}, expected ${conv.organizationId}.`,
        );
      }

      const memberInsertDoc = {
        _id: memberOid,
        organizationId: orgOid,
        conversationId: resolvedConvOid,
        userId: member.userId,
        displayName: member.displayName,
        searchLabel: member.searchLabel,
        avatarUrl: member.avatarUrl,
        role: member.role,
        status: 'ACTIVE',
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
        updatedAt: conv.lastMessage.createdAt,
      };

      if (resetFixture && existingByPair) {
        await membersCol.updateOne(
          {
            _id: existingByPair._id,
            conversationId: resolvedConvOid,
            userId: member.userId,
          },
          {
            $set: {
              organizationId: orgOid,
              displayName: member.displayName,
              searchLabel: member.searchLabel,
              avatarUrl: member.avatarUrl,
              role: member.role,
              status: 'ACTIVE',
              updatedAt: conv.lastMessage.createdAt,
            },
          },
          { upsert: false },
        );
        membersReset += 1;
      } else {
        const res = await membersCol.updateOne(
          { conversationId: resolvedConvOid, userId: member.userId },
          { $setOnInsert: memberInsertDoc },
          { upsert: true },
        );
        if (res.upsertedCount > 0) membersUpserted += 1;
        else membersMatched += 1;
      }
    }

    // 3) Verify NO unexpected active members (including C, Manager, Org 2, or any extra 3rd member) exist in this DM!
    const expectedMemberIds = new Set(conv.members.map((m) => m.userId.toLowerCase()));
    const activeMembers = await membersCol
      .find(
        { conversationId: resolvedConvOid, status: 'ACTIVE' },
        { projection: { userId: 1 } },
      )
      .toArray();
    const unexpectedMembers = activeMembers.filter(
      (m) => !expectedMemberIds.has(String(m.userId).toLowerCase()),
    );
    if (unexpectedMembers.length > 0) {
      const offending = unexpectedMembers.map((m) => m.userId).join(', ');
      throw new Error(
        `ACL invariant violated: unexpected active member(s) [${offending}] found in ${conv.key} (${resolvedConvOid}).`,
      );
    }

    // 4) Pre-write collision check across ALL fixture message _ids in this conversation!
    const convMsgOids = conv.messages.map((m) => toObjectId(m.id));
    const existingMsgs = await msgsCol
      .find(
        { _id: { $in: convMsgOids } },
        { projection: { _id: 1, organizationId: 1, conversationId: 1 } },
      )
      .toArray();
    const existingMsgById = new Map(
      existingMsgs.map((doc) => [String(doc._id).toLowerCase(), doc]),
    );
    for (const msg of conv.messages) {
      const existing = existingMsgById.get(msg.id);
      if (!existing) continue;
      const existingOrg = String(existing.organizationId ?? '').toLowerCase();
      const existingConvId = String(existing.conversationId ?? '').toLowerCase();
      if (existingOrg !== conv.organizationId || existingConvId !== resolvedConvIdHex) {
        throw new Error(
          `Message ID collision: fixture _id ${msg.id} already belongs to another conversation/organization ` +
            `(existing org=${existingOrg || 'missing'}, conv=${existingConvId || 'missing'}; ` +
            `expected org=${conv.organizationId}, conv=${resolvedConvIdHex}).`,
        );
      }
    }

    // 5) Strictly insert-only ($setOnInsert) by default; --reset-fixture restores ONLY verified fixture-owned _ids.
    let messagesUpserted = 0;
    let messagesMatched = 0;
    let messagesReset = 0;
    for (const msg of conv.messages) {
      const msgOid = toObjectId(msg.id);
      const replyOid = msg.replyToMessageId ? toObjectId(msg.replyToMessageId) : null;
      const baselineFields = {
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
      };

      if (resetFixture && existingMsgById.has(msg.id)) {
        await msgsCol.updateOne(
          {
            _id: msgOid,
            organizationId: orgOid,
            conversationId: resolvedConvOid,
          },
          {
            $set: baselineFields,
            $unset: {
              contentVersion: '',
              authorType: '',
              assistantMention: '',
              triggerMessageId: '',
              assistantStatus: '',
              assistantMeta: '',
              sourceReferences: '',
            },
          },
          { upsert: false },
        );
        messagesReset += 1;
      } else {
        const res = await msgsCol.updateOne(
          { _id: msgOid },
          {
            $setOnInsert: {
              _id: msgOid,
              ...baselineFields,
            },
          },
          { upsert: true },
        );
        if (res.upsertedCount > 0) messagesUpserted += 1;
        else messagesMatched += 1;
      }
    }

    // 6) Advance lastMessage* only if conversation has no newer live messages (and never clobber same-ts in default mode)!
    const lastMsgOid = toObjectId(conv.lastMessage.id);
    const lastMessageComparator = resetFixture
      ? { $lte: conv.lastMessage.createdAt }
      : { $lt: conv.lastMessage.createdAt };
    await convCol.updateOne(
      {
        _id: resolvedConvOid,
        organizationId: orgOid,
        $or: [
          { lastMessageAt: null },
          { lastMessageAt: lastMessageComparator },
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
      membersReset,
      messagesUpserted,
      messagesMatched,
      messagesReset,
      totalSeedMessages: conv.messages.length,
      offPageMessages: conv.offPageCount,
      verifiedNonMembersAbsent: conv.verifiedNonMembers.map((nm) => nm.actorKey),
    });
  }

  return {
    mode: resetFixture ? 'apply-reset-fixture' : 'apply',
    resetFixture: Boolean(resetFixture),
    datasetId: plan.datasetId,
    anchorDate: plan.anchorDate,
    timezone: plan.timezone,
    totals: plan.totals,
    conversations: summaryConversations,
  };
}

export async function verifySeededData(
  chatDb,
  plan,
  toObjectId,
  { allowE2eMutations = false, throwOnFailure = true } = {},
) {
  const convCol = chatDb.collection('chat_conversations');
  const membersCol = chatDb.collection('chat_members');
  const msgsCol = chatDb.collection('chat_conversation_messages');

  const checks = [];
  const failures = [];

  for (const conv of plan.conversations) {
    const orgOid = toObjectId(conv.organizationId);
    const convDoc = await convCol.findOne(
      { organizationId: orgOid, directKey: conv.directKey },
      { projection: { _id: 1, type: 1, status: 1 } },
    );
    if (!convDoc) {
      failures.push(`Verify failed: missing conversation ${conv.key} (${conv.directKey}).`);
      checks.push({
        key: conv.key,
        conversationFound: false,
        exactMemberSetMatch: false,
        mutatedFixtureMessages: [],
        allowedE2eMutations: [],
      });
      continue;
    }

    const resolvedConvIdHex = String(convDoc._id).toLowerCase();

    // 1) Exact ACTIVE member set equality (no missing members, no forbidden non-members, no extra 3rd member!)
    const activeMembers = await membersCol
      .find(
        { conversationId: convDoc._id, status: 'ACTIVE' },
        { projection: { userId: 1, organizationId: 1 } },
      )
      .toArray();
    const actualActiveMemberIds = activeMembers
      .map((m) => String(m.userId).toLowerCase())
      .sort();
    const expectedActiveMemberIds = conv.members
      .map((m) => m.userId.toLowerCase())
      .sort();
    const actualActiveSet = new Set(actualActiveMemberIds);
    const expectedActiveSet = new Set(expectedActiveMemberIds);

    const missingActiveMemberIds = expectedActiveMemberIds.filter(
      (id) => !actualActiveSet.has(id),
    );
    const unexpectedActiveMemberIds = [...actualActiveSet]
      .filter((id) => !expectedActiveSet.has(id))
      .sort();

    for (const missingId of missingActiveMemberIds) {
      failures.push(`Verify failed: missing active member ${missingId} in ${conv.key}.`);
    }
    for (const nonMember of conv.verifiedNonMembers) {
      if (actualActiveSet.has(nonMember.userId.toLowerCase())) {
        failures.push(
          `Verify failed: forbidden non-member ${nonMember.actorKey} (${nonMember.userId}) is active in ${conv.key}.`,
        );
      }
    }
    if (unexpectedActiveMemberIds.length > 0) {
      failures.push(
        `Verify failed: exact active member set mismatch in ${conv.key}; unexpected active member(s): [${unexpectedActiveMemberIds.join(', ')}].`,
      );
    }
    if (activeMembers.length !== actualActiveSet.size) {
      failures.push(
        `Verify failed: duplicate ACTIVE member rows detected in ${conv.key}.`,
      );
    }
    const wrongOrgMembers = activeMembers.filter(
      (m) =>
        m.organizationId !== undefined &&
        m.organizationId !== null &&
        String(m.organizationId).toLowerCase() !== conv.organizationId,
    );
    if (wrongOrgMembers.length > 0) {
      failures.push(
        `Verify failed: active member organizationId mismatch in ${conv.key}.`,
      );
    }

    const exactMemberSetMatch =
      missingActiveMemberIds.length === 0 &&
      unexpectedActiveMemberIds.length === 0 &&
      activeMembers.length === expectedActiveMemberIds.length &&
      wrongOrgMembers.length === 0 &&
      actualActiveMemberIds.every((id, idx) => id === expectedActiveMemberIds[idx]);

    // 2) Full per-message integrity audit for every fixture message ID
    const expectedMsgIds = conv.messages.map((m) => toObjectId(m.id));
    const actualDocs = await msgsCol
      .find(
        { _id: { $in: expectedMsgIds } },
        {
          projection: {
            _id: 1,
            organizationId: 1,
            conversationId: 1,
            senderId: 1,
            authorType: 1,
            content: 1,
            editedAt: 1,
            deletedAt: 1,
          },
        },
      )
      .toArray();
    const actualById = new Map(
      actualDocs.map((doc) => [String(doc._id).toLowerCase(), doc]),
    );

    const allowedCandidateSet = new Set(conv.liveE2eCandidateIds ?? []);
    const mutatedFixtureMessages = [];
    const allowedE2eMutations = [];
    let exactMatchedMessages = 0;

    for (const expectedMsg of conv.messages) {
      const actual = actualById.get(expectedMsg.id);
      if (!actual) {
        mutatedFixtureMessages.push({
          messageId: expectedMsg.id,
          reasons: ['missing'],
        });
        continue;
      }

      const hardViolations = [];
      if (String(actual.organizationId ?? '').toLowerCase() !== conv.organizationId) {
        hardViolations.push(
          `organizationId_mismatch(actual=${actual.organizationId},expected=${conv.organizationId})`,
        );
      }
      if (String(actual.conversationId ?? '').toLowerCase() !== resolvedConvIdHex) {
        hardViolations.push(
          `conversationId_mismatch(actual=${actual.conversationId},expected=${resolvedConvIdHex})`,
        );
      }
      if (String(actual.senderId ?? '').toLowerCase() !== expectedMsg.senderId.toLowerCase()) {
        hardViolations.push(
          `senderId_mismatch(actual=${actual.senderId},expected=${expectedMsg.senderId})`,
        );
      }
      if (
        actual.authorType === 'ASSISTANT' ||
        String(actual.senderId ?? '').toLowerCase() === 'assistant:continuum_ai' ||
        (actual.authorType !== undefined &&
          actual.authorType !== null &&
          actual.authorType !== 'USER')
      ) {
        hardViolations.push(
          `forbidden_authorType(actual=${actual.authorType ?? actual.senderId})`,
        );
      }

      const contentViolations = [];
      if (actual.content !== expectedMsg.content) {
        contentViolations.push('content_mismatch');
      }
      const actualEdited = actual.editedAt !== null && actual.editedAt !== undefined;
      const expectedEdited = expectedMsg.editedAt !== null && expectedMsg.editedAt !== undefined;
      if (actualEdited !== expectedEdited) {
        contentViolations.push(
          `editedAt_state_mismatch(actual=${actualEdited},expected=${expectedEdited})`,
        );
      }
      const actualDeleted = actual.deletedAt !== null && actual.deletedAt !== undefined;
      const expectedDeleted = expectedMsg.deletedAt !== null && expectedMsg.deletedAt !== undefined;
      if (actualDeleted !== expectedDeleted) {
        contentViolations.push(
          `deletedAt_state_mismatch(actual=${actualDeleted},expected=${expectedDeleted})`,
        );
      }
      if (actualDeleted && actual.content !== '') {
        contentViolations.push('deleted_message_non_empty_content');
      }

      if (hardViolations.length > 0) {
        mutatedFixtureMessages.push({
          messageId: expectedMsg.id,
          reasons: [...hardViolations, ...contentViolations],
        });
      } else if (contentViolations.length > 0) {
        if (allowE2eMutations && allowedCandidateSet.has(expectedMsg.id)) {
          allowedE2eMutations.push({
            messageId: expectedMsg.id,
            reasons: contentViolations,
          });
        } else {
          mutatedFixtureMessages.push({
            messageId: expectedMsg.id,
            reasons: contentViolations,
          });
        }
      } else {
        exactMatchedMessages += 1;
      }
    }

    if (mutatedFixtureMessages.length > 0) {
      const detail = mutatedFixtureMessages
        .slice(0, 10)
        .map((m) => `${m.messageId}[${m.reasons.join(',')}]`)
        .join('; ');
      failures.push(
        `Verify failed: ${conv.key} has ${mutatedFixtureMessages.length} corrupted/mutated fixture message(s): ${detail}.`,
      );
    }

    checks.push({
      key: conv.key,
      conversationId: String(convDoc._id),
      exactMemberSetMatch,
      activeMembersCount: activeMembers.length,
      actualActiveMemberIds,
      expectedActiveMemberIds,
      missingActiveMemberIds,
      unexpectedActiveMemberIds,
      seededMessagesVerified: exactMatchedMessages + allowedE2eMutations.length,
      exactMatchedMessages,
      mutatedFixtureMessages,
      allowedE2eMutations,
      nonMembersVerifiedAbsent: conv.verifiedNonMembers
        .filter((nm) => !actualActiveSet.has(nm.userId.toLowerCase()))
        .map((nm) => nm.actorKey),
    });
  }

  const report = {
    mode: 'verify',
    verified: failures.length === 0,
    allowE2eMutations: Boolean(allowE2eMutations),
    anchorDate: plan.anchorDate,
    failures,
    checks,
  };

  if (!report.verified && throwOnFailure) {
    const err = new Error(failures.join(' | '));
    err.report = report;
    throw err;
  }

  return report;
}

export function parseCliArgs(argv) {
  const options = {
    mode: 'dry-run',
    anchorDate: null,
    fixturePath: DEFAULT_FIXTURE_PATH,
    org1Slug: null,
    org2Slug: null,
    allowFallbackIam: false,
    allowSharedDatabase: false,
    approvedClusterHost: null,
    approvedOrg1Id: null,
    approvedOrg2Id: null,
    resetFixture: false,
    allowE2eMutations: false,
    envFile: null,
  };

  function readFlagValue(flag, inlineValue, idx) {
    const val = inlineValue !== undefined ? inlineValue : argv[idx + 1];
    if (val === undefined || val === '' || (inlineValue === undefined && val.startsWith('--'))) {
      throw new Error(`Missing value for argument: ${flag}`);
    }
    return { val, advance: inlineValue === undefined ? 1 : 0 };
  }

  for (let i = 0; i < argv.length; i += 1) {
    const rawArg = argv[i];
    const eqIndex = rawArg.indexOf('=');
    const flag = eqIndex > 0 && rawArg.startsWith('--') ? rawArg.slice(0, eqIndex) : rawArg;
    const inlineValue = eqIndex > 0 && rawArg.startsWith('--') ? rawArg.slice(eqIndex + 1) : undefined;

    if (flag === '--apply') options.mode = 'apply';
    else if (flag === '--dry-run') options.mode = 'dry-run';
    else if (flag === '--verify') options.mode = 'verify';
    else if (flag === '--allow-fallback-iam') options.allowFallbackIam = true;
    else if (flag === '--allow-shared-database') options.allowSharedDatabase = true;
    else if (flag === '--reset-fixture') options.resetFixture = true;
    else if (flag === '--allow-e2e-mutations') options.allowE2eMutations = true;
    else if (flag === '--approved-cluster-host') {
      const { val, advance } = readFlagValue(flag, inlineValue, i);
      options.approvedClusterHost = val;
      i += advance;
    } else if (flag === '--approved-org1-id') {
      const { val, advance } = readFlagValue(flag, inlineValue, i);
      options.approvedOrg1Id = val;
      i += advance;
    } else if (flag === '--approved-org2-id') {
      const { val, advance } = readFlagValue(flag, inlineValue, i);
      options.approvedOrg2Id = val;
      i += advance;
    } else if (flag === '--anchor-date') {
      const { val, advance } = readFlagValue(flag, inlineValue, i);
      options.anchorDate = val;
      i += advance;
    } else if (flag === '--fixture') {
      const { val, advance } = readFlagValue(flag, inlineValue, i);
      options.fixturePath = path.resolve(val);
      i += advance;
    } else if (flag === '--org1-slug') {
      const { val, advance } = readFlagValue(flag, inlineValue, i);
      options.org1Slug = val;
      i += advance;
    } else if (flag === '--org2-slug') {
      const { val, advance } = readFlagValue(flag, inlineValue, i);
      options.org2Slug = val;
      i += advance;
    } else if (flag === '--env-file') {
      const { val, advance } = readFlagValue(flag, inlineValue, i);
      options.envFile = path.resolve(val);
      i += advance;
    } else if (flag === '--help' || flag === '-h') options.help = true;
    else throw new Error(`Unknown argument: ${rawArg}`);
  }

  if (options.resetFixture && options.mode !== 'apply') {
    throw new Error('Safety guard: --reset-fixture requires --apply.');
  }
  if (options.allowE2eMutations && options.mode !== 'verify') {
    throw new Error('Safety guard: --allow-e2e-mutations is only valid with --verify.');
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
        '  --anchor-date YYYY-MM-DD         Anchor date in Asia/Ho_Chi_Minh (default: today)',
        '  --fixture <path>                 Path to dm_seed_fixture.json',
        '  --approved-cluster-host <host>   Explicitly allowlisted non-prod remote cluster host (or DATN_SEED_APPROVED_CLUSTER_HOST)',
        '  --approved-org1-id <24-hex>      Optional pinned ObjectId for Org 1 (continuum-ai-labs)',
        '  --approved-org2-id <24-hex>      Optional pinned ObjectId for Org 2 (datn-dev)',
        '  --reset-fixture                  Explicitly restore fixture-owned members & messages (requires --apply)',
        '  --allow-e2e-mutations            Allow live E2E mutations ONLY on candidates #59/#60/#61 during --verify',
        '  --org1-slug <slug>               Override Org 1 slug lookup in continuum_iam (still checked against dev allowlist)',
        '  --org2-slug <slug>               Override Org 2 slug lookup in continuum_iam (still checked against dev allowlist)',
        '  --allow-fallback-iam             Allow fallback deterministic IDs on loopback sandbox when IAM users are absent',
        '  --env-file <path>                Optional .env file to load MONGODB_URI from (never logged)',
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
    redactedTarget = assertApprovedDevTarget(mergedEnv, mongoUri, {
      approvedClusterHost: options.approvedClusterHost,
      allowSharedDatabase: options.allowSharedDatabase,
    });
  } else if (mongoUri) {
    // Still parse safely to emit only redacted host metadata.
    const parsed = new URL(mongoUri);
    redactedTarget = {
      protocol: parsed.protocol,
      hostname: parsed.hostname.replace(/^\[|\]$/g, '').toLowerCase().replace(/\.$/, ''),
      iamDb: mergedEnv.IAM_DB_NAME || APPROVED_IAM_DB_NAME,
      chatDb: mergedEnv.CHAT_DB_NAME || APPROVED_CHAT_DB_NAME,
    };
  } else {
    throw new Error('Safety guard: MONGODB_URI (or CHAT_MONGODB_URI) is required for --verify.');
  }

  const { MongoClient, ObjectId } = loadMongoDriver();
  const toObjectId = (hex) => new ObjectId(hex);
  const client = new MongoClient(mongoUri, { serverSelectionTimeoutMS: 10_000 });
  await client.connect();

  try {
    const iamDb = client.db(redactedTarget.iamDb || APPROVED_IAM_DB_NAME);
    const chatDb = client.db(redactedTarget.chatDb || APPROVED_CHAT_DB_NAME);

    const identities = await resolveIdentitiesFromIam(iamDb, fixture, {
      allowFallbackIam: options.allowFallbackIam || options.mode === 'dry-run',
      org1Slug: options.org1Slug,
      org2Slug: options.org2Slug,
    });

    if (options.mode === 'apply') {
      assertApprovedDevOrganizations(identities, fixture, {
        targetClass: redactedTarget.targetClass,
        allowFallbackIam: options.allowFallbackIam,
        approvedOrg1Id:
          options.approvedOrg1Id ?? mergedEnv.DATN_SEED_APPROVED_ORG1_ID ?? null,
        approvedOrg2Id:
          options.approvedOrg2Id ?? mergedEnv.DATN_SEED_APPROVED_ORG2_ID ?? null,
      });
    }

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
      const report = await verifySeededData(chatDb, plan, toObjectId, {
        allowE2eMutations: options.allowE2eMutations,
        throwOnFailure: false,
      });
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
      if (!report.verified) {
        process.exitCode = 1;
      }
      return;
    }

    const report = await applySeedPlan(chatDb, plan, toObjectId, {
      resetFixture: options.resetFixture,
    });
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
