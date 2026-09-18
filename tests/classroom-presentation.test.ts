import { describe, expect, it } from 'vitest'
import { publicComments, publicResults, validateActivityDraft } from '../services/classroom-presentation'
import { readCourseMetadata, resolveClassroomConfig, sameCourse, studentJoinUrl } from '../services/slidev-classroom-adapter'
import { metadata, snapshot } from './classroom-fixtures'

describe('课件配置隔离', () => {
  it('默认关闭，缺少元数据不猜测课程身份', () => {
    expect(resolveClassroomConfig({}, 'https://study.example').enabled).toBe(false)
    expect(readCourseMetadata({ title: '课程 · 第一章' })).toBeNull()
    expect(readCourseMetadata({ classroom: metadata })).toEqual(metadata)
    expect(sameCourse(metadata, { ...metadata, courseId: 'another-course' })).toBe(false)
  })
  it.each(['https://other.example/api', '//other.example/api', 'javascript:alert(1)', '/api?token=x', '/api#fragment'])('拒绝危险配置 %s', apiBase => {
    expect(() => resolveClassroomConfig({ VITE_CLASSROOM_API_BASE: apiBase }, 'https://study.example')).toThrow('同源')
  })
  it('二维码只包含同源学生路径与编码后的加入码，不依赖章节 base', () => {
    expect(studentJoinUrl('/classroom/', 'AB CD/123', 'https://study.example')).toBe('https://study.example/classroom/join/AB%20CD%2F123')
  })
})

describe('投影公开字段', () => {
  it('未关题或未公开时不得显示教师统计', () => {
    const state = snapshot()
    expect(publicResults(state)).toBeNull()
    state.currentActivity!.resultsPublished = true
    expect(publicResults(state)).toBeNull()
    state.currentActivity!.status = 'closed'
    expect(publicResults(state)).toEqual(state.results)
  })
  it('评论墙过滤未审核及其他题目，限制 20 条并优先精选', () => {
    const state = snapshot()
    state.comments = Array.from({ length: 25 }, (_, i) => ({ responseId: String(i), activityId: 'a1', text: `观点 ${i}`, visibility: 'visible', pinned: i === 0, createdAt: new Date(i * 1000).toISOString() }))
    state.comments.push({ ...state.comments[0], responseId: 'pending', visibility: 'pending' }, { ...state.comments[0], responseId: 'other', activityId: 'a2' }, { ...state.comments[0], responseId: 'hidden', visibility: 'hidden' })
    const comments = publicComments(state)
    expect(comments).toHaveLength(20)
    expect(comments[0].responseId).toBe('0')
    expect(comments.some(comment => ['pending', 'other', 'hidden'].includes(comment.responseId))).toBe(false)
  })
})

describe('题目约束', () => {
  it('投票可以不设正确答案，单选不能有多个答案', () => {
    const draft = { ...snapshot().currentActivity!, correctOptionIds: [] }
    expect(validateActivityDraft(draft)).toBeNull()
    expect(validateActivityDraft({ ...draft, correctOptionIds: ['a', 'b'] })).toContain('单选')
    expect(validateActivityDraft({ ...draft, selectionMode: 'multiple', correctOptionIds: ['a', 'b'] })).toBeNull()
  })
  it('校验题干、选项范围、重复 ID 和无效答案', () => {
    const draft = snapshot().currentActivity!
    expect(validateActivityDraft({ type: 'text', title: ' ' })).toContain('题干')
    expect(validateActivityDraft({ type: 'text', title: '中'.repeat(501) })).toContain('题干')
    expect(validateActivityDraft({ ...draft, options: [] })).toContain('2～8')
    expect(validateActivityDraft({ ...draft, options: [{ id: 'a', label: 'A' }, { id: 'a', label: 'B' }] })).toContain('重复')
    expect(validateActivityDraft({ ...draft, correctOptionIds: ['none'] })).toContain('无效')
  })
})
