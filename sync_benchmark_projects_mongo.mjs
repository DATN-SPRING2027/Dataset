import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire('file:///D:/DoAnTotnghiep/DATN-BE/package.json');
const { MongoClient, ObjectId } = require('mongodb');

const MANIFEST_PATH = 'D:/DoAnTotnghiep/Dataset/reports/sag-mongo-sync-manifest.json';
const VAULT_ROOT = 'D:/DoAnTotnghiep/.data/continuum-vault';
const MONGO_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017';

async function ensureVaultFile(vaultKey, storagePath, contentType, updatedAtIso) {
  const targetPath = path.join(VAULT_ROOT, ...vaultKey.split('/'));
  const metaPath = `${targetPath}.meta.json`;
  await fs.mkdir(path.dirname(targetPath), { recursive: true });
  const bytes = await fs.readFile(storagePath);
  await fs.writeFile(targetPath, bytes);
  await fs.writeFile(
    metaPath,
    JSON.stringify(
      {
        size: bytes.length,
        contentType,
        updatedAt: updatedAtIso,
      },
      null,
      2,
    ),
    'utf8',
  );
  return bytes;
}

async function main() {
  const rawManifest = await fs.readFile(MANIFEST_PATH, 'utf8');
  const manifest = JSON.parse(rawManifest);

  const client = new MongoClient(MONGO_URI);
  await client.connect();

  try {
    const iamDb = client.db('continuum_iam');
    const captureDb = client.db('continuum_capture');

    const projectsCol = iamDb.collection('projects');
    const membershipsCol = iamDb.collection('project_memberships');
    const rolesCol = iamDb.collection('role_assignments');

    const docsCol = captureDb.collection('project_documents');
    const versCol = captureDb.collection('project_document_versions');

    const orgOid = new ObjectId(manifest.organizationId);
    const userOid = new ObjectId(manifest.userId);
    const roleOid = new ObjectId(manifest.teamLeaderRoleId);

    let syncedProjects = 0;
    let syncedDocs = 0;
    let syncedVaultFiles = 0;

    for (const proj of manifest.projects) {
      const projOid = new ObjectId(proj.projectId);
      const now = new Date();

      await projectsCol.updateOne(
        { _id: projOid },
        {
          $set: {
            organizationId: orgOid,
            name: proj.name,
            code: proj.code,
            description: proj.description,
            visibility: 'PRIVATE',
            status: 'ACTIVE',
            createdBy: userOid,
            updatedAt: now,
          },
          $setOnInsert: {
            createdAt: now,
          },
        },
        { upsert: true },
      );

      await membershipsCol.updateOne(
        {
          organizationId: orgOid,
          projectId: projOid,
          userId: userOid,
        },
        {
          $set: {
            status: 'ACTIVE',
            updatedAt: now,
          },
          $setOnInsert: {
            joinedAt: now,
            createdAt: now,
          },
        },
        { upsert: true },
      );

      await rolesCol.updateOne(
        {
          organizationId: orgOid,
          projectId: projOid,
          userId: userOid,
          roleCode: 'TEAM_LEADER',
        },
        {
          $set: {
            roleId: roleOid,
            assignedBy: userOid,
            updatedAt: now,
          },
          $setOnInsert: {
            createdAt: now,
          },
        },
        { upsert: true },
      );

      const activeDocOids = [];

      for (const doc of proj.documents) {
        const docOid = new ObjectId(doc.mongoDocId);
        const verOid = new ObjectId(doc.mongoVerId);
        activeDocOids.push(docOid);

        const createdAt = doc.createdAt ? new Date(doc.createdAt) : now;
        const updatedAt = doc.updatedAt ? new Date(doc.updatedAt) : now;
        const vaultKey = `work-notes/${manifest.organizationId}/${proj.projectId}/${doc.mongoDocId}/${doc.vaultUuid}`;

        const bytes = await ensureVaultFile(
          vaultKey,
          doc.storagePath,
          doc.contentType,
          updatedAt.toISOString(),
        );
        syncedVaultFiles += 1;

        let textContent = '';
        if (
          doc.contentType.includes('markdown') ||
          doc.contentType.includes('text') ||
          doc.filename.toLowerCase().endsWith('.md')
        ) {
          textContent = bytes.toString('utf8');
        } else {
          textContent = `# ${doc.title}\n\nBinary document artifact (${doc.filename}, ${bytes.length} bytes, SHA-256: \`${doc.fileHash}\`).`;
        }

        const knowledgeSync = {
          documentId: doc.mongoDocId,
          version: 1,
          sagDocumentId: doc.sagDocumentId,
          sagVersionId: doc.sagVersionId,
          sagVersionNo: doc.sagVersionNo,
          runId: doc.runId,
          fileHash: doc.fileHash,
          status: 'SEARCH_READY',
          searchStatus: 'SEARCH_READY',
          knowledgeStatus: 'DATA_READY',
          searchReady: true,
          knowledgeReady: true,
          isDuplicate: false,
          currentStage: 'COMPLETE',
          progress: 100,
          documentStatus: 'READY',
          parserProvider: doc.parserProvider,
          parserStatus: doc.parserStatus,
          chunkCount: doc.chunkCount,
          eventCount: doc.eventCount,
          tokenUsage: doc.tokenUsage,
          syncedAt: updatedAt.toISOString(),
        };

        const contStatus = doc.continuumStatus || 'APPROVED';
        const keFlag = doc.knowledgeEligible !== false;

        await docsCol.updateOne(
          { _id: docOid },
          {
            $set: {
              organizationId: orgOid,
              projectId: projOid,
              title: doc.title,
              description: doc.description,
              documentType: doc.documentType,
              createdByUserId: userOid,
              updatedByUserId: userOid,
              currentVersionNumber: 1,
              latestApprovedVersionNumber: contStatus === 'APPROVED' ? 1 : null,
              status: contStatus,
              datasetStatus: doc.datasetStatus || contStatus,
              knowledgeEligible: keFlag,
              knowledgeSync,
              updatedAt,
            },
            $setOnInsert: {
              createdAt,
            },
          },
          { upsert: true },
        );

        await versCol.updateOne(
          { _id: verOid },
          {
            $set: {
              organizationId: orgOid,
              projectId: projOid,
              documentId: docOid,
              versionNumber: 1,
              title: doc.title,
              description: doc.description,
              documentType: doc.documentType,
              content: textContent,
              file: {
                key: vaultKey,
                name: doc.filename,
                contentType: doc.contentType,
                size: bytes.length,
                sha256: doc.fileHash,
              },
              status: contStatus,
              datasetStatus: doc.datasetStatus || contStatus,
              knowledgeEligible: keFlag,
              editedByUserId: userOid,
              submittedAt: createdAt,
              reviewedByUserId: userOid,
              reviewedAt: updatedAt,
              reviewComment: `${contStatus} (datasetStatus=${doc.datasetStatus || contStatus}, knowledgeEligible=${keFlag}) — synchronized with SAG benchmark corpus.`,
              reviewHistory: [
                {
                  action: 'PENDING_REVIEW',
                  reviewerId: userOid,
                  at: createdAt,
                },
                {
                  action: contStatus,
                  reviewerId: userOid,
                  reviewerRole: 'MANAGER',
                  comment: `${contStatus} (datasetStatus=${doc.datasetStatus || contStatus}, knowledgeEligible=${keFlag}) — synchronized with SAG benchmark corpus.`,
                  at: updatedAt,
                },
              ],
              knowledgeSync,
              updatedAt,
            },
            $setOnInsert: {
              createdAt,
            },
          },
          { upsert: true },
        );

        syncedDocs += 1;
      }

      if (activeDocOids.length > 0) {
        await docsCol.deleteMany({
          projectId: projOid,
          _id: { $nin: activeDocOids },
        });
        await versCol.deleteMany({
          projectId: projOid,
          documentId: { $nin: activeDocOids },
        });
      }

      syncedProjects += 1;
      console.log(
        `[MongoSync] Synced project ${proj.code} (${proj.projectId}): ${proj.documents.length} documents`,
      );
    }

    console.log(
      `[MongoSync] COMPLETE: ${syncedProjects} projects, ${syncedDocs} documents, ${syncedVaultFiles} vault files.`,
    );
  } finally {
    await client.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
