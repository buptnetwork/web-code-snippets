import { afterEach, describe, expect, it, vi } from 'vitest'
import { ClassroomStream, createClassroomApi, parseSnapshot } from '../services/classroom-client'
import { FakeSource, json, snapshot } from './classroom-fixtures'

afterEach(() => vi.useRealTimers())

describe('HTTP 契约', () => {
  it('构造客户端不联网；写请求携带同源 Cookie、JSON 和幂等键', async () => {
    const fetcher = vi.fn(async () => json({ ok: true }))
    const api = createClassroomApi('/classroom-api/v1', fetcher)
    expect(fetcher).not.toHaveBeenCalled()
    await api.request('/sessions', { method: 'POST', body: { classLabel: '一班' }, key: 'same-key' })
    expect(fetcher).toHaveBeenCalledWith('/classroom-api/v1/sessions', expect.objectContaining({ credentials: 'same-origin', redirect: 'error', headers: expect.objectContaining({ 'Idempotency-Key': 'same-key', 'Content-Type': 'application/json' }) }))
  })
  it('拒绝静态 HTML 回退与无效 JSON', async () => {
    await expect(createClassroomApi('', async () => new Response('<html>课件</html>')).request('/auth/me')).rejects.toMatchObject({ code: 'PROTOCOL_ERROR' })
    await expect(createClassroomApi('', async () => new Response('{', { headers: { 'Content-Type': 'application/json' } })).request('/state')).rejects.toMatchObject({ code: 'PROTOCOL_ERROR' })
  })
  it('传递限流等待时间及中文错误', async () => {
    const api = createClassroomApi('', async () => json({ code: 'RATE_LIMIT', message: '稍后重试' }, 429, { 'Retry-After': '3' }))
    await expect(api.request('/sessions')).rejects.toMatchObject({ status: 429, retryAfter: 3000, message: '稍后重试' })
  })
  it('超时与用户取消可以区分', async () => {
    vi.useFakeTimers()
    const api = createClassroomApi('', (_url, init) => new Promise((_resolve, reject) => { init?.signal?.addEventListener('abort', () => reject(new DOMException('', 'AbortError'))) }))
    const request = api.request('/state')
    const check = expect(request).rejects.toThrow('请求超时')
    await vi.advanceTimersByTimeAsync(10_000)
    await check
    const controller = new AbortController()
    const cancelled = api.request('/state', { signal: controller.signal })
    controller.abort()
    await expect(cancelled).rejects.toMatchObject({ name: 'AbortError' })
    expect(vi.getTimerCount()).toBe(0)
  })
})

describe('快照校验', () => {
  it('接受当前契约', () => expect(parseSnapshot(snapshot(), 's1').revision).toBe(1))
  it.each([
    { schemaVersion: 2 }, { sessionId: 'other' }, { revision: -1 }, { comments: [{}] },
    { displayMode: 'unknown' }, { results: { respondentCount: -1, counts: {} } }, { currentActivity: undefined },
  ])('拒绝不兼容快照 %j', patch => {
    expect(() => parseSnapshot({ ...snapshot(), ...patch }, 's1')).toThrow('格式不兼容')
  })
})

function harness() {
  vi.useFakeTimers()
  const sources: FakeSource[] = []
  const fetcher = vi.fn(async () => json(snapshot()))
  const stream = new ClassroomStream(createClassroomApi('/classroom-api/v1', fetcher), () => { const source = new FakeSource(); sources.push(source); return source })
  const callbacks = { snapshot: vi.fn(), phase: vi.fn(), fatal: vi.fn(), warning: vi.fn() }
  return { sources, fetcher, stream, callbacks }
}

describe('SSE 生命周期', () => {
  it('初始零连接；重复绑定关闭旧连接；旧回调不能生效', () => {
    const { sources, stream, callbacks } = harness()
    expect(sources).toHaveLength(0)
    stream.start('s1', 'teacher', callbacks)
    stream.start('s1', 'teacher', callbacks)
    expect(sources[0].close).toHaveBeenCalledOnce()
    sources[0].emit('snapshot', snapshot())
    expect(callbacks.snapshot).not.toHaveBeenCalled()
    sources[1].emit('snapshot', snapshot())
    expect(callbacks.phase).toHaveBeenLastCalledWith('connected')
    stream.stop()
    expect(vi.getTimerCount()).toBe(0)
  })
  it('断线关闭原生连接，读取 state 后只建立一条新连接', async () => {
    const { sources, stream, callbacks, fetcher } = harness()
    stream.start('s1', 'display', callbacks)
    sources[0].emit('error')
    sources[0].emit('error')
    expect(sources[0].close).toHaveBeenCalledOnce()
    await vi.advanceTimersByTimeAsync(1300)
    expect(fetcher).toHaveBeenCalledOnce()
    expect(fetcher.mock.calls[0]).toEqual(expect.arrayContaining(['/classroom-api/v1/sessions/s1/state?view=display']))
    expect(sources).toHaveLength(2)
    stream.stop()
    expect(vi.getTimerCount()).toBe(0)
  })
  it.each([401, 403, 404, 410])('重连得到 %i 后终止，不无限重试', async status => {
    const { sources, stream, callbacks, fetcher } = harness()
    fetcher.mockImplementation(async () => json({ message: '授权不可用' }, status))
    stream.start('s1', 'teacher', callbacks)
    sources[0].emit('error')
    await vi.advanceTimersByTimeAsync(30_000)
    expect(fetcher).toHaveBeenCalledOnce()
    expect(callbacks.fatal).toHaveBeenCalledOnce()
    expect(sources).toHaveLength(1)
    expect(vi.getTimerCount()).toBe(0)
  })
  it('429 尊重 Retry-After', async () => {
    const { sources, stream, callbacks, fetcher } = harness()
    fetcher.mockImplementationOnce(async () => json({ message: '限流' }, 429, { 'Retry-After': '5' }))
    stream.start('s1', 'teacher', callbacks)
    sources[0].emit('error')
    await vi.advanceTimersByTimeAsync(1300)
    expect(fetcher).toHaveBeenCalledOnce()
    await vi.advanceTimersByTimeAsync(4000)
    expect(fetcher).toHaveBeenCalledOnce()
    await vi.advanceTimersByTimeAsync(1000)
    expect(sources).toHaveLength(2)
    stream.stop()
  })
  it.each(['auth.expired', 'session.ended'])('%s 关闭连接并清除重连任务', async event => {
    const { sources, stream, callbacks, fetcher } = harness()
    stream.start('s1', 'teacher', callbacks)
    const ended = snapshot(2); ended.session.status = 'ended'
    sources[0].emit(event, ended)
    sources[0].emit('error')
    await vi.advanceTimersByTimeAsync(60_000)
    expect(sources[0].close).toHaveBeenCalledOnce()
    expect(fetcher).not.toHaveBeenCalled()
    expect(vi.getTimerCount()).toBe(0)
  })
  it('首帧超时后校验状态，非法事件停止连接', async () => {
    const { sources, stream, callbacks, fetcher } = harness()
    stream.start('s1', 'teacher', callbacks)
    await vi.advanceTimersByTimeAsync(16_300)
    expect(fetcher).toHaveBeenCalledOnce()
    sources[1].emit('snapshot', { schemaVersion: 2 })
    expect(callbacks.fatal).toHaveBeenCalledOnce()
    expect(vi.getTimerCount()).toBe(0)
  })
  it('退出使已发出的恢复请求及旧事件失效', async () => {
    const { sources, stream, callbacks, fetcher } = harness()
    let resolve!: (value: Response) => void
    fetcher.mockImplementation(() => new Promise(done => { resolve = done }))
    stream.start('s1', 'teacher', callbacks)
    stream.reconnect()
    await vi.advanceTimersByTimeAsync(0)
    stream.stop()
    resolve(json(snapshot(10)))
    await vi.advanceTimersByTimeAsync(0)
    sources[0].emit('snapshot', snapshot(20))
    expect(callbacks.snapshot).not.toHaveBeenCalled()
    expect(sources).toHaveLength(1)
  })
})
