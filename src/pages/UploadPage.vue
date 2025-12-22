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
                <div v-if="processing" class="q-mt-md">
                  <q-spinner-dots color="primary" size="50px" />
                  <div>Видео обрабатывается...</div>
                </div>
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
        jobId: null,
        videoUrl: null,
        processing: false
    }
  },
  methods: {
    async onUploaded(info) {
      const response = JSON.parse(info.xhr.response);
      this.jobId = response.job_id;
      console.log("JOB ID:", this.jobId);
      this.processing = true;
      this.videoUrl = null;


        // Периодически проверяем статус
      this.checkStatus();
    },


    async checkStatus() {
      if (!this.jobId) return;


      try {
        const res = await fetch(`http://localhost:8000/status/${this.jobId}`);
        const data = await res.json();


        if (data.status === "done") {
          this.videoUrl = `http://172.19.0.1:8000/video/${this.jobId}`;
          this.processing = false;
          console.log("videoUrl =", this.videoUrl)


        } else if (data.status === "error") {
          alert("Ошибка обработки: " + data.error);
          this.processing = false;
        } else {
            // Ещё не готово, проверяем через секунду
          setTimeout(this.checkStatus, 1000);
        }


      } catch (err) {
        console.error(err);
        this.processing = false;
      }
    }
  },
};
</script>