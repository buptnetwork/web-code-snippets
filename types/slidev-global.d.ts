import 'vue'

// 仅声明本地集成使用的模板接口；字段与已安装的 Slidev 52 useNav 核对。
// 不把 Slidev/Vite 的虚拟模块源码引入独立的课堂模块类型检查。
declare module 'vue' {
  interface ComponentCustomProperties {
    $nav: {
      slides: { meta?: { slide?: { frontmatter?: unknown } } }[]
      isPlaying: boolean
      isPresenter: boolean
      isPrintMode: boolean
      currentSlideNo: number
      currentLayout: string
    }
  }
}

declare global {
  interface ImportMetaEnv {
    readonly VITE_CLASSROOM_ENABLED?: string
    readonly VITE_CLASSROOM_API_BASE?: string
    readonly VITE_CLASSROOM_STUDENT_BASE?: string
    [key: string]: string | boolean | undefined
  }
  interface ImportMeta {
    readonly env: ImportMetaEnv
  }
}
