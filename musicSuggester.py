import tkinter as tk
from tkinter import ttk, messagebox
from ytmusicapi import YTMusic
import webbrowser

class MusicSuggester:
    def __init__(self, master):
        self.master = master
        self.master.title("🎵 Music Suggester 🎵")
        self.master.geometry("600x500")
        self.master.resizable(False, False)

        # Apply custom theme
        self.style = ttk.Style()
        self.style.configure(
            "TLabel", font=("Helvetica", 12), padding=5, foreground="#4A4A4A"
        )
        self.style.configure(
            "TButton", font=("Helvetica", 11, "bold"), background="#4CAF50", padding=5
        )
        self.style.map(
            "TButton",
            background=[("active", "#45A049")],
        )
        self.style.configure("TEntry", font=("Helvetica", 12), padding=5)
        self.style.configure("TFrame", background="#F7F7F7")

        self.ytmusic = YTMusic()
        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.master, padding=10, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame, text="Find Songs by Your Favorite Artist or Genre", anchor="center", font=("Helvetica", 16, "bold")
        )
        title_label.pack(pady=10)

        # Artist input
        input_frame = ttk.Frame(main_frame, style="TFrame")
        input_frame.pack(fill=tk.X, pady=10)
        ttk.Label(input_frame, text="Enter artist name or genre:", style="TLabel").pack(
            side=tk.LEFT, padx=5
        )
        self.artist_entry = ttk.Entry(input_frame, width=40)
        self.artist_entry.pack(side=tk.LEFT, padx=5)

        # Buttons
        button_frame = ttk.Frame(main_frame, style="TFrame")
        button_frame.pack(pady=10)
        suggest_button = ttk.Button(button_frame, text="Suggest Songs", command=self.suggest_songs)
        suggest_button.pack(side=tk.LEFT, padx=5)
        clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_results)
        clear_button.pack(side=tk.LEFT, padx=5)

        # Results
        self.results_label = ttk.Label(main_frame, text="Results:", style="TLabel")
        self.results_label.pack(pady=5)

        self.results_list = tk.Listbox(
            main_frame, width=70, height=15, font=("Courier", 10), bg="#F1F1F1"
        )
        self.results_list.pack(pady=10)
        self.results_list.bind("<Double-1>", self.open_song_url)

        # Status label
        self.status_label = ttk.Label(
            main_frame, text="", font=("Helvetica", 11, "italic"), foreground="#3C763D"
        )
        self.status_label.pack(pady=5)

    def suggest_songs(self):
        artist = self.artist_entry.get().strip()
        if not artist:
            messagebox.showwarning("Input Error", "Please enter an artist name or genre.")
            return

        # Clear previous results
        self.clear_results()
        self.status_label.config(text="Searching...")
        self.results_list.insert(tk.END, "Searching... Please wait.")

        try:
            search_results = self.ytmusic.search(artist, filter="artists")
            self.results_list.delete(0, tk.END)  # Clear "Searching..." message

            if not search_results:
                self.results_list.insert(tk.END, "No artist found.")
                self.status_label.config(text="No results found.")
                return

            # Get the first artist result
            artist_id = search_results[0]['browseId']
            artist_name = search_results[0].get('artist', 'Unknown Artist')
            artist_info = self.ytmusic.get_artist(artist_id)

            # Fetch all songs
            all_songs = []
            if 'songs' in artist_info:
                songs_data = artist_info['songs']
                all_songs.extend(songs_data.get('results', []))

                # Handle additional songs if there are more
                while 'continuations' in songs_data:
                    songs_data = self.ytmusic.get_continuations(
                        songs_data['continuations'], 'artist'
                    )
                    all_songs.extend(songs_data.get('results', []))

            if not all_songs:
                self.results_list.insert(tk.END, f"No songs found for {artist_name}.")
                self.status_label.config(text="No songs available.")
                return

            # Display all songs
            for i, song in enumerate(all_songs, 1):
                self.results_list.insert(tk.END, f"{i}. {song['title']} ({song['videoId']})")
                self.results_list.insert(tk.END, "-" * 60)

            self.status_label.config(text=f"Found {len(all_songs)} songs for {artist_name}.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_label.config(text="Error occurred.")

    def clear_results(self):
        self.artist_entry.delete(0, tk.END)
        self.results_list.delete(0, tk.END)
        self.status_label.config(text="")

    def open_song_url(self, event):
        try:
            selection = self.results_list.get(self.results_list.curselection())
            if selection and "(" in selection:
                video_id = selection.split("(")[-1].rstrip(")")
                webbrowser.open(f"https://www.youtube.com/watch?v={video_id}")
            else:
                messagebox.showinfo("Invalid Selection", "Please select a valid song to open.")
        except Exception:
            messagebox.showwarning("Selection Error", "Unable to open the selected item.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicSuggester(root)
    root.mainloop()
