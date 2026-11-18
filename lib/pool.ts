/** Run `worker` over `items` with at most `concurrency` in flight; stops early when `signal` aborts. */
export async function runPool<T>(items: T[], concurrency: number, worker: (item: T) => Promise<void>, signal: AbortSignal): Promise<void> {
  const queue = [...items];
  const lane = async () => {
    while (queue.length && !signal.aborted) await worker(queue.shift() as T);
  };
  await Promise.all(Array.from({ length: Math.min(concurrency, queue.length) }, lane));
}
