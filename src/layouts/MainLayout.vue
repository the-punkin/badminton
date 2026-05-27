<template>
  <q-layout view="hHh lpR fFf">
    <!-- Кастомный хедер -->
    <q-header class="app-header" :class="$q.dark.isActive ? 'header-dark' : 'header-light'">
      <q-toolbar>
        <div class="logo row items-center q-gutter-sm">
          <div class="logo-icon">
            <q-icon name="scatter_plot" size="28px" color="white" />
          </div>
          <span class="logo-text">PoseVision</span>
        </div>

        <q-space />

        <q-tabs dense align="right" class="q-mr-sm" indicator-color="transparent">
          <q-route-tab to="/"       name="home"   no-caps label="Главная"  icon="home"        exact />
          <q-route-tab to="/upload" name="upload" no-caps label="Загрузка" icon="cloud_upload" />
        </q-tabs>

        <q-btn
          :icon="$q.dark.isActive ? 'light_mode' : 'dark_mode'"
          flat round dense
          @click="$q.dark.toggle()"
        />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>

    <!-- Кастомный футер -->
    <q-footer :class="$q.dark.isActive ? 'footer-dark' : 'footer-light'">
      <q-toolbar>
        <q-toolbar-title class="text-caption text-center footer-text">
          PoseVision · Сервис оценки игры в бадминтон · {{ new Date().getFullYear() }}
        </q-toolbar-title>
      </q-toolbar>
    </q-footer>
  </q-layout>
</template>

<script setup>
import { useQuasar } from 'quasar'

const $q = useQuasar()
</script>

<style scoped>
.app-header { transition: background .3s; }
.header-light { background: #ffffff; border-bottom: 1px solid #e8e8f0; color: #1a1a2e; }
.header-dark  { background: #16161f; border-bottom: 1px solid #2a2a3a; color: #e8e8f0; }

.logo-icon {
  width: 32px; height: 32px; border-radius: 8px;
  background: linear-gradient(135deg, #5c6ef8, #9b8ef8);
  display: flex; align-items: center; justify-content: center;
}
.logo-text { font-size: 1rem; font-weight: 700; letter-spacing: -.01em; }

.footer-light { background: #ffffff; border-top: 1px solid #e8e8f0; color: #bbb; }
.footer-dark  { background: #16161f; border-top: 1px solid #2a2a3a; color: #444; }
.footer-text  { font-size: .72rem; }
</style>