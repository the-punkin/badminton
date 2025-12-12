<template>
  <q-page class="flex flex-center bg-grey-2">
    <div class="column items-center q-pa-xl q-gutter-md">

      <div class="text-h4 text-primary text-weight-bold">
        Добро пожаловать!
      </div>

      <div class="text-subtitle1 text-grey-7">
        Здесь вы можете загрузить видео и просмотреть результат
      </div>

      <q-btn 
        label="Перейти к загрузке видео"
        color="primary"
        size="lg"
        icon="videocam"
        to="/upload"
        class="q-mt-md"
        unelevated
        rounded
      />
    </div>
  </q-page>
  <q-footer class="text-center bg-primary text-white q-pa-md">

      <div class="text-subtitle2">
        Видео-сервис • {{ new Date().getFullYear() }}
      </div>
      <div class="text-caption q-mt-xs">
        Создано для тестирования загрузки и воспроизведения видео
      </div>
    </q-footer>
</template>
