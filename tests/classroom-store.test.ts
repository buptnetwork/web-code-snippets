import { afterEach, describe, expect, it, vi } from 'vitest'
import { createClassroomStore } from '../composables/useClassroom'
import { createClassroomApi } from '../services/classroom-client'
import { config, FakeSource, json, memoryStorage, metadata, snapshot } from './classroom-fixtures'
import type { ClassroomSnapshot } from '../types/classroom'

const stores: ReturnType<typeof createClassroomStore>[] = []
afterEach(() => { stores.splice(0).forEach(store => store.dispose()); vi.useRealTimers() })
function harness(storage = memoryStorage()) {
  let current = snapshot()
  const sources: FakeSource[] = []
  const fetcher = vi.fn(async (url: string, _init?: RequestInit): Promise<Response> => {
    if (url.endsWith('/auth/me') || url.endsWith('/auth/login')) return json({ teacherId: 't1', displayName: '模拟教师' })
    if (url.includes('/state?')) return json(current)
    if (url.endsWith('/sessions')) return json(current.session)
    if (url.endsWith('/display/exchange')) return json({ sessionId: 's1' })
    if (url.includes('/sessions?')) return json({ items: [current.session], nextCursor: null })
    if (url.endsWith('/activities')) return json({ items: [current.currentActivity], nextCursor: null })
    return json({ ok: true })
  })
  const store = createClassroomStore(metadata, config, { storage, api: createClassroomApi(config.apiBase, fetcher), sourceFactory: () => { const source = new FakeSource(); sources.push(source); return source } })
  stores.push(store)
  return { store, storage, sources, fetcher, setSnapshot: (value: ClassroomSnapshot) => { current = value } }
}

describe('显式连接与课堂状态', () => {
  it('有恢复记录也不查询身份、不创建 SSE', () => {
    const storage = memoryStorage()
    storage.setItem(`classroom:${metadata.courseId}:${metadata.deckId}`, JSON.stringify({ ...metadata, sessionId: 's1', role: 'teacher' }))
    const { store, fetcher, sources } = harness(storage)
    expect(store.state.resume?.sessionId).toBe('s1')
    expect(fetcher).not.toHaveBeenCalled()
    expect(sources).toHaveLength(0)
  })
  it('教师身份查询不连接；显式选择课堂后才连接', async () => {
    const { store, sources } = harness()
    await store.checkTeacher()
    expect(store.state.teacher?.teacherId).toBe('t1')
    expect(sources).toHaveLength(0)
    await store.connect('s1')
    expect(sources).toHaveLength(1)
    sources[0].emit('snapshot', snapshot(2))
    sources[0].emit('snapshot', snapshot(1))
    expect(store.state.snapshot?.revision).toBe(2)
    expect(store.state.phase).toBe('connected')
  })
  it('拒绝其他章节，即使 sessionId 有效', async () => {
    const { store, sources, setSnapshot } = harness()
    const other = snapshot(); other.session.deckId = 'ch01'
    setSnapshot(other)
    await store.connect('s1')
    expect(store.state.error).toContain('其他课程或章节')
    expect(sources).toHaveLength(0)
    expect(store.state.snapshot).toBeNull()
  })
  it('401 后展示登录表单，而非自动创建课堂', async () => {
    const { store, sources, fetcher } = harness()
    fetcher.mockImplementationOnce(async () => json({ message: '请登录' }, 401))
    await store.checkTeacher()
    expect(store.state.role).toBe('teacher')
    expect(store.state.teacher).toBeNull()
    expect(sources).toHaveLength(0)
  })
  it('授权失效清除敏感状态、恢复绑定与旧事件', async () => {
    const { store, sources, storage } = harness()
    await store.checkTeacher(); await store.connect('s1'); await store.loadActivities()
    sources[0].emit('auth.expired')
    sources[0].emit('snapshot', snapshot(100))
    expect(store.state.snapshot).toBeNull()
    expect(store.state.teacher).toBeNull()
    expect(store.state.activities).toEqual([])
    expect(storage.values.size).toBe(0)
    expect(store.state.busy).toBe(false)
    expect(store.state.error).toContain('授权')
  })
  it('HTTP 读到终态同样关闭 SSE，不能复活课堂', async () => {
    const { store, sources, setSnapshot } = harness()
    await store.checkTeacher(); await store.connect('s1')
    const ended = snapshot(2); ended.session.status = 'ended'
    setSnapshot(ended)
    await store.setDisplay('hidden')
    expect(store.state.phase).toBe('ended')
    expect(sources[0].close).toHaveBeenCalled()
    sources[0].emit('snapshot', snapshot(3))
    expect(store.state.snapshot?.session.status).toBe('ended')
  })
  it('重复点击及未知结果重试复用创建幂等键', async () => {
    const { store, fetcher, sources } = harness()
    await store.checkTeacher()
    fetcher.mockImplementationOnce(async () => { throw new TypeError('network') })
    await store.createSession('一班')
    await Promise.all([store.createSession('一班'), store.createSession('一班')])
    const calls = fetcher.mock.calls.filter(([url]) => url.endsWith('/sessions'))
    expect(calls).toHaveLength(2)
    expect(calls[0][1]?.headers).toEqual(calls[1][1]?.headers)
    expect(sources).toHaveLength(1)
  })
  it('禁用 storage 时仍复用内存创建键', async () => {
    const storage = memoryStorage()
    storage.setItem = () => { throw new Error('storage blocked') }
    const { store, fetcher } = harness(storage)
    fetcher.mockImplementationOnce(async () => { throw new TypeError('network') })
    await store.createSession('一班'); await store.createSession('一班')
    const calls = fetcher.mock.calls.filter(([url]) => url.endsWith('/sessions'))
    expect(calls[0][1]?.headers).toEqual(calls[1][1]?.headers)
  })
  it('退出取消正在登录的请求，迟到响应不能恢复身份', async () => {
    const { store, fetcher } = harness()
    let resolve!: (value: Response) => void
    fetcher.mockImplementationOnce(() => new Promise(done => { resolve = done }))
    const pending = store.login('mock', 'not-a-real-password')
    store.leave()
    resolve(json({ teacherId: 't1', displayName: '迟到教师' }))
    await pending
    expect(store.state.teacher).toBeNull()
    expect(store.state.busy).toBe(false)
  })
  it('切题丢弃旧评论分页响应', async () => {
    const { store, sources, fetcher } = harness()
    await store.checkTeacher(); await store.connect('s1')
    let resolve!: (value: Response) => void
    fetcher.mockImplementationOnce(() => new Promise(done => { resolve = done }))
    const pending = store.loadComments('pending')
    const next = snapshot(2); next.currentActivity!.activityId = 'a2'
    sources[0].emit('snapshot', next)
    resolve(json({ items: [{ responseId: 'old' }], nextCursor: 'old-page' }))
    await pending
    expect(store.state.comments).toEqual([])
    expect(store.state.nextCommentCursor).toBeNull()
  })
  it('展示端配对后只有展示 SSE，不能通过 store 执行教师操作', async () => {
    const { store, sources, fetcher } = harness()
    await store.exchange('abc123abcd')
    expect(store.state.role).toBe('display')
    expect(sources).toHaveLength(1)
    fetcher.mockClear()
    await store.setDisplay('join')
    expect(fetcher).not.toHaveBeenCalled()
    expect(store.state.error).toContain('教师身份')
  })
  it('仅 dispose 保留显式恢复记录；leave 则清除', async () => {
    const { store, storage, sources } = harness()
    await store.connect('s1')
    store.dispose()
    expect(storage.values.size).toBe(1)
    expect(sources[0].close).toHaveBeenCalled()
    store.leave()
    expect(storage.values.size).toBe(0)
  })
  it('活动分页追加，刷新重置游标', async () => {
    const { store, fetcher } = harness()
    await store.checkTeacher(); await store.connect('s1')
    fetcher.mockImplementationOnce(async () => json({ items: [snapshot().currentActivity], nextCursor: 'p2' }))
    await store.loadActivities()
    fetcher.mockImplementationOnce(async () => json({ items: [{ ...snapshot().currentActivity, activityId: 'a2' }], nextCursor: null }))
    await store.loadActivities(true)
    expect(fetcher.mock.lastCall?.[0]).toContain('cursor=p2')
    expect(store.state.activities).toHaveLength(2)
    await store.loadActivities()
    expect(store.state.activities).toHaveLength(1)
    expect(store.state.nextActivityCursor).toBeNull()
  })
})
