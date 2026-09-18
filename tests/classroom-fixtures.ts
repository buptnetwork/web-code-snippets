import { vi } from 'vitest'
import type { ClassroomSnapshot, CourseMetadata } from '../types/classroom'
import type { EventSourceLike } from '../services/classroom-client'

export const metadata: CourseMetadata = { courseId: 'web-development-2026b', courseName: '现代Web开发技术', deckId: 'ch00', chapterName: '课程导论' }
export const config = { enabled: true, apiBase: '/classroom-api/v1', studentBase: '/classroom' }
export function snapshot(revision = 1): ClassroomSnapshot {
  return {
    schemaVersion: 1, sessionId: 's1', revision, displayMode: 'hidden',
    session: { ...metadata, sessionId: 's1', displayName: '模拟课堂', status: 'active', startedAt: '2026-09-17T00:00:00Z', expiresAt: '2026-09-17T08:00:00Z', joinCode: 'ABCD2345' },
    currentActivity: { activityId: 'a1', sessionId: 's1', title: '你更喜欢哪种方式？', type: 'choice', selectionMode: 'single', options: [{ id: 'a', label: '先讨论' }, { id: 'b', label: '先实践' }], correctOptionIds: ['b'], status: 'open', resultsPublished: false, answersRevealed: false },
    results: { respondentCount: 2, counts: { a: 1, b: 1 } }, comments: [], participantCount: 3, pendingCount: 0,
  }
}
export class FakeSource implements EventSourceLike {
  listeners = new Map<string, ((event: MessageEvent) => void)[]>()
  close = vi.fn()
  addEventListener(name: string, callback: (event: MessageEvent) => void) {
    this.listeners.set(name, [...(this.listeners.get(name) || []), callback])
  }
  emit(name: string, value: unknown = {}) {
    for (const callback of this.listeners.get(name) || []) callback({ data: JSON.stringify(value) } as MessageEvent)
  }
}
export function memoryStorage() {
  const values = new Map<string, string>()
  return { getItem: (key: string) => values.get(key) ?? null, setItem: (key: string, value: string) => { values.set(key, value) }, removeItem: (key: string) => { values.delete(key) }, values }
}
export const json = (value: unknown, status = 200, headers = {}) => new Response(JSON.stringify(value), { status, headers: { 'Content-Type': 'application/json', ...headers } })
