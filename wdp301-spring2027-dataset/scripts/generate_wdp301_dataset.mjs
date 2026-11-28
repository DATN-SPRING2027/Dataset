#!/usr/bin/env node
/**
 * Deterministic generator for `wdp301-spring2027-dataset` (Full 360° synthetic dataset for WDP301-SPRING-2027).
 * Running this script repeatedly produces byte-for-byte identical JSON outputs.
 */

import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  ACTORS,
  DEFAULT_TIMEZONE,
  DEFAULT_UTC_OFFSET,
  FIXTURE_ID_PREFIX,
  ORG_ID,
  ORG_NAME,
  ORG_SLUG,
  PROJECTS,
  REAL_DOCS,
  REAL_TASKS,
  TIMELINE_EVENTS,
} from './_wdp301_catalog.mjs';
import { buildChatFixture } from './_wdp301_chat_data.mjs';
import {
  buildEvalCases,
  buildWorkspaceEnrichmentFixture,
} from './_wdp301_workspace_eval_data.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PKG_ROOT = path.resolve(__dirname, '..');

function assertValid(chatFixture, workspaceFixture, evalData) {
  // 1) Chronology check per conversation
  const anchor = '2026-11-28';
  for (const conv of chatFixture.conversations) {
    let prevTs = null;
    for (const msg of conv.messages) {
      const base = new Date(`${anchor}T00:00:00Z`);
      base.setUTCDate(base.getUTCDate() + msg.dayOffset);
      const localDate = base.toISOString().slice(0, 10);
      const ts = Date.parse(`${localDate}T${msg.timeLocal}${DEFAULT_UTC_OFFSET}`);
      if (!Number.isFinite(ts)) {
        throw new Error(`Invalid timestamp in ${conv.key} msg ${msg.id}`);
      }
      if (prevTs !== null && ts <= prevTs) {
        throw new Error(
          `Non-ascending timestamp in ${conv.key} at ${msg.id} (${localDate} ${msg.timeLocal})`,
        );
      }
      prevTs = ts;
    }
  }

  // 2) Strict dev / test source disjointness
  const devSources = new Set();
  const testSources = new Set();
  for (const c of evalData.cases) {
    const target = c.split === 'dev' ? devSources : testSources;
    for (const sid of [...c.requiredSourceIds, ...c.optionalSourceIds]) {
      target.add(sid);
    }
  }
  const overlap = [...devSources].filter((id) => testSources.has(id));
  if (overlap.length > 0) {
    throw new Error(
      `dev/test source overlap detected (${overlap.length}): ${overlap.join(', ')}`,
    );
  }

  // 3) Check off-page count in dm_wdp_01_pm_be
  const dm01 = chatFixture.conversations.find((c) => c.key === 'dm_wdp_01_pm_be');
  if (dm01.messages.length <= chatFixture.uiInitialPageSizeReference) {
    throw new Error('dm_wdp_01_pm_be must exceed UI initial page size (50)');
  }

  // 4) Check long technical message critical facts fit within 1180 chars
  const longMsg = dm01.messages.find((m) => m.alias === 'dm01_56');
  if (!longMsg || longMsg.content.length < 1200) {
    throw new Error('dm01_56 must be >= 1200 chars');
  }
  const head = longMsg.content.slice(0, 1180);
  for (const token of [
    '12 giây',
    '45 giây',
    'PAYMENT_BOUNDED_RETRY_ENABLED=true',
    'không xóa bản ghi sổ cái',
    '403 FORBIDDEN',
  ]) {
    if (!head.includes(token)) {
      throw new Error(`Missing critical token "${token}" inside first 1180 chars of dm01_56`);
    }
  }

  // 5) Check unique fixture IDs across ALL collections
  const allIds = new Set();
  const register = (id, label) => {
    if (!id.startsWith(FIXTURE_ID_PREFIX) || !/^[0-9a-f]{24}$/.test(id)) {
      throw new Error(`Invalid fixture ID ${id} for ${label}`);
    }
    if (allIds.has(id)) {
      throw new Error(`Duplicate fixture ID ${id} for ${label}`);
    }
    allIds.add(id);
  };
  for (const c of chatFixture.conversations) {
    register(c.id, `conv:${c.key}`);
    for (const m of c.messages) register(m.id, `msg:${c.key}:${m.id}`);
  }
  for (const r of workspaceFixture.taskComments) register(r.id, 'taskComment');
  for (const r of workspaceFixture.taskWorklogs) register(r.id, 'taskWorklog');
  for (const r of workspaceFixture.workNotes) {
    register(r.id, 'workNote');
    register(r.versionId, 'workNoteVersion');
  }
  for (const r of workspaceFixture.workReports) register(r.id, 'workReport');
  for (const h of workspaceFixture.handovers) {
    register(h.id, 'handover');
    register(h.item.id, 'handoverItemDoc');
    register(h.item.itemId, 'handoverItemId');
    register(h.revision.id, 'handoverRevision');
  }
}

async function main() {
  const { chatFixture, aliasToId } = buildChatFixture();
  const workspaceFixture = buildWorkspaceEnrichmentFixture();
  const evalData = buildEvalCases(aliasToId, workspaceFixture);

  assertValid(chatFixture, workspaceFixture, evalData);

  const metadata = {
    schemaVersion: '1.0.0',
    datasetId: 'wdp301-spring2027-full360-v1',
    datasetKind: 'synthetic_wdp301_timeline_and_reference_metadata',
    synthetic: true,
    review_status: 'unreviewed',
    targetOrganization: {
      organizationId: ORG_ID,
      slug: ORG_SLUG,
      name: ORG_NAME,
    },
    schedulePolicy: {
      timezone: DEFAULT_TIMEZONE,
      utcOffset: DEFAULT_UTC_OFFSET,
      businessHours: 'Mon-Fri 08:00-12:00, 13:00-17:00',
      lunchBreak: '12:00-13:00',
      justifiedOvertimePolicy:
        'Evening OT (17:30-22:00) and midnight boundary messages are explicitly tagged with reason and participants.',
      fixtureIdPrefix: FIXTURE_ID_PREFIX,
      preserveExistingRecordsPolicy:
        '100% additive insert-only ($setOnInsert). Never mutates or deletes pre-existing WDP301 tasks (474), documents (143), old reports (165), archived project PRTRESDAD131, existing DMs (9) or legacy messages ("helo", "Danh").',
    },
    counts: {
      actors: ACTORS.length,
      activeProjectsLinked: Object.keys(PROJECTS).length,
      realTasksReferenced: Object.keys(REAL_TASKS).length,
      realApprovedDocsReferenced: Object.keys(REAL_DOCS).length,
      directConversations: chatFixture.conversations.filter((c) => c.type === 'DIRECT').length,
      roomConversations: chatFixture.conversations.filter((c) => c.type === 'ROOM').length,
      chatMessages: chatFixture.conversations.reduce((sum, c) => sum + c.messages.length, 0),
      taskComments: workspaceFixture.taskComments.length,
      taskWorklogs: workspaceFixture.taskWorklogs.length,
      workNotes: workspaceFixture.workNotes.length,
      workReports: workspaceFixture.workReports.length,
      handovers: workspaceFixture.handovers.length,
      evalCasesTotal: evalData.cases.length,
      evalDevCases: evalData.splitSummary.devCases,
      evalTestCases: evalData.splitSummary.testCases,
      evalAclAndPolicyCases: evalData.splitSummary.aclDenyAndPolicyCases,
      liveE2eScenarios: evalData.liveE2eScenarios.length,
    },
    actors: ACTORS,
    projects: PROJECTS,
    referencedRealTasks: REAL_TASKS,
    referencedRealApprovedDocuments: REAL_DOCS,
    timelineEvents: TIMELINE_EVENTS,
  };

  for (const rel of ['metadata', 'seed', 'eval']) {
    await fs.mkdir(path.join(PKG_ROOT, rel), { recursive: true });
  }

  const writes = [
    ['metadata/timeline_and_mapping.json', metadata],
    ['seed/chat_fixture.json', chatFixture],
    ['seed/workspace_enrichment_fixture.json', workspaceFixture],
    ['eval/wdp301_eval_cases.json', evalData],
  ];

  for (const [relPath, payload] of writes) {
    const absPath = path.join(PKG_ROOT, relPath);
    await fs.writeFile(absPath, JSON.stringify(payload, null, 2) + '\n', 'utf8');
  }

  console.log('Generated wdp301-spring2027-dataset successfully:');
  console.log(JSON.stringify(metadata.counts, null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
