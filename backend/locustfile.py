from locust import HttpUser, task, between

class AnalyzeSongUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def analyze_song(self):
        song_id = "1"
        filename = "let_it_be_256.mp3"
        self.client.get(
            f"/api/songs/{song_id}/analyze-song",
            params={
                "isYoutube": "false",
                "filename": filename
            }
        )

