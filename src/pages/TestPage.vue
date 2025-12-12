<template>
  <q-page class="q-pa-lg">

    <h4>Учебник всплывающих элементов Quasar</h4>

    <!-- Q-TOOLBAR -->
    <q-toolbar class="bg-primary text-white q-mt-md q-mb-lg">
      <q-btn flat round dense icon="menu" />
      <q-toolbar-title>Моя панель инструментов</q-toolbar-title>
      <q-btn flat label="Профиль" />
    </q-toolbar>

    <!-- Q-DIALOG -->
    <q-btn color="primary" label="Открыть диалог" @click="showDialog = true" />

    <q-dialog v-model="showDialog">
      <q-card style="min-width: 300px">
        <q-card-section>
          <div class="text-h6">Диалоговое окно</div>
        </q-card-section>

        <q-card-section>
          Это пример QDialog. Он закрывается по кнопке ниже.
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat color="primary" label="Закрыть" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Q-POPUP-PROXY -->
    <div class="q-mt-lg">
      <q-btn color="secondary" label="Показать popup" ref="popupBtn">
        <q-popup-proxy>
          <q-card class="q-pa-md">
            Всплывающее окно через QPopupProxy.
          </q-card>
        </q-popup-proxy>
      </q-btn>
    </div>

    <!-- Q-TOOLTIP -->
    <div class="q-mt-lg">
      <q-btn color="accent" icon="help">
        <q-tooltip>
          Это подсказка!
        </q-tooltip>
      </q-btn>
    </div>

    <!-- Q-NOTIFY -->
    <div class="q-mt-lg">
      <q-btn
        color="positive"
        label="Показать уведомление"
        @click="notifySuccess"
      />
    </div>

  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { useQuasar } from 'quasar'

const $q = useQuasar()

// Dialog
const showDialog = ref(false)

// Notify
const notifySuccess = () => {
  console.log('notifySuccess called')
  $q.notify({
    message: 'Операция успешно выполнена!',
    icon: 'check',
    color: 'positive',
    position: 'top-right'
  })
}
</script>
