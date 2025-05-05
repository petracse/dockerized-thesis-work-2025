<template>
  <div class="chord-timeline" @click="onSeek($event)" ref="timeline">
    <div
      v-for="(section, idx) in visibleSections"
      :key="idx"
      class="chord-section"
      :style="{
        left: section.startPercent + '%',
        width: section.widthPercent + '%',
        background: section.color
      }"
    >
      <span class="chord-label">{{ section.chord }}</span>
    </div>
    <div class="playhead" :style="{ left: playheadPercent + '%' }"></div>
  </div>
</template>

<script>
const COLORS = [
  '#fbb4ae', '#b3cde3', '#ccebc5', '#decbe4',
  '#fed9a6', '#ffffcc', '#e5d8bd', '#fddaec',
  '#f2f2f2', '#b3e2cd', '#fdcdac', '#cbd5e8'
];

export default {
  name: "ChordTimeline",
  props: {
    chordsByTime: { type: Object, required: true },
    duration: { type: Number, required: true },
    currentTime: { type: Number, required: true },
    windowSize: { type: Number, default: 10 } // másodpercben
  },
  computed: {
    windowStart() {
      // Az ablak bal széle (ne menjen 0 alá)
      return Math.max(0, this.currentTime - this.windowSize / 2);
    },
    windowEnd() {
      // Az ablak jobb széle (ne menjen a dal végén túl)
      return Math.min(this.duration, this.windowStart + this.windowSize);
    },
    visibleSections() {
      if (!this.chordsByTime || this.duration === 0) return [];
      const times = Object.keys(this.chordsByTime)
        .map(Number)
        .sort((a, b) => a - b);
      const sections = [];
      for (let i = 0; i < times.length; i++) {
        const start = times[i];
        const end = times[i + 1] !== undefined ? times[i + 1] : this.duration;
        // Csak az ablakba eső szakaszokat vesszük figyelembe
        if (end < this.windowStart || start > this.windowEnd) continue;
        // A szakasz kezdete/vége az ablakhoz igazítva
        const clippedStart = Math.max(start, this.windowStart);
        const clippedEnd = Math.min(end, this.windowEnd);
        sections.push({
          start: clippedStart,
          end: clippedEnd,
          chord: this.chordsByTime[start],
          startPercent: ((clippedStart - this.windowStart) / (this.windowEnd - this.windowStart)) * 100,
          widthPercent: ((clippedEnd - clippedStart) / (this.windowEnd - this.windowStart)) * 100,
          color: COLORS[i % COLORS.length]
        });
      }
      return sections;
    },
    playheadPercent() {
      // A playhead pozíciója az ablakon belül
      return ((this.currentTime - this.windowStart) / (this.windowEnd - this.windowStart)) * 100;
    }
  },
  methods: {
    onSeek(event) {
      const rect = this.$refs.timeline.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const percent = x / rect.width;
      const seekTime = this.windowStart + percent * (this.windowEnd - this.windowStart);
      this.$emit('seek', seekTime);
    }
  }
};
</script>

<style scoped>
.chord-timeline {
  position: relative;
  height: 40px;
  background: #eee;
  border-radius: 8px;
  margin: 10px 0 20px 0;
  user-select: none;
  cursor: pointer;
  overflow: hidden;
}
.chord-section {
  position: absolute;
  top: 0;
  bottom: 0;
  border-right: 1px solid #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #222;
  font-size: 14px;
  opacity: 0.95;
  pointer-events: none;
}
.chord-label {
  padding: 0 6px;
  text-shadow: 1px 1px 2px #fff;
}
.playhead {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 3px;
  background: #222;
  border-radius: 2px;
  pointer-events: none;
  z-index: 10;
}
</style>
