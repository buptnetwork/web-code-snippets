import { reactive } from 'vue'

// 公开浏览只加载这份轻量 UI 状态，不导入或初始化网络客户端。
export const classroomUi = reactive({ activated: false, panelOpen: false, status: '未连接' })

export function openClassroom() {
  classroomUi.activated = true
  classroomUi.panelOpen = true
}
