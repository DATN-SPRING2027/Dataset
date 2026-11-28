#!/usr/bin/env node
/**
 * Safe multi-DB dev seeder for the WDP301-SPRING-2027 Full 360° synthetic dataset.
 *
 * Safety invariants:
 * - Defaults to `--dry-run` (zero DB writes unless `--apply` or `--reset-fixture` is explicitly passed).
 * - Requires isolated development environment (`NODE_ENV=development` AND `DATN_DB_ENV=development`),
 *   exact service-owned databases (`continuum_iam`, `continuum_chat`, `continuum_task`,
 *   `continuum_capture`, `continuum_handover`), exact `--expected-org-id=6ad76c7d938f3bf53df7335e`,
 *   and for non-loopback hosts: explicit `--approved-cluster-host`, TLS enforced, auth enforced,
 *   and rejection of any prod/staging/uat/live-like hostname.
 * - Never prints credentials, MongoDB URIs, emails, or tokens.
 * - Strictly additive insert-only (`$setOnInsert`) with fail-closed `_id` collision detection;
 *   100% preserves all pre-existing WDP301 tasks (474), docs (143), old reports (165), archived
 *   project PRTRESDAD131, existing 9 DMs, 4 existing handovers, and legacy messages ("helo", "Danh").
 * - Reuses existing DIRECT conversations cleanly via `directKey`.
 * - `--reset-fixture` deletes ONLY fixture-owned `_id`s (prefix `6f301`), restoring reused DMs'
 *   `lastMessage*` pointers cleanly back to remaining legacy messages.
 */

import { createHash } from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PKG_ROOT = path.resolve(__dirname, '..');
const REPO_ROOT = path.resolve(PKG_ROOT, '..');
const WORKSPACE_ROOT = path.resolve(REPO_ROOT, '..');

export const DEFAULT_CHAT_FIXTURE_PATH = path.join(PKG_ROOT, 'seed', 'chat_fixture.json');
export const DEFAULT_WORKSPACE_FIXTURE_PATH = path.join(
  PKG_ROOT,
  'seed',
  'workspace_enrichment_fixture.json',
);
export const DEFAULT_ACTOR_MAP_PATH = path.join(WORKSPACE_ROOT, '.local', 'wdp301-actor-map.json');
export const DEFAULT_TIMEZONE = 'Asia/Ho_Chi_Minh';
export const DEFAULT_UTC_OFFSET = '+07:00';
export const FIXTURE_ID_PREFIX = '6f301';
export const MEMBER_ID_PREFIX = '6f3019';
export const EXPECTED_ORG_ID = '6ad76c7d938f3bf53df7335e';
export const EXPECTED_ORG_SLUG = 'datn-spring2027';

export const APPROVED_DB_NAMES = Object.freeze({
  iam: 'continuum_iam',
  chat: 'continuum_chat',
  task: 'continuum_task',
  capture: 'continuum_capture',
  handover: 'continuum_handover',
});

export const LOOPBACK_HOSTS = new Set(['127.0.0.1', 'localhost', '::1']);
const ALLOWED_MONGODB_SCHEMES = new Set(['mongodb:', 'mongodb+srv:']);
const OBJECT_ID_RE = /^[a-f0-9]{24}$/i;
const UUID_V4_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const ISO_DATE_RE = /^(\d{4})-(\d{2})-(\d{2})$/;
const LOCAL_TIME_RE = /^(\d{2}):(\d{2}):(\d{2})$/;
const FORBIDDEN_REMOTE_HOST_RE =
  /(^|[.-])(prod|production|prd|live|staging|stage|stg|uat|preprod)([.-]|$)/i;
const SAFE_HOSTNAME_RE = /^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/i;
const TLS_TRUTHY_VALUES = new Set(['true', '1', 'yes']);
const TLS_FALSY_VALUES = new Set(['false', '0', 'no']);
const PASSWORD_AUTH_MECHANISMS = new Set([
  'SCRAM-SHA-256',
  'SCRAM-SHA-1',
  'PLAIN',
  'DEFAULT',
]);
const EXTERNAL_AUTH_MECHANISMS = new Set([
  'MONGODB-AWS',
  'MONGODB-X509',
  'GSSAPI',
  'MONGODB-OIDC',
]);

const FORBIDDEN_SEED_KEYS = new Set([
  'expectedAnswer',
  'goldAnswer',
  'goldAnswers',
  'requiredAnswerFacts',
  'requiredSourceMessageIds',
  'requiredSourceIds',
  'expectedStatus',
  'forbiddenSubstrings',
  'evalCases',
  'groundTruth',
  'password',
  'passwordHash',
]);

const FORBIDDEN_CHAT_MSG_FIELDS = new Set([
  'authorType',
  'assistantMention',
  'triggerMessageId',
  'assistantStatus',
  'assistantFailureCode',
  'assistantMeta',
  'sourceReferences',
]);

export function loadMongoDriver(
  beRoot = process.env.DATN_BE_ROOT || path.join(WORKSPACE_ROOT, 'DATN_BE'),
) {
  const candidates = [
    path.join(beRoot, 'package.json'),
    path.join(WORKSPACE_ROOT, '.local', 'worktrees', 'be-dm-api', 'package.json'),
    path.join(WORKSPACE_ROOT, 'be-dm-api', 'package.json'),
    path.join(WORKSPACE_ROOT, 'DATN_BE', 'package.json'),
    path.resolve(WORKSPACE_ROOT, '..', '..', 'DATN_BE', 'package.json'),
  ];
  for (const pkg of candidates) {
    try {
      const req = createRequire(pathToFileURL(pkg).href);
      return req('mongodb');
    } catch {
      // Try next candidate
    }
  }
  const reqLocal = createRequire(import.meta.url);
  return reqLocal('mongodb');
}

function decodeUriComponentSafe(value) {
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
}

export function stableFixtureMemberIdHex(convIdHex, userIdHex) {
  const hash = createHash('sha256')
    .update(JSON.stringify(['wdp301.member.v1', String(convIdHex).toLowerCase(), String(userIdHex).toLowerCase()]))
    .digest('hex')
    .slice(0, 18);
  return `${MEMBER_ID_PREFIX}${hash}`;
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
  const value = anchorDateInput
    ? String(anchorDateInput).trim()
    : formatTodayInTimezone(now, timeZone);
  const match = ISO_DATE_RE.exec(value);
  if (!match) {
    throw new Error(`Invalid --anchor-date "${value}". Expected YYYY-MM-DD.`);
  }
  const y = Number(match[1]);
  const m = Number(match[2]);
  const d = Number(match[3]);
  const probe = new Date(Date.UTC(y, m - 1, d));
  if (
    probe.getUTCFullYear() !== y ||
    probe.getUTCMonth() !== m - 1 ||
    probe.getUTCDate() !== d
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

export function computeLocalTimestamp(
  anchorDate,
  dayOffset,
  timeLocal = '09:00:00',
  utcOffset = DEFAULT_UTC_OFFSET,
) {
  if (!LOCAL_TIME_RE.test(String(timeLocal))) {
    throw new Error(`Invalid timeLocal "${timeLocal}". Expected HH:MM:SS.`);
  }
  const localDate = shiftIsoDate(anchorDate, dayOffset);
  const dt = new Date(`${localDate}T${timeLocal}${utcOffset}`);
  if (!Number.isFinite(dt.valueOf())) {
    throw new Error(`Failed to compute timestamp for ${localDate}T${timeLocal}${utcOffset}.`);
  }
  return dt;
}

export function computeMessageTimestamps(anchorDate, message, utcOffset = DEFAULT_UTC_OFFSET) {
  const createdAt = computeLocalTimestamp(anchorDate, message.dayOffset, message.timeLocal, utcOffset);
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
  return { createdAt, editedAt, deletedAt, updatedAt };
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

export function parseApprovedClusterHosts(rawAllowlist) {
  const entries = Array.isArray(rawAllowlist)
    ? rawAllowlist
    : String(rawAllowlist ?? '')
        .split(',')
        .map((s) => s.trim());
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
        `Safety guard: invalid --approved-cluster-host entry "${entry}". Expected exact DNS hostname(s) with no wildcards or credentials.`,
      );
    }
    hosts.add(entry);
  }
  return hosts;
}

export function assertApprovedDevTarget(env, mongoUri, options = {}) {
  if (env?.DATN_DB_ENV !== 'development' || env?.NODE_ENV !== 'development') {
    throw new Error(
      'Safety guard: NODE_ENV and DATN_DB_ENV must both be exactly "development" for write operations.',
    );
  }

  const expectedOrgId = String(options.expectedOrgId ?? '').trim().toLowerCase();
  if (expectedOrgId !== EXPECTED_ORG_ID) {
    throw new Error(
      `Safety guard: --expected-org-id must be explicitly set to "${EXPECTED_ORG_ID}" for WDP301-SPRING-2027 writes.`,
    );
  }

  const dbChecks = [
    ['IAM_DB_NAME', options.iamDbName ?? env?.IAM_DB_NAME ?? APPROVED_DB_NAMES.iam, APPROVED_DB_NAMES.iam],
    ['CHAT_DB_NAME', options.chatDbName ?? env?.CHAT_DB_NAME ?? APPROVED_DB_NAMES.chat, APPROVED_DB_NAMES.chat],
    ['TASK_DB_NAME', options.taskDbName ?? env?.TASK_DB_NAME ?? APPROVED_DB_NAMES.task, APPROVED_DB_NAMES.task],
    ['CAPTURE_DB_NAME', options.captureDbName ?? env?.CAPTURE_DB_NAME ?? APPROVED_DB_NAMES.capture, APPROVED_DB_NAMES.capture],
    ['HANDOVER_DB_NAME', options.handoverDbName ?? env?.HANDOVER_DB_NAME ?? APPROVED_DB_NAMES.handover, APPROVED_DB_NAMES.handover],
  ];
  for (const [label, actual, expected] of dbChecks) {
    if (String(actual).trim() !== expected) {
      throw new Error(`Safety guard: ${label} must be exactly "${expected}" (got "${actual}").`);
    }
  }

  if (!mongoUri || typeof mongoUri !== 'string') {
    throw new Error('Safety guard: MONGODB_URI is required.');
  }

  let parsed;
  try {
    parsed = new URL(mongoUri);
  } catch {
    throw new Error('Safety guard: MONGODB_URI must be a valid MongoDB URI.');
  }
  if (!ALLOWED_MONGODB_SCHEMES.has(parsed.protocol)) {
    throw new Error('Safety guard: MONGODB_URI must use mongodb:// or mongodb+srv://.');
  }

  const authorityStart = mongoUri.indexOf('://') + 3;
  const authority = mongoUri.slice(authorityStart).split(/[/?#]/, 1)[0];
  const hosts = authority.slice(authority.lastIndexOf('@') + 1);
  if (!parsed.hostname || !hosts || hosts.includes(',')) {
    throw new Error('Safety guard: MONGODB_URI must identify exactly one host.');
  }

  const hostname = parsed.hostname.replace(/^\[|\]$/g, '').toLowerCase().replace(/\.$/, '');
  if (hostname === '0.0.0.0' || hostname === '::') {
    throw new Error('Safety guard: MONGODB_URI must not use an unspecified host address.');
  }
  if (!['', '/'].includes(parsed.pathname)) {
    throw new Error(
      'Safety guard: MONGODB_URI must not select a database in the path; service-owned DBs are selected explicitly.',
    );
  }

  const isLoopback = LOOPBACK_HOSTS.has(hostname) && parsed.protocol === 'mongodb:';
  if (!isLoopback) {
    if (FORBIDDEN_REMOTE_HOST_RE.test(hostname)) {
      throw new Error(
        `Safety guard: refusing production/staging-like MongoDB hostname "${hostname}".`,
      );
    }

    const rawAllowlist =
      options.approvedClusterHost ?? env?.DATN_SEED_APPROVED_CLUSTER_HOST ?? '';
    const approvedHosts = parseApprovedClusterHosts(rawAllowlist);
    if (!approvedHosts.has(hostname)) {
      throw new Error(
        `Safety guard: remote MongoDB host "${hostname}" is not allowlisted. ` +
          `Pass --approved-cluster-host=${hostname} or set DATN_SEED_APPROVED_CLUSTER_HOST.`,
      );
    }

    let hasExplicitTlsTrue = false;
    const authMechanisms = [];
    for (const [rawName, rawValue] of parsed.searchParams.entries()) {
      const name = rawName.toLowerCase();
      const value = rawValue.trim().toLowerCase();
      if (name === 'tls' || name === 'ssl') {
        if (TLS_FALSY_VALUES.has(value)) {
          throw new Error(`Safety guard: remote MongoDB connection must enforce TLS (${rawName}=${rawValue} is forbidden).`);
        }
        if (TLS_TRUTHY_VALUES.has(value)) hasExplicitTlsTrue = true;
      } else if (
        name === 'tlsinsecure' ||
        name === 'tlsallowinvalidcertificates' ||
        name === 'tlsallowinvalidhostnames'
      ) {
        if (TLS_TRUTHY_VALUES.has(value)) {
          throw new Error(`Safety guard: weakening TLS via ${rawName}=${rawValue} is forbidden.`);
        }
      } else if (name === 'sslvalidate') {
        if (TLS_FALSY_VALUES.has(value)) {
          throw new Error(`Safety guard: weakening TLS via ${rawName}=${rawValue} is forbidden.`);
        }
      } else if (name === 'authmechanism') {
        if (rawValue.trim()) authMechanisms.push(rawValue.trim().toUpperCase());
      }
    }

    const tlsEnabled = parsed.protocol === 'mongodb+srv:' || hasExplicitTlsTrue;
    if (!tlsEnabled) {
      throw new Error(
        'Safety guard: remote mongodb:// connections must explicitly enable TLS (tls=true or ssl=true).',
      );
    }

    const decodedUser = decodeUriComponentSafe(parsed.username);
    const decodedPass = decodeUriComponentSafe(parsed.password);
    const hasPasswordCredentials = decodedUser.length > 0 && decodedPass.length > 0;
    const usesPasswordAuth =
      authMechanisms.length === 0 ||
      authMechanisms.some((m) => PASSWORD_AUTH_MECHANISMS.has(m));
    const hasValidExternalAuth =
      authMechanisms.length > 0 &&
      authMechanisms.every((m) => EXTERNAL_AUTH_MECHANISMS.has(m));

    if (usesPasswordAuth && !hasPasswordCredentials) {
      throw new Error(
        'Safety guard: remote MongoDB URI must include non-empty username and password credentials (or a valid external authMechanism).',
      );
    }
    if (!usesPasswordAuth && !hasValidExternalAuth) {
      throw new Error(
        `Safety guard: unsupported authMechanism "${authMechanisms.join(', ')}" for remote MongoDB target.`,
      );
    }
  }

  return { hostname, isLoopback, protocol: parsed.protocol };
}

function walkObjectKeys(obj, found = new Set()) {
  if (Array.isArray(obj)) {
    for (const item of obj) walkObjectKeys(item, found);
  } else if (obj && typeof obj === 'object') {
    for (const [k, v] of Object.entries(obj)) {
      found.add(k);
      walkObjectKeys(v, found);
    }
  }
  return found;
}

export function validateSeedFixtures(chatFixture, workspaceFixture) {
  if (!chatFixture?.synthetic || chatFixture.containsGoldAnswers !== false) {
    throw new Error('chat_fixture.json must declare synthetic=true and containsGoldAnswers=false.');
  }
  if (!workspaceFixture?.synthetic || workspaceFixture.containsGoldAnswers !== false) {
    throw new Error(
      'workspace_enrichment_fixture.json must declare synthetic=true and containsGoldAnswers=false.',
    );
  }

  for (const [label, payload] of [
    ['chat_fixture.json', chatFixture],
    ['workspace_enrichment_fixture.json', workspaceFixture],
  ]) {
    const keys = walkObjectKeys(payload);
    for (const forbidden of FORBIDDEN_SEED_KEYS) {
      if (keys.has(forbidden)) {
        throw new Error(`Forbidden gold/secret key "${forbidden}" found in ${label}.`);
      }
    }
  }

  for (const conv of chatFixture.conversations) {
    if (!String(conv.id).startsWith(FIXTURE_ID_PREFIX) || !OBJECT_ID_RE.test(conv.id)) {
      throw new Error(`Invalid fixture conversation ID "${conv.id}".`);
    }
    for (const msg of conv.messages) {
      if (!String(msg.id).startsWith(FIXTURE_ID_PREFIX) || !OBJECT_ID_RE.test(msg.id)) {
        throw new Error(`Invalid fixture message ID "${msg.id}".`);
      }
      if (!UUID_V4_RE.test(msg.clientMessageId)) {
        throw new Error(`Invalid clientMessageId UUIDv4 on message "${msg.id}".`);
      }
      for (const badField of FORBIDDEN_CHAT_MSG_FIELDS) {
        if (badField in msg) {
          throw new Error(`Human-only seed violation: "${badField}" found on message "${msg.id}".`);
        }
      }
    }
  }
}

export async function loadEnvFile(envFilePath) {
  if (!envFilePath) return {};
  const text = await fs.readFile(envFilePath, 'utf8');
  const out = {};
  for (const line of text.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eq = trimmed.indexOf('=');
    if (eq <= 0) continue;
    const key = trimmed.slice(0, eq).trim();
    let val = trimmed.slice(eq + 1).trim();
    if (
      (val.startsWith('"') && val.endsWith('"')) ||
      (val.startsWith("'") && val.endsWith("'"))
    ) {
      val = val.slice(1, -1);
    }
    out[key] = val;
  }
  return out;
}

export async function loadActorMap(actorMapPath) {
  const raw = JSON.parse(await fs.readFile(actorMapPath, 'utf8'));
  if (String(raw.organizationId ?? '').toLowerCase() !== EXPECTED_ORG_ID) {
    throw new Error(
      `Actor map organizationId mismatch: expected ${EXPECTED_ORG_ID}, got ${raw.organizationId}.`,
    );
  }
  const actors = raw.actors ?? {};
  const seenIds = new Set();
  for (const [alias, uid] of Object.entries(actors)) {
    const hex = String(uid ?? '').trim().toLowerCase();
    if (!OBJECT_ID_RE.test(hex)) {
      throw new Error(`Invalid userId for actor "${alias}" in actor map.`);
    }
    if (seenIds.has(hex)) {
      throw new Error(`Duplicate userId mapped across multiple actors in actor map (${alias}).`);
    }
    seenIds.add(hex);
    actors[alias] = hex;
  }
  return { organizationId: EXPECTED_ORG_ID, actors };
}

export function buildAllFixtureIdSets(chatFixture, workspaceFixture) {
  const ids = {
    newConversations: new Set(),
    chatMessages: new Set(),
    taskComments: new Set(),
    taskWorklogs: new Set(),
    workNotes: new Set(),
    workNoteVersions: new Set(),
    workReports: new Set(),
    handovers: new Set(),
    handoverItems: new Set(),
    handoverRevisions: new Set(),
  };
  for (const c of chatFixture.conversations) {
    if (!c.reuseExistingDirect) ids.newConversations.add(c.id);
    for (const m of c.messages) ids.chatMessages.add(m.id);
  }
  for (const r of workspaceFixture.taskComments) ids.taskComments.add(r.id);
  for (const r of workspaceFixture.taskWorklogs) ids.taskWorklogs.add(r.id);
  for (const r of workspaceFixture.workNotes) {
    ids.workNotes.add(r.id);
    ids.workNoteVersions.add(r.versionId);
  }
  for (const r of workspaceFixture.workReports) ids.workReports.add(r.id);
  for (const h of workspaceFixture.handovers) {
    ids.handovers.add(h.id);
    ids.handoverItems.add(h.item.id);
    ids.handoverRevisions.add(h.revision.id);
  }
  return ids;
}

export function parseCliArgs(argv) {
  const args = {
    mode: 'dry-run',
    anchorDate: null,
    envFile: null,
    actorMap: DEFAULT_ACTOR_MAP_PATH,
    expectedOrgId: null,
    approvedClusterHost: null,
    chatFixturePath: DEFAULT_CHAT_FIXTURE_PATH,
    workspaceFixturePath: DEFAULT_WORKSPACE_FIXTURE_PATH,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const tok = argv[i];
    if (tok === '--dry-run') args.mode = 'dry-run';
    else if (tok === '--apply') args.mode = 'apply';
    else if (tok === '--verify') args.mode = 'verify';
    else if (tok === '--reset-fixture') args.mode = 'reset-fixture';
    else if (tok === '--anchor-date') args.anchorDate = argv[++i];
    else if (tok.startsWith('--anchor-date=')) args.anchorDate = tok.split('=')[1];
    else if (tok === '--env-file') args.envFile = argv[++i];
    else if (tok.startsWith('--env-file=')) args.envFile = tok.split('=')[1];
    else if (tok === '--actor-map') args.actorMap = argv[++i];
    else if (tok.startsWith('--actor-map=')) args.actorMap = tok.split('=')[1];
    else if (tok === '--expected-org-id') args.expectedOrgId = argv[++i];
    else if (tok.startsWith('--expected-org-id=')) args.expectedOrgId = tok.split('=')[1];
    else if (tok === '--approved-cluster-host') args.approvedClusterHost = argv[++i];
    else if (tok.startsWith('--approved-cluster-host='))
      args.approvedClusterHost = tok.split('=')[1];
    else throw new Error(`Unknown CLI argument: ${tok}`);
  }
  return args;
}

async function resolveLiveActorsAndOrg(iamDb, ObjectId, actorMap, requiredActorKeys) {
  const orgOid = new ObjectId(EXPECTED_ORG_ID);
  const org = await iamDb.collection('organizations').findOne({ _id: orgOid });
  if (!org || org.slug !== EXPECTED_ORG_SLUG) {
    throw new Error(
      `Target organization mismatch: expected ${EXPECTED_ORG_ID} (${EXPECTED_ORG_SLUG}).`,
    );
  }

  for (const key of requiredActorKeys) {
    if (!actorMap.actors[key]) {
      throw new Error(`Missing required actor alias "${key}" in actor map.`);
    }
  }

  const userOids = Object.values(actorMap.actors).map((hex) => new ObjectId(hex));
  const users = await iamDb
    .collection('users')
    .find({ _id: { $in: userOids } }, { projection: { _id: 1, fullName: 1, status: 1 } })
    .toArray();
  const oms = await iamDb
    .collection('organization_memberships')
    .find({ organizationId: orgOid, userId: { $in: userOids }, status: 'ACTIVE' })
    .toArray();

  const userById = new Map(users.map((u) => [String(u._id).toLowerCase(), u]));
  const activeMemberIds = new Set(oms.map((m) => String(m.userId).toLowerCase()));

  const resolved = {};
  for (const [alias, hex] of Object.entries(actorMap.actors)) {
    const u = userById.get(hex);
    if (!u || u.status !== 'ACTIVE') {
      throw new Error(`Actor "${alias}" (${hex}) is not ACTIVE in continuum_iam.users.`);
    }
    if (!activeMemberIds.has(hex)) {
      throw new Error(
        `Actor "${alias}" (${hex}) does not have an ACTIVE organization membership in WDP301-SPRING-2027.`,
      );
    }
    resolved[alias] = {
      userIdHex: hex,
      userOid: new ObjectId(hex),
      displayName: String(u.fullName || alias),
    };
  }
  return { orgOid, resolved };
}

function collectRequiredActorKeys(chatFixture, workspaceFixture) {
  const keys = new Set(chatFixture.verifiedNonMemberActorKeys ?? []);
  for (const c of chatFixture.conversations) {
    keys.add(c.ownerActorKey);
    for (const k of c.memberActorKeys) keys.add(k);
    for (const k of c.managerActorKeys ?? []) keys.add(k);
    for (const m of c.messages) {
      keys.add(m.senderActorKey);
      for (const mk of m.mentionActorKeys ?? []) keys.add(mk);
      for (const r of m.reactions ?? []) {
        for (const ak of r.actorKeys) keys.add(ak);
      }
    }
  }
  for (const r of workspaceFixture.taskComments) keys.add(r.authorActorKey);
  for (const r of workspaceFixture.taskWorklogs) keys.add(r.authorActorKey);
  for (const r of workspaceFixture.workNotes) keys.add(r.authorActorKey);
  for (const r of workspaceFixture.workReports) {
    keys.add(r.memberActorKey);
    if (r.reviewerActorKey) keys.add(r.reviewerActorKey);
  }
  for (const h of workspaceFixture.handovers) {
    keys.add(h.departingActorKey);
    keys.add(h.assignedLeaderActorKey);
    keys.add(h.successorActorKey);
    keys.add(h.createdByActorKey);
    if (h.completedByActorKey) keys.add(h.completedByActorKey);
    keys.add(h.item.updatedByActorKey);
    keys.add(h.revision.publishedByActorKey);
  }
  return keys;
}

async function refreshConversationLastMessage(chatDb, conversationOid) {
  const latest = await chatDb
    .collection('chat_conversation_messages')
    .find({ conversationId: conversationOid })
    .sort({ createdAt: -1, _id: -1 })
    .limit(1)
    .toArray();
  if (latest.length === 0) {
    await chatDb.collection('chat_conversations').updateOne(
      { _id: conversationOid },
      {
        $set: {
          lastMessageAt: null,
          lastMessageId: null,
          lastMessagePreview: '',
          lastMessageSenderId: null,
        },
      },
    );
    return;
  }
  const msg = latest[0];
  const preview = msg.deletedAt ? 'Tin nhắn đã được thu hồi' : String(msg.content ?? '').slice(0, 120);
  await chatDb.collection('chat_conversations').updateOne(
    { _id: conversationOid },
    {
      $set: {
        lastMessageAt: msg.createdAt,
        lastMessageId: msg._id,
        lastMessagePreview: preview,
        lastMessageSenderId: msg.senderId,
        updatedAt: msg.updatedAt ?? msg.createdAt,
      },
    },
  );
}

export async function applySeed({
  dbs,
  ObjectId,
  chatFixture,
  workspaceFixture,
  resolvedActors,
  orgOid,
  anchorDate,
}) {
  const stats = {
    conversationsCreated: 0,
    conversationsReused: 0,
    chatMembersInserted: 0,
    chatMessagesInserted: 0,
    chatMessagesSkipped: 0,
    taskCommentsInserted: 0,
    taskWorklogsInserted: 0,
    workNotesInserted: 0,
    workNoteVersionsInserted: 0,
    workReportsInserted: 0,
    handoversInserted: 0,
    handoverItemsInserted: 0,
    handoverRevisionsInserted: 0,
  };

  // Pre-verify referenced real tasks & documents exist (never insert orphan refs)
  const neededTaskIds = [
    ...new Set([
      ...workspaceFixture.taskComments.map((r) => r.taskId),
      ...workspaceFixture.taskWorklogs.map((r) => r.taskId),
      ...workspaceFixture.workNotes.map((r) => r.taskId),
      ...workspaceFixture.handovers.flatMap((h) => h.selectedTasks.map((t) => t.taskId)),
    ]),
  ];
  const existingTasks = await dbs.task
    .collection('tasks')
    .find(
      { _id: { $in: neededTaskIds.map((id) => new ObjectId(id)) }, organizationId: orgOid },
      { projection: { _id: 1, projectId: 1 } },
    )
    .toArray();
  if (existingTasks.length !== neededTaskIds.length) {
    throw new Error(
      `Pre-check failed: expected ${neededTaskIds.length} real WDP301 tasks, found ${existingTasks.length}.`,
    );
  }

  // 1) Chat Conversations, Members & Messages (insert-only!)
  const resolvedConvIds = new Map();
  for (const conv of chatFixture.conversations) {
    const firstMsgTs = computeMessageTimestamps(anchorDate, conv.messages[0]).createdAt;
    const owner = resolvedActors[conv.ownerActorKey];
    let convOid;

    if (conv.type === 'DIRECT') {
      const [akA, akB] = conv.memberActorKeys;
      const directKey = buildDirectKey(
        EXPECTED_ORG_ID,
        resolvedActors[akA].userIdHex,
        resolvedActors[akB].userIdHex,
      );
      const existing = await dbs.chat
        .collection('chat_conversations')
        .findOne({ directKey });
      if (existing) {
        if (String(existing.organizationId).toLowerCase() !== EXPECTED_ORG_ID) {
          throw new Error(`Collision: directKey "${directKey}" belongs to another organization.`);
        }
        convOid = existing._id;
        stats.conversationsReused += 1;
      } else {
        convOid = new ObjectId(conv.id);
        const res = await dbs.chat.collection('chat_conversations').updateOne(
          { _id: convOid },
          {
            $setOnInsert: {
              _id: convOid,
              organizationId: orgOid,
              type: 'DIRECT',
              directKey,
              title: null,
              createdBy: owner.userIdHex,
              lastMessageAt: null,
              lastMessageId: null,
              lastMessagePreview: '',
              lastMessageSenderId: null,
              membershipVersion: 0,
              contextRevision: 0,
              status: 'ACTIVE',
              createdAt: firstMsgTs,
              updatedAt: firstMsgTs,
            },
          },
          { upsert: true },
        );
        if (res.upsertedCount > 0) stats.conversationsCreated += 1;
        else stats.conversationsReused += 1;
      }
    } else {
      const existing = await dbs.chat
        .collection('chat_conversations')
        .findOne({ creationKey: conv.creationKey });
      if (existing) {
        if (String(existing.organizationId).toLowerCase() !== EXPECTED_ORG_ID) {
          throw new Error(`Collision: creationKey "${conv.creationKey}" belongs to another org.`);
        }
        convOid = existing._id;
        stats.conversationsReused += 1;
      } else {
        convOid = new ObjectId(conv.id);
        const res = await dbs.chat.collection('chat_conversations').updateOne(
          { _id: convOid },
          {
            $setOnInsert: {
              _id: convOid,
              organizationId: orgOid,
              type: 'ROOM',
              creationKey: conv.creationKey,
              title: conv.title,
              createdBy: owner.userIdHex,
              lastMessageAt: null,
              lastMessageId: null,
              lastMessagePreview: '',
              lastMessageSenderId: null,
              membershipVersion: 0,
              contextRevision: 0,
              status: 'ACTIVE',
              createdAt: firstMsgTs,
              updatedAt: firstMsgTs,
            },
          },
          { upsert: true },
        );
        if (res.upsertedCount > 0) stats.conversationsCreated += 1;
        else stats.conversationsReused += 1;
      }
    }
    resolvedConvIds.set(conv.key, convOid);

    // Members (insert-only by conversationId + userId; preserves pre-existing members untouched!)
    const managers = new Set(conv.managerActorKeys ?? []);
    for (const memberAk of conv.memberActorKeys) {
      const actor = resolvedActors[memberAk];
      const role =
        memberAk === conv.ownerActorKey
          ? 'OWNER'
          : managers.has(memberAk)
            ? 'MANAGER'
            : 'MEMBER';
      let searchLabel = conv.title || '';
      if (conv.type === 'DIRECT') {
        const peerAk = conv.memberActorKeys.find((k) => k !== memberAk);
        searchLabel = resolvedActors[peerAk].displayName;
      }
      const memberOid = new ObjectId(
        stableFixtureMemberIdHex(String(convOid), actor.userIdHex),
      );
      const res = await dbs.chat.collection('chat_members').updateOne(
        { conversationId: convOid, userId: actor.userIdHex },
        {
          $setOnInsert: {
            _id: memberOid,
            organizationId: orgOid,
            conversationId: convOid,
            userId: actor.userIdHex,
            displayName: actor.displayName,
            searchLabel,
            avatarUrl: null,
            role,
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
            draftAssistantMention: false,
            draftUpdatedAt: null,
            joinedAt: firstMsgTs,
            createdAt: firstMsgTs,
            updatedAt: firstMsgTs,
          },
        },
        { upsert: true },
      );
      if (res.upsertedCount > 0) stats.chatMembersInserted += 1;
    }

    // Messages (fail-closed _id collision check + strict insert-only)
    for (const msg of conv.messages) {
      const msgOid = new ObjectId(msg.id);
      const existing = await dbs.chat
        .collection('chat_conversation_messages')
        .findOne({ _id: msgOid }, { projection: { _id: 1, organizationId: 1, conversationId: 1 } });
      if (existing) {
        if (
          String(existing.organizationId).toLowerCase() !== EXPECTED_ORG_ID ||
          String(existing.conversationId).toLowerCase() !== String(convOid).toLowerCase()
        ) {
          throw new Error(
            `Fail-closed _id collision on message ${msg.id}: belongs to a different org/conversation.`,
          );
        }
        stats.chatMessagesSkipped += 1;
        continue;
      }

      const sender = resolvedActors[msg.senderActorKey];
      const { createdAt, editedAt, deletedAt, updatedAt } = computeMessageTimestamps(
        anchorDate,
        msg,
      );
      const doc = {
        _id: msgOid,
        organizationId: orgOid,
        conversationId: convOid,
        senderId: sender.userIdHex,
        senderName: sender.displayName,
        senderAvatarUrl: null,
        clientMessageId: msg.clientMessageId,
        content: msg.content,
        mentionUserIds: (msg.mentionActorKeys ?? []).map((ak) => resolvedActors[ak].userIdHex),
        links: msg.links ?? [],
        isPinned: Boolean(msg.isPinned),
        editedAt,
        deletedAt,
        replyToMessageId: msg.replyToMessageId ? new ObjectId(msg.replyToMessageId) : null,
        reactions: (msg.reactions ?? []).map((r) => ({
          emoji: r.emoji,
          userIds: r.actorKeys.map((ak) => resolvedActors[ak].userIdHex),
        })),
        attachments: [],
        createdAt,
        updatedAt,
      };
      const res = await dbs.chat.collection('chat_conversation_messages').updateOne(
        { _id: msgOid },
        { $setOnInsert: doc },
        { upsert: true },
      );
      if (res.upsertedCount > 0) stats.chatMessagesInserted += 1;
      else stats.chatMessagesSkipped += 1;
    }

    await refreshConversationLastMessage(dbs.chat, convOid);
  }

  // 2) Task Comments (strict schema, insert-only)
  for (const c of workspaceFixture.taskComments) {
    const createdAt = computeLocalTimestamp(anchorDate, c.dayOffset, c.timeLocal);
    const res = await dbs.task.collection('task_comments').updateOne(
      { _id: new ObjectId(c.id) },
      {
        $setOnInsert: {
          _id: new ObjectId(c.id),
          taskId: new ObjectId(c.taskId),
          projectId: new ObjectId(c.projectId),
          organizationId: orgOid,
          authorId: resolvedActors[c.authorActorKey].userOid,
          body: c.body,
          createdAt,
        },
      },
      { upsert: true },
    );
    if (res.upsertedCount > 0) stats.taskCommentsInserted += 1;
  }

  // 3) Task Worklogs (strict schema, insert-only)
  for (const w of workspaceFixture.taskWorklogs) {
    const loggedAt = computeLocalTimestamp(anchorDate, w.dayOffset, w.timeLocal);
    const res = await dbs.task.collection('task_worklogs').updateOne(
      { _id: new ObjectId(w.id) },
      {
        $setOnInsert: {
          _id: new ObjectId(w.id),
          taskId: new ObjectId(w.taskId),
          projectId: new ObjectId(w.projectId),
          organizationId: orgOid,
          authorId: resolvedActors[w.authorActorKey].userOid,
          minutes: w.minutes,
          note: w.note,
          loggedAt,
          createdAt: loggedAt,
        },
      },
      { upsert: true },
    );
    if (res.upsertedCount > 0) stats.taskWorklogsInserted += 1;
  }

  // 4) Work Notes & Work Note Versions (v1 + v2, insert-only)
  for (const n of workspaceFixture.workNotes) {
    const author = resolvedActors[n.authorActorKey];
    const createdAt = computeLocalTimestamp(anchorDate, n.dayOffset, n.timeLocal);
    const noteOid = new ObjectId(n.id);
    const baseNote = {
      _id: noteOid,
      organizationId: orgOid,
      projectId: new ObjectId(n.projectId),
      taskId: new ObjectId(n.taskId),
      authorUserId: author.userOid,
      authorName: author.displayName,
      type: 'TASK_NOTE',
      taskKey: n.taskKey,
      title: n.title,
      status: n.status,
      authorConfirmedAt: createdAt,
      tags: n.tags ?? [],
      category: n.category ?? 'Decision',
      ...(n.nextStep ? { nextStep: n.nextStep } : {}),
      pinned: Boolean(n.pinned),
      mentionUserIds: [],
      deletedAt: null,
      timeSpentMinutes: n.timeSpentMinutes,
      createdAt,
      updatedAt: createdAt,
      ...(n.schemaVersion === 2
        ? {
            contentSchemaVersion: 2,
            currentVersionNumber: 1,
            contentMarkdown: n.contentMarkdown,
          }
        : {
            whatDone: n.whatDone,
            howSolved: n.howSolved,
            whyThisWay: n.whyThisWay,
          }),
    };
    const resNote = await dbs.capture.collection('work_notes').updateOne(
      { _id: noteOid },
      { $setOnInsert: baseNote },
      { upsert: true },
    );
    if (resNote.upsertedCount > 0) stats.workNotesInserted += 1;

    const versionOid = new ObjectId(n.versionId);
    const versionDoc = {
      _id: versionOid,
      workNoteId: noteOid,
      versionNumber: 1,
      title: n.title,
      editedByUserId: author.userOid,
      createdAt,
      updatedAt: createdAt,
      ...(n.schemaVersion === 2
        ? { contentSchemaVersion: 2, contentMarkdown: n.contentMarkdown }
        : { whatDone: n.whatDone, howSolved: n.howSolved, whyThisWay: n.whyThisWay }),
    };
    const resVer = await dbs.capture.collection('work_note_versions').updateOne(
      { _id: versionOid },
      { $setOnInsert: versionDoc },
      { upsert: true },
    );
    if (resVer.upsertedCount > 0) stats.workNoteVersionsInserted += 1;
  }

  // 5) Work Reports (insert-only)
  for (const r of workspaceFixture.workReports) {
    const periodStart = computeLocalTimestamp(anchorDate, r.periodStartOffset, '00:00:00');
    const periodEnd = computeLocalTimestamp(anchorDate, r.periodEndOffset, '00:00:00');
    const dueAt = computeLocalTimestamp(anchorDate, r.dueOffset, '17:00:00');
    const createdAt = computeLocalTimestamp(anchorDate, r.periodStartOffset + 1, '09:00:00');
    const submittedAt =
      r.submittedOffset !== null && r.submittedOffset !== undefined
        ? computeLocalTimestamp(anchorDate, r.submittedOffset, '16:30:00')
        : null;
    const reviewedAt =
      r.reviewedOffset !== null && r.reviewedOffset !== undefined
        ? computeLocalTimestamp(anchorDate, r.reviewedOffset, '10:30:00')
        : null;
    const reviewHistory =
      r.reviewerActorKey && reviewedAt && ['APPROVED', 'CHANGES_REQUESTED', 'REJECTED'].includes(r.status)
        ? [
            {
              action: r.status,
              reviewerId: resolvedActors[r.reviewerActorKey].userIdHex,
              ...(r.reviewerRole ? { reviewerRole: r.reviewerRole } : {}),
              comment: r.reviewComment ?? '',
              at: reviewedAt,
            },
          ]
        : [];
    const doc = {
      _id: new ObjectId(r.id),
      organizationId: orgOid,
      projectId: new ObjectId(r.projectId),
      memberUserId: resolvedActors[r.memberActorKey].userOid,
      reportScope: r.reportScope,
      frequency: r.frequency,
      periodStart,
      periodEnd,
      dueAt,
      accomplishments: r.accomplishments,
      approach: r.approach,
      reason: r.reason,
      blockers: r.blockers,
      nextSteps: r.nextSteps,
      documentIds: r.documentIds,
      status: r.status,
      ...(submittedAt ? { submittedAt } : {}),
      ...(r.reviewerActorKey ? { reviewedByUserId: resolvedActors[r.reviewerActorKey].userOid } : {}),
      ...(reviewedAt ? { reviewedAt } : {}),
      reviewComment: r.reviewComment ?? '',
      reviewHistory,
      createdAt,
      updatedAt: reviewedAt ?? submittedAt ?? createdAt,
    };
    const res = await dbs.capture.collection('work_reports').updateOne(
      { _id: doc._id },
      { $setOnInsert: doc },
      { upsert: true },
    );
    if (res.upsertedCount > 0) stats.workReportsInserted += 1;
  }

  // 6) Handovers v2 (handovers + handover_items + handover_revisions, strict $jsonSchema!)
  for (const h of workspaceFixture.handovers) {
    const hoOid = new ObjectId(h.id);
    const projectOid = new ObjectId(h.projectId);
    const createdAt = computeLocalTimestamp(anchorDate, h.createdDayOffset, '10:00:00');
    const publishedAt = computeLocalTimestamp(anchorDate, h.publishedDayOffset, '16:00:00');
    const targetCompletionDate = computeLocalTimestamp(anchorDate, h.targetCompletionDayOffset, '00:00:00');
    const completedAt =
      h.status === 'COMPLETED'
        ? computeLocalTimestamp(anchorDate, h.completedDayOffset, '15:30:00')
        : null;

    const selectedTasks = h.selectedTasks.map((t) => ({
      taskId: new ObjectId(t.taskId),
      expectedVersion: t.expectedVersion,
      expectedAssigneeId: t.expectedAssigneeActorKey
        ? resolvedActors[t.expectedAssigneeActorKey].userIdHex
        : null,
    }));

    const hoDoc = {
      _id: hoOid,
      schemaVersion: 2,
      organizationId: orgOid,
      projectId: projectOid,
      departingUserId: resolvedActors[h.departingActorKey].userIdHex,
      assignedLeaderId: resolvedActors[h.assignedLeaderActorKey].userIdHex,
      successorUserId: resolvedActors[h.successorActorKey].userIdHex,
      title: h.title,
      targetCompletionDate,
      status: h.status,
      version: h.version,
      draftVersion: h.draftVersion,
      assignmentVersion: h.assignmentVersion,
      publishedRevisionId: new ObjectId(h.publishedRevisionId),
      selectedSources: h.selectedSources,
      selectedTasks,
      createdBy: resolvedActors[h.createdByActorKey].userIdHex,
      ...(h.status === 'COMPLETED'
        ? {
            completedAt,
            completedBy: resolvedActors[h.completedByActorKey].userIdHex,
            completionReviewNote: h.completionReviewNote,
          }
        : {}),
      createdAt,
      updatedAt: completedAt ?? publishedAt,
    };
    const resHo = await dbs.handover.collection('handovers').updateOne(
      { _id: hoOid },
      { $setOnInsert: hoDoc },
      { upsert: true },
    );
    if (resHo.upsertedCount > 0) stats.handoversInserted += 1;

    const itemOid = new ObjectId(h.item.id);
    const logicalItemOid = new ObjectId(h.item.itemId);
    const itemDoc = {
      _id: itemOid,
      schemaVersion: 2,
      organizationId: orgOid,
      projectId: projectOid,
      handoverId: hoOid,
      itemId: logicalItemOid,
      contentVersion: h.item.contentVersion,
      dependencyFingerprint: h.item.dependencyFingerprint,
      title: h.item.title,
      body: h.item.body,
      requirement: h.item.requirement,
      isRequired: h.item.isRequired,
      evidenceRequired: h.item.evidenceRequired,
      sources: h.item.sources,
      citations: h.item.citations,
      updatedBy: resolvedActors[h.item.updatedByActorKey].userIdHex,
      createdAt: publishedAt,
      updatedAt: publishedAt,
    };
    const resItem = await dbs.handover.collection('handover_items').updateOne(
      { _id: itemOid },
      { $setOnInsert: itemDoc },
      { upsert: true },
    );
    if (resItem.upsertedCount > 0) stats.handoverItemsInserted += 1;

    const revOid = new ObjectId(h.revision.id);
    const revDoc = {
      _id: revOid,
      schemaVersion: 2,
      organizationId: orgOid,
      projectId: projectOid,
      handoverId: hoOid,
      number: h.revision.number,
      draftVersion: h.revision.draftVersion,
      assignmentVersion: h.revision.assignmentVersion,
      successorUserId: resolvedActors[h.successorActorKey].userIdHex,
      items: [
        {
          itemId: logicalItemOid,
          contentVersion: h.item.contentVersion,
          dependencyFingerprint: h.item.dependencyFingerprint,
          title: h.item.title,
          body: h.item.body,
          requirement: h.item.requirement,
          isRequired: h.item.isRequired,
          evidenceRequired: h.item.evidenceRequired,
          sources: h.item.sources,
          citations: h.item.citations,
        },
      ],
      selectedSources: h.selectedSources,
      selectedTasks,
      reviews: [
        {
          itemId: logicalItemOid,
          contentVersion: h.item.contentVersion,
          decision: 'CONTENT_APPROVED',
          impact: 'CHANGED',
          reason: h.revision.reviewReason,
        },
      ],
      gaps: [],
      publishedBy: resolvedActors[h.revision.publishedByActorKey].userIdHex,
      publishedAt,
      sourceFingerprint: h.revision.sourceFingerprint,
      reviewNote: h.revision.reviewNote,
      createdAt: publishedAt,
    };
    const resRev = await dbs.handover.collection('handover_revisions').updateOne(
      { _id: revOid },
      { $setOnInsert: revDoc },
      { upsert: true },
    );
    if (resRev.upsertedCount > 0) stats.handoverRevisionsInserted += 1;
  }

  return { stats, resolvedConvIds };
}

export async function verifySeed({
  dbs,
  ObjectId,
  chatFixture,
  workspaceFixture,
  resolvedActors,
  orgOid,
  anchorDate,
}) {
  const errors = [];
  const idSets = buildAllFixtureIdSets(chatFixture, workspaceFixture);

  // 1) Verify chat conversations, members, messages, timestamps, 0 AI messages & non-member isolation
  const convOids = [];
  for (const conv of chatFixture.conversations) {
    let convDoc;
    if (conv.type === 'DIRECT') {
      const [akA, akB] = conv.memberActorKeys;
      const directKey = buildDirectKey(
        EXPECTED_ORG_ID,
        resolvedActors[akA].userIdHex,
        resolvedActors[akB].userIdHex,
      );
      convDoc = await dbs.chat.collection('chat_conversations').findOne({ directKey });
    } else {
      convDoc = await dbs.chat
        .collection('chat_conversations')
        .findOne({ creationKey: conv.creationKey });
    }
    if (!convDoc) {
      errors.push(`Missing conversation ${conv.key}`);
      continue;
    }
    convOids.push(convDoc._id);

    const members = await dbs.chat
      .collection('chat_members')
      .find({ conversationId: convDoc._id, status: 'ACTIVE' })
      .toArray();
    const memberIds = new Set(members.map((m) => String(m.userId).toLowerCase()));
    const expectedMemberIds = new Set(
      conv.memberActorKeys.map((ak) => resolvedActors[ak].userIdHex),
    );
    if (
      memberIds.size !== expectedMemberIds.size ||
      [...expectedMemberIds].some((id) => !memberIds.has(id))
    ) {
      errors.push(`Member set mismatch in ${conv.key}`);
    }
    for (const nonMemberAk of chatFixture.verifiedNonMemberActorKeys ?? []) {
      if (memberIds.has(resolvedActors[nonMemberAk].userIdHex)) {
        errors.push(`ACL violation: non-member ${nonMemberAk} present in ${conv.key}`);
      }
    }

    const msgIds = conv.messages.map((m) => new ObjectId(m.id));
    const foundMsgs = await dbs.chat
      .collection('chat_conversation_messages')
      .find({ _id: { $in: msgIds } })
      .toArray();
    if (foundMsgs.length !== conv.messages.length) {
      errors.push(
        `Message count mismatch in ${conv.key}: expected ${conv.messages.length}, found ${foundMsgs.length}`,
      );
    }
    const byId = new Map(foundMsgs.map((d) => [String(d._id).toLowerCase(), d]));
    for (const expected of conv.messages) {
      const actual = byId.get(expected.id);
      if (!actual) continue;
      if (actual.authorType === 'ASSISTANT' || actual.sourceReferences !== undefined) {
        errors.push(`Pre-seeded AI field found on fixture message ${expected.id}`);
      }
      const expectedTs = computeMessageTimestamps(anchorDate, expected).createdAt;
      if (actual.createdAt?.valueOf() !== expectedTs.valueOf()) {
        errors.push(
          `Anchor timestamp mismatch on ${expected.id}: expected ${expectedTs.toISOString()}, got ${actual.createdAt?.toISOString()}`,
        );
      }
    }
  }

  // 2) Verify exact seeded counts in task, capture, handover
  const countChecks = [
    [dbs.task, 'task_comments', idSets.taskComments],
    [dbs.task, 'task_worklogs', idSets.taskWorklogs],
    [dbs.capture, 'work_notes', idSets.workNotes],
    [dbs.capture, 'work_note_versions', idSets.workNoteVersions],
    [dbs.capture, 'work_reports', idSets.workReports],
    [dbs.handover, 'handovers', idSets.handovers],
    [dbs.handover, 'handover_items', idSets.handoverItems],
    [dbs.handover, 'handover_revisions', idSets.handoverRevisions],
  ];
  const verifiedCounts = {};
  for (const [db, col, set] of countChecks) {
    const found = await db
      .collection(col)
      .countDocuments({ _id: { $in: [...set].map((hex) => new ObjectId(hex)) } });
    verifiedCounts[`${db.databaseName}.${col}`] = `${found}/${set.size}`;
    if (found !== set.size) {
      errors.push(`Count mismatch in ${db.databaseName}.${col}: expected ${set.size}, found ${found}`);
    }
  }

  // 3) Verify legacy WDP301 data preservation (non-destructive guarantee!)
  const totalTasks = await dbs.task.collection('tasks').countDocuments({ organizationId: orgOid });
  const totalDocs = await dbs.capture
    .collection('project_documents')
    .countDocuments({ organizationId: orgOid });
  const legacyHelo = await dbs.chat
    .collection('chat_conversation_messages')
    .findOne({ _id: new ObjectId('6adc877aa2fed46274ba66ad') });
  const legacyDanh = await dbs.chat
    .collection('chat_conversation_messages')
    .findOne({ _id: new ObjectId('6ae92dddbdef3c1ce07d0d7a') });

  if (totalTasks < 474) errors.push(`Legacy tasks preservation violated: count=${totalTasks} < 474`);
  if (totalDocs < 143) errors.push(`Legacy docs preservation violated: count=${totalDocs} < 143`);
  if (!legacyHelo || legacyHelo.content !== 'helo') {
    errors.push('Legacy "helo" message was modified or missing!');
  }
  if (!legacyDanh || legacyDanh.content !== 'Danh') {
    errors.push('Legacy "Danh" message was modified or missing!');
  }

  return {
    ok: errors.length === 0,
    errors,
    verifiedCounts,
    legacyPreserved: {
      tasks: totalTasks,
      projectDocuments: totalDocs,
      legacyHeloIntact: legacyHelo?.content === 'helo',
      legacyDanhIntact: legacyDanh?.content === 'Danh',
    },
  };
}

export async function resetFixture({ dbs, ObjectId, chatFixture, workspaceFixture, resolvedActors }) {
  const idSets = buildAllFixtureIdSets(chatFixture, workspaceFixture);
  const del = async (db, col, set) => {
    if (set.size === 0) return 0;
    const res = await db
      .collection(col)
      .deleteMany({ _id: { $in: [...set].map((hex) => new ObjectId(hex)) } });
    return res.deletedCount;
  };

  // Delete ONLY fixture-owned records (NEVER deletes reused pre-existing DMs or legacy messages!)
  const deleted = {
    chatMessages: await del(dbs.chat, 'chat_conversation_messages', idSets.chatMessages),
    taskComments: await del(dbs.task, 'task_comments', idSets.taskComments),
    taskWorklogs: await del(dbs.task, 'task_worklogs', idSets.taskWorklogs),
    workNotes: await del(dbs.capture, 'work_notes', idSets.workNotes),
    workNoteVersions: await del(dbs.capture, 'work_note_versions', idSets.workNoteVersions),
    workReports: await del(dbs.capture, 'work_reports', idSets.workReports),
    handovers: await del(dbs.handover, 'handovers', idSets.handovers),
    handoverItems: await del(dbs.handover, 'handover_items', idSets.handoverItems),
    handoverRevisions: await del(dbs.handover, 'handover_revisions', idSets.handoverRevisions),
    chatMembersFixtureOwned: 0,
    newConversations: 0,
  };

  // Delete fixture-owned chat_members (identifiable by deterministic `6f3019...` _id prefix)
  const newConvOids = [...idSets.newConversations].map((hex) => new ObjectId(hex));
  const fixtureMemberIds = [];
  for (const conv of chatFixture.conversations) {
    let convOid = null;
    if (conv.type === 'DIRECT') {
      const [akA, akB] = conv.memberActorKeys;
      const dk = buildDirectKey(
        EXPECTED_ORG_ID,
        resolvedActors[akA].userIdHex,
        resolvedActors[akB].userIdHex,
      );
      const found = await dbs.chat.collection('chat_conversations').findOne({ directKey: dk });
      convOid = found?._id ?? null;
    } else {
      convOid = new ObjectId(conv.id);
    }
    if (!convOid) continue;
    for (const ak of conv.memberActorKeys) {
      fixtureMemberIds.push(
        new ObjectId(stableFixtureMemberIdHex(String(convOid), resolvedActors[ak].userIdHex)),
      );
    }
    if (conv.reuseExistingDirect) {
      await refreshConversationLastMessage(dbs.chat, convOid);
    }
  }
  if (fixtureMemberIds.length > 0) {
    const rMem = await dbs.chat
      .collection('chat_members')
      .deleteMany({ _id: { $in: fixtureMemberIds } });
    deleted.chatMembersFixtureOwned = rMem.deletedCount;
  }
  if (newConvOids.length > 0) {
    const rConv = await dbs.chat
      .collection('chat_conversations')
      .deleteMany({ _id: { $in: newConvOids } });
    deleted.newConversations = rConv.deletedCount;
  }

  return deleted;
}

async function main() {
  const args = parseCliArgs(process.argv.slice(2));
  const anchorDate = resolveAnchorDate(args.anchorDate);

  const chatFixture = JSON.parse(await fs.readFile(args.chatFixturePath, 'utf8'));
  const workspaceFixture = JSON.parse(await fs.readFile(args.workspaceFixturePath, 'utf8'));
  validateSeedFixtures(chatFixture, workspaceFixture);

  const requiredActors = collectRequiredActorKeys(chatFixture, workspaceFixture);
  const summary = {
    mode: args.mode,
    anchorDate,
    organizationId: EXPECTED_ORG_ID,
    organizationSlug: EXPECTED_ORG_SLUG,
    conversations: chatFixture.conversations.length,
    chatMessages: chatFixture.conversations.reduce((s, c) => s + c.messages.length, 0),
    taskComments: workspaceFixture.taskComments.length,
    taskWorklogs: workspaceFixture.taskWorklogs.length,
    workNotes: workspaceFixture.workNotes.length,
    workReports: workspaceFixture.workReports.length,
    handovers: workspaceFixture.handovers.length,
    requiredActors: requiredActors.size,
  };

  if (args.mode === 'dry-run') {
    let actorMapLoaded = false;
    try {
      await loadActorMap(args.actorMap);
      actorMapLoaded = true;
    } catch {
      actorMapLoaded = false;
    }
    console.log(JSON.stringify({ ok: true, dryRun: true, actorMapLoaded, summary }, null, 2));
    return;
  }

  const fileEnv = await loadEnvFile(args.envFile);
  const mergedEnv = { ...fileEnv, ...process.env };
  const mongoUri = mergedEnv.MONGODB_URI || mergedEnv.CHAT_MONGODB_URI || '';

  if (args.mode === 'apply' || args.mode === 'reset-fixture') {
    assertApprovedDevTarget(mergedEnv, mongoUri, {
      expectedOrgId: args.expectedOrgId,
      approvedClusterHost: args.approvedClusterHost,
    });
  } else if (!mongoUri) {
    throw new Error('MONGODB_URI is required for --verify.');
  }

  const actorMap = await loadActorMap(args.actorMap);
  const { MongoClient, ObjectId } = loadMongoDriver();
  const client = new MongoClient(mongoUri, { serverSelectionTimeoutMS: 12_000 });
  await client.connect();

  try {
    const dbs = {
      iam: client.db(APPROVED_DB_NAMES.iam),
      chat: client.db(APPROVED_DB_NAMES.chat),
      task: client.db(APPROVED_DB_NAMES.task),
      capture: client.db(APPROVED_DB_NAMES.capture),
      handover: client.db(APPROVED_DB_NAMES.handover),
    };
    const { orgOid, resolved } = await resolveLiveActorsAndOrg(
      dbs.iam,
      ObjectId,
      actorMap,
      requiredActors,
    );

    if (args.mode === 'apply') {
      const { stats } = await applySeed({
        dbs,
        ObjectId,
        chatFixture,
        workspaceFixture,
        resolvedActors: resolved,
        orgOid,
        anchorDate,
      });
      console.log(JSON.stringify({ ok: true, mode: 'apply', anchorDate, stats }, null, 2));
    } else if (args.mode === 'verify') {
      const result = await verifySeed({
        dbs,
        ObjectId,
        chatFixture,
        workspaceFixture,
        resolvedActors: resolved,
        orgOid,
        anchorDate,
      });
      console.log(JSON.stringify(result, null, 2));
      if (!result.ok) process.exitCode = 1;
    } else if (args.mode === 'reset-fixture') {
      const deleted = await resetFixture({
        dbs,
        ObjectId,
        chatFixture,
        workspaceFixture,
        resolvedActors: resolved,
      });
      console.log(JSON.stringify({ ok: true, mode: 'reset-fixture', deleted }, null, 2));
    }
  } finally {
    await client.close();
  }
}

if (
  process.argv[1] &&
  pathToFileURL(path.resolve(process.argv[1])).href === import.meta.url
) {
  main().catch((err) => {
    console.error('Seeder failed:', err.message);
    process.exit(1);
  });
}
