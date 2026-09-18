<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from 'vue'
import type { ClassroomStore } from '../../composables/useClassroom'
import type { ActivityDraft, ClassroomActivity, ClassroomConfig, CourseMetadata, DisplayMode, Visibility } from '../../types/classroom'
import ActivityEditor from './ActivityEditor.vue'
import ChoiceResults from './ChoiceResults.vue'
import JoinQrCode from './JoinQrCode.vue'
const props = defineProps<{ store: ClassroomStore; config: ClassroomConfig; metadata: CourseMetadata; page: number }>()
const emit = defineEmits<{ close: []; restoreDisplay: [] }>()
const state = props.store.state
const username = ref('')
const password = ref('')
const classLabel = ref('')
const pairingCode = ref('')
const tab = ref('session')
const confirmEnd = ref(false)
const visibility = ref<Visibility>('pending')
const editor = ref<{ initial?: ActivityDraft; id?: string; key: number } | null>(null)
let editorKey = 0
const active = computed(() => state.snapshot?.currentActivity)
const modes: { value: DisplayMode; label: string }[] = [
  { value: 'hidden', label: '隐藏投影' }, { value: 'join', label: '显示二维码' },
  { value: 'activity', label: '显示题目' }, { value: 'results', label: '显示结果 / 评论' },
]
const now = ref(Date.now())
const clock = setInterval(() => { now.value = Date.now() }, 1000)
onUnmounted(() => clearInterval(clock))
const pairingValid = computed(() => state.pairing && Date.parse(state.pairing.expiresAt) > now.value)
const phaseLabels = { idle: '未连接', connecting: '正在连接', connected: '实时同步中', reconnecting: '正在重连', ended: '课堂已结束' }

watch(() => state.snapshot?.sessionId, () => { editor.value = null; confirmEnd.value = false; tab.value = 'session' })
async function login() { try { await props.store.login(username.value.trim(), password.value) } finally { password.value = '' } }
async function resume() {
  const binding = state.resume
  if (!binding) return
  if (binding.role === 'teacher') { await props.store.checkTeacher(); if (!state.teacher) return }
  await props.store.connect(binding.sessionId, binding.role)
}
function edit(activity?: ClassroomActivity, copy = false) {
  editor.value = { initial: activity ? { type: activity.type, title: activity.title, options: activity.options?.map(option => ({ ...option })), selectionMode: activity.selectionMode, correctOptionIds: activity.correctOptionIds ? [...activity.correctOptionIds] : [], sourceSlide: activity.sourceSlide } : undefined, id: copy ? undefined : activity?.activityId, key: ++editorKey }
}
async function save(draft: ActivityDraft) { if (await props.store.saveActivity(draft, editor.value?.id)) editor.value = null }
async function changeTab(value: string) {
  tab.value = value
  if (value === 'activities') await props.store.loadActivities()
  if (value === 'comments') await props.store.loadComments(visibility.value)
}
</script>

<template>
  <div class="cr-stack">
    <p class="cr-muted">{{ metadata.courseName }} / {{ metadata.chapterName }}</p>
    <p v-if="state.error" class="cr-error" role="alert">{{ state.error }}</p>
    <p v-if="state.warning" class="cr-notice" role="status">{{ state.warning }}</p>
    <div v-if="!state.snapshot" class="cr-stack">
      <p class="cr-muted">公开课件无需登录。只有明确加入课堂后才连接实时服务。</p>
      <button v-if="state.resume" class="cr-button cr-primary" :disabled="state.busy" @click="resume">恢复上次{{ state.resume.role === 'teacher' ? '教师' : '展示端' }}连接</button>
      <div class="cr-row">
        <button class="cr-button" :disabled="state.busy" @click="store.checkTeacher()">教师登录 / 选择课堂</button>
        <button class="cr-button" :disabled="state.busy" @click="state.role = 'display'">作为展示端连接</button>
      </div>
      <form v-if="state.role === 'teacher' && !state.teacher" class="cr-card cr-stack" @submit.prevent="login">
        <h3 class="cr-subheading">教师登录</h3>
        <label class="cr-label">账号<input v-model="username" class="cr-input" autocomplete="username" maxlength="100" required></label>
        <label class="cr-label">密码<input v-model="password" type="password" class="cr-input" autocomplete="current-password" maxlength="256" required></label>
        <button class="cr-button cr-primary" :disabled="state.busy" type="submit">登录</button>
        <p class="cr-muted">账号由互动后端管理员创建。未部署后端时无法登录。</p>
      </form>
      <template v-else-if="state.role === 'teacher' && state.teacher">
        <div class="cr-row cr-between"><strong>{{ state.teacher.displayName }}</strong><button class="cr-button" :disabled="state.busy" @click="store.refreshSessions()">刷新课堂列表</button></div>
        <div v-for="session in state.sessions" :key="session.sessionId" class="cr-card cr-row cr-between">
          <span>{{ session.displayName }}</span><button class="cr-button" :disabled="state.busy" @click="store.connect(session.sessionId)">进入课堂</button>
        </div>
        <button v-if="state.nextSessionCursor" class="cr-button" :disabled="state.busy" @click="store.refreshSessions(true)">加载更多课堂</button>
        <p v-if="!state.sessions.length" class="cr-muted">当前章节暂无进行中的课堂，可以开启一次新课堂。</p>
        <form class="cr-card cr-stack" @submit.prevent="store.createSession(classLabel)">
          <label class="cr-label">班级标签（可选）<input v-model="classLabel" class="cr-input" maxlength="60" placeholder="例如：周四 1 班"></label>
          <button class="cr-button cr-primary" :disabled="state.busy" type="submit">开启新课堂</button>
          <p class="cr-muted">课程与章节来自课件；开始时间和唯一标识由后端生成。</p>
        </form>
      </template>
      <form v-else-if="state.role === 'display'" class="cr-card cr-stack" @submit.prevent="store.exchange(pairingCode)">
        <h3 class="cr-subheading">连接只读投影</h3>
        <label class="cr-label">教师提供的展示配对码<input v-model="pairingCode" class="cr-input" autocomplete="off" maxlength="10" pattern="[A-Za-z0-9]{10}" required></label>
        <button class="cr-button cr-primary" :disabled="state.busy" type="submit">连接展示端</button>
        <p class="cr-muted">配对码有效期 5 分钟，不是学生加入码。</p>
      </form>
    </div>
    <template v-else>
      <div class="cr-row cr-between"><h3 class="cr-subheading">{{ state.snapshot.session.displayName }}</h3><span class="cr-tag" role="status">{{ phaseLabels[state.phase] }}</span></div>
      <div class="cr-row"><button class="cr-button" @click="emit('restoreDisplay'); emit('close')">返回本地展示</button><button v-if="state.phase === 'reconnecting'" class="cr-button" @click="store.reconnect()">立即重连</button></div>
      <p v-if="state.role === 'display'" class="cr-notice">此窗口只有展示权限。题目、二维码与公开结果由教师窗口控制。</p>
      <p v-else-if="state.snapshot.session.status === 'ended'" class="cr-notice">课堂已结束，连接已关闭。退出互动后可开启新课堂。</p>
      <template v-else-if="state.role === 'teacher'">
        <p class="cr-notice">教师私有面板：包含待审核评论和未公开结果。使用双窗口授课可避免投影泄露。</p>
        <div class="cr-row"><span>已加入 {{ state.snapshot.participantCount ?? '—' }} 人</span><span>待审核 {{ state.snapshot.pendingCount ?? 0 }} 条</span></div>
        <div class="cr-row cr-wrap">
          <button v-for="mode in modes" :key="mode.value" class="cr-button" :class="{ 'cr-primary': state.snapshot.displayMode === mode.value }" :disabled="state.busy || ((mode.value === 'activity' || mode.value === 'results') && !active)" @click="store.setDisplay(mode.value)">{{ mode.label }}</button>
        </div>
        <nav class="cr-row cr-tabs" aria-label="教师操作分区">
          <button v-for="item in [{ id: 'session', label: '课堂与投影' }, { id: 'activities', label: '互动题目' }, { id: 'comments', label: '评论审核' }]" :key="item.id" class="cr-button" :class="{ 'cr-primary': tab === item.id }" :disabled="state.busy" @click="changeTab(item.id)">{{ item.label }}</button>
        </nav>
        <template v-if="tab === 'session'">
          <JoinQrCode v-if="state.snapshot.session.joinCode" :code="state.snapshot.session.joinCode" :student-base="config.studentBase" />
          <div class="cr-card cr-stack">
            <h3 class="cr-subheading">独立投影窗口</h3>
            <p class="cr-muted">在另一窗口打开同一章，选择“作为展示端连接”，输入下方配对码。</p>
            <div class="cr-row"><button class="cr-button" :disabled="state.busy" @click="store.createPairing()">生成展示配对码</button><button class="cr-button cr-danger" :disabled="state.busy" @click="store.revokeDisplay()">撤销全部展示授权</button></div>
            <p v-if="pairingValid" class="cr-join-code">{{ state.pairing?.code }}</p>
            <p v-else-if="state.pairing" class="cr-muted">配对码已到期，请重新生成。</p>
          </div>
        </template>
        <template v-else-if="tab === 'activities'">
          <div class="cr-row"><button class="cr-button cr-primary" :disabled="state.busy" @click="edit()">新建活动</button><button class="cr-button" :disabled="state.busy" @click="store.loadActivities()">刷新活动</button></div>
          <ActivityEditor v-if="editor" :key="editor.key" :initial="editor.initial" :page="page" :busy="state.busy" @save="save" @cancel="editor = null" />
          <article v-for="activity in state.activities" :key="activity.activityId" class="cr-card cr-stack">
            <div class="cr-row cr-between"><strong class="cr-prewrap">{{ activity.title }}</strong><span class="cr-tag">{{ { draft: '草稿', open: '进行中', closed: '已关闭' }[activity.status] }}</span></div>
            <div class="cr-row cr-wrap">
              <button v-if="activity.status === 'draft'" class="cr-button" :disabled="state.busy" @click="edit(activity)">编辑</button>
              <button class="cr-button" :disabled="state.busy" @click="edit(activity, true)">复制为新题</button>
              <button v-if="activity.status === 'draft'" class="cr-button cr-primary" :disabled="state.busy || active?.status === 'open'" @click="store.activityCommand(activity.activityId, 'open')">开始活动</button>
              <button v-if="activity.status === 'open'" class="cr-button" :disabled="state.busy" @click="store.activityCommand(activity.activityId, 'close')">停止收集</button>
              <button v-if="activity.type === 'choice' && activity.status === 'closed' && !activity.resultsPublished" class="cr-button" :disabled="state.busy" @click="store.activityCommand(activity.activityId, 'publication', { resultsPublished: true })">公开统计</button>
              <button v-if="activity.type === 'choice' && activity.resultsPublished && !activity.answersRevealed && activity.correctOptionIds?.length" class="cr-button" :disabled="state.busy" @click="store.activityCommand(activity.activityId, 'publication', { answersRevealed: true })">揭晓答案</button>
            </div>
          </article>
          <button v-if="state.nextActivityCursor" class="cr-button" :disabled="state.busy" @click="store.loadActivities(true)">加载更多活动</button>
          <div v-if="active?.type === 'choice' && state.snapshot.results" class="cr-card"><h3 class="cr-subheading">教师实时统计（不代表已公开）</h3><ChoiceResults :options="active.options || []" :results="state.snapshot.results" :multiple="active.selectionMode === 'multiple'" /></div>
        </template>
        <template v-else>
          <p v-if="active?.type !== 'text'" class="cr-empty">当前没有自由文本活动。</p>
          <template v-else>
            <div class="cr-row"><label class="cr-label">筛选<select v-model="visibility" class="cr-input" :disabled="state.busy" @change="store.loadComments(visibility)"><option value="pending">待审核</option><option value="visible">已公开</option><option value="hidden">已隐藏</option></select></label><button class="cr-button" :disabled="state.busy" @click="store.loadComments(visibility)">刷新评论</button></div>
            <p class="cr-muted">新评论数量实时更新；点击刷新加载列表。只有获准展示的内容会进入投影。</p>
            <article v-for="comment in state.comments" :key="comment.responseId" class="cr-card cr-stack">
              <p class="cr-prewrap">{{ comment.text }}</p>
              <div class="cr-row cr-wrap"><span class="cr-tag">{{ { pending: '待审核', visible: '已公开', hidden: '已隐藏' }[comment.visibility] }}</span><button class="cr-button" :disabled="state.busy" @click="store.moderate(comment.responseId, 'visible')">允许展示</button><button class="cr-button" :disabled="state.busy" @click="store.moderate(comment.responseId, 'visible', !comment.pinned)">{{ comment.pinned ? '取消精选' : '精选置顶' }}</button><button class="cr-button cr-danger" :disabled="state.busy" @click="store.moderate(comment.responseId, 'hidden')">隐藏</button></div>
            </article>
            <button v-if="state.nextCommentCursor" class="cr-button" :disabled="state.busy" @click="store.loadComments(visibility, true)">加载更多</button>
          </template>
        </template>
        <div class="cr-divider" />
        <button v-if="!confirmEnd" class="cr-button cr-danger" @click="confirmEnd = true">结束本次课堂…</button>
        <div v-else class="cr-error"><p>结束后学生不能再投稿，也不能恢复本次课堂。确认结束？</p><div class="cr-row"><button class="cr-button cr-danger" :disabled="state.busy" @click="store.endSession(); confirmEnd = false">确认结束课堂</button><button class="cr-button" @click="confirmEnd = false">取消</button></div></div>
      </template>
    </template>
    <p v-if="state.busy" class="cr-muted" role="status">正在处理…</p>
    <footer class="cr-row cr-wrap cr-footer"><button class="cr-button" @click="store.leave()">退出互动</button><button v-if="state.teacher" class="cr-button" :disabled="state.busy" @click="store.logout()">退出教师登录</button><span class="cr-muted">收起面板或退出互动不会结束课堂。</span></footer>
  </div>
</template>
