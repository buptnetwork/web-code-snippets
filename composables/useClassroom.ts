import { reactive } from 'vue'
import type { ActivityDraft, ClassroomActivity, ClassroomBinding, ClassroomComment, ClassroomConfig, ClassroomRole, ClassroomSession, ClassroomSnapshot, ConnectionPhase, CourseMetadata, DisplayMode, PageResult, Pairing, Teacher, Visibility } from '../types/classroom'
import { ClassroomError, ClassroomStream, createClassroomApi, parseSnapshot } from '../services/classroom-client'
import type { ClassroomApi, EventSourceLike } from '../services/classroom-client'
import { sameCourse } from '../services/slidev-classroom-adapter'

export function randomRequestId(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(16))
  return Array.from(bytes, value => value.toString(16).padStart(2, '0')).join('')
}

export function createClassroomStore(metadata: CourseMetadata, config: ClassroomConfig, options: {
  api?: ClassroomApi
  sourceFactory?: (url: string) => EventSourceLike
  storage?: Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>
} = {}) {
  const api = options.api || createClassroomApi(config.apiBase)
  const stream = new ClassroomStream(api, options.sourceFactory)
  const storage = options.storage
  const storageKey = `classroom:${metadata.courseId}:${metadata.deckId}`
  const state = reactive({
    role: null as ClassroomRole | null,
    teacher: null as Teacher | null,
    busy: false,
    error: '',
    warning: '',
    phase: 'idle' as ConnectionPhase,
    sessions: [] as ClassroomSession[],
    nextSessionCursor: null as string | null,
    snapshot: null as ClassroomSnapshot | null,
    activities: [] as ClassroomActivity[],
    nextActivityCursor: null as string | null,
    comments: [] as ClassroomComment[],
    nextCommentCursor: null as string | null,
    pairing: null as Pairing | null,
    resume: null as ClassroomBinding | null,
  })
  let generation = 0
  let controller: AbortController | undefined
  let commentRequest = 0
  const activityKeys = new Map<string, string>()
  let pendingCreation: { key: string; classLabel: string } | null = null

  function read(key: string): unknown {
    try { return JSON.parse(storage?.getItem(key) || 'null') }
    catch { return null }
  }
  function save(key: string, value: unknown) {
    try { if (value === null) storage?.removeItem(key); else storage?.setItem(key, JSON.stringify(value)) }
    catch { /* 禁用浏览器存储时仍可使用当前窗口。 */ }
  }
  const resume = read(storageKey) as ClassroomBinding | null
  if (resume && sameCourse(resume, metadata) && typeof resume.sessionId === 'string' && ['teacher', 'display'].includes(resume.role)) state.resume = resume

  function assertCurrent(token: number) {
    if (token !== generation) throw new DOMException('操作已取消', 'AbortError')
  }
  function invalidate(message: string) {
    leave()
    state.error = message
  }
  function accept(snapshot: ClassroomSnapshot) {
    if (!sameCourse(snapshot.session, metadata)) throw new ClassroomError('此课堂属于其他课程或章节，请打开对应课件。', 0, 'PROTOCOL_ERROR')
    const previous = state.snapshot
    if (previous?.sessionId === snapshot.sessionId && previous.revision > snapshot.revision) return
    if (previous?.currentActivity?.activityId !== snapshot.currentActivity?.activityId) {
      state.comments = []
      state.nextCommentCursor = null
      commentRequest++
    }
    state.snapshot = snapshot
    if (snapshot.session.status === 'ended') {
      stream.stop()
      state.warning = ''
      state.phase = 'ended'
      state.pairing = null
      state.resume = null
      save(storageKey, null)
    }
  }

  async function run<T>(operation: (signal: AbortSignal, token: number) => Promise<T>): Promise<T | undefined> {
    if (state.busy) return
    const token = generation
    controller = new AbortController()
    const signal = controller.signal
    state.busy = true
    state.error = ''
    try { return await operation(signal, token) }
    catch (error) {
      if (token !== generation || signal.aborted) return
      if (error instanceof ClassroomError && [401, 403].includes(error.status)) invalidate(error.message)
      else state.error = error instanceof Error ? error.message : '操作失败，请稍后重试。'
    }
    finally { if (token === generation) { state.busy = false; controller = undefined } }
  }

  async function listSessions(signal: AbortSignal, token: number, more = false) {
    const query = new URLSearchParams({ courseId: metadata.courseId, deckId: metadata.deckId, status: 'active', ...(more && state.nextSessionCursor ? { cursor: state.nextSessionCursor } : {}) })
    const result = await api.request<PageResult<ClassroomSession>>(`/sessions?${query}`, { signal })
    assertCurrent(token)
    if (!Array.isArray(result.items)) throw new ClassroomError('课堂列表格式不兼容。', 0, 'PROTOCOL_ERROR')
    const items = result.items.filter(session => sameCourse(session, metadata))
    state.sessions = more ? [...state.sessions, ...items] : items
    state.nextSessionCursor = result.nextCursor
  }
  async function checkTeacher() {
    return run(async (signal, token) => {
      state.role = 'teacher'
      let teacher: Teacher
      try { teacher = await api.request<Teacher>('/auth/me', { signal }) }
      catch (error) {
        if (error instanceof ClassroomError && error.status === 401) { assertCurrent(token); state.teacher = null; return }
        throw error
      }
      assertCurrent(token)
      state.teacher = teacher
      await listSessions(signal, token)
    })
  }
  async function login(username: string, password: string) {
    return run(async (signal, token) => {
      const teacher = await api.request<Teacher>('/auth/login', { method: 'POST', body: { username, password }, signal })
      assertCurrent(token)
      state.teacher = teacher
      state.role = 'teacher'
      await listSessions(signal, token)
    })
  }

  async function bind(sessionId: string, role: ClassroomRole, signal: AbortSignal, token: number) {
    const raw = await api.request<unknown>(`/sessions/${encodeURIComponent(sessionId)}/state?view=${role}`, { signal })
    assertCurrent(token)
    const snapshot = parseSnapshot(raw, sessionId)
    if (!sameCourse(snapshot.session, metadata)) throw new ClassroomError('此课堂属于其他课程或章节，请打开对应课件。')
    stream.stop()
    state.snapshot = null
    state.activities = []
    state.nextActivityCursor = null
    state.comments = []
    state.nextCommentCursor = null
    state.warning = ''
    state.pairing = null
    state.role = role
    accept(snapshot)
    if (snapshot.session.status === 'ended') return
    state.resume = { ...metadata, sessionId, role }
    save(storageKey, state.resume)
    stream.start(sessionId, role, {
      snapshot: accept,
      phase: phase => { state.phase = phase },
      warning: message => { state.warning = message },
      fatal: error => invalidate(error.message),
    })
  }
  const connect = (sessionId: string, role: ClassroomRole = 'teacher') => run((signal, token) => bind(sessionId, role, signal, token))

  async function createSession(classLabel: string) {
    return run(async (signal, token) => {
      const body = { ...metadata, classLabel: classLabel.trim() }
      const pendingKey = `${storageKey}:create`
      let pending = pendingCreation || read(pendingKey) as { key: string; classLabel: string } | null
      if (!pending || pending.classLabel !== body.classLabel || typeof pending.key !== 'string') {
        pending = { key: randomRequestId(), classLabel: body.classLabel }
        save(pendingKey, pending)
      }
      pendingCreation = pending
      const session = await api.request<ClassroomSession>('/sessions', { method: 'POST', body, key: pending.key, signal })
      assertCurrent(token)
      await bind(session.sessionId, 'teacher', signal, token)
      save(pendingKey, null)
      pendingCreation = null
    })
  }
  const exchange = (code: string) => run(async (signal, token) => {
    const result = await api.request<{ sessionId: string }>('/display/exchange', { method: 'POST', body: { code: code.trim().toUpperCase() }, signal })
    assertCurrent(token)
    // 配对已消费，即使随后读取失败，也能通过现有 Cookie 显式恢复。
    state.resume = { ...metadata, sessionId: result.sessionId, role: 'display' }
    save(storageKey, state.resume)
    await bind(result.sessionId, 'display', signal, token)
  })

  function sessionId() {
    if (state.role !== 'teacher' || !state.teacher || !state.snapshot || state.snapshot.session.status !== 'active')
      throw new ClassroomError('请先以教师身份连接一个进行中的课堂。')
    return state.snapshot.sessionId
  }
  async function refreshSnapshot(id: string, signal: AbortSignal, token: number) {
    const raw = await api.request<unknown>(`/sessions/${encodeURIComponent(id)}/state?view=teacher`, { signal })
    assertCurrent(token)
    accept(parseSnapshot(raw, id))
  }
  const setDisplay = (displayMode: DisplayMode) => run(async (signal, token) => {
    const id = sessionId()
    await api.request(`/sessions/${encodeURIComponent(id)}/display`, { method: 'PATCH', body: { displayMode }, signal })
    assertCurrent(token)
    await refreshSnapshot(id, signal, token)
  })
  const endSession = () => run(async (signal, token) => {
    const id = sessionId()
    await api.request(`/sessions/${encodeURIComponent(id)}/end`, { method: 'POST', signal })
    assertCurrent(token)
    stream.stop()
    state.phase = 'ended'
    state.pairing = null
    state.resume = null
    save(storageKey, null)
    if (state.snapshot) { state.snapshot.session.status = 'ended'; state.snapshot.displayMode = 'hidden' }
    await refreshSnapshot(id, signal, token)
  })
  const createPairing = () => run(async (signal, token) => {
    const result = await api.request<Pairing>(`/sessions/${encodeURIComponent(sessionId())}/pairings`, { method: 'POST', signal })
    assertCurrent(token)
    state.pairing = result
  })
  const revokeDisplay = () => run(async (signal, token) => {
    await api.request(`/sessions/${encodeURIComponent(sessionId())}/display-revoke`, { method: 'POST', signal })
    assertCurrent(token)
    state.pairing = null
  })

  async function fetchActivities(id: string, signal: AbortSignal, token: number, more = false) {
    const query = more && state.nextActivityCursor ? `?${new URLSearchParams({ cursor: state.nextActivityCursor })}` : ''
    const result = await api.request<PageResult<ClassroomActivity>>(`/sessions/${encodeURIComponent(id)}/activities${query}`, { signal })
    assertCurrent(token)
    if (!Array.isArray(result.items)) throw new ClassroomError('活动列表格式不兼容。', 0, 'PROTOCOL_ERROR')
    state.activities = more ? [...state.activities, ...result.items] : result.items
    state.nextActivityCursor = result.nextCursor
  }
  const loadActivities = (more = false) => run((signal, token) => fetchActivities(sessionId(), signal, token, more))
  const saveActivity = (draft: ActivityDraft, activityId?: string) => run(async (signal, token) => {
    const id = sessionId()
    const signature = `${id}:${JSON.stringify(draft)}`
    if (!activityKeys.has(signature)) activityKeys.set(signature, randomRequestId())
    await api.request(activityId ? `/activities/${encodeURIComponent(activityId)}` : `/sessions/${encodeURIComponent(id)}/activities`, {
      method: activityId ? 'PATCH' : 'POST', body: draft, key: activityId ? undefined : activityKeys.get(signature), signal,
    })
    assertCurrent(token)
    await fetchActivities(id, signal, token)
    activityKeys.delete(signature)
    return true
  })
  const activityCommand = (activityId: string, command: 'open' | 'close' | 'publication', publication?: { resultsPublished?: boolean; answersRevealed?: boolean }) => run(async (signal, token) => {
    const id = sessionId()
    await api.request(`/activities/${encodeURIComponent(activityId)}/${command}`, { method: command === 'publication' ? 'PATCH' : 'POST', body: publication, signal })
    assertCurrent(token)
    await refreshSnapshot(id, signal, token)
    await fetchActivities(id, signal, token)
  })
  const loadComments = (visibility: Visibility, more = false) => run(async (signal, token) => {
    sessionId()
    const activityId = state.snapshot?.currentActivity?.activityId
    if (!activityId) return
    const requestId = ++commentRequest
    const query = new URLSearchParams({ visibility, ...(more && state.nextCommentCursor ? { cursor: state.nextCommentCursor } : {}) })
    const result = await api.request<PageResult<ClassroomComment>>(`/activities/${encodeURIComponent(activityId)}/responses?${query}`, { signal })
    assertCurrent(token)
    if (requestId !== commentRequest || activityId !== state.snapshot?.currentActivity?.activityId) return
    state.comments = more ? [...state.comments, ...result.items] : result.items
    state.nextCommentCursor = result.nextCursor
  })
  const moderate = (responseId: string, visibility: 'visible' | 'hidden', pinned = false) => run(async (signal, token) => {
    const id = sessionId()
    const response = await api.request<ClassroomComment>(`/responses/${encodeURIComponent(responseId)}/moderation`, { method: 'PATCH', body: { visibility, pinned }, signal })
    assertCurrent(token)
    state.comments = state.comments.map(item => item.responseId === responseId ? response : item)
    await refreshSnapshot(id, signal, token)
  })
  const logout = () => run(async (signal, token) => {
    await api.request('/auth/logout', { method: 'POST', signal })
    assertCurrent(token)
    leave()
  })

  function dispose() {
    generation++
    controller?.abort()
    stream.stop()
    state.busy = false
  }
  function leave() {
    dispose()
    save(storageKey, null)
    state.role = null
    state.teacher = null
    state.snapshot = null
    state.sessions = []
    state.nextSessionCursor = null
    state.activities = []
    state.nextActivityCursor = null
    state.comments = []
    state.nextCommentCursor = null
    state.pairing = null
    state.resume = null
    state.phase = 'idle'
    state.error = state.warning = ''
    activityKeys.clear()
    pendingCreation = null
    save(`${storageKey}:create`, null)
  }
  return { state, checkTeacher, login, connect, createSession, exchange, setDisplay, endSession, createPairing, revokeDisplay,
    loadActivities, saveActivity, activityCommand, loadComments, moderate, logout, leave, dispose, reconnect: () => stream.reconnect(),
    refreshSessions: (more = false) => run((signal, token) => listSessions(signal, token, more)) }
}
export type ClassroomStore = ReturnType<typeof createClassroomStore>
