import customtkinter as ctk
import tkinter as tk 
import pyperclip 
from tkinter import messagebox 

import core_password_manager as core
from typing import Optional, Tuple

# Configuration de l'apparence (à faire une seule fois)
ctk.set_appearance_mode("System") 
ctk.set_default_color_theme("blue")


class LoginWindow(ctk.CTk):
    """Fenêtre de connexion pour entrer le mot de passe maître."""
    def __init__(self):
        super().__init__()

        self.title("Déverrouiller Big Key")
        self.geometry("380x220")
        self.resizable(False, False)
        self.passwords_data = None
        self.master_password = None

        self._center_window()

        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text="Entrez votre mot de passe maître :")
        self.label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        self.password_entry = ctk.CTkEntry(self, show="*", width=300)
        self.password_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.password_entry.bind("<Return>", self._attempt_login)
        self.password_entry.focus() # Mettre le focus sur le champ

        self.login_button = ctk.CTkButton(self, text="Déverrouiller", command=self._attempt_login)
        self.login_button.grid(row=2, column=0, padx=20, pady=10)

        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.grid(row=3, column=0, padx=20, pady=(0, 10))

        # Initialiser le stockage (crée le fichier de sel si besoin)
        try:
            core.initialiser_stockage()
        except Exception as e:
            self.status_label.configure(text=f"Erreur init stockage: {e}")
            self.login_button.configure(state="disabled") # Désactiver si erreur critique

    def _center_window(self):
        """Centre la fenêtre sur l'écran."""
        self.update_idletasks() # Assurer que les dimensions sont calculées
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _attempt_login(self, event=None):
        self.master_password = self.password_entry.get()
        if not self.master_password:
            self.status_label.configure(text="Veuillez entrer un mot de passe.", text_color="orange")
            return

        try:
            self.status_label.configure(text="Déverrouillage...", text_color="gray")
            self.update_idletasks() # Mettre à jour l'UI
            self.passwords_data = core.charger_ou_creer_stockage(self.master_password)
            self.status_label.configure(text="Succès !", text_color="green")
            self.after(500, self.destroy) # Fermer après un court délai

        except (ValueError, FileNotFoundError, IOError, Exception) as e:
            error_message = str(e)
            # Simplifier le message pour l'utilisateur si c'est une InvalidToken
            if "Impossible de déchiffrer" in error_message:
                 error_message = "Mot de passe incorrect ou données corrompues."
            self.status_label.configure(text=error_message, text_color="red")
            self.password_entry.delete(0, 'end') # Vider le champ


class AddEditDialog(ctk.CTkToplevel):
    """Boîte de dialogue pour ajouter ou modifier une entrée."""
    def __init__(self, parent, title="Ajouter/Modifier", site="", username="", password="", callback=None):
        super().__init__(parent)
        self.transient(parent) 
        self.title(title)
        self.geometry("450x350")
        self.resizable(False, False)
        self.callback = callback 
        self.result = None 

        self.grid_columnconfigure(1, weight=1)

        # --- Widgets ---
        ctk.CTkLabel(self, text="Site/Service:").grid(row=0, column=0, padx=(20, 5), pady=10, sticky="w")
        self.site_entry = ctk.CTkEntry(self, width=250)
        self.site_entry.grid(row=0, column=1, padx=(0, 20), pady=10, sticky="ew")
        self.site_entry.insert(0, site)

        ctk.CTkLabel(self, text="Nom d'utilisateur:").grid(row=1, column=0, padx=(20, 5), pady=10, sticky="w")
        self.username_entry = ctk.CTkEntry(self, width=250)
        self.username_entry.grid(row=1, column=1, padx=(0, 20), pady=10, sticky="ew")
        self.username_entry.insert(0, username)

        ctk.CTkLabel(self, text="Mot de passe:").grid(row=2, column=0, padx=(20, 5), pady=10, sticky="w")
        self.password_entry = ctk.CTkEntry(self, show="*", width=250)
        self.password_entry.grid(row=2, column=1, padx=(0, 20), pady=10, sticky="ew")
        self.password_entry.insert(0, password)

        self.reveal_button = ctk.CTkButton(self, text="👁", width=30, font=("Arial", 16), command=self._toggle_password)
        self.reveal_button.grid(row=2, column=2, padx=(0,10),pady=10)
        
        self.generate_button = ctk.CTkButton(self, text="Générer", command=self._generate_password)
        self.generate_button.grid(row=3, column=1, padx=(0, 20), pady=10, sticky="e")
        
        self.strength_label = ctk.CTkLabel(self, text="Force: N/A")
        self.strength_label.grid(row=4, column=1, padx=(0, 20), pady=5, sticky="w")
       

        # Boutons Sauvegarder/Annuler
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        self.save_button = ctk.CTkButton(button_frame, text="Sauvegarder", command=self._save)
        self.save_button.pack(side="left", padx=10)
        self.cancel_button = ctk.CTkButton(button_frame, text="Annuler", command=self.destroy, fg_color="gray")
        self.cancel_button.pack(side="left", padx=10)

       
        if not site:
            self.site_entry.focus()
        elif not username:
            self.username_entry.focus()
        else:
            self.password_entry.focus()
            
    
        self.grab_set()
        self.update_idletasks()
        parent_geo = parent.geometry()
        parent_x, parent_y = map(int, parent_geo.split('+')[1:])
        parent_w, parent_h = map(int, parent_geo.split('+')[0].split('x'))
        
        dialog_w = self.winfo_width()
        dialog_h = self.winfo_height()
        
        x = parent_x + (parent_w // 2) - (dialog_w // 2)
        y = parent_y + (parent_h // 2) - (dialog_h // 2)
        self.geometry(f"{dialog_w}x{dialog_h}+{x}+{y}")


    def _toggle_password(self):
        current_show = self.password_entry.cget("show")
        if current_show == "*":
            self.password_entry.configure(show="")
            self.reveal_button.configure(text="🙈")
        else:
            self.password_entry.configure(show="*")
            self.reveal_button.configure(text="👁")

    def _generate_password(self):
        new_password = core.generer_mot_de_passe() 
        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, new_password)
       

    def _save(self):
        site = self.site_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get() 

        if not site or not username:
            messagebox.showwarning("Champs manquants", "Le nom du site et le nom d'utilisateur sont requis.", parent=self)
            return
        if not password:
             if not messagebox.askyesno("Mot de passe vide", "Le champ mot de passe est vide. Voulez-vous continuer ?", parent=self):
                 return

        self.result = (site, username, password)
        if self.callback:
            self.callback(self.result) 
        self.destroy()


class MainWindow(ctk.CTk):
    """Fenêtre principale du gestionnaire de mots de passe."""
    def __init__(self, passwords_data: core.PasswordData, master_password: str):
        super().__init__()
        self.passwords = passwords_data
        self.master_password = master_password

        self.title("Big Key")
        self.geometry("900x600")

        # --- Variables d'état ---
        self.selected_site: Optional[str] = None
        self.selected_user: Optional[str] = None
        self.password_visible = False

        # --- Configuration du Layout Principal (3 colonnes) ---
        self.grid_columnconfigure(0, weight=1, minsize=200) # Liste sites
        self.grid_columnconfigure(1, weight=1, minsize=200) # Liste utilisateurs
        self.grid_columnconfigure(2, weight=3, minsize=350) # Détails
        self.grid_rowconfigure(1, weight=1) # Pour que les listes s'étendent

        
        self._create_search_bar()
        self._create_site_list_frame()
        self._create_user_list_frame()
        self._create_details_frame()
        self._create_action_buttons()

        # --- Chargement initial ---
        self._populate_site_list()

        # --- Gestion de la fermeture ---
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_search_bar(self):
        """Crée la barre de recherche en haut."""
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._filter_sites())
        search_entry = ctk.CTkEntry(self, placeholder_text="Rechercher un site...", textvariable=self.search_var)
        search_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    def _create_site_list_frame(self):
        """Crée le cadre pour la liste des sites."""
        site_list_frame = ctk.CTkFrame(self)
        site_list_frame.grid(row=1, column=0, padx=(10, 5), pady=(0, 10), sticky="nsew")
        site_list_frame.grid_rowconfigure(0, weight=1)
        site_list_frame.grid_columnconfigure(0, weight=1)

        self.site_listbox = tk.Listbox(site_list_frame, background=self._get_widget_bg_color(), fg=self._get_widget_fg_color(),
                                       borderwidth=0, highlightthickness=0, exportselection=False,
                                       selectbackground=ctk.ThemeManager.theme["CTkButton"]["fg_color"][0], # Utilise la couleur du bouton pour la sélection
                                       selectforeground=ctk.ThemeManager.theme["CTkButton"]["text_color"][0])
        self.site_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.site_listbox.bind("<<ListboxSelect>>", self._on_site_selected)
        

    def _create_user_list_frame(self):
        """Crée le cadre pour la liste des utilisateurs."""
        user_list_frame = ctk.CTkFrame(self)
        user_list_frame.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="nsew")
        user_list_frame.grid_rowconfigure(0, weight=1)
        user_list_frame.grid_columnconfigure(0, weight=1)

        self.user_listbox = tk.Listbox(user_list_frame, background=self._get_widget_bg_color(), fg=self._get_widget_fg_color(),
                                       borderwidth=0, highlightthickness=0, exportselection=False,
                                       selectbackground=ctk.ThemeManager.theme["CTkButton"]["fg_color"][0],
                                       selectforeground=ctk.ThemeManager.theme["CTkButton"]["text_color"][0])
        self.user_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.user_listbox.bind("<<ListboxSelect>>", self._on_user_selected)

    def _create_details_frame(self):
        """Crée le cadre pour afficher les détails de l'entrée."""
        self.details_frame = ctk.CTkFrame(self)
        self.details_frame.grid(row=1, column=2, padx=(5, 10), pady=(0, 10), sticky="nsew")
        self.details_frame.grid_columnconfigure(1, weight=1)

        
        ctk.CTkLabel(self.details_frame, text="Site:", anchor="w").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.site_details_label = ctk.CTkLabel(self.details_frame, text="-", anchor="w", wraplength=300)
        self.site_details_label.grid(row=0, column=1, columnspan=2, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(self.details_frame, text="Utilisateur:", anchor="w").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.user_details_entry = ctk.CTkEntry(self.details_frame, state="readonly", fg_color="transparent", border_width=0)
        self.user_details_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.copy_user_button = ctk.CTkButton(self.details_frame, text="Copier", width=60, command=self._copy_username, state="disabled")
        self.copy_user_button.grid(row=1, column=2, padx=(0, 10), pady=5)

        ctk.CTkLabel(self.details_frame, text="Mot de passe:", anchor="w").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.pass_details_entry = ctk.CTkEntry(self.details_frame, show="*", state="readonly", fg_color="transparent", border_width=0)
        self.pass_details_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        pass_button_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        pass_button_frame.grid(row=2, column=2, padx=(0, 10), pady=5, sticky="w")
        self.reveal_pass_button = ctk.CTkButton(pass_button_frame, text="👁", width=30, font=("Arial", 16), command=self._toggle_password_visibility, state="disabled")
        self.reveal_pass_button.pack(side="left", padx=(0,5))
        self.copy_pass_button = ctk.CTkButton(pass_button_frame, text="Copier", width=60, command=self._copy_password, state="disabled")
        self.copy_pass_button.pack(side="left")

        
        entry_action_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        entry_action_frame.grid(row=3, column=0, columnspan=3, pady=20)
        self.edit_button = ctk.CTkButton(entry_action_frame, text="Modifier", command=self._open_edit_dialog, state="disabled")
        self.edit_button.pack(side="left", padx=10)
        self.delete_button = ctk.CTkButton(entry_action_frame, text="Supprimer", fg_color="#D32F2F", hover_color="#C62828", command=self._delete_selected_entry, state="disabled")
        self.delete_button.pack(side="left", padx=10)

    def _create_action_buttons(self):
        """Crée les boutons d'action généraux (Ajouter)."""
        action_button_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_button_frame.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="e")

        self.add_button = ctk.CTkButton(action_button_frame, text="＋ Ajouter une Entrée", command=self._open_add_dialog)
        self.add_button.pack()

    

    def _populate_site_list(self):
        """Remplit la liste des sites."""
        self.site_listbox.delete(0, "end")
        search_term = self.search_var.get().lower()
        sites = core.lister_sites(self.passwords)
        for site in sites:
            if search_term in site.lower():
                self.site_listbox.insert("end", site)
        self._clear_user_list()
        self._clear_details()

    def _populate_user_list(self, site: str):
        """Remplit la liste des utilisateurs pour le site sélectionné."""
        self._clear_user_list()
        if site:
            users = core.recuperer_utilisateurs_pour_site(self.passwords, site)
            for user in sorted(users):
                self.user_listbox.insert("end", user)
        self._clear_details()

    def _filter_sites(self):
        """Met à jour la liste des sites basée sur la recherche."""
        self._populate_site_list()

    def _clear_site_selection(self):
        self.site_listbox.selection_clear(0, 'end')
        self.selected_site = None
        self._clear_user_list()

    def _clear_user_list(self):
        self.user_listbox.delete(0, 'end')
        self.selected_user = None
        self._clear_details()

    def _clear_details(self):
        """Réinitialise le panneau de détails."""
        self.site_details_label.configure(text="-")
        
        self.user_details_entry.configure(state="normal")
        self.user_details_entry.delete(0, "end")
        self.user_details_entry.configure(state="readonly")
        
        self.pass_details_entry.configure(state="normal")
        self.pass_details_entry.delete(0, "end")
        self.pass_details_entry.configure(show="*", state="readonly") 
        self.password_visible = False
        self.reveal_pass_button.configure(text="👁")

        
        self.copy_user_button.configure(state="disabled")
        self.copy_pass_button.configure(state="disabled")
        self.reveal_pass_button.configure(state="disabled")
        self.edit_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")

    def _show_entry_details(self, site: str, user: str):
        """Affiche les détails de l'entrée sélectionnée."""
        password = core.recuperer_entree(self.passwords, site, user)
        if password is None:
            self._clear_details()
            return

        self.site_details_label.configure(text=site)

        self.user_details_entry.configure(state="normal")
        self.user_details_entry.delete(0, "end")
        self.user_details_entry.insert(0, user)
        self.user_details_entry.configure(state="readonly")

        self.pass_details_entry.configure(state="normal")
        self.pass_details_entry.delete(0, "end")
        self.pass_details_entry.insert(0, password)
        self.pass_details_entry.configure(show="*" if not self.password_visible else "", state="readonly")

        
        self.copy_user_button.configure(state="normal")
        self.copy_pass_button.configure(state="normal")
        self.reveal_pass_button.configure(state="normal")
        self.edit_button.configure(state="normal")
        self.delete_button.configure(state="normal")

   

    def _on_site_selected(self, event=None):
        """Appelé quand un site est sélectionné dans la liste."""
        selected_indices = self.site_listbox.curselection()
        if not selected_indices:
            self.selected_site = None
            self._clear_user_list()
            return

        self.selected_site = self.site_listbox.get(selected_indices[0])
        self._populate_user_list(self.selected_site)

    def _on_user_selected(self, event=None):
        """Appelé quand un utilisateur est sélectionné dans la liste."""
        selected_indices = self.user_listbox.curselection()
        if not selected_indices or not self.selected_site:
            self.selected_user = None
            self._clear_details()
            return
            
        self.selected_user = self.user_listbox.get(selected_indices[0])
        self._show_entry_details(self.selected_site, self.selected_user)


    def _toggle_password_visibility(self):
        """Affiche ou masque le mot de passe dans le champ de détails."""
        if self.pass_details_entry.cget("state") == "disabled" or not self.selected_user:
            return
            
        self.password_visible = not self.password_visible
        new_show = "" if self.password_visible else "*"
        self.pass_details_entry.configure(state="normal") 
        self.pass_details_entry.configure(show=new_show)
        self.pass_details_entry.configure(state="readonly")
        
        self.reveal_pass_button.configure(text="🙈" if self.password_visible else "👁")

    def _copy_username(self):
        """Copie le nom d'utilisateur dans le presse-papiers."""
        if self.selected_user and self.user_details_entry.cget("state") != "disabled":
            username = self.user_details_entry.get()
            try:
                pyperclip.copy(username)
                print(f"Utilisateur '{username}' copié.")
                
            except Exception as e:
                print(f"Erreur de copie (utilisateur): {e}")
                messagebox.showerror("Erreur de copie", f"Impossible de copier l'utilisateur: {e}", parent=self)

    def _copy_password(self):
        """Copie le mot de passe dans le presse-papiers."""
        if self.selected_user and self.pass_details_entry.cget("state") != "disabled":
            # Récupérer le mot de passe réel depuis les données, pas seulement l'affichage
            password = core.recuperer_entree(self.passwords, self.selected_site, self.selected_user)
            if password:
                try:
                    pyperclip.copy(password)
                    print("Mot de passe copié.")
                  
                except Exception as e:
                    print(f"Erreur de copie (mot de passe): {e}")
                    messagebox.showerror("Erreur de copie", f"Impossible de copier le mot de passe: {e}", parent=self)

    # --- Dialogues et Actions ---

    def _open_add_dialog(self):
        """Ouvre la boîte de dialogue pour ajouter une nouvelle entrée."""
        dialog = AddEditDialog(self, title="Ajouter une Entrée", callback=self._save_new_entry)
        # La fenêtre devient modale grâce à grab_set() dans AddEditDialog

    def _save_new_entry(self, result: Tuple[str, str, str]):
        """Callback pour sauvegarder la nouvelle entrée."""
        if result:
            site, username, password = result
            try:
                # Vérifier si l'entrée existe déjà
                if core.recuperer_entree(self.passwords, site, username) is not None:
                    if not messagebox.askyesno("Entrée existante", f"Une entrée pour '{username}' sur '{site}' existe déjà.\nVoulez-vous l'écraser ?", parent=self):
                        return # Annuler si l'utilisateur refuse

                core.ajouter_ou_modifier_entree(self.passwords, site, username, password)
                self._save_storage_and_refresh(select_site=site, select_user=username)
                print("Nouvelle entrée sauvegardée.")
            except Exception as e:
                 messagebox.showerror("Erreur Sauvegarde", f"Impossible de sauvegarder l'entrée: {e}", parent=self)


    def _open_edit_dialog(self):
        """Ouvre la boîte de dialogue pour modifier l'entrée sélectionnée."""
        if not self.selected_site or not self.selected_user:
            return

        password = core.recuperer_entree(self.passwords, self.selected_site, self.selected_user)
        if password is None: return # Sécurité

        dialog = AddEditDialog(self, title="Modifier l'Entrée",
                               site=self.selected_site,
                               username=self.selected_user,
                               password=password,
                               callback=self._save_edited_entry)

    def _save_edited_entry(self, result: Tuple[str, str, str]):
        """Callback pour sauvegarder l'entrée modifiée."""
        if result and self.selected_site and self.selected_user:
            new_site, new_username, new_password = result
            original_site = self.selected_site
            original_user = self.selected_user
            
            try:
                # Si le site ou l'utilisateur a changé, il faut supprimer l'ancienne entrée
                entry_changed = (new_site != original_site) or (new_username != original_user)
                
                if entry_changed:
                    # Vérifier si la nouvelle combinaison existe déjà (et n'est pas l'entrée originale)
                    existing_pass = core.recuperer_entree(self.passwords, new_site, new_username)
                    if existing_pass is not None :
                         if not messagebox.askyesno("Conflit d'entrée", f"Une entrée pour '{new_username}' sur '{new_site}' existe déjà.\nVoulez-vous l'écraser ?", parent=self):
                             return # Annuler si l'utilisateur refuse
                             
                    # Supprimer l'ancienne entrée avant d'ajouter la nouvelle pour éviter les conflits temporaires
                    core.supprimer_entree(self.passwords, original_site, original_user)

                # Ajouter/Mettre à jour avec les nouvelles informations
                core.ajouter_ou_modifier_entree(self.passwords, new_site, new_username, new_password)
                self._save_storage_and_refresh(select_site=new_site, select_user=new_username)
                print("Entrée modifiée sauvegardée.")
            except Exception as e:
                 messagebox.showerror("Erreur Sauvegarde", f"Impossible de sauvegarder l'entrée modifiée: {e}", parent=self)


    def _delete_selected_entry(self):
        """Supprime l'entrée actuellement sélectionnée après confirmation."""
        if not self.selected_site or not self.selected_user:
            return

        if messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer l'entrée pour\n'{self.selected_user}' sur '{self.selected_site}' ?", parent=self):
            try:
                if core.supprimer_entree(self.passwords, self.selected_site, self.selected_user):
                     self._save_storage_and_refresh(select_site=None, select_user=None) 
                     print("Entrée supprimée.")
                else:
                    messagebox.showwarning("Erreur", "L'entrée n'a pas pu être supprimée (déjà supprimée?).", parent=self)
            except Exception as e:
                messagebox.showerror("Erreur Suppression", f"Impossible de supprimer l'entrée: {e}", parent=self)

    def _save_storage_and_refresh(self, select_site: Optional[str] = None, select_user: Optional[str] = None):
        """Sauvegarde le stockage et rafraîchit l'interface."""
        try:
            core.sauvegarder_stockage(self.passwords, self.master_password)
            self._populate_site_list()
            
            if select_site and select_site in core.lister_sites(self.passwords):
                try:
                    site_index = list(self.site_listbox.get(0, 'end')).index(select_site)
                    self.site_listbox.selection_set(site_index)
                    self.site_listbox.activate(site_index)
                    self.selected_site = select_site
                    self._populate_user_list(select_site)

                    if select_user and select_user in core.recuperer_utilisateurs_pour_site(self.passwords, select_site):
                         user_index = list(self.user_listbox.get(0, 'end')).index(select_user)
                         self.user_listbox.selection_set(user_index)
                         self.user_listbox.activate(user_index)
                         self.selected_user = select_user
                         self._show_entry_details(select_site, select_user)
                    else:
                         self._clear_details() #
                except ValueError:
                     print("Info: Impossible de re-sélectionner l'entrée après rafraîchissement.")
                     self._clear_site_selection() 
            else:
                 self._clear_site_selection() 

        except Exception as e:
            messagebox.showerror("Erreur Sauvegarde", f"Une erreur est survenue lors de la sauvegarde: {e}", parent=self)
            

    def _on_closing(self):
        """Appelé lorsque l'utilisateur essaie de fermer la fenêtre."""
       
        print("Sauvegarde avant fermeture...")
        try:
            core.sauvegarder_stockage(self.passwords, self.master_password)
        except Exception as e:
             
             if not messagebox.askokcancel("Erreur de Sauvegarde", f"Impossible de sauvegarder les données avant de quitter:\n{e}\n\nVoulez-vous quitter quand même (les modifications non sauvegardées seront perdues) ?", parent=self):
                 return 
        self.destroy() 

   
    def _get_widget_bg_color(self):
        """Retourne la couleur de fond attendue pour les widgets Tkinter."""
        
        try:
             return ctk.ThemeManager.theme["CTkFrame"]["fg_color"][0 if ctk.get_appearance_mode() == "Light" else 1]
        except:
             return "white" if ctk.get_appearance_mode() == "Light" else "black" # Fallback

    def _get_widget_fg_color(self):
        """Retourne la couleur de texte attendue."""
        try:
             return ctk.ThemeManager.theme["CTkLabel"]["text_color"][0 if ctk.get_appearance_mode() == "Light" else 1]
        except:
            return "black" if ctk.get_appearance_mode() == "Light" else "white" # Fallback


# --- Point d'Entrée Principal ---
if __name__ == "__main__":
    login_app = LoginWindow()
    login_app.mainloop() 

    
    if login_app.passwords_data is not None and login_app.master_password is not None:
        print("Connexion réussie. Lancement de l'application principale...")
        main_app = MainWindow(login_app.passwords_data, login_app.master_password)
        main_app.mainloop() 
    else:
        print("\nConnexion échouée ou annulée. Fermeture.")