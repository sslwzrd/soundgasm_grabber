import customtkinter as ctk
import requests
from bs4 import BeautifulSoup
import re, os, threading, time, subprocess

class SoundgasmGrabber(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Soundgasm Downloader")
        self.geometry("450x300")
        ctk.set_appearance_mode("dark")

        # UI Layout
        self.label = ctk.CTkLabel(self, text="Soundgasm Username:", font=("Arial", 14, "bold"))
        self.label.pack(pady=(20, 5))
        
        self.entry = ctk.CTkEntry(self, placeholder_text="Enter username here...", width=300)
        self.entry.pack(pady=10)
        
        self.btn = ctk.CTkButton(self, text="Download Audios", command=self.start_thread, fg_color="#ff5a5f", hover_color="#e04e52")
        self.btn.pack(pady=10)

        self.progress = ctk.CTkProgressBar(self, width=350)
        self.progress.pack(pady=10)
        self.progress.set(0)
        
        self.status = ctk.CTkLabel(self, text="Ready to go!", text_color="gray")
        self.status.pack()

        self.folder_btn = ctk.CTkButton(self, text="Open Downloads Folder", command=self.open_folder, state="disabled", fg_color="transparent", border_width=1)
        self.folder_btn.pack(pady=10)

    def open_folder(self):
        folder = f"soundgasm_{self.entry.get().strip()}"
        if os.path.exists(folder):
            subprocess.Popen(['open', folder] if os.name != 'nt' else ['explorer', folder])

    def start_thread(self):
        threading.Thread(target=self.run_download, daemon=True).start()

    def run_download(self):
        user = self.entry.get().strip()
        if not user: return
        
        self.btn.configure(state="disabled")
        folder = f"soundgasm_{user}"
        if not os.path.exists(folder): os.makedirs(folder)

        try:
            self.status.configure(text="Searching for posts...")
            res = requests.get(f"https://soundgasm.net/u/{user}")
            soup = BeautifulSoup(res.text, 'html.parser')
            links = list(set([a['href'] for a in soup.find_all('a', href=True) if f"/u/{user}/" in a['href']]))
            
            if not links:
                self.status.configure(text="No posts found. Check username!")
                self.btn.configure(state="normal")
                return

            for i, post in enumerate(links):
                self.status.configure(text=f"Downloading {i+1} of {len(links)}...")
                self.progress.set((i + 1) / len(links))
                
                page = requests.get(post).text
                match = re.search(r'https://media\.soundgasm\.net/sounds/[a-z0-9]+\.m4a', page)
                if match:
                    audio_url = match.group(0)
                    filename = post.split('/')[-1] + ".m4a"
                    with open(os.path.join(folder, filename), 'wb') as f:
                        f.write(requests.get(audio_url).content)
                time.sleep(0.3)

            self.status.configure(text="Finished! All files saved.")
            self.folder_btn.configure(state="normal")
        except:
            self.status.configure(text="Connection error. Try again.")
        
        self.btn.configure(state="normal")

if __name__ == "__main__":
    app = SoundgasmGrabber()
    app.mainloop()