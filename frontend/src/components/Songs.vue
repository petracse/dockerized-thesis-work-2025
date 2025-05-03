<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Songs</h1>
        <router-link to="/music-processing">Go to Music Processing</router-link>
        <hr><br><br>
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
                    Update
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
                <label for="addSongFile" class="form-label">File:</label>
                <input
                  type="file"
                  class="form-control"
                  id="addSongFile"
                  @change="handleFileUpload">
                <!-- Audio file player -->
                <audio controls v-if="addSongForm.audioUrl">
                  <source :src="addSongForm.audioUrl" type="audio/mpeg">
                  Your browser does not support the audio element.
                </audio>
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
                <label for="editSongFile" class="form-label">File:</label>
                <input
                  type="file"
                  class="form-control"
                  id="editSongFile"
                  @change="handleEditFileUpload">
                <!-- Audio file player -->
                <audio controls v-if="editSongForm.audioUrl">
                  <source :src="editSongForm.audioUrl" type="audio/mpeg">
                  Your browser does not support the audio element.
                </audio>
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
                  v-if="editSongForm.filename">
                  Analyze Song
                </button>
              </div>
              <div v-if="chordsByTime && Object.keys(chordsByTime).length">
                <h5>Detected Chords:</h5>
                <ul>
                  <li v-for="(chord, time) in chordsByTime" :key="time">
                    {{ time }} s: {{ chord }}
                  </li>
                </ul>
              </div>
              <canvas
                v-if="editSongForm.audioUrl && chordsByTime"
                ref="waveformCanvas"
                width="600"
                height="100"
                style="width: 100%; height: 100px; border: 1px solid #ccc; margin-bottom: 16px;"
              ></canvas>


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
import { nextTick } from 'vue';
export default {
  data() {
    return {
      chordNames: [
        'A:min', 'A:maj', 'A#:min', 'A#:maj', 'B:min', 'B:maj', 'C:min', 'C:maj', 'C#:min', 'C#:maj',
        'D:min', 'D:maj', 'D#:min', 'D#:maj', 'E:min', 'E:maj', 'F:min', 'F:maj', 'F#:min', 'F#:maj',
        'G:min', 'G:maj', 'G#:min', 'G#:maj'
      ],
      editSongMessage: '',
      showEditSongMessage: false,
      activeAddSongModal: false,
      activeEditSongModal: false,
      addSongForm: {
        title: '',
        author: '',
        audioUrl: null,
      },
      songs: [],
      editSongForm: {
        id: '',
        title: '',
        author: '',
        filename: null,
        audioUrl: null,
      },
      message: '',
      showMessage: false,
      selectedFile: null,
      selectedEditFile: null,
      chordsByTime: null,
    };
  },
  components: {
    alert: Alert,
  },
  methods: {
    async drawWaveformWithChords() {
      const audioUrl = this.editSongForm.audioUrl;
      const chordsByTime = this.chordsByTime;
      if (!audioUrl || !chordsByTime) return;

      const canvas = this.$refs.waveformCanvas;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Betöltjük az audio buffert
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const response = await fetch(audioUrl);
      const arrayBuffer = await response.arrayBuffer();
      const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);

      const duration = audioBuffer.duration;
      const width = canvas.width;
      const height = canvas.height;

      // Akkord-szín hozzárendelés (fix, vagy generált)
      const chordColors = this.getChordColors();

      // chordsByTime -> [{time, chord}]
      const chordSegments = Object.keys(chordsByTime)
        .map(t => ({ time: Number(t), chord: chordsByTime[t] }))
        .sort((a, b) => a.time - b.time);

      // Hullámforma szakaszok és akkordnevek rajzolása
      for (let i = 0; i < chordSegments.length; i++) {
        const startTime = chordSegments[i].time;
        const endTime = (i < chordSegments.length - 1)
          ? chordSegments[i + 1].time
          : duration;
        const chord = chordSegments[i].chord;
        const color = chordColors[chord] || '#888';

        // Hullámforma szakasz
        this.drawWaveformSegment(ctx, audioBuffer, startTime, endTime, width, height, color, duration);

        // Akkordnév kiírása a szakasz elejére
        const startX = (startTime / duration) * width;
        ctx.fillStyle = color;
        ctx.font = 'bold 14px Arial';
        ctx.textBaseline = 'top';
        ctx.fillText(chord, startX + 2, 2); // +2 px eltolás, hogy ne lógjon le a széléről
      }
    },

    drawWaveformSegment(ctx, audioBuffer, startTime, endTime, width, height, color, duration) {
      ctx.strokeStyle = color;
      ctx.beginPath();
      const channelData = audioBuffer.getChannelData(0);

      const startX = (startTime / duration) * width;
      const endX = (endTime / duration) * width;

      // Skálázás: egy pixelre hány minta jut[3]
      const samplesPerPixel = channelData.length / width;

      for (let x = Math.floor(startX); x < Math.floor(endX); x++) {
        const sampleIndex = Math.floor(x * samplesPerPixel);
        const v = channelData[sampleIndex] || 0;
        const y = (1 - v) * height / 2;
        if (x === Math.floor(startX)) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      ctx.stroke();
    },

    getChordColors() {
      // Minden akkordhoz egyedi szín (pl. HSL színkör alapján)
      const colors = {};
      const baseColors = [
        '#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4',
        '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff'
      ];
      this.chordNames.forEach((chord, i) => {
        colors[chord] = baseColors[i % baseColors.length];
      });
      return colors;
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
    addSong(payload) {
      const path = 'http://localhost:5001/songs';
      axios.post(path, payload)
        .then(() => {
          this.getSongs();
          this.message = 'Song added!';
          this.showMessage = true;
        })
        .catch((error) => {
          console.log(error);
          this.getSongs();
        });
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
          this.message = 'File removed!';
          this.showMessage = true;
          this.getSongs();
        } else {
          console.error('Error removing file:', response.data);
          this.message = 'Error removing file!';
          this.showMessage = true;
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
      this.addSongForm.audioUrl = null;
      this.editSongForm.id = '';
      this.editSongForm.title = '';
      this.editSongForm.author = '';
      this.editSongForm.filename = null;
      this.editSongForm.audioUrl = null;
      this.chordsByTime = null;
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
    updateSong(payload, songID) {
      const path = `http://localhost:5001/songs/${songID}`;
      axios.put(path, payload)
        .then(() => {
          this.getSongs();
          this.message = 'Song updated!';
          this.showMessage = true;
        })
        .catch((error) => {
          console.error(error);
          this.getSongs();
        });
    },
    async handleAnalyzeSong() {
      const songId = this.editSongForm.id;
      const filename = this.editSongForm.filename;

      try {
        const response = await axios.get(`http://localhost:5001/songs/${songId}/analyze-song`, {
          params: { filename: filename }
        });
        this.chordsByTime = response.data.chords_by_time;
        this.editSongMessage = 'Song analyzed!';
        this.showEditSongMessage = true;

        // Várd meg, hogy a DOM és a reaktív változók frissüljenek
        await this.$nextTick();
        this.drawWaveformWithChords();
      } catch (error) {
        console.error('Error analyzing song:', error);
        this.editSongMessage = 'Error analyzing song!';
        this.showEditSongMessage = true;
      }
    },
  },
  watch: {
    'editSongForm.audioUrl'(val) {
      if (val && this.chordsByTime) this.drawWaveformWithChords();
    },
    chordsByTime(val) {
      if (val && this.editSongForm.audioUrl) this.drawWaveformWithChords();
    }
  },
  created() {
    this.getSongs();
  },
};
</script>
