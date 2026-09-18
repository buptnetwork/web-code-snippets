export type ClassroomRole = 'teacher' | 'display'
export type ConnectionPhase = 'idle' | 'connecting' | 'connected' | 'reconnecting' | 'ended'
export type DisplayMode = 'hidden' | 'join' | 'activity' | 'results'
export type Visibility = 'pending' | 'visible' | 'hidden'

export interface CourseMetadata {
  courseId: string
  courseName: string
  deckId: string
  chapterName: string
}

export interface ClassroomConfig {
  enabled: boolean
  apiBase: string
  studentBase: string
}

export interface Teacher { teacherId: string; displayName: string }
export interface ClassroomSession extends CourseMetadata {
  sessionId: string
  displayName: string
  classLabel?: string
  status: 'active' | 'ended'
  startedAt: string
  expiresAt: string
  joinCode?: string
}

export interface ChoiceOption { id: string; label: string }
export interface ActivityDraft {
  type: 'choice' | 'text'
  title: string
  selectionMode?: 'single' | 'multiple'
  options?: ChoiceOption[]
  correctOptionIds?: string[]
  sourceSlide?: number
}
export interface ClassroomActivity extends ActivityDraft {
  activityId: string
  sessionId: string
  status: 'draft' | 'open' | 'closed'
  resultsPublished: boolean
  answersRevealed: boolean
}
export interface ChoiceStatistics {
  respondentCount: number
  counts: Record<string, number>
}
export interface ClassroomComment {
  responseId: string
  activityId: string
  text: string
  visibility: Visibility
  pinned: boolean
  createdAt: string
}
export interface ClassroomSnapshot {
  schemaVersion: 1
  revision: number
  sessionId: string
  session: ClassroomSession
  displayMode: DisplayMode
  currentActivity: ClassroomActivity | null
  results: ChoiceStatistics | null
  comments: ClassroomComment[]
  participantCount?: number
  pendingCount?: number
}
export interface PageResult<T> { items: T[]; nextCursor: string | null }
export interface Pairing { code: string; expiresAt: string }
export interface ClassroomBinding extends CourseMetadata { sessionId: string; role: ClassroomRole }
