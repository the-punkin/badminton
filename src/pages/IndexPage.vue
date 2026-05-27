<template>
  <q-page class="pv-page" :class="dark ? 'pv-page--dark' : 'pv-page--light'">

    <!-- ── Hero ─────────────────────────────────────────── -->
    <section class="pv-hero">
      <div class="pv-container">
        <div class="row items-center q-col-gutter-xl">

          <!-- Left -->
          <div class="col-12 col-md-6">
            <div class="pv-eyebrow q-mb-md">
              <span>✦&nbsp; Pose Estimation · Biomechanics</span>
            </div>
            <h1 class="pv-hero__title q-mb-md"
                :class="dark ? 'text-grey-2' : 'text-grey-10'">
              Анализ движений<br>
              <span class="pv-gradient-text">на видео</span>
            </h1>
            <p class="pv-hero__desc q-mb-xl"
               :class="dark ? 'text-grey-5' : 'text-grey-7'">
              Загрузите видео, выделите спортсмена — получите аннотированное видео,
              графики угла локтя, скорости и высоты запястья в реальном времени.
            </p>
            <div class="row q-gutter-sm">
              <q-btn to="/upload" no-caps unelevated rounded
                     label="Загрузить видео" icon="cloud_upload"
                     class="pv-btn-primary q-px-xl q-py-sm" />
            </div>
          </div>

          <!-- Right: stat cards -->
          <div class="col-12 col-md-6">
            <div class="column q-gutter-md">

              <div class="pv-stat-card pv-card"
                   :class="dark ? 'pv-card--dark' : 'pv-card--light'">
                <div class="pv-stat-card__icon"
                     style="background:rgba(92,110,248,.12)">
                  <q-icon name="adjust" color="deep-purple-5" size="22px" />
                </div>
                <div>
                  <div class="pv-stat-card__value text-deep-purple-5">17</div>
                  <div class="pv-stat-card__label"
                       :class="dark ? 'text-grey-5' : 'text-grey-6'">
                    Ключевых точек скелета
                  </div>
                </div>
                <q-space />
              </div>

              <div class="pv-stat-card pv-card"
                   :class="dark ? 'pv-card--dark' : 'pv-card--light'">
                <div class="pv-stat-card__icon"
                     style="background:rgba(61,214,140,.12)">
                  <q-icon name="speed" color="green-6" size="22px" />
                </div>
                <div>
                  <div class="pv-stat-card__value text-green-6">30</div>
                  <div class="pv-stat-card__label"
                       :class="dark ? 'text-grey-5' : 'text-grey-6'">
                    Кадров в секунду
                  </div>
                </div>
                <q-space />
              </div>

              <div class="pv-stat-card pv-card"
                   :class="dark ? 'pv-card--dark' : 'pv-card--light'">
                <div class="pv-stat-card__icon"
                     style="background:rgba(255,152,0,.12)">
                  <q-icon name="movie" color="orange-7" size="22px" />
                </div>
                <div>
                  <div class="pv-stat-card__value text-orange-7">H.264</div>
                  <div class="pv-stat-card__label"
                       :class="dark ? 'text-grey-5' : 'text-grey-6'">
                    Кодек вывода · ffmpeg
                  </div>
                </div>
                <q-space />
              </div>

            </div>
          </div>

        </div>
      </div>
    </section>

    <q-separator :color="dark ? 'grey-9' : 'grey-3'" />

    <!-- ── Features ──────────────────────────────────────── -->
    <section class="pv-section">
      <div class="pv-container">
        <div class="pv-section__label q-mb-xl"
             :class="dark ? 'text-grey-6' : 'text-grey-5'">
          Возможности платформы
        </div>
        <div class="row q-col-gutter-md">
          <div v-for="feat in features" :key="feat.title"
               class="col-12 col-sm-6 col-md-3">
            <div class="pv-feat pv-card q-pa-lg full-height"
                 :class="dark ? 'pv-card--dark' : 'pv-card--light'">
              <div class="pv-feat__icon q-mb-md"
                   :style="{ background: feat.bg }">
                <q-icon :name="feat.icon" :color="feat.color" size="20px" />
              </div>
              <div class="pv-feat__title q-mb-xs"
                   :class="dark ? 'text-grey-2' : 'text-grey-10'">
                {{ feat.title }}
              </div>
              <div class="pv-feat__desc"
                   :class="dark ? 'text-grey-6' : 'text-grey-7'">
                {{ feat.desc }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <q-separator :color="dark ? 'grey-9' : 'grey-3'" />

    <!-- ── How it works ───────────────────────────────────── -->
    <section class="pv-section"
             :class="dark ? 'pv-section--alt-dark' : 'pv-section--alt-light'">
      <div class="pv-container">
        <div class="pv-section__label q-mb-xl"
             :class="dark ? 'text-grey-6' : 'text-grey-5'">
          Как это работает
        </div>
        <div class="row q-col-gutter-lg">
          <div v-for="(step, i) in steps" :key="i"
               class="col-12 col-sm-4">
            <div class="row items-start q-gutter-md">
              <div class="pv-step-num"
                   :class="dark ? 'pv-step-num--dark' : 'pv-step-num--light'">
                {{ i + 1 }}
              </div>
              <div class="col">
                <div class="pv-feat__title q-mb-xs"
                     :class="dark ? 'text-grey-2' : 'text-grey-10'">
                  {{ step.title }}
                </div>
                <div class="pv-feat__desc"
                     :class="dark ? 'text-grey-6' : 'text-grey-7'">
                  {{ step.desc }}
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="row justify-center q-mt-xl">
          <q-btn to="/upload" no-caps unelevated rounded
                 label="Начать анализ" icon="arrow_forward"
                 class="pv-btn-primary q-px-xl q-py-sm" />
        </div>
      </div>
    </section>

  </q-page>
</template>

<script>
export default {
  name: 'IndexPage',

  data() {
    return {
      features: [
        {
          icon: 'scatter_plot', color: 'deep-purple-5',
          bg: 'rgba(92,110,248,.1)',
          title: 'YOLO11 Pose',
          desc: 'Детекция 17 ключевых точек скелета на каждом кадре видео',
        },
        {
          icon: 'crop_free', color: 'green-6',
          bg: 'rgba(61,214,140,.1)',
          title: 'ROI-выделение',
          desc: 'Интерактивный выбор области интереса прямо на первом кадре видео',
        },
        {
          icon: 'show_chart', color: 'orange-7',
          bg: 'rgba(255,152,0,.1)',
          title: 'Биомеханика',
          desc: 'Угол локтя, высота и скорость запястья в динамике по времени',
        },
        {
          icon: 'sync', color: 'blue-6',
          bg: 'rgba(33,150,243,.1)',
          title: 'Async-обработка',
          desc: 'FastAPI BackgroundTasks — прогресс в реальном времени, не блокируя UI',
        },
      ],
      steps: [
        {
          title: 'Загрузите видео',
          desc: 'Поддерживаются форматы MP4, MOV, AVI, MKV. Файл отправляется на сервер и сохраняется.',
        },
        {
          title: 'Выделите игрока (ROI)',
          desc: 'На первом кадре нарисуйте прямоугольник вокруг спортсмена — сервер будет искать позу только внутри этой области.',
        },
        {
          title: 'Получите результат',
          desc: 'Аннотированное видео с наложенным скелетом и графики биомеханических показателей.',
        },
      ],
    }
  },

  computed: {
    dark() { return this.$q.dark.isActive },
  },
}
</script>

<style scoped>
/* ── Page ─────────────────────────────────────────────── */
.pv-page--light { background: #f7f8fc; }
.pv-page--dark  { background: #0e0e16; }

/* ── Container ────────────────────────────────────────── */
.pv-container {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 0 1.5rem;
}

/* ── Sections ─────────────────────────────────────────── */
.pv-hero    { padding: 5rem 0 4rem; }
.pv-section { padding: 4rem 0; }
.pv-section--alt-light { background: #ffffff; }
.pv-section--alt-dark  { background: #13131c; }
.pv-section__label {
  font-size: .7rem;
  font-weight: 700;
  letter-spacing: .12em;
  text-transform: uppercase;
}

/* ── Eyebrow ──────────────────────────────────────────── */
.pv-eyebrow span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: .72rem;
  font-weight: 700;
  letter-spacing: .12em;
  text-transform: uppercase;
  padding: .35rem 1rem;
  border-radius: 20px;
  background: rgba(92,110,248,.1);
  color: #7c8ef8;
  border: 1px solid rgba(92,110,248,.2);
}

/* ── Hero ─────────────────────────────────────────────── */
.pv-hero__title {
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 800;
  line-height: 1.12;
  letter-spacing: -.035em;
  margin: 0;
}
.pv-gradient-text {
  background: linear-gradient(95deg, #5c6ef8, #c084f8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.pv-hero__desc {
  font-size: .95rem;
  line-height: 1.75;
  max-width: 460px;
}

/* ── Buttons ──────────────────────────────────────────── */
.pv-btn-primary {
  background: linear-gradient(135deg, #5c6ef8, #9b8ef8) !important;
  color: #fff !important;
  font-weight: 600 !important;
}
.pv-btn-primary:hover {
  box-shadow: 0 8px 28px rgba(92,110,248,.35);
}

/* ── Cards ────────────────────────────────────────────── */
.pv-card { border-radius: 14px !important; transition: box-shadow .2s; }
.pv-card--light {
  background: #ffffff !important;
  border: 1px solid #ebebf5 !important;
}
.pv-card--dark {
  background: #18182a !important;
  border: 1px solid #25253a !important;
}
.pv-card--light:hover { box-shadow: 0 4px 24px rgba(92,110,248,.1); }
.pv-card--dark:hover  { box-shadow: 0 4px 24px rgba(0,0,0,.4); }

/* ── Stat cards ───────────────────────────────────────── */
.pv-stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
}
.pv-stat-card__icon {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.pv-stat-card__value {
  font-size: 1.6rem;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -.02em;
}
.pv-stat-card__label { font-size: .75rem; margin-top: 3px; }

/* ── Feature cards ────────────────────────────────────── */
.pv-feat { border-radius: 14px !important; }
.pv-feat__icon {
  width: 40px; height: 40px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
}
.pv-feat__title { font-size: .9rem; font-weight: 700; letter-spacing: -.01em; }
.pv-feat__desc  { font-size: .78rem; line-height: 1.65; }

/* ── Steps ────────────────────────────────────────────── */
.pv-step-num {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: .9rem; font-weight: 800; flex-shrink: 0;
}
.pv-step-num--light { background: rgba(92,110,248,.1);  color: #5c6ef8; }
.pv-step-num--dark  { background: rgba(92,110,248,.15); color: #9b8ef8; }

/* ── Responsive ───────────────────────────────────────── */
@media (max-width: 599px) {
  .pv-hero    { padding: 3rem 0 2.5rem; }
  .pv-section { padding: 2.5rem 0; }
  .pv-hero__title { font-size: 2rem; }
  .pv-container { padding: 0 1rem; }
}
</style>