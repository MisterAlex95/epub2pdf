"""
Gestion du thème sombre pour l'interface avec animations et réactivité
"""

from tkinter import ttk
import tkinter as tk

class DarkTheme:
    """Configuration du thème sombre avec animations"""
    
    def __init__(self):
        self.colors = {
            'bg_dark': '#1e1e1e',
            'bg_medium': '#2b2b2b',
            'bg_light': '#3a3a3a',
            'bg_accent': '#007acc',
            'bg_accent_hover': '#1a8ad8',
            'bg_accent_active': '#0066b3',
            'text_primary': '#ffffff',
            'text_secondary': '#e0e0e0',
            'text_muted': '#a0a0a0',
            'border': '#404040',
            'border_hover': '#505050',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545',
            'success_hover': '#218838',
            'warning_hover': '#e0a800',
            'error_hover': '#c82333'
        }
        self._setup_styles()
    
    def _setup_styles(self):
        """Configuration des styles ttk avec animations"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frames avec effets de survol
        style.configure('Dark.TFrame', background=self.colors['bg_dark'])
        style.configure('Medium.TFrame', background=self.colors['bg_medium'])
        style.configure('Light.TFrame', background=self.colors['bg_light'])
        style.configure('Hover.TFrame', background=self.colors['bg_light'])
        
        # Labels avec styles réactifs
        style.configure('Title.TLabel',
                      background=self.colors['bg_dark'],
                      foreground=self.colors['text_primary'],
                      font=('Segoe UI', 16, 'bold'))
        
        style.configure('Section.TLabel',
                      background=self.colors['bg_medium'],
                      foreground=self.colors['text_primary'],
                      font=('Segoe UI', 12, 'bold'))
        
        style.configure('Body.TLabel',
                      background=self.colors['bg_medium'],
                      foreground=self.colors['text_secondary'],
                      font=('Segoe UI', 10))
        
        style.configure('Status.TLabel',
                      background=self.colors['bg_medium'],
                      foreground=self.colors['success'],
                      font=('Segoe UI', 9, 'bold'))
        
        # Boutons avec effets de survol uniformes
        style.configure('Primary.TButton',
                      background=self.colors['bg_accent'],
                      foreground=self.colors['text_primary'],
                      borderwidth=0,
                      relief='flat',
                      font=('Segoe UI', 10, 'bold'),
                      padding=(12, 6))
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['bg_accent_active']),
                           ('pressed', self.colors['bg_accent_active']),
                           ('hover', self.colors['bg_accent_hover'])])
        
        style.configure('Secondary.TButton',
                      background=self.colors['bg_light'],
                      foreground=self.colors['text_primary'],
                      borderwidth=1,
                      relief='flat',
                      font=('Segoe UI', 9),
                      padding=(10, 5))
        
        style.map('Secondary.TButton',
                 background=[('active', self.colors['bg_accent']),
                           ('pressed', self.colors['bg_accent']),
                           ('hover', self.colors['bg_medium'])])
        
        style.configure('Success.TButton',
                      background=self.colors['success'],
                      foreground=self.colors['text_primary'],
                      borderwidth=0,
                      relief='flat',
                      font=('Segoe UI', 9, 'bold'),
                      padding=(10, 5))
        
        style.map('Success.TButton',
                 background=[('active', self.colors['success_hover']),
                           ('pressed', self.colors['success_hover']),
                           ('hover', self.colors['success_hover'])])
        
        style.configure('Warning.TButton',
                      background=self.colors['warning'],
                      foreground=self.colors['text_primary'],
                      borderwidth=0,
                      relief='flat',
                      font=('Segoe UI', 9, 'bold'),
                      padding=(10, 6))
        
        style.map('Warning.TButton',
                 background=[('active', self.colors['warning_hover']),
                           ('pressed', self.colors['warning_hover'])])
        
        # Entrées avec focus
        style.configure('Dark.TEntry',
                      fieldbackground=self.colors['bg_light'],
                      foreground=self.colors['text_primary'],
                      borderwidth=1,
                      relief='flat',
                      font=('Segoe UI', 10))
        
        style.map('Dark.TEntry',
                 bordercolor=[('focus', self.colors['bg_accent'])])
        
        # Combobox avec focus
        style.configure('Dark.TCombobox',
                      fieldbackground=self.colors['bg_light'],
                      foreground=self.colors['text_primary'],
                      borderwidth=1,
                      relief='flat',
                      font=('Segoe UI', 10))
        
        style.map('Dark.TCombobox',
                 bordercolor=[('focus', self.colors['bg_accent'])])
        
        # Checkbox avec animations
        style.configure('Dark.TCheckbutton',
                      background=self.colors['bg_medium'],
                      foreground=self.colors['text_primary'],
                      font=('Segoe UI', 9))
        
        style.map('Dark.TCheckbutton',
                 background=[('active', self.colors['bg_accent'])])
        
        # Treeview avec sélection
        style.configure('Dark.Treeview',
                      background=self.colors['bg_light'],
                      foreground=self.colors['text_primary'],
                      fieldbackground=self.colors['bg_light'],
                      borderwidth=1,
                      relief='flat',
                      font=('Segoe UI', 10))
        
        style.map('Dark.Treeview',
                 background=[('selected', self.colors['bg_accent'])])
        
        style.configure('Dark.Treeview.Heading',
                      background=self.colors['bg_medium'],
                      foreground=self.colors['text_primary'],
                      font=('Segoe UI', 10, 'bold'))
        
        # Progress bar
        style.configure('Dark.Horizontal.TProgressbar',
                      background=self.colors['bg_accent'],
                      troughcolor=self.colors['bg_light'],
                      borderwidth=0,
                      lightcolor=self.colors['bg_accent'],
                      darkcolor=self.colors['bg_accent'])
    
    def get_color(self, color_name):
        """Retourne une couleur par nom"""
        return self.colors.get(color_name, self.colors['text_primary'])
    
    def create_hover_effect(self, widget, hover_color=None, normal_color=None):
        """Crée un effet de survol pour un widget"""
        if hover_color is None:
            hover_color = self.colors['bg_accent']
        if normal_color is None:
            normal_color = self.colors['bg_light']
        
        def on_enter(event):
            widget.configure(background=hover_color)
        
        def on_leave(event):
            widget.configure(background=normal_color)
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave) 