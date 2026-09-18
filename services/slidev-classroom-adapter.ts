import type { ClassroomConfig, CourseMetadata } from '../types/classroom'

export function readCourseMetadata(frontmatter: unknown): CourseMetadata | null {
  const value = (frontmatter as { classroom?: Record<string, unknown> } | null)?.classroom
  const fields = ['courseId', 'courseName', 'deckId', 'chapterName'] as const
  if (!value || fields.some(key => typeof value[key] !== 'string' || !value[key].trim())) return null
  return Object.fromEntries(fields.map(key => [key, (value[key] as string).trim()])) as unknown as CourseMetadata
}

export function sameCourse(a: CourseMetadata, b: CourseMetadata): boolean {
  return a.courseId === b.courseId && a.deckId === b.deckId
}

// Cookie 方案仅支持同源地址；错误配置不能把教师登录信息发往其他站点。
export function sameOriginBase(value: string, origin: string): string {
  const url = new URL(value, origin)
  if (!['http:', 'https:'].includes(url.protocol) || url.origin !== origin || url.username || url.password || url.search || url.hash)
    throw new Error('互动地址必须是同源 HTTP(S) 路径，且不能包含查询参数。')
  return url.pathname.replace(/\/+$/, '')
}

export function resolveClassroomConfig(env: Record<string, string | boolean | undefined>, origin: string): ClassroomConfig {
  return {
    enabled: env.VITE_CLASSROOM_ENABLED === 'true',
    apiBase: sameOriginBase(String(env.VITE_CLASSROOM_API_BASE || '/classroom-api/v1'), origin),
    studentBase: sameOriginBase(String(env.VITE_CLASSROOM_STUDENT_BASE || '/classroom'), origin),
  }
}

export function studentJoinUrl(base: string, code: string, origin: string): string {
  return new URL(`${sameOriginBase(base, origin)}/join/${encodeURIComponent(code)}`, origin).href
}
