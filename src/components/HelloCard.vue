<template>
  <q-card class="q-ma-md">
    <q-card-section>
      <h4>{{ name }}</h4>
      <p>Возраст: {{ age }}</p>
    </q-card-section>
  </q-card>
</template>

<script setup>
defineProps({
  name: String,
  age: Number
})
</script>
