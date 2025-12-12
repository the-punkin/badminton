<template>
    <q-page class="flex flex-center bg-grey-1">
        <q-card class="q-pa-lg" style="width: 600px; max-width: 90%;">
            <div class="column items-center">
                <div class="q-mt-lg col">
                <q-uploader
                    url="http://localhost:8000/upload"
                    label="Выберите видеофайл"
                    field-name="file"
                    accept="video/*"
                    @uploaded="onUploaded"
                />
                </div>
                <div class="q-mt-lg col">
                <div v-if="videoUrl">
                    <video class="shadow-2" style="max-width: 600px; width: 100%;" controls>
                    <source :src="videoUrl" type="video/mp4" />
                    </video>
                </div>
                </div>
            </div>
        </q-card>
    </q-page>   
</template>

<script>
export default {
  data() {
    return {
      videoUrl: null,
    };
  },
  methods: {
    onUploaded(info) {
      const response = JSON.parse(info.xhr.response);
      this.videoUrl = `http://localhost:8000/video/${response.filename}`;
    },
  },
};
</script>