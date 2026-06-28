# ProofFrame B2 Key Scope Checklist

Mode: `scope_ready_key_not_created`
OK: `true`
Safe to commit: `true`
Requires user confirmation before key creation: `true`

## Required Pre-Key Confirmation

- Status: `required_before_key_creation`
- Phrase: `I confirm ProofFrame B2 key scope: standard key, bucket proofframe-demo-a6b4e49, prefix campaigns/, no all-bucket access, no delete/admin permissions, and no secrets in chat/docs/git.`
- Do not include any key id, application key, account identifier, cookie, or screenshot in the confirmation.

## Target

- Bucket: `proofframe-demo-a6b4e49`
- Bucket type: `private`
- Endpoint: `s3.us-west-004.backblazeb2.com`
- Key name: `proofframe-demo-live-proof`
- Key kind: `standard_application_key`
- Forbidden key kind: `master_application_key`
- File prefix: `campaigns/`
- Preferred access: `Write Only`
- Recommended max duration: `604800` seconds

## Required Capabilities

- `writeFiles` - ProofFrame's B2 backend uploads generated media and manifests with S3 PutObject.
- `listAllBucketNames` - Backblaze documents this as required for bucket-restricted app keys used with S3 SDKs and integrations.

## Conditional Only

- `readFiles` - A final verification command is changed to perform HeadObject or GetObject against the uploaded proof objects.
- `listFiles` - A final verification command is changed to list only the configured ProofFrame prefix.

## Forbidden

- `deleteFiles` - The live proof only uploads new media and manifest objects; deletion is unnecessary.
- `writeBuckets/deleteBuckets` - The bucket is already created; key must not create, modify, or delete buckets.
- `writeBucketLifecycleRules` - Lifecycle policy changes are outside the proof path.
- `writeBucketEncryption` - Encryption configuration is not needed for the one-bucket upload proof.
- `writeBucketRetentions/writeFileRetentions/bypassGovernance` - Object Lock and governance operations are not part of ProofFrame's proof.
- `writeFileLegalHolds` - Legal hold updates are not needed for submission evidence.
- `writeBucketReplications/writeBucketNotifications/writeBucketLogging` - Replication, notifications, and logging are admin features outside the live proof.

## Operator Steps

1. Before creating the key, explicitly confirm the confirmation phrase from this checklist without adding any key values.
2. Create a standard application key, not a master application key.
3. Set the key name to `proofframe-demo-live-proof`.
4. Limit bucket access to the single bucket `proofframe-demo-a6b4e49`; do not choose all buckets.
5. Set the file name prefix to `campaigns/` so the key can only write ProofFrame proof objects.
6. Use Write Only access for the upload proof; add read/list only if a changed verification command explicitly needs it.
7. Enable `listAllBucketNames` for S3 SDK compatibility with the bucket-restricted key.
8. Set an expiration no longer than 604800 seconds for the hackathon proof window.
9. Copy the key id and application key only into `.env.final.local` through `python scripts/final_env_wizard.py --output .env.final.local --missing-only --force`.
10. Immediately run `python scripts/live_env_handoff.py --env-file .env.final.local --strict` and then the B2 proof runner.

## Stop Conditions

- Stop if the UI asks for or displays a master application key.
- Stop if bucket access cannot be limited to `proofframe-demo-a6b4e49`.
- Stop if the file prefix cannot be set to `campaigns/` and ask before widening scope.
- Stop if the key requires all-bucket access, bucket write/delete permissions, or deleteFiles.
- Stop if a screenshot, recording, terminal, browser address bar, or chat message would expose the key id or application key.
- Stop if any key value appears in a commit diff, generated report, or Devpost field.

## Next Commands After Key Entry

- `python scripts/live_env_handoff.py --env-file .env.final.local --strict`
- `python scripts/run_b2_live_proof.py --env-file .env.final.local --evidence-out docs/assets/b2-live-proof-evidence.json`

## Sources

- [Backblaze B2 S3-Compatible App Keys](https://www.backblaze.com/docs/cloud-storage-s3-compatible-app-keys) - Manual app key requirement, listAllBucketNames compatibility, and S3 capability mapping.
- [Backblaze Cloud Storage Application Keys](https://www.backblaze.com/docs/cloud-storage-application-keys) - Standard versus master application key, single-bucket scope, file prefix, and duration controls.

No key id, application key, token, cookie, signed URL, or account secret is stored here.
