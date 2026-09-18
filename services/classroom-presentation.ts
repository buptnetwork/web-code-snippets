import type { ActivityDraft, ClassroomSnapshot } from '../types/classroom'

export function validateActivityDraft(draft: ActivityDraft): string | null {
  if (!draft.title.trim() || [...draft.title.trim()].length > 500) return '题干需要 1～500 个字符。'
  if (draft.type === 'text') return null
  if (draft.type !== 'choice' || !['single', 'multiple'].includes(draft.selectionMode || '')) return '请选择有效题型。'
  const options = draft.options || []
  if (options.length < 2 || options.length > 8) return '选择题需要 2～8 个选项。'
  if (options.some(option => !option.label.trim() || [...option.label.trim()].length > 100)) return '每个选项需要 1～100 个字符。'
  if (new Set(options.map(option => option.id)).size !== options.length) return '选项编号不能重复。'
  const correct = draft.correctOptionIds || []
  if (correct.some(id => !options.some(option => option.id === id)) || new Set(correct).size !== correct.length) return '正确答案包含无效或重复的选项。'
  if (draft.selectionMode === 'single' && correct.length > 1) return '单选题最多设置一个正确答案。'
  return null
}

// 教师快照可能含未公开统计；投影渲染始终再按公开规则提取。
export function publicResults(snapshot: ClassroomSnapshot) {
  const activity = snapshot.currentActivity
  if (activity?.type !== 'choice' || activity.status !== 'closed' || !activity.resultsPublished) return null
  return snapshot.results
}
export function publicComments(snapshot: ClassroomSnapshot) {
  return snapshot.comments
    .filter(comment => comment.visibility === 'visible' && comment.activityId === snapshot.currentActivity?.activityId)
    .sort((a, b) => Number(b.pinned) - Number(a.pinned) || b.createdAt.localeCompare(a.createdAt))
    .slice(0, 20)
}
