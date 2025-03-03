<template>
  <div>
    <h2>Music Processing</h2>
    <button @click="processMusic" :disabled="isProcessing">Process Music</button>

    <!-- Ha zajlik a feldolgozás, ezt jelezhetjük -->
    <div v-if="isProcessing">Processing...</div>

    <!-- Az eredmény megjelenítése -->
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
      isProcessing: false,  // Jelzi, hogy zajlik a feldolgozás
      chromagramData: null, // Az API válasz
    };
  },
  methods: {
    async processMusic() {
      // A feldolgozás elindítása
      this.isProcessing = true;

      try {
        // Küldjük a kérés a backendnek, hogy indítsa el a zenei feldolgozást
        const response = await axios.post('http://localhost:5001/process-audio', {}, {
          headers: {
            'Content-Type': 'application/json',
          },
        });

        // A válasz (pl. a chromagram adatok) tárolása
        this.chromagramData = response.data.chromagram;
      } catch (error) {
        console.error("Hiba történt:", error);
      } finally {
        // A feldolgozás vége
        this.isProcessing = false;
      }
    },
  },
};
</script>

<style scoped>
/* Stílusok, ha szükséges */
</style>
