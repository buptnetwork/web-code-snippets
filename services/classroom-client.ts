import type { ClassroomRole, ClassroomSnapshot, ConnectionPhase } from '../types/classroom'

export class ClassroomError extends Error {
  constructor(message: string, public status = 0, public code = 'NETWORK_ERROR', public retryAfter = 0) {
    super(message)
    this.name = 'ClassroomError'
  }
}

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH'
  body?: unknown
  key?: string
  signal?: AbortSignal
}

export type ClassroomFetch = (input: string, init?: RequestInit) => Promise<Response>

export function createClassroomApi(base: string, fetcher: ClassroomFetch = (input, init) => fetch(input, init)) {
  async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const controller = new AbortController()
    const abort = () => controller.abort()
    options.signal?.addEventListener('abort', abort, { once: true })
    if (options.signal?.aborted) controller.abort()
    const timeout = setTimeout(abort, 10_000)
    try {
      const method = options.method || 'GET'
      const response = await fetcher(`${base}${path}`, {
        method,
        credentials: 'same-origin',
        cache: 'no-store',
        redirect: 'error',
        signal: controller.signal,
        headers: {
          Accept: 'application/json',
          ...(method !== 'GET' ? { 'Content-Type': 'application/json' } : {}),
          ...(options.key ? { 'Idempotency-Key': options.key } : {}),
        },
        body: method === 'GET' ? undefined : JSON.stringify(options.body ?? {}),
      })
      if (response.status === 204) return undefined as T
      const json = response.headers.get('content-type')?.includes('application/json')
      let body: unknown = null
      if (json) {
        try { body = await response.json() }
        catch { throw new ClassroomError('互动服务返回了无效 JSON。', response.status, 'PROTOCOL_ERROR') }
      }
      const problem = record(body) ? body : null
      if (!response.ok) {
        const retry = response.headers.get('retry-after')
        const retryAfter = retry ? (Number.isFinite(Number(retry)) ? Number(retry) * 1000 : Math.max(0, Date.parse(retry) - Date.now())) : 0
        throw new ClassroomError(
          typeof problem?.message === 'string' ? problem.message : response.status === 401 ? '请先登录教师账号。' : `互动服务请求失败（${response.status}），请检查后端和代理配置。`,
          response.status, typeof problem?.code === 'string' ? problem.code : 'HTTP_ERROR', Number.isFinite(retryAfter) ? retryAfter : 0,
        )
      }
      if (!json || !body) throw new ClassroomError('互动服务未返回 JSON；可能尚未部署后端，或请求被静态站点回退。', 0, 'PROTOCOL_ERROR')
      return body as T
    }
    catch (error) {
      if (error instanceof ClassroomError) throw error
      if (options.signal?.aborted) throw new DOMException('操作已取消', 'AbortError')
      throw new ClassroomError(controller.signal.aborted ? '请求超时，请重试；创建操作会复用原请求编号。' : '无法连接互动服务，请检查网络或后端部署。')
    }
    finally {
      clearTimeout(timeout)
      options.signal?.removeEventListener('abort', abort)
    }
  }
  return { request, eventsUrl: (id: string, role: ClassroomRole) => `${base}/sessions/${encodeURIComponent(id)}/events?view=${role}` }
}
export type ClassroomApi = ReturnType<typeof createClassroomApi>

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}
const string = (value: unknown): value is string => typeof value === 'string'
const count = (value: unknown): value is number => typeof value === 'number' && Number.isInteger(value) && value >= 0

export function parseSnapshot(value: unknown, sessionId: string): ClassroomSnapshot {
  const fail = () => { throw new ClassroomError('课堂数据格式不兼容，请检查后端接口版本。', 0, 'PROTOCOL_ERROR') }
  if (!record(value) || value.schemaVersion !== 1 || value.sessionId !== sessionId || !count(value.revision)) return fail()
  const session = value.session
  if (!record(session) || session.sessionId !== sessionId || !['active', 'ended'].includes(String(session.status))
    || ['courseId', 'courseName', 'deckId', 'chapterName', 'displayName', 'startedAt', 'expiresAt'].some(key => !string(session[key]))) return fail()
  if (!['hidden', 'join', 'activity', 'results'].includes(String(value.displayMode))) return fail()
  const activity = value.currentActivity
  if (activity !== null) {
    if (!record(activity) || !string(activity.activityId) || activity.sessionId !== sessionId || !string(activity.title)
      || !['choice', 'text'].includes(String(activity.type)) || !['draft', 'open', 'closed'].includes(String(activity.status))
      || typeof activity.resultsPublished !== 'boolean' || typeof activity.answersRevealed !== 'boolean') return fail()
    if (activity.type === 'choice' && (!Array.isArray(activity.options) || !['single', 'multiple'].includes(String(activity.selectionMode))
      || activity.options.some(option => !record(option) || !string(option.id) || !string(option.label)))) return fail()
    if (activity.correctOptionIds !== undefined && (!Array.isArray(activity.correctOptionIds) || activity.correctOptionIds.some(id => !string(id)))) return fail()
  }
  if (value.results !== null && (!record(value.results) || !count(value.results.respondentCount) || !record(value.results.counts)
    || Object.values(value.results.counts).some(n => !count(n)))) return fail()
  if (!Array.isArray(value.comments) || value.comments.some(comment => !record(comment) || !string(comment.responseId)
    || !string(comment.activityId) || !string(comment.text) || !string(comment.createdAt)
    || !['pending', 'visible', 'hidden'].includes(String(comment.visibility)) || typeof comment.pinned !== 'boolean')) return fail()
  if (value.participantCount !== undefined && !count(value.participantCount)) return fail()
  if (value.pendingCount !== undefined && !count(value.pendingCount)) return fail()
  return value as unknown as ClassroomSnapshot
}

export interface EventSourceLike {
  addEventListener: (name: string, callback: (event: MessageEvent) => void) => void
  close: () => void
}
export interface StreamCallbacks {
  snapshot: (snapshot: ClassroomSnapshot) => void
  phase: (phase: ConnectionPhase) => void
  fatal: (error: ClassroomError) => void
  warning: (message: string) => void
}

// 每个管理器最多一个连接、一个重连定时器；构造函数没有网络副作用。
export class ClassroomStream {
  private source?: EventSourceLike
  private timer?: ReturnType<typeof setTimeout>
  private watchdog?: ReturnType<typeof setTimeout>
  private controller?: AbortController
  private generation = 0
  private attempt = 0
  private binding?: { id: string; role: ClassroomRole; callbacks: StreamCallbacks }

  constructor(private api: ClassroomApi, private sourceFactory: (url: string) => EventSourceLike = url => new EventSource(url)) {}

  start(id: string, role: ClassroomRole, callbacks: StreamCallbacks) {
    this.stop()
    this.binding = { id, role, callbacks }
    this.attempt = 0
    callbacks.phase('connecting')
    this.open(this.generation)
  }

  stop() {
    this.generation++
    this.source?.close()
    this.source = undefined
    clearTimeout(this.timer)
    clearTimeout(this.watchdog)
    this.timer = this.watchdog = undefined
    this.controller?.abort()
    this.controller = undefined
    this.binding = undefined
  }

  reconnect() {
    if (!this.binding) return
    this.source?.close()
    this.source = undefined
    clearTimeout(this.watchdog)
    clearTimeout(this.timer)
    this.controller?.abort()
    const generation = ++this.generation
    this.schedule(generation, 0)
  }

  private terminal(error: ClassroomError) {
    const callbacks = this.binding?.callbacks
    this.stop()
    callbacks?.fatal(error)
  }

  private receive(value: unknown, generation: number) {
    if (generation !== this.generation || !this.binding) return
    const snapshot = parseSnapshot(value, this.binding.id)
    const callbacks = this.binding.callbacks
    callbacks.snapshot(snapshot)
    if (snapshot.session.status === 'ended') {
      this.stop()
      callbacks.phase('ended')
    }
  }

  private open(generation: number) {
    const binding = this.binding
    if (!binding || generation !== this.generation) return
    const source = this.sourceFactory(this.api.eventsUrl(binding.id, binding.role))
    this.source = source
    const current = () => generation === this.generation && this.source === source
    const receive = (event: MessageEvent) => {
      if (!current()) return
      try {
        this.receive(JSON.parse(event.data), generation)
        if (!current()) return
        clearTimeout(this.watchdog)
        this.attempt = 0
        binding.callbacks.warning('')
        binding.callbacks.phase('connected')
      }
      catch (error) { this.terminal(error instanceof ClassroomError ? error : new ClassroomError('无法解析课堂事件。', 0, 'PROTOCOL_ERROR')) }
    }
    source.addEventListener('snapshot', receive)
    source.addEventListener('session.ended', receive)
    source.addEventListener('auth.expired', () => {
      if (current()) this.terminal(new ClassroomError('课堂授权已过期或被撤销，请重新连接。', 401, 'AUTH_EXPIRED'))
    })
    const retry = () => {
      if (!current()) return
      source.close()
      this.source = undefined
      clearTimeout(this.watchdog)
      binding.callbacks.warning('连接已断开，正在重新同步课堂。')
      this.schedule(generation)
    }
    source.addEventListener('error', retry)
    this.watchdog = setTimeout(retry, 15_000)
  }

  private schedule(generation: number, delay?: number) {
    if (generation !== this.generation || !this.binding) return
    this.binding.callbacks.phase('reconnecting')
    clearTimeout(this.timer)
    const wait = delay ?? Math.min(15_000, 1000 * 2 ** Math.min(this.attempt++, 4) * (1 + Math.random() * 0.2))
    this.timer = setTimeout(() => { void this.recover(generation) }, wait)
  }

  private async recover(generation: number) {
    if (generation !== this.generation || !this.binding) return
    const { id, role } = this.binding
    this.controller = new AbortController()
    try {
      const snapshot = await this.api.request<unknown>(`/sessions/${encodeURIComponent(id)}/state?view=${role}`, { signal: this.controller.signal })
      if (generation !== this.generation) return
      this.receive(snapshot, generation)
      if (this.binding && generation === this.generation) this.open(generation)
    }
    catch (error) {
      if (generation !== this.generation) return
      const problem = error instanceof ClassroomError ? error : new ClassroomError('重新连接失败。')
      if ([401, 403, 404, 410].includes(problem.status) || problem.code === 'PROTOCOL_ERROR') this.terminal(problem)
      else this.schedule(generation, problem.retryAfter || undefined)
    }
  }
}
