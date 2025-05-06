<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Songs</h1>
        <hr>
        <alert :message="message" v-if="showMessage"></alert>
        <button
          type="button"
          class="btn btn-success btn-sm"
          @click="toggleAddSongModal">
          Add Song
        </button>
        <br><br>
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col">Title</th>
              <th scope="col">Author</th>
              <th scope="col">File</th>
              <th scope="col">Created At</th>
              <th scope="col">Updated At</th>
            <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(song, index) in songs" :key="index">
              <td>{{ song.title }}</td>
              <td>{{ song.author }}</td>
              <td>
                <a :href="'http://localhost:5001/uploads/' + song.filename" target="_blank" v-if="song.filename">{{ song.filename }}</a>
                <span v-else>No file</span>
              </td>
              <td>{{ formatIsoDate(song.created_at) }}</td>
              <td>{{ formatIsoDate(song.updated_at) }}</td>
              <td>
                <div class="btn-group" role="group">
                  <button
                    type="button"
                    class="btn btn-warning btn-sm"
                    @click="toggleEditSongModal(song)">
                    Analyze / Update
                  </button>
                  <button
                    type="button"
                    class="btn btn-danger btn-sm"
                    @click="handleDeleteSong(song)">
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add new song modal -->
    <div
      ref="addSongModal"
      class="modal fade"
      :class="{ show: activeAddSongModal, 'd-block': activeAddSongModal }"
      tabindex="-1"
      role="dialog">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add a new song</h5>
            <button
              type="button"
              class="close"
              data-dismiss="modal"
              aria-label="Close"
              @click="toggleAddSongModal">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="handleAddSubmit" enctype="multipart/form-data">
              <div class="mb-3">
                <label for="addSongTitle" class="form-label">Title:</label>
                <input
                  type="text"
                  class="form-control"
                  id="addSongTitle"
                  v-model="addSongForm.title"
                  placeholder="Enter title">
              </div>
              <div class="mb-3">
                <label for="addSongAuthor" class="form-label">Author:</label>
                <input
                  type="text"
                  class="form-control"
                  id="addSongAuthor"
                  v-model="addSongForm.author"
                  placeholder="Enter author">
              </div>
              <div class="mb-3">
                <label for="addSongYtUrl" class="form-label">(Optional) YouTube URL:</label>
                <input
                  type="text"
                  class="form-control"
                  id="addSongYtUrl"
                  v-model="addSongForm.yt_url"
                  placeholder="Enter YouTube URL">
              </div>

              <div class="mb-3">
                <label for="addSongFile" class="form-label">File:</label>
                <input
                  type="file"
                  class="form-control"
                  id="addSongFile"
                  @change="handleFileUpload">
                <!-- File deletion button -->
                <button
                  type="button"
                  class="btn btn-danger btn-sm mt-2"
                  @click="handleFileRemove"
                  v-if="selectedFile">
                  Remove File
                </button>
              </div>
              <div class="btn-group" role="group">
                <button
                  type="submit"
                  class="btn btn-primary btn-sm">
                  Submit
                </button>
                <button
                  type="button"
                  class="btn btn-danger btn-sm"
                  @click="handleAddReset">
                  Reset
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    <div v-if="activeAddSongModal" class="modal-backdrop fade show"></div>

    <!-- Edit song modal -->
    <div
      ref="editSongModal"
      class="modal fade"
      :class="{ show: activeEditSongModal, 'd-block': activeEditSongModal }"
      tabindex="-1"
      role="dialog">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Update</h5>
            <button
              type="button"
              class="close"
              data-dismiss="modal"
              aria-label="Close"
              @click="toggleEditSongModal">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <alert :message="editSongMessage" v-if="showEditSongMessage"></alert>
            <form @submit.prevent="handleEditSubmit" enctype="multipart/form-data">
              <div class="mb-3">
                <label for="editSongTitle" class="form-label">Title:</label>
                <input
                  type="text"
                  class="form-control"
                  id="editSongTitle"
                  v-model="editSongForm.title"
                  placeholder="Enter title">
              </div>
              <div class="mb-3">
                <label for="editSongAuthor" class="form-label">Author:</label>
                <input
                  type="text"
                  class="form-control"
                  id="editSongAuthor"
                  v-model="editSongForm.author"
                  placeholder="Enter author">
              </div>
              <div class="mb-3">
                <label for="editSongYtUrl" class="form-label">(Optional) YouTube URL:</label>
                <input
                  type="text"
                  class="form-control"
                  id="editSongYtUrl"
                  v-model="editSongForm.yt_url"
                  placeholder="Enter YouTube URL">
              </div>

              <div class="mb-3">
                <input
                  ref="editFileInput"
                  type="file"
                  style="display: none;"
                  id="editSongFile"
                  @change="handleEditFileUpload"
                >
                <!-- Gomb a file input triggereléséhez -->
                <button
                  type="button"
                  class="btn btn-secondary btn-sm mt-2"
                  @click="openEditFileInput"
                >
                  Change file
                </button>
                <!-- Fájlnév kijelzése, ha van kiválasztott fájl -->
                <span
                  v-if="selectedEditFile && selectedEditFile.name !== editSongForm.filename"
                >
                  {{ selectedEditFile.name }}
                </span>
                <!-- File deletion button -->
                <button
                  type="button"
                  class="btn btn-danger btn-sm mt-2"
                  @click="handleEditFileRemove"
                  v-if="editSongForm.filename">
                  Remove File
                </button>
                <button
                  type="button"
                  class="btn btn-info btn-sm mt-2"
                  @click="handleAnalyzeSong"
                  v-if="editSongForm.filename"
                  :disabled="isAnalyzing"
                >
                  <span v-if="!isAnalyzing">Analyze Song</span>
                  <span v-else>
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    <span class="sr-only">Analyzing...</span>
                  </span>
                </button>
              </div>
              <!-- Edit song modal, audio player részlet -->
              <!-- YouTube beágyazás, ha yt_url van -->
              <div v-if="editSongForm.yt_url && chordsByTime">
                <iframe
                  width="100%"
                  height="315"
                  :src="getYoutubeEmbedUrl(editSongForm.yt_url)"
                  title="YouTube video player"
                  style="border:0;"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowfullscreen>
                </iframe>
              </div>

              <!-- Audio player, ha nincs yt_url -->
              <audio
                ref="editAudio"
                v-else-if="editSongForm.audioUrl && chordsByTime"
                :src="editSongForm.audioUrl"
                controls
                @play="onAudioPlay"
                @pause="onAudioPause"
                @ended="onAudioEnded"
                @timeupdate="onAudioTimeUpdate"
              >Your browser does not support the audio element.</audio>

              <ChordTimeline
                v-if="editSongForm.audioUrl && chordsByTime"
                :chords-by-time="chordsByTime"
                :duration="editAudioDuration"
                :current-time="editAudioCurrentTime"
                :window-size="timelineWindowSize"
                @seek="onTimelineSeek"
              />
              <transition name="fade">
                <div v-if="currentChord && chordsByTime" class="chord-display">
                  {{ currentChord }}
                </div>
              </transition>
              <div v-if="currentChord && chordsByTime && songBpm" class="bpm-display">
                {{ normalizedSongBpm }} BPM
              </div>
              <div v-if="chordsByTime" class="mt-3">
                <strong>Detected chords:</strong>
                <textarea
                  class="form-control"
                  rows="10"
                  style="resize:vertical; min-height:150px; max-height:400px; font-family:monospace;"
                  readonly
                  :value="chordsText"
                ></textarea>
              </div>

              <div class="btn-group" role="group">
                <button
                  type="submit"
                  class="btn btn-primary btn-sm">
                  Submit
                </button>
                <button
                  type="button"
                  class="btn btn-danger btn-sm"
                  @click="handleEditCancel">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    <div v-if="activeEditSongModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script>
import axios from 'axios';
import Alert from './Alert.vue';
import ChordTimeline from './ChordTimeline.vue';
export default {
  data() {
    return {
      songBpm: null,
      currentChord: '',
      chordIntervalId: null,
      editSongMessage: '',
      showEditSongMessage: false,
      activeAddSongModal: false,
      activeEditSongModal: false,
      addSongForm: {
        title: '',
        author: '',
        audioUrl: null,
        yt_url: ''
      },
      songs: [],
      editSongForm: {
        id: '',
        title: '',
        author: '',
        filename: null,
        audioUrl: null,
        yt_url: ''
      },
      message: '',
      showMessage: false,
      selectedFile: null,
      selectedEditFile: null,
      chordsByTime: null,
      isAnalyzing: false,
      editAudioCurrentTime: 0,
      editAudioDuration: 0,
    };
  },
  computed: {
    chordsText() {
    if (!this.chordsByTime) return '';
    return Object.entries(this.chordsByTime)
      .map(([time, chord]) => `${time}: ${chord}`)
      .join('\n');
    },
    timelineWindowSize() {
      if (!this.songBpm) return 240 / 106;
      return 240 / this.songBpm;
    },
    normalizedSongBpm() {
      let bpm = Number(this.songBpm);
      if (!bpm) return '';
      // Addig osztjuk vagy szorozzuk 2-vel, amíg a tartományba nem esik
      while (bpm < 50) bpm *= 2;
      while (bpm > 200) bpm /= 2;
      return bpm.toFixed(2);
    }
  },
  components: {
    alert: Alert,
    ChordTimeline
  },
  methods: {
    getYoutubeEmbedUrl(ytUrl) {
      // Kinyeri a videó azonosítót és beágyazhatóvá alakítja
      const match = ytUrl.match(
        /(?:youtube\.com\/(?:watch\?v=|embed\/|v\/)|youtu\.be\/)([A-Za-z0-9_-]{11})/
      );
      const videoId = match ? match[1] : null;
      return videoId
        ? `https://www.youtube.com/embed/${videoId}`
        : '';
    },
    getChordAtTime(currentTime) {
      if (!this.chordsByTime) return '';
      // Az időpontokat növekvő sorrendbe rendezzük
      const times = Object.keys(this.chordsByTime)
        .map(Number)
        .sort((a, b) => a - b);

      // Ha nincs akkord, vagy üres a lista
      if (times.length === 0) return '';

      // Ha az első akkord NEM 0-nál kezdődik
      if (times[0] > 0) {
        if (currentTime < times[0]) {
          return '<READY>';
        }
      }

      // Alapértelmezett működés: az utolsó, még el nem múlt akkordot keressük
      let lastChord = '';
      for (const t of times) {
        if (currentTime >= t) {
          lastChord = this.chordsByTime[t];
        } else {
          break;
        }
      }
      return lastChord;
    },
    onAudioPlay() {
      const audio = this.$refs.editAudio;
      if (!audio) return;
      this.editAudioDuration = audio.duration || 0;
      this.chordIntervalId = setInterval(() => {
        this.editAudioCurrentTime = audio.currentTime;
        const chord = this.getChordAtTime(audio.currentTime);
        if (chord !== this.currentChord) {
          this.currentChord = chord;
        }
      }, 100);
    },
    onAudioPause() {
      clearInterval(this.chordIntervalId);
      this.chordIntervalId = null;
    },
    onAudioEnded() {
      this.onAudioPause();
      this.currentChord = '';
      this.editAudioCurrentTime = 0;
    },
    onAudioTimeUpdate(e) {
      this.editAudioCurrentTime = e.target.currentTime;
    },
    onTimelineSeek(time) {
      const audio = this.$refs.editAudio;
      if (audio) {
        audio.currentTime = time;
        this.editAudioCurrentTime = time;
      }
    },
    formatIsoDate(isoDate) {
        if (!isoDate) return 'N/A';
        const date = new Date(isoDate);
        const options = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            hour12: false,
        };

        return date.toLocaleString('hu-HU', options).replace(',', '');
    },
    getSongs() {
      const path = 'http://localhost:5001/songs';
      axios.get(path)
        .then((res) => {
          this.songs = res.data.songs;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    handleAddReset() {
      this.initForm();
      this.selectedFile = null;
      this.addSongForm.audioUrl = null;
      this.chordsByTime= null;
    },
    handleAddSubmit() {
      this.toggleAddSongModal();

      let formData = new FormData();
      formData.append('title', this.addSongForm.title);
      formData.append('author', this.addSongForm.author);
      formData.append('yt_url', this.addSongForm.yt_url);

      if (this.selectedFile) {
        formData.append('file', this.selectedFile);
      }

      const path = 'http://localhost:5001/songs';
      axios.post(path, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
        .then(() => {
          this.getSongs();
          this.message = 'Song added!';
          this.showMessage = true;
        })
        .catch((error) => {
          console.log(error);
          this.getSongs();
        });

      this.initForm();
      this.selectedFile = null;
      this.addSongForm.audioUrl = null;
      this.chordsByTime = null;
    },
    handleDeleteSong(song) {
      this.removeSong(song.id);
    },
    handleEditCancel() {
      this.toggleEditSongModal(null);
      this.initForm();
      this.getSongs();
    },
    handleEditSubmit() {
      this.toggleEditSongModal(null);

      let formData = new FormData();
      formData.append('title', this.editSongForm.title);
      formData.append('author', this.editSongForm.author);
      formData.append('yt_url', this.editSongForm.yt_url);


      if (this.selectedEditFile) {
        formData.append('file', this.selectedEditFile);
      }

      const path = `http://localhost:5001/songs/${this.editSongForm.id}`;
      axios.put(path, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
        .then(() => {
          this.getSongs();
          this.message = 'Song updated!';
          this.showMessage = true;
        })
        .catch((error) => {
          console.log(error);
          this.getSongs();
        });

      this.initForm();
      this.selectedEditFile = null;
      this.chordsByTime = null;
    },
    handleFileUpload(event) {
      this.selectedFile = event.target.files[0];
      this.addSongForm.audioUrl = URL.createObjectURL(this.selectedFile);
    },
    handleFileRemove() {
      this.selectedFile = null;
      this.addSongForm.audioUrl = null;
    },
    openEditFileInput() {
      this.$refs.editFileInput.click();
    },
    handleEditFileUpload(event) {
      this.selectedEditFile = event.target.files[0];
      this.editSongForm.audioUrl = URL.createObjectURL(this.selectedEditFile);
    },
    async handleEditFileRemove() {
      const songId = this.editSongForm.id;
      const filename = this.editSongForm.filename;

      try {
        const response = await axios.delete(`http://localhost:5001/songs/${songId}/file`, {
          data: { filename: filename }
        });

        if (response.status === 200) {
          this.editSongForm.audioUrl = null;
          this.editSongForm.filename = null;
          this.selectedEditFile = null;
          this.chordsByTime = null;
          this.editSongMessage = 'File removed!';
          this.showEditSongMessage = true;
          this.getSongs();
        } else {
          console.error('Error removing file:', response.data);
          this.editSongMessage  = 'Error removing file!';
          this.showEditSongMessage = true;
        }
      } catch (error) {
        console.error('Error removing file:', error);
        this.message = 'Error removing file!';
        this.showMessage = true;
      }
    },
    initForm() {
      this.addSongForm.title = '';
      this.addSongForm.author = '';
      this.addSongForm.yt_url = '';
      this.editSongForm.yt_url = '';
      this.addSongForm.audioUrl = null;
      this.editSongForm.id = '';
      this.editSongForm.title = '';
      this.editSongForm.author = '';
      this.editSongForm.filename = null;
      this.editSongForm.audioUrl = null;
      this.chordsByTime = null;
      this.currentChord = '';
      this.chordIntervalId = null;
      this.isAnalyzing = false;
    },
    removeSong(songID) {
      const path = `http://localhost:5001/songs/${songID}`;
      axios.delete(path)
        .then(() => {
          this.getSongs();
          this.message = 'Song removed!';
          this.showMessage = true;

        })
        .catch((error) => {
          console.error(error);
          this.getSongs();
        });
    },
    toggleAddSongModal() {
      const body = document.querySelector('body');
      this.activeAddSongModal = !this.activeAddSongModal;
      if (this.activeAddSongModal) {
        body.classList.add('modal-open');
      } else {
        body.classList.remove('modal-open');
      }
    },
    toggleEditSongModal(song) {
        if (song) {
          this.editSongForm = { ...song };
          if (song.filename) {
            this.editSongForm.audioUrl = `http://localhost:5001/uploads/${song.filename}`;
          } else {
            this.editSongForm.audioUrl = null;
          }
        }
        const body = document.querySelector('body');
        this.activeEditSongModal = !this.activeEditSongModal;
        if (!this.activeEditSongModal) {
          this.chordsByTime = null;
          this.editSongMessage = '';
          this.showEditSongMessage = false;
        }
        if (this.activeEditSongModal) {
          body.classList.add('modal-open');
        } else {
          body.classList.remove('modal-open');
        }
    },
    async handleAnalyzeSong() {
      const songId = this.editSongForm.id;
      const filename = this.editSongForm.filename;
      if (
        this.selectedEditFile &&
        this.selectedEditFile.name !== this.editSongForm.filename
      ) {
        window.alert('Before analyzing, you must submit!');
        return;
      }
      this.isAnalyzing = true;
      try {
        const response = await axios.get(`http://localhost:5001/songs/${songId}/analyze-song`, {
          params: { filename: filename }
        });
        this.chordsByTime = response.data.chords_by_time;
        this.songBpm = response.data.bpm;
        this.editSongMessage = 'Song analyzed!';
        this.showEditSongMessage = true;
        this.currentChord = '<READY>';
      } catch (error) {
        console.error('Error analyzing song:', error);
        this.editSongMessage = 'Error analyzing song!';
        this.showEditSongMessage = true;
      } finally {
        this.isAnalyzing = false;
      }
    },
  },
  created() {
    this.getSongs();
  },
  beforeUnmount() {
    clearInterval(this.chordIntervalId);
  },
};
</script>
