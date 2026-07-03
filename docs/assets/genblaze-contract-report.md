# Genblaze SDK Contract Check

Mode: `sdk_contract_ready`
OK: `true`
Created: `2026-07-03T10:26:50Z`

## Package Versions

- `genblaze_core`: `0.3.4`
- `genblaze_gmicloud`: `0.3.2`
- `genblaze_openai`: `0.3.1`
- `genblaze_s3`: `0.3.4`

## Checks

- OK `genblaze_core_import`: genblaze_core is importable.
- OK `genblaze_core_KeyStrategy`: genblaze_core.KeyStrategy is present.
- OK `genblaze_core_Modality`: genblaze_core.Modality is present.
- OK `genblaze_core_ObjectStorageSink`: genblaze_core.ObjectStorageSink is present.
- OK `genblaze_core_Pipeline`: genblaze_core.Pipeline is present.
- OK `genblaze_gmicloud_import`: genblaze_gmicloud is importable.
- OK `genblaze_gmicloud_GMICloudImageProvider`: genblaze_gmicloud.GMICloudImageProvider is present.
- OK `genblaze_openai_import`: genblaze_openai is importable.
- OK `genblaze_openai_DalleProvider`: genblaze_openai.DalleProvider is present.
- OK `genblaze_s3_import`: genblaze_s3 is importable.
- OK `genblaze_s3_S3StorageBackend`: genblaze_s3.S3StorageBackend is present.
- OK `gmicloud_image_provider_ctor`: Required params: ['api_key', 'base_url', 'http_timeout']; observed params: ['api_key', 'base_url', 'http_client', 'http_timeout', 'models', 'poll_interval', 'probe_cache_max_entries', 'probe_cache_ttl', 'retry_policy'].
- OK `openai_image_provider_ctor`: Required params: ['api_key', 'http_timeout']; observed params: ['api_key', 'http_timeout', 'models', 'output_dir', 'probe_cache_max_entries', 'probe_cache_ttl', 'retry_policy'].
- OK `pipeline_ctor`: Required params: ['project_id']; observed params: ['chain', 'max_concurrency', 'moderation', 'name', 'preflight', 'project_id', 'structured_log', 'tenant_id', 'tracer'].
- OK `pipeline_methods_inspectable`: Required methods: ['run', 'step']; observed: ['run', 'step'].
- OK `pipeline_step_signature`: Required params: ['modality', 'model', 'prompt', 'provider']; observed params: ['expected_duration_sec', 'external_inputs', 'fallback_models', 'input_from', 'modality', 'model', 'params', 'prompt', 'provider', 'self', 'step_type'].
- OK `pipeline_step_aspect_ratio`: Pipeline.step must accept ProofFrame's aspect_ratio generation parameter directly or through **kwargs.
- OK `pipeline_run_signature`: Required params: ['max_retries', 'raise_on_failure', 'sink', 'timeout']; observed params: ['_config_override', '_owns_sink', 'fail_fast', 'max_retries', 'on_progress', 'on_retry', 'on_step_complete', 'pipeline_timeout', 'progress', 'raise_on_failure', 'self', 'sink', 'timeout'].
- OK `s3_for_backblaze_signature`: Required params: ['app_key', 'bucket', 'key_id', 'preflight', 'public_url_base', 'region']; observed params: ['app_key', 'auto_lifecycle', 'bucket', 'key_id', 'preflight', 'public_url_base', 'region'].
- OK `object_storage_sink_signature`: Required params: ['backend', 'key_strategy', 'prefix']; observed params: ['allow_unverified_manifest_reads', 'asset_url_policy', 'backend', 'eager_transfer', 'key_strategy', 'legacy_index_tenant_id', 'manifest_lock', 'max_upload_workers', 'parquet_sink', 'pipelined_transfer', 'prefix', 'strict_manifest_reads'].
- OK `s3_readback_methods`: Required methods: ['close', 'get', 'key_from_url']; observed: ['close', 'get', 'key_from_url'].
- OK `key_strategy_hierarchical`: KeyStrategy exposes HIERARCHICAL for per-campaign Genblaze B2 keys.

## Secret Policy

This report reads Python package metadata and callable signatures only. It does not read environment variables, credential files, provider responses, Backblaze keys, Genblaze provider keys, cookies, or signed URLs.
