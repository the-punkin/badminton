<template>
  <q-page class="pv-page" :class="dark ? 'pv-page--dark' : 'pv-page--light'">
    <div class="pv-container q-py-xl">

      <!-- ── Page heading ──────────────────────────────── -->
      <div class="q-mb-xl">
        <h1 class="pv-page-title q-mb-xs"
            :class="dark ? 'text-grey-2' : 'text-grey-10'">
          Обработка видео
        </h1>
        <p class="pv-page-sub q-mb-none"
           :class="dark ? 'text-grey-6' : 'text-grey-6'">
          Форматы: MP4 · MOV · AVI · MKV
        </p>
      </div>

      <!-- ── Pipeline indicator ────────────────────────── -->
      <div class="pv-pipeline q-mb-xl">
        <div v-for="(label, i) in pipelineSteps" :key="i"
             class="pv-pipeline__item">
          <div class="pv-pipeline__dot"
               :class="{
                 'pv-pipeline__dot--active':  currentStep === i,
                 'pv-pipeline__dot--done':    currentStep > i,
                 'pv-pipeline__dot--pending': currentStep < i,
               }">
            <q-icon v-if="currentStep > i" name="check" size="12px" />
            <span v-else>{{ i + 1 }}</span>
          </div>
          <div class="pv-pipeline__label gt-xs"
               :class="dark ? 'text-grey-6' : 'text-grey-5'">
            {{ label }}
          </div>
          <div v-if="i < pipelineSteps.length - 1"
               class="pv-pipeline__line"
               :class="currentStep > i ? 'pv-pipeline__line--done' : ''" />
        </div>
      </div>

      <!-- ── Row: Upload + Status ──────────────────────── -->
      <div class="row q-col-gutter-md q-mb-md">

        <!-- Upload -->
        <div class="col-12 col-md-6">
          <div class="pv-card pv-card--padded full-height"
               :class="dark ? 'pv-card--dark' : 'pv-card--light'">
            <div class="pv-card-head">
              <div class="pv-pill">1</div>
              <span class="pv-card-title"
                    :class="dark ? 'text-grey-5' : 'text-grey-5'">
                Загрузка файла
              </span>
            </div>
            <q-uploader
              ref="uploader"
              :url="uploadUrl"
              label="Выберите видеофайл"
              field-name="file"
              accept="video/*"
              flat bordered
              style="width:100%; border-radius:12px"
              :disable="uploading"
              @uploaded="onUploaded"
              @failed="onFailed"
            />
          </div>
        </div>

        <!-- Status -->
        <div class="col-12 col-md-6">
          <div class="pv-card pv-card--padded full-height"
               :class="dark ? 'pv-card--dark' : 'pv-card--light'">
            <div class="pv-card-head">
              <div class="pv-pill pv-pill--info">i</div>
              <span class="pv-card-title"
                    :class="dark ? 'text-grey-5' : 'text-grey-5'">
                Статус задачи
              </span>
              <q-space />
              <q-btn
                v-if="jobId && status !== 'done' && status !== 'error' && status !== null"
                icon="cancel" flat dense round size="sm" color="negative"
                @click="confirmCancel = true"
              />
            </div>

            <!-- idle -->
            <div v-if="!jobId" class="pv-empty">
              <q-icon name="hourglass_empty" size="2.2rem" />
              <span>Загрузите видео для начала</span>
            </div>

            <!-- uploaded: loading frame -->
            <div v-if="jobId && status === 'uploaded'" class="pv-empty">
              <q-spinner color="deep-purple-5" size="2rem" />
              <span>Загрузка первого кадра...</span>
            </div>

            <!-- roi ready -->
            <div v-if="jobId && status === 'roi_set'" class="pv-empty">
              <q-icon name="crop_free" size="2.2rem" color="deep-purple-4" />
              <span>Выбор ROI. Далее нажмите «Запустить»</span>
            </div>

            <!-- processing -->
            <template v-if="jobId && status === 'processing'">
              <div class="pv-meta q-mb-md">
                <div class="pv-meta-row">
                  <span class="pv-meta-key">Job ID</span>
                  <span class="pv-meta-val pv-meta-val--accent mono">{{ jobId }}</span>
                </div>
                <div class="pv-meta-row">
                  <span class="pv-meta-key">Статус</span>
                  <q-badge color="deep-purple-1" text-color="deep-purple-8"
                           label="processing" />
                </div>
                <div class="pv-meta-row">
                  <span class="pv-meta-key">Прогресс</span>
                  <span class="pv-meta-val mono">{{ progress }}%</span>
                </div>
              </div>
              <q-linear-progress
                :value="progress / 100"
                rounded size="6px"
                color="deep-purple-5"
                :track-color="dark ? 'deep-purple-10' : 'deep-purple-1'"
                class="q-mb-md"
              />
              <div class="row items-center q-gutter-sm">
                <q-spinner-dots color="deep-purple-5" size="20px" />
                <span class="text-caption"
                      :class="dark ? 'text-grey-6' : 'text-grey-6'">
                  Обработка кадров через YOLO11-pose...
                </span>
              </div>
            </template>

            <!-- done -->
            <template v-if="jobId && status === 'done'">
              <q-badge
                color="green-1" text-color="green-9"
                class="q-mb-md q-px-sm q-py-xs"
                style="border-radius:20px;letter-spacing:.06em;text-transform:uppercase;font-size:.68rem;font-weight:700"
              >
                <q-icon name="check_circle" color="positive" size="13px" class="q-mr-xs" />
                Готово
              </q-badge>
              <div class="pv-meta q-mb-md">
                <div class="pv-meta-row">
                  <span class="pv-meta-key">Job ID</span>
                  <span class="pv-meta-val pv-meta-val--accent mono">{{ jobId }}</span>
                </div>
                <div class="pv-meta-row">
                  <span class="pv-meta-key">Файл</span>
                  <span class="pv-meta-val mono">{{ jobId }}_pose.mp4</span>
                </div>
                <div class="pv-meta-row">
                  <span class="pv-meta-key">Кодек</span>
                  <span class="pv-meta-val mono">H.264 / yuv420p</span>
                </div>
                <div v-if="metrics.processed_points" class="pv-meta-row">
                  <span class="pv-meta-key">Точек данных</span>
                  <span class="pv-meta-val mono">{{ metrics.processed_points }}</span>
                </div>
                <div v-if="metrics.avg_angle" class="pv-meta-row">
                  <span class="pv-meta-key">Макс. угол локтя</span>
                  <span class="pv-meta-val mono">{{ metrics.avg_angle }}°</span>
                </div>
                <div v-if="metrics.max_velocity" class="pv-meta-row">
                  <span class="pv-meta-key">Макс. скорость</span>
                  <span class="pv-meta-val mono">{{ metrics.max_velocity }} px/s</span>
                </div>
              </div>
              <q-btn
                no-caps unelevated rounded
                icon="refresh" label="Новый файл"
                class="pv-btn-primary full-width"
                @click="resetState"
              />
            </template>

            <!-- error -->
            <q-banner
              v-if="errorMsg"
              rounded dense class="q-mt-sm"
              :class="dark ? 'bg-red-10 text-red-3' : 'bg-red-1 text-red-9'"
            >
              <template #avatar>
                <q-icon name="error_outline"
                        :color="dark ? 'red-4' : 'negative'" />
              </template>
              {{ errorMsg }}
            </q-banner>

          </div>
        </div>

      </div>

      <!-- ── Metric summary cards ───────────────────────── -->
      <div v-if="status === 'done' && metricsKeys.length > 0"
           class="row q-col-gutter-md q-mb-md">
        <div v-for="m in metricCards" :key="m.key" class="col-6 col-sm-3">
          <div v-if="metrics[m.key]"
               class="pv-metric-card pv-card"
               :class="dark ? 'pv-card--dark' : 'pv-card--light'">
            <div class="pv-metric-card__icon" :style="{ background: m.bg }">
              <q-icon :name="m.icon" :color="m.color" size="18px" />
            </div>
            <div class="pv-metric-card__val" :class="'text-' + m.color">
              {{ metrics[m.key] }}<span class="pv-metric-card__unit">{{ m.unit }}</span>
            </div>
            <div class="pv-metric-card__lbl"
                 :class="dark ? 'text-grey-6' : 'text-grey-6'">
              {{ m.label }}
            </div>
          </div>
        </div>
      </div>

      <!-- ── ROI selector ───────────────────────────────── -->
      <div
        v-if="jobId && firstFrameUrl && status !== 'processing' && !videoUrl"
        class="q-mb-md"
      >
        <div class="pv-card pv-card--padded"
             :class="dark ? 'pv-card--dark' : 'pv-card--light'">
          <div class="pv-card-head q-mb-md">
            <div class="pv-pill">2</div>
            <span class="pv-card-title"
                  :class="dark ? 'text-grey-5' : 'text-grey-5'">
              Выбор области интереса (ROI)
            </span>
            <q-space />
            <q-btn flat dense no-caps icon="refresh" label="Сбросить"
                   :color="dark ? 'grey-5' : 'grey-7'"
                   size="sm" class="q-mr-sm"
                   @click="clearROI" />
            <q-btn no-caps unelevated rounded
                   icon="play_arrow" label="Запустить обработку"
                   class="pv-btn-primary q-px-md"
                   :disable="!roiSelected"
                   @click="startProcessing" />
          </div>

          <q-banner dense rounded class="q-mb-md"
                    :class="dark ? 'bg-blue-10 text-blue-3' : 'bg-blue-1 text-blue-9'">
            <template #avatar>
              <q-icon name="info"
                      :color="dark ? 'blue-4' : 'blue-8'" size="18px" />
            </template>
            Зажмите левую кнопку мыши и перетащите для выделения области с игроком.
          </q-banner>

          <div class="roi-wrap"
               :class="dark ? 'roi-wrap--dark' : 'roi-wrap--light'">
            <canvas
              ref="roiCanvas"
              class="roi-canvas"
              @mousedown="onCanvasMouseDown"
              @mousemove="onCanvasMouseMove"
              @mouseup="onCanvasMouseUp"
              @mouseleave="onCanvasMouseUp"
            />
          </div>

          <div v-if="roiSelected"
               class="q-mt-sm row items-center q-gutter-xs">
            <q-icon name="check_circle" color="positive" size="16px" />
            <span class="text-caption text-positive text-weight-medium">
              ROI: x={{ roi.x }}, y={{ roi.y }}, {{ roi.w }}×{{ roi.h }} px
            </span>
          </div>
        </div>
      </div>

      <!-- ── Video result ───────────────────────────────── -->
      <div v-if="videoUrl" class="q-mb-md">
        <div class="pv-card pv-card--padded"
             :class="dark ? 'pv-card--dark' : 'pv-card--light'">
          <div class="pv-card-head q-mb-md">
            <div class="pv-pill pv-pill--done">
              <q-icon name="check" size="13px" />
            </div>
            <span class="pv-card-title"
                  :class="dark ? 'text-grey-5' : 'text-grey-5'">
              Аннотированное видео
            </span>
            <q-space />
            <q-btn flat dense no-caps icon="download" label="Скачать"
                   :color="dark ? 'grey-4' : 'grey-7'"
                   size="sm" tag="a" :href="videoUrl" target="_blank" />
          </div>
          <video :src="videoUrl" controls
                 style="width:100%;border-radius:10px;display:block;background:#000" />
        </div>
      </div>

      <!-- ── Charts ────────────────────────────────────── -->
      <div v-if="chartsUrl">
        <div class="pv-card pv-card--padded"
             :class="dark ? 'pv-card--dark' : 'pv-card--light'">
          <div class="pv-card-head q-mb-md">
            <div class="pv-pill pv-pill--done">
              <q-icon name="check" size="13px" />
            </div>
            <span class="pv-card-title"
                  :class="dark ? 'text-grey-5' : 'text-grey-5'">
              Графики биомеханики
            </span>
          </div>
          <q-img :src="chartsUrl"
                 style="width:100%;border-radius:10px"
                 spinner-color="deep-purple-5"
                 :ratio="16/9" />
        </div>
      </div>

    </div>

    <!-- ── Cancel dialog ─────────────────────────────────── -->
    <q-dialog v-model="confirmCancel">
      <q-card class="pv-dialog"
              :class="dark ? 'pv-dialog--dark' : ''">
        <q-card-section class="row items-center q-pa-lg q-gutter-md">
          <div class="pv-dialog-icon">
            <q-icon name="warning_amber" color="negative" size="26px" />
          </div>
          <div>
            <div class="text-weight-bold q-mb-xs">Отменить обработку?</div>
            <div class="text-caption"
                 :class="dark ? 'text-grey-5' : 'text-grey-6'">
              Загруженное видео и все данные будут удалены.
            </div>
          </div>
        </q-card-section>
        <q-separator :color="dark ? 'grey-8' : 'grey-3'" />
        <q-card-actions align="right" class="q-pa-md q-gutter-sm">
          <q-btn flat no-caps label="Нет"
                 :color="dark ? 'grey-4' : 'grey-7'"
                 v-close-popup />
          <q-btn no-caps unelevated rounded
                 label="Да, отменить" color="negative"
                 v-close-popup @click="cancelJob" />
        </q-card-actions>
      </q-card>
    </q-dialog>

  </q-page>
</template>

<script>
const API_BASE = 'http://localhost:8000'

export default {
  name: 'UploadPage',

  data() {
    return {
      // Upload
      uploadUrl: `${API_BASE}/upload`,
      uploading: false,

      // Job
      jobId: null,
      status: null,
      progress: 0,
      metrics: {},
      errorMsg: null,

      // First frame + ROI
      firstFrameUrl: null,
      firstFrameImage: null,
      roi: { x: 0, y: 0, w: 0, h: 0 },
      roiSelected: false,

      // Canvas drawing state
      isDrawing: false,
      startX: 0,
      startY: 0,
      canvasScale: 1,
      originalWidth: 0,
      originalHeight: 0,

      // Result
      videoUrl: null,
      chartsUrl: null,
      confirmCancel: false,

      // UI config
      pipelineSteps: ['Загрузка', 'ROI', 'Обработка', 'Результат'],

      metricCards: [
        {
          key: 'total_frames', icon: 'movie',
          color: 'deep-purple-5', bg: 'rgba(92,110,248,.1)',
          label: 'Кадров', unit: '',
        },
        {
          key: 'processed_points', icon: 'scatter_plot',
          color: 'green-6', bg: 'rgba(61,214,140,.1)',
          label: 'Точек данных', unit: '',
        },
        {
          key: 'avg_angle', icon: 'rotate_right',
          color: 'orange-7', bg: 'rgba(255,152,0,.1)',
          label: 'Макс. угол локтя', unit: '°',
        },
        {
          key: 'max_velocity', icon: 'speed',
          color: 'blue-6', bg: 'rgba(33,150,243,.1)',
          label: 'Макс. скорость', unit: ' px/s',
        },
      ],
    }
  },

  computed: {
    dark() { return this.$q.dark.isActive },

    metricsKeys() {
      return Object.keys(this.metrics)
        .filter(k => this.metrics[k] != null)
    },

    currentStep() {
      if (!this.jobId)                              return 0
      if (this.status === 'uploaded' ||
          this.status === 'roi_set')                return 1
      if (this.status === 'processing')             return 2
      if (this.status === 'done')                   return 4
      return 0
    },
  },

  methods: {

    // ── Upload ────────────────────────────────────────────

    onUploaded(info) {
      const response = JSON.parse(info.xhr.response)
      this.jobId = response.job_id
      this.status = 'uploaded'
      this.errorMsg = null
      this.videoUrl = null
      this.chartsUrl = null
      this.metrics = {}
      this.roiSelected = false
      this.progress = 0
      this.fetchFirstFrame()
    },

    onFailed() {
      this.errorMsg = 'Ошибка загрузки файла. Попробуйте снова.'
      this.status = null
      this.jobId = null
    },

    // ── First frame ───────────────────────────────────────

    async fetchFirstFrame() {
      if (!this.jobId) return
      try {
        const response = await fetch(`${API_BASE}/first_frame/${this.jobId}`)
        if (!response.ok) throw new Error('Failed to load first frame')
        const blob = await response.blob()
        this.firstFrameUrl = URL.createObjectURL(blob)
        this.$nextTick(() => this.loadImageToCanvas())
      } catch (err) {
        this.errorMsg = 'Ошибка загрузки первого кадра: ' + err.message
        this.status = 'error'
      }
    },

    // ── Canvas ────────────────────────────────────────────

    loadImageToCanvas() {
      const canvas = this.$refs.roiCanvas
      if (!canvas || !this.firstFrameUrl) return
      const ctx = canvas.getContext('2d')
      const img = new Image()
      img.onload = () => {
        this.originalWidth  = img.width
        this.originalHeight = img.height
        const maxW = Math.min(900, canvas.parentElement.clientWidth - 32)
        this.canvasScale = maxW / img.width
        const dW = Math.round(img.width  * this.canvasScale)
        const dH = Math.round(img.height * this.canvasScale)
        canvas.width  = dW
        canvas.height = dH
        canvas.style.width  = dW + 'px'
        canvas.style.height = dH + 'px'
        ctx.drawImage(img, 0, 0, dW, dH)
        this.firstFrameImage = img
        this.status = 'roi_set'
      }
      img.src = this.firstFrameUrl
    },

    onCanvasMouseDown(e) {
      if (!this.firstFrameImage) return
      const r = this.$refs.roiCanvas.getBoundingClientRect()
      this.isDrawing  = true
      this.startX     = e.clientX - r.left
      this.startY     = e.clientY - r.top
      this.roiSelected = false
    },

    onCanvasMouseMove(e) {
      if (!this.isDrawing) return
      const canvas = this.$refs.roiCanvas
      const r  = canvas.getBoundingClientRect()
      const cx = e.clientX - r.left
      const cy = e.clientY - r.top
      const ctx = canvas.getContext('2d')
      ctx.drawImage(this.firstFrameImage, 0, 0, canvas.width, canvas.height)
      const x = Math.min(this.startX, cx)
      const y = Math.min(this.startY, cy)
      const w = Math.abs(cx - this.startX)
      const h = Math.abs(cy - this.startY)
      ctx.strokeStyle = '#5c6ef8'
      ctx.lineWidth   = 2
      ctx.setLineDash([6, 4])
      ctx.strokeRect(x, y, w, h)
      ctx.fillStyle = 'rgba(92,110,248,0.15)'
      ctx.fillRect(x, y, w, h)
      ctx.setLineDash([])
      ctx.fillStyle = '#5c6ef8'
      ctx.font = 'bold 12px system-ui'
      ctx.fillText(
        `${Math.round(w / this.canvasScale)}×${Math.round(h / this.canvasScale)}`,
        x + 4, y - 6,
      )
    },

    onCanvasMouseUp(e) {
      if (!this.isDrawing) return
      this.isDrawing = false
      const canvas = this.$refs.roiCanvas
      const r    = canvas.getBoundingClientRect()
      const endX = e.clientX - r.left
      const endY = e.clientY - r.top
      const x = Math.round(Math.min(this.startX, endX) / this.canvasScale)
      const y = Math.round(Math.min(this.startY, endY) / this.canvasScale)
      const w = Math.round(Math.abs(endX - this.startX) / this.canvasScale)
      const h = Math.round(Math.abs(endY - this.startY) / this.canvasScale)
      if (w < 10 || h < 10) {
        const ctx = canvas.getContext('2d')
        ctx.drawImage(this.firstFrameImage, 0, 0, canvas.width, canvas.height)
        this.roiSelected = false
        return
      }
      this.roi         = { x, y, w, h }
      this.roiSelected = true
      // Draw final selection
      const ctx = canvas.getContext('2d')
      ctx.drawImage(this.firstFrameImage, 0, 0, canvas.width, canvas.height)
      const dx = Math.round(x * this.canvasScale)
      const dy = Math.round(y * this.canvasScale)
      const dw = Math.round(w * this.canvasScale)
      const dh = Math.round(h * this.canvasScale)
      ctx.strokeStyle = '#5c6ef8'
      ctx.lineWidth   = 2
      ctx.strokeRect(dx, dy, dw, dh)
      ctx.fillStyle = 'rgba(92,110,248,0.15)'
      ctx.fillRect(dx, dy, dw, dh)
      ctx.fillStyle = '#5c6ef8'
      ctx.font = 'bold 12px system-ui'
      ctx.fillText(`ROI ${w}×${h}`, dx + 4, dy - 6)
    },

    clearROI() {
      this.roi         = { x: 0, y: 0, w: 0, h: 0 }
      this.roiSelected = false
      if (this.firstFrameImage && this.$refs.roiCanvas) {
        const canvas = this.$refs.roiCanvas
        canvas.getContext('2d')
          .drawImage(this.firstFrameImage, 0, 0, canvas.width, canvas.height)
      }
    },

    // ── Start processing ──────────────────────────────────

    async startProcessing() {
      if (!this.jobId || !this.roiSelected) return
      try {
        const roiRes = await fetch(`${API_BASE}/roi/${this.jobId}`, {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify(this.roi),
        })
        if (!roiRes.ok) {
          throw new Error((await roiRes.json()).error || 'ROI error')
        }

        const procRes = await fetch(`${API_BASE}/process/${this.jobId}`, {
          method: 'POST',
        })
        if (!procRes.ok) {
          throw new Error((await procRes.json()).error || 'Process error')
        }

        this.status   = 'processing'
        this.errorMsg = null
        this.checkStatus()
      } catch (err) {
        this.errorMsg = 'Ошибка запуска обработки: ' + err.message
        this.status   = 'error'
      }
    },

    // ── Status polling ────────────────────────────────────

    async checkStatus() {
      if (!this.jobId) return
      try {
        const res  = await fetch(`${API_BASE}/status/${this.jobId}`)
        const data = await res.json()
        this.status   = data.status
        this.progress = data.progress || 0
        if (data.metrics) this.metrics = data.metrics
        if (data.status === 'done') {
          this.videoUrl  = `${API_BASE}/video/${this.jobId}`
          this.chartsUrl = `${API_BASE}/charts/${this.jobId}?t=${Date.now()}`
        } else if (data.status === 'error') {
          this.errorMsg = 'Ошибка обработки: ' + (data.error || 'Unknown error')
        } else {
          setTimeout(this.checkStatus, 1000)
        }
      } catch (err) {
        this.errorMsg = 'Ошибка сети: ' + err.message
        this.status   = 'error'
      }
    },

    // ── Cancel ────────────────────────────────────────────

    async cancelJob() {
      if (!this.jobId) return
      if (this.status !== 'done' && this.status !== 'error') {
        try {
          await fetch(`${API_BASE}/cancel/${this.jobId}`, { method: 'POST' })
        } catch (err) {
          console.warn('Cancel error:', err)
        }
      }
      this.resetState()
    },

    resetState() {
      if (this._pollTimer) {
        clearTimeout(this._pollTimer)
        this._pollTimer = null
      }
      this.jobId          = null
      this.status         = null
      this.progress       = 0
      this.metrics        = {}
      this.errorMsg       = null
      this.firstFrameUrl  = null
      this.firstFrameImage = null
      this.roi            = { x: 0, y: 0, w: 0, h: 0 }
      this.roiSelected    = false
      this.isDrawing      = false
      this.videoUrl       = null
      this.chartsUrl      = null
      this.confirmCancel  = false
      if (this.$refs.roiCanvas) {
        const ctx = this.$refs.roiCanvas.getContext('2d')
        ctx.clearRect(0, 0, this.$refs.roiCanvas.width, this.$refs.roiCanvas.height)
      }
      if (this.$refs.uploader) this.$refs.uploader.reset()
    },
  },
}
</script>

<style scoped>
/* ── Page ─────────────────────────────────────────────── */
.pv-page--light { background: #f7f8fc; }
.pv-page--dark  { background: #0e0e16; }

.pv-container {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 0 1.5rem;
}

/* ── Page title ───────────────────────────────────────── */
.pv-page-title {
  font-size: 1.6rem;
  font-weight: 800;
  letter-spacing: -.03em;
  margin: 0;
}
.pv-page-sub { font-size: .82rem; }

/* ── Pipeline ─────────────────────────────────────────── */
.pv-pipeline {
  display: flex;
  align-items: flex-start;
  gap: 0;
}
.pv-pipeline__item {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  flex: 1;
}
.pv-pipeline__dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: .75rem;
  font-weight: 700;
  transition: all .25s;
  z-index: 1;
}
.pv-pipeline__dot--active  { background: #5c6ef8; color: #fff; }
.pv-pipeline__dot--done    { background: #3dd68c; color: #fff; }
.pv-pipeline__dot--pending { background: #e8e9f1; color: #aaa; }
.pv-pipeline__label {
  font-size: .65rem;
  letter-spacing: .05em;
  text-transform: uppercase;
  margin-top: 5px;
  text-align: center;
}
.pv-pipeline__line {
  position: absolute;
  top: 14px;
  left: 50%;
  width: 100%;
  height: 2px;
  background: rgba(150,150,180,.2);
  z-index: 0;
}
.pv-pipeline__line--done { background: #3dd68c; }

/* ── Cards ────────────────────────────────────────────── */
.pv-card { border-radius: 14px !important; transition: box-shadow .2s; }
.pv-card--padded { padding: 1.25rem; }
.pv-card--light {
  background: #ffffff !important;
  border: 1px solid #ebebf5 !important;
}
.pv-card--dark {
  background: #18182a !important;
  border: 1px solid #25253a !important;
}

.pv-card-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 1rem;
}
.pv-card-title {
  font-size: .68rem;
  font-weight: 700;
  letter-spacing: .1em;
  text-transform: uppercase;
}

/* ── Step pills ───────────────────────────────────────── */
.pv-pill {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: .72rem;
  font-weight: 800;
  flex-shrink: 0;
  background: rgba(92,110,248,.12);
  color: #5c6ef8;
}
.pv-pill--info { background: rgba(33,150,243,.12); color: #2196f3; }
.pv-pill--done { background: rgba(61,214,140,.15); color: #3dd68c; }

/* ── Empty state ──────────────────────────────────────── */
.pv-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 140px;
  gap: 10px;
  font-size: .82rem;
  color: #9090a8;
}

/* ── Meta table ───────────────────────────────────────── */
.pv-meta { font-size: .8rem; }
.pv-meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: .5rem 0;
  border-bottom: 1px solid rgba(128,128,180,.1);
}
.pv-meta-row:last-child { border: none; }
.pv-meta-key {
  font-size: .68rem;
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: #9090a8;
}
.pv-meta-val { font-family: 'JetBrains Mono', monospace; font-size: .8rem; }
.pv-meta-val--accent { color: #7c8ef8; font-weight: 600; }
.mono { font-family: 'JetBrains Mono', monospace; font-size: .82rem; }

/* ── Buttons ──────────────────────────────────────────── */
.pv-btn-primary {
  background: linear-gradient(135deg, #5c6ef8, #9b8ef8) !important;
  color: #fff !important;
  font-weight: 600 !important;
}
.pv-btn-primary:hover { box-shadow: 0 8px 28px rgba(92,110,248,.35); }

/* ── Metric summary cards ─────────────────────────────── */
.pv-metric-card {
  padding: 1rem;
  border-radius: 12px !important;
  transition: transform .2s, box-shadow .2s;
}
.pv-metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,.1);
}
.pv-metric-card__icon {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: .6rem;
}
.pv-metric-card__val  {
  font-size: 1.35rem;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -.02em;
}
.pv-metric-card__unit { font-size: .75rem; font-weight: 500; }
.pv-metric-card__lbl  { font-size: .72rem; margin-top: 4px; }

/* ── ROI canvas ───────────────────────────────────────── */
.roi-wrap {
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  justify-content: center;
  max-height: 560px;
  overflow-y: auto;
}
.roi-wrap--light { background: #111; }
.roi-wrap--dark  { background: #050508; }
.roi-canvas {
  display: block;
  cursor: crosshair;
  max-width: 100%;
}

/* ── Dialog ───────────────────────────────────────────── */
.pv-dialog { border-radius: 16px !important; min-width: 320px; }
.pv-dialog--dark { background: #1a1a2e !important; color: #e8e8f4 !important; }
.pv-dialog-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(244,67,54,.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ── Responsive ───────────────────────────────────────── */
@media (max-width: 599px) {
  .pv-container   { padding: 0 1rem; }
  .pv-card--padded { padding: 1rem; }
  .pv-page-title  { font-size: 1.3rem; }
}
</style>