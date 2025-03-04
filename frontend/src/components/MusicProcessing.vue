<template>
  <div>
    <h2>Music Processing</h2>
    <button @click="processMusic" :disabled="isProcessing">Process Music</button>

    <div v-if="isProcessing">Processing...</div>

    <div v-if="chromagramData">
      <h3>Chromagram Data:</h3>
      <pre>{{ chromagramData }}</pre>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      isProcessing: false,
      chromagramData: null,
    };
  },
  methods: {
    async processMusic() {

      this.isProcessing = true;

      try {
        const response = await axios.post('http://localhost:5001/process-audio', {}, {
          headers: {
            'Content-Type': 'application/json',
          },
        });

        this.chromagramData = response.data.chromagram;
      } catch (error) {
        console.error("Error occured:", error);
      } finally {
        this.isProcessing = false;
      }
    },
  },
};
</script>

<style scoped>
/* Styling for later on */
</style>
