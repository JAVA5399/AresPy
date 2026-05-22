import threading
from tkinter import *
from tkinter import messagebox, filedialog, scrolledtext
import pyperclip as clipboard
from pytubefix import YouTube, Playlist 
from moviepy.editor import AudioFileClip
import os

class DownloadMusic(Frame):
    def __init__(self, master, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)
        self.grid()
        self.formato_seleccionado = StringVar(value=".m4a")
        self.crear_widgets()
          
    def pegar_portapapeles(self):
        url = clipboard.paste()
        if not url: return 
        
        if "list=" in url or "youtube.com/watch?v=" in url or "youtu.be/" in url:
            self.display_urls.config(state='normal')
            self.display_urls.insert(END, url + "\n\n")
            self.display_urls.config(state='disabled')
        else:
            messagebox.showerror("Error", "La URL no es un enlace de YouTube válido.")
        
    def limpiar_display_urls(self):
        self.display_urls.config(state="normal")
        self.display_urls.delete(1.0,END)
        self.display_urls.config(state="disabled")
    
    def init_descarga_hilo(self):
        self.ruta_destino = filedialog.askdirectory()
        if self.ruta_destino:
            t = threading.Thread(target=self.init_descarga)
            t.daemon = True #investigar que es
            t.start()
        else:
            messagebox.showwarning("Aviso", "No se ha seleccionado ninguna carpeta")
              
    def init_descarga(self):
        try:
            content = self.display_urls.get(1.0, END).strip()
            if not content:
                messagebox.showwarning("Aviso", "No hay enlaces para descargar")
                return

            self.rbtn_m4a.config(state="disabled")
            self.btn_limpiar.config(state="disabled")
            self.rbtn_mp3.config(state="disabled")
            self.btn_pegar.config(state="disabled")
            self.btn_descargar.config(state="disabled")
            urls = content.split('\n')
            
            for url in urls:
                url = url.strip()
                if not url: continue
                
                if "list=" in url:
                    playlist = Playlist(url)
                    for video in playlist.videos:
                        self.descargar_audio(video)
                else:
                    video = YouTube(url)
                    self.descargar_audio(video)
            
            messagebox.showinfo("Información", "La descarga ha finalizado")
            self.lb_cancion_actual.config(text="---------------")
            self.display_urls.config(state='normal')
            self.display_urls.delete(1.0, END)
            self.display_urls.config(state='disabled')         
            
        except Exception as e:
            messagebox.showerror("Error", f"Problema: {str(e)}")
        
        self.btn_limpiar.config(state="normal")
        self.rbtn_m4a.config(state="normal")
        self.rbtn_mp3.config(state="normal")
        self.btn_pegar.config(state="normal")
        self.btn_descargar.config(state="normal")


    def descargar_audio(self, video_obj):
        try:
            title = video_obj.title
            self.lb_cancion_actual.config(text=f"{title}")
            audio = video_obj.streams.get_audio_only()
            audio_m4a=audio.download(output_path=self.ruta_destino)
            if self.formato_seleccionado.get() == ".mp3":
                audio_mp3 = os.path.splitext(audio_m4a)[0] + ".mp3"
                audio_clip = AudioFileClip(audio_m4a)
                audio_clip.write_audiofile(audio_mp3, verbose=False, logger=None)
                audio_clip.close()
                os.remove(audio_m4a)
            
            self.display_descargas.config(state='normal')
            self.display_descargas.insert(1.0, f"{title}\n")
            self.display_descargas.config(state='disabled')

        except Exception as e:
            self.display_descargas.insert(1.0, f"Error al intentar dercargar: {video_obj.title}\n")
            
    def crear_widgets(self):
        self.btn_pegar = Button(self, text="Pegar Enlaces\n (Videos o Playlists)", font=("Roboto", 10, "bold"), bg="#2793ff", fg="#ffffff", cursor="hand2", command=self.pegar_portapapeles)
        self.btn_pegar.grid(row=0, column=0, padx=(10,2), pady=(10,2), sticky="nsew")
        
        self.btn_limpiar = Button(self, text="Eliminar enlaces", font=("Roboto", 10, "bold"), bg="#e50e0e", fg="#ffffff", cursor="hand2", command=self.limpiar_display_urls)
        self.btn_limpiar.grid(row=0, column=1, padx=(0,10), pady=(10,2), sticky="nsew")
        
        self.display_urls = scrolledtext.ScrolledText(self, font=("Roboto", 10), bg="#ffffff", fg="#666666", height=8, width=50, relief="solid", state='disabled')
        self.display_urls.vbar.config(cursor="hand2")
        self.display_urls.grid(row=1, column=0, columnspan=2, padx=10, sticky="nesw")

        Label(self, text="Descargando:", font=("Roboto", 10, "bold"), bg="#666666", fg="#ffffff").grid(row=2, column=0, columnspan=2, padx=10,pady=(10,2), sticky="nsew")
        
        self.lb_cancion_actual = Label(self, text="---------------", bg="#ffffff", fg="#666666", relief="solid", borderwidth=1, wraplength=350)
        self.lb_cancion_actual.grid(row=3, column=0, columnspan=2, padx=10,  sticky="nsew")

        Label(self, text="Descargadas:", font=("Roboto", 10, "bold"), bg="#666666", fg="#ffffff").grid(row=4, column=0, columnspan=2, padx=10, pady=(10,2), sticky="nsew")
        
        self.display_descargas = scrolledtext.ScrolledText(self, font=("Roboto", 10), bg="#ffffff", fg="#666666", height=8, width=50, relief="solid", state='disabled')
        self.display_descargas.vbar.config(cursor="hand2")
        self.display_descargas.grid(row=5, column=0, columnspan=2, padx=10, sticky="nesw")
        
        Label(self, text="Formato:", font=("Roboto", 10, "bold"), bg="#666666", fg="#ffffff").grid(row=6, column=0, columnspan=2, padx=10,  pady=(10,2), sticky="nsew")
        
        self.rbtn_m4a = Radiobutton(self, text=".m4a", font=("Roboto", 10, "bold"), bg="#2793ff", fg="#ffffff", selectcolor="#2793ff",  activebackground="#0463c3", activeforeground="#e2e2e2",
                                     cursor="hand2", value=".m4a", variable=self.formato_seleccionado)
        self.rbtn_m4a.grid(row=7, column=0, padx=(10,2), sticky="nsew")

        self.rbtn_mp3 = Radiobutton(self, text=".mp3", font=("Roboto", 10, "bold"), bg="#2793ff", fg="#ffffff", selectcolor="#2793ff",  activebackground="#0463c3", activeforeground="#e2e2e2",
                                    cursor="hand2", value=".mp3", variable=self.formato_seleccionado)
        self.rbtn_mp3.grid(row=7, column=1, padx=(0,10), sticky="nsew")
        
        self.btn_descargar = Button(self, text="DESCARGAR", font=("Roboto", 12, "bold"), bg="#00bb06", fg="#ffffff", 
                                    cursor="hand2", command=self.init_descarga_hilo)
        self.btn_descargar.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

arespy = Tk()
arespy.title("ARESPY")
arespy.resizable(False, False)
app = DownloadMusic(arespy)
arespy.mainloop()