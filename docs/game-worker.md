# Game worker rollout

Queuesome currently defaults to `GAME_TASK_EXECUTION=legacy_thread`. This keeps
deployed behavior unchanged while the historical long-running game loop is
converted into bounded, retryable tasks.

The Procfile declares a database-backed worker process:

```text
worker: python manage.py process_tasks --queue game --sleep 1 --log-std
```

Do not set `GAME_TASK_EXECUTION=database_worker` until the game task is bounded
and a worker process is running. Enabling the setting without a worker leaves
games queued; scaling a worker without changing the setting starts an idle
process but does not move games off web threads.

## Staging activation checklist

1. Deploy the bounded game-task implementation with the legacy backend active.
2. Scale one staging worker and confirm it starts cleanly.
3. Set `GAME_TASK_EXECUTION=database_worker` on staging.
4. Complete a two-person round and verify queue, restart, and cancellation
   behavior.
5. Roll back by restoring `GAME_TASK_EXECUTION=legacy_thread`, then scale the
   worker to zero.

Production activation requires a separate cost and release approval.
