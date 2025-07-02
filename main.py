
import flet as ft
import json
import os
from datetime import datetime, date
from typing import List, Dict, Optional
import calendar

class Modul:
    def __init__(self, name: str, farbe: str = "#2196F3", beschreibung: str = ""):
        self.name = name
        self.farbe = farbe
        self.beschreibung = beschreibung
        self.aufgaben: List[Aufgabe] = []
        self.erstellt_am = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "name": self.name,
            "farbe": self.farbe,
            "beschreibung": self.beschreibung,
            "aufgaben": [aufgabe.to_dict() for aufgabe in self.aufgaben],
            "erstellt_am": self.erstellt_am
        }
    
    @classmethod
    def from_dict(cls, data):
        modul = cls(data["name"], data.get("farbe", "#2196F3"), data.get("beschreibung", ""))
        modul.erstellt_am = data.get("erstellt_am", datetime.now().isoformat())
        modul.aufgaben = [Aufgabe.from_dict(aufgabe_data) for aufgabe_data in data.get("aufgaben", [])]
        return modul
    
    def get_fortschritt(self):
        if not self.aufgaben:
            return 0
        erledigte = sum(1 for aufgabe in self.aufgaben if aufgabe.erledigt)
        return erledigte / len(self.aufgaben)

class Aufgabe:
    def __init__(self, titel: str, beschreibung: str = "", faelligkeitsdatum: Optional[str] = None, prioritaet: str = "Normal"):
        self.titel = titel
        self.beschreibung = beschreibung
        self.faelligkeitsdatum = faelligkeitsdatum
        self.prioritaet = prioritaet
        self.erledigt = False
        self.erstellt_am = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "titel": self.titel,
            "beschreibung": self.beschreibung,
            "faelligkeitsdatum": self.faelligkeitsdatum,
            "prioritaet": self.prioritaet,
            "erledigt": self.erledigt,
            "erstellt_am": self.erstellt_am
        }
    
    @classmethod
    def from_dict(cls, data):
        aufgabe = cls(
            data["titel"],
            data.get("beschreibung", ""),
            data.get("faelligkeitsdatum"),
            data.get("prioritaet", "Normal")
        )
        aufgabe.erledigt = data.get("erledigt", False)
        aufgabe.erstellt_am = data.get("erstellt_am", datetime.now().isoformat())
        return aufgabe
    
    def ist_ueberfaellig(self):
        if not self.faelligkeitsdatum or self.erledigt:
            return False
        try:
            faellig = datetime.fromisoformat(self.faelligkeitsdatum).date()
            return faellig < date.today()
        except:
            return False

class StudienplanerApp:
    def __init__(self):
        self.module: List[Modul] = []
        self.aktuelles_modul: Optional[Modul] = None
        self.datei_pfad = "studienplaner_data.json"
        self.aktuelle_ansicht = "module"
        
    def daten_laden(self):
        try:
            if os.path.exists(self.datei_pfad):
                with open(self.datei_pfad, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.module = [Modul.from_dict(modul_data) for modul_data in data.get("module", [])]
        except Exception as e:
            print(f"Fehler beim Laden der Daten: {e}")
    
    def daten_speichern(self):
        try:
            data = {
                "module": [modul.to_dict() for modul in self.module],
                "gespeichert_am": datetime.now().isoformat()
            }
            with open(self.datei_pfad, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern der Daten: {e}")
    
    def export_csv(self):
        try:
            import csv
            datei_name = f"studienplaner_export_{date.today().isoformat()}.csv"
            with open(datei_name, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Modul', 'Aufgabe', 'Beschreibung', 'Fälligkeitsdatum', 'Priorität', 'Status'])
                
                for modul in self.module:
                    if modul.aufgaben:
                        # Modul mit Aufgaben 
                        for aufgabe in modul.aufgaben:
                            writer.writerow([
                                modul.name,
                                aufgabe.titel,
                                aufgabe.beschreibung,
                                aufgabe.faelligkeitsdatum or '',
                                aufgabe.prioritaet,
                                'Erledigt' if aufgabe.erledigt else 'Offen'
                            ])
                    else:
                        # Modul ohne Aufgaben → leere Aufgabenspalten
                        writer.writerow([
                            modul.name,
                            '', '', '', '', ''  # leere Spalten für Titel, Beschreibung usw.
                        ])

            return datei_name
        except Exception as e:
            print(f"Fehler beim CSV-Export: {e}")
            return None

def main(page: ft.Page):
    page.title = "Studienplaner"
    page.favicon = "studienplaner_favicon.png"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1000
    page.window_height = 700
    page.padding = 20
    
    app = StudienplanerApp()
    app.daten_laden()
    
    module_list = ft.ListView(expand=True, spacing=10)
    aufgaben_list = ft.ListView(expand=True, spacing=5)
    kalender_content = ft.Column(expand=True, scroll="auto")
    dashboard_content = ft.Column(expand=True, scroll="auto")
    
    def modul_hinzufuegen_dialog(e=None):
        modul_name = ft.TextField(label="Name", width=300)
        modul_beschreibung = ft.TextField(label="Beschreibung", multiline=True, width=300)
        modul_farbe = ft.Dropdown(
            label="Farbe",
            width=300,
             options=[
                ft.dropdown.Option(text="Blau", key="#2196F3"),
                ft.dropdown.Option(text="Grün", key="#4CAF50"),
                ft.dropdown.Option(text="Orange", key="#FF9800"),
                ft.dropdown.Option(text="Rot", key="#F44336"),
                ft.dropdown.Option(text="Lila", key="#9C27B0"),
                ft.dropdown.Option(text="Türkis", key="#009688"),
                ft.dropdown.Option(text="Violet", key="#6959CD"),
                ft.dropdown.Option(text="Braun", key="#8B4513"),
                ft.dropdown.Option(text="Grau", key="#BABABA"),
                ft.dropdown.Option(text="Gelb", key="#FFFF00"),
                ft.dropdown.Option(text="Beige", key="#FFE7BA")
            ],
            key="#2196F3"
        )

        def modul_speichern(e=None):  # Optionales Event-Argument
            if modul_name.value and modul_name.value.strip():
                
                # modul erstellen
                neues_modul = Modul(
                    modul_name.value.strip(),
                    modul_farbe.value,
                    modul_beschreibung.value.strip() if modul_beschreibung.value else ""
                )
                
                # Zur Liste hinzufügen
                app.module.append(neues_modul)
                
                # Speichern und UI aktualisieren
                app.daten_speichern()       
                aktualisiere_module_liste()
                
                # Dialog schließen - ERST AM SCHLUSS!
                page.close(dialog)
            else:
                modul_name.error_text = "itte geben Sie einen Modulnamen ein"
                page.update()

        def dialog_abbrechen(e=None):
            page.close(dialog)

        def on_key(e: ft.KeyboardEvent):
            if not dialog.open:
                return
            if e.key == "Escape":
                dialog_abbrechen()
            elif e.key == "Enter":
                modul_speichern()

        # Dialog-Definition
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Neues Modul hinzufügen"),
            content=ft.Column([
                modul_name,
                modul_beschreibung,
                modul_farbe
            ], tight=True, height=200),
            actions=[
                ft.TextButton("Abbrechen", on_click=dialog_abbrechen),
                ft.ElevatedButton("Speichern", on_click=modul_speichern)
            ]
        )

        # Keyboard-Handler registrieren (einmalig z. B. beim Initialisieren deiner Seite)
        page.on_keyboard_event = on_key

        # Dialog öffnen
        page.open(dialog)
        page.update()
        modul_name.focus()
        page.update()


    # Block 3: Aufgabe hinzufügen Dialog
    def aufgabe_hinzufuegen_dialog(e=None):
        if not app.aktuelles_modul:
            return

        # Eingabefelder definieren
        aufgabe_titel = ft.TextField(label="Aufgabentitel", width=300)
        aufgabe_beschreibung = ft.TextField(label="Beschreibung", multiline=True, width=300)
        aufgabe_datum = ft.TextField(label="Fälligkeitsdatum (YYYY-MM-DD)", width=300)
        aufgabe_prioritaet = ft.Dropdown(
            label="Priorität",
            width=300,
            options=[
                ft.dropdown.Option("Selbststudium"),
                ft.dropdown.Option("Praktische Arbeit"),
                ft.dropdown.Option("Abgabe"),
                ft.dropdown.Option("Prüfung")
            ],
            value="Selbststudium"
        )

        # Funktion zum Dialog-Schließen
        def dialog_schliessen(e=None):
            dialog.open = False
            page.update()

        # Funktion zum Speichern
        def aufgabe_speichern(e=None):
            if aufgabe_titel.value.strip():
                # Datum validieren
                faelligkeitsdatum = None
                if aufgabe_datum.value.strip():
                    try:
                        datetime.fromisoformat(aufgabe_datum.value.strip())
                        faelligkeitsdatum = aufgabe_datum.value.strip()
                    except:
                        pass

                neue_aufgabe = Aufgabe(
                    aufgabe_titel.value.strip(),
                    aufgabe_beschreibung.value.strip(),
                    faelligkeitsdatum,
                    aufgabe_prioritaet.value
                )
                app.aktuelles_modul.aufgaben.append(neue_aufgabe)
                app.daten_speichern()
                aktualisiere_aufgaben_liste()
                aktualisiere_dashboard()
                dialog.open = False
                page.update()

        # Tasteneingaben behandeln
        def on_key(e: ft.KeyboardEvent):
            if not dialog.open:
                return
            if e.key == "Escape":
                dialog_schliessen()
            elif e.key == "Enter":
                aufgabe_speichern()

        # Dialog-Definition
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Neue Aufgabe für {app.aktuelles_modul.name}"),
            content=ft.Column([
                aufgabe_titel,
                aufgabe_beschreibung,
                aufgabe_datum,
                aufgabe_prioritaet
            ], tight=True, height=250),
            actions=[
                ft.TextButton("Abbrechen", on_click=dialog_schliessen),
                ft.ElevatedButton("Speichern", on_click=aufgabe_speichern)
            ]
        )

        # Dialog anzeigen & Fokus setzen
        page.dialog = dialog
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
        aufgabe_titel.focus()  # Cursor in erstes Feld setzen
        page.update()

        # Tastatureingaben aktivieren (nur einmal registrieren in main!)
        page.on_keyboard_event = on_key

    def aktualisiere_module_liste():
        module_list.controls.clear()     

        if not app.module:
            module_list.controls.append(
                ft.Container(
                    content=ft.Text("Noch keine Module vorhanden.", 
                                    size=18, text_align=ft.TextAlign.CENTER, italic=True),
                    padding=20,
                    alignment=ft.alignment.center
                )
            )
        else:
            for modul in app.module:
                fortschritt = modul.get_fortschritt()
                aufgaben_anzahl = len(modul.aufgaben)
                erledigte_anzahl = sum(1 for a in modul.aufgaben if a.erledigt)

                def loesche_modul(e, zu_loeschendes_modul=modul):
                    def modul_loeschen_bestaetigt(e=None):
                        if zu_loeschendes_modul in app.module:
                            app.module.remove(zu_loeschendes_modul)
                            app.aktuelles_modul = None if app.aktuelles_modul == zu_loeschendes_modul else app.aktuelles_modul
                            app.daten_speichern()
                            aktualisiere_module_liste()
                            aktualisiere_aufgaben_liste()
                            aktualisiere_dashboard()

                            # Snackbar anzeigen
                            snack = ft.SnackBar(
                                ft.Text(f"Modul '{zu_loeschendes_modul.name}' erfolgreich gelöscht."),
                                duration=3000
                            )
                            page.snack_bar = snack
                            page.overlay.append(snack)
                            snack.open = True
                            
                        page.dialog.open = False
                        page.update()

                    def modul_loeschen_abbrechen(e=None):
                        page.dialog.open = False
                        page.update()

                    def on_key(e: ft.KeyboardEvent):
                        if not dialog.open:
                            return
                        if e.key == "Escape":
                            modul_loeschen_abbrechen()
                        elif e.key == "Enter":
                            modul_loeschen_bestaetigt()

                    dialog = ft.AlertDialog(
                        modal=True,
                        title=ft.Text("Modul löschen"),
                        content=ft.Text(f"Möchten Sie das Modul '{zu_loeschendes_modul.name}' wirklich löschen?"),
                        actions=[
                            ft.TextButton("Abbrechen", on_click=modul_loeschen_abbrechen),
                            ft.ElevatedButton("Löschen", on_click=modul_loeschen_bestaetigt, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE)
                        ],
                        actions_alignment=ft.MainAxisAlignment.END
                    )
                    page.dialog = dialog
                    page.overlay.append(dialog)
                    dialog.open = True
                    page.on_keyboard_event = on_key
                    page.update()


                modul_card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(modul.name, size=20, weight=ft.FontWeight.BOLD),
                                    expand=True
                                ),
                                ft.Text(f"{erledigte_anzahl}/{aufgaben_anzahl}", size=14),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=ft.Colors.RED_700,
                                    tooltip="Modul löschen",
                                    on_click=lambda e, m=modul: loesche_modul(e, m)
                                )
                            ]),
                            ft.Text(modul.beschreibung, size=18, opacity=0.9) if modul.beschreibung else ft.Container(),
                            ft.ProgressBar(value=fortschritt, color=modul.farbe, height=8),
                        ]),
                        padding=15,
                        border_radius=8,
                        bgcolor=ft.Colors.with_opacity(0.3, modul.farbe),
                        on_click=lambda e, m=modul: modul_auswaehlen(m)
                    )
                )

                module_list.controls.append(modul_card)

        page.update()



    def modul_auswaehlen(modul: Modul):
        app.aktuelles_modul = modul
        aktualisiere_aufgaben_liste()
    
    def aktualisiere_aufgaben_liste():
        aufgaben_list.controls.clear()
        
        if not app.aktuelles_modul:
            aufgaben_list.controls.append(
                ft.Container(
                    content=ft.Text("Wählen Sie ein Modul aus der Liste links aus", 
                                  size=18, text_align=ft.TextAlign.CENTER, italic=True),
                    padding=20,
                    alignment=ft.alignment.center
                )
            )
            page.update()
            return
        
        # Header
        header = ft.Row([
            ft.Text(f"Aufgaben für {app.aktuelles_modul.name}", size=20, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("Neue Aufgabe", icon=ft.Icons.ADD, on_click=aufgabe_hinzufuegen_dialog)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        aufgaben_list.controls.append(header)
        
        if not app.aktuelles_modul.aufgaben:
            aufgaben_list.controls.append(
                ft.Container(
                    content=ft.Text("Noch keine Aufgaben vorhanden.", 
                                  size=18, text_align=ft.TextAlign.CENTER, italic=True),
                    padding=20,
                    alignment=ft.alignment.center
                )
            )
        else:
            for i, aufgabe in enumerate(app.aktuelles_modul.aufgaben):
                prioritaet_farbe = {
                    "Selbststudium": ft.Colors.GREEN,
                    "Praktische Arbeit": ft.Colors.BLUE,
                    "Abgabe (schriftlich)": ft.Colors.ORANGE,
                    "Prüfung": ft.Colors.RED
                }.get(aufgabe.prioritaet, ft.Colors.BLUE)
                
                status_icon = ft.Icons.CHECK_CIRCLE if aufgabe.erledigt else ft.Icons.RADIO_BUTTON_UNCHECKED
                status_farbe = ft.Colors.GREEN if aufgabe.erledigt else ft.Colors.GREY
                
                card_farbe = ft.Colors.RED_50 if aufgabe.ist_ueberfaellig() else None
                
                def toggle_aufgabe_status(e, aufgabe_idx=i):
                    app.aktuelles_modul.aufgaben[aufgabe_idx].erledigt = not app.aktuelles_modul.aufgaben[aufgabe_idx].erledigt
                    app.daten_speichern()
                    aktualisiere_aufgaben_liste()
                    aktualisiere_module_liste()
                    aktualisiere_dashboard()

                def aufgabe_loeschen(e, aufgabe_idx=i):
                    def aufgabe_loeschen_bestaetigen(e=None):
                        del app.aktuelles_modul.aufgaben[aufgabe_idx]
                        app.daten_speichern()
                        aktualisiere_aufgaben_liste()
                        aktualisiere_module_liste()
                        aktualisiere_dashboard()
                        page.dialog.open = False

                        # Snackbar anzeigen
                        snack = ft.SnackBar(
                            ft.Text(f"Aufgabe erfolgreich gelöscht."),
                            duration=3000
                        )
                        page.snack_bar = snack
                        page.overlay.append(snack)
                        snack.open = True

                        page.update()

                    def aufgabe_loeschen_abbrechen(e=None):
                        page.dialog.open = False
                        page.update()

                    def on_key(e: ft.KeyboardEvent):
                        if not dialog.open:
                            return
                        if e.key == "Escape":
                            aufgabe_loeschen_abbrechen()
                        elif e.key == "Enter":
                            aufgabe_loeschen_bestaetigen()

                    dialog = ft.AlertDialog(
                        modal=True,
                        title=ft.Text("Aufgabe löschen"),
                        content=ft.Text(f"Möchten Sie die Aufgabe '{app.aktuelles_modul.aufgaben[aufgabe_idx].titel}' wirklich löschen?"),
                        actions=[
                            ft.TextButton("Abbrechen", on_click=aufgabe_loeschen_abbrechen),
                            ft.ElevatedButton(
                                "Löschen",
                                on_click=aufgabe_loeschen_bestaetigen,
                                bgcolor=ft.Colors.RED,
                                color=ft.Colors.WHITE
                            )
                        ],
                        actions_alignment=ft.MainAxisAlignment.END
                    )
                    page.dialog = dialog
                    page.overlay.append(dialog)
                    dialog.open = True
                    page.on_keyboard_event = on_key
                    page.update()



                aufgabe_card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.IconButton(
                                    icon=status_icon,
                                    icon_color=status_farbe,
                                    on_click=toggle_aufgabe_status
                                ),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(
                                            aufgabe.titel,
                                            size=18,
                                            weight=ft.FontWeight.BOLD,
                                            style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH) if aufgabe.erledigt else None
                                        ),
                                        ft.Text(aufgabe.beschreibung, size=16) if aufgabe.beschreibung else ft.Container(height=0),
                                        ft.Row([
                                            ft.Container(
                                                content=ft.Text(aufgabe.prioritaet, size=14, color=ft.Colors.WHITE),
                                                bgcolor=prioritaet_farbe,
                                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                                border_radius=4
                                            ),
                                            ft.Text(
                                                f"Fällig: {aufgabe.faelligkeitsdatum}" if aufgabe.faelligkeitsdatum else "",
                                                size=14,
                                                color=ft.Colors.RED if aufgabe.ist_ueberfaellig() else ft.Colors.GREY
                                            )
                                        ], spacing=10)
                                    ], spacing=5),
                                    expand=True
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=ft.Colors.RED,
                                    on_click=aufgabe_loeschen
                                )
                            ])
                        ]),
                        padding=10,
                        bgcolor=card_farbe
                    )
                )
                aufgaben_list.controls.append(aufgabe_card)
        
        page.update()
    

    def aktualisiere_kalender():
        kalender_content.controls.clear()
        heute = date.today()
        kalender_content.controls.append(
            ft.Text(f"Überfällige, sowie die ab heute bis Ende nächsten Monat fällig werdenden Aufgaben", size=24, weight=ft.FontWeight.BOLD)
        )
        
        monatliche_aufgaben = []
        for modul in app.module:
            for aufgabe in modul.aufgaben:
                if aufgabe.faelligkeitsdatum:
                    try:
                        aufgabe_datum = datetime.fromisoformat(aufgabe.faelligkeitsdatum).date()
                        if (aufgabe_datum.month == heute.month and aufgabe_datum.year == heute.year and not aufgabe.erledigt or
                            aufgabe_datum.month == heute.month+1 and aufgabe_datum.year == heute.year and not aufgabe.erledigt or
                            aufgabe_datum.month < heute.month and not aufgabe.erledigt):
                            monatliche_aufgaben.append((aufgabe_datum, aufgabe, modul))
                    except:
                        continue
                    
        monatliche_aufgaben.sort(key=lambda x: x[0])
        
        if not monatliche_aufgaben:
            kalender_content.controls.append(ft.Text("Keine offenen Aufgaben ab heute bis Ende des nächsten Monates", italic=True))
        else:
            for aufgabe_datum, aufgabe, modul in monatliche_aufgaben:
                ist_heute = aufgabe_datum == heute
                ist_ueberfaellig = aufgabe_datum < heute and not aufgabe.erledigt
                
                card_farbe = None
                if ist_heute:
                    card_farbe = ft.Colors.BLUE_50
                elif ist_ueberfaellig:
                    card_farbe = ft.Colors.RED_50

                termin_card = ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Text(str(f"{aufgabe_datum.day}.{aufgabe_datum.month}."), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                width=75,
                                height=50,
                                #bgcolor=modul.farbe,
                                bgcolor=ft.Colors.with_opacity(0.5, modul.farbe),
                                border_radius=25,
                                alignment=ft.alignment.center
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(aufgabe.titel, size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Modul: {modul.name}", size=14, color=modul.farbe),
                                    ft.Text(
                                        "Heute!" if ist_heute else "Überfällig!" if ist_ueberfaellig else "",
                                        size=14,
                                        color=ft.Colors.RED if ist_ueberfaellig else ft.Colors.BLUE
                                    )
                                ], spacing=5),
                                expand=True,
                                padding=ft.padding.only(left=15)
                            )
                        ]),
                        padding=10,
                        bgcolor=card_farbe
                    )
                )
                kalender_content.controls.append(termin_card)
        
        page.update()
    
    def aktualisiere_dashboard():
        dashboard_content.controls.clear()
        
        dashboard_content.controls.append(
            ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD)
        )
        
        if not app.module:
            dashboard_content.controls.append(ft.Text("Noch keine Module vorhanden", italic=True))
            page.update()
            return
        
        gesamt_aufgaben = sum(len(modul.aufgaben) for modul in app.module)
        gesamt_erledigt = sum(sum(1 for a in modul.aufgaben if a.erledigt) for modul in app.module)
        gesamt_ueberfaellig = sum(sum(1 for a in modul.aufgaben if a.ist_ueberfaellig()) for modul in app.module)
        
        stats_row = ft.Row([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Gesamt Aufgaben", size=12, opacity=0.7),
                        ft.Text(str(gesamt_aufgaben), size=32, weight=ft.FontWeight.BOLD)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=20,
                    bgcolor=ft.Colors.BLUE_50,
                    width=150,
                    height=100
                )
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Erledigt", size=12, opacity=0.7),
                        ft.Text(str(gesamt_erledigt), size=32, weight=ft.FontWeight.BOLD)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=20,
                    bgcolor=ft.Colors.GREEN_50,
                    width=150,
                    height=100
                )
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Überfällig", size=12, opacity=0.7),
                        ft.Text(str(gesamt_ueberfaellig), size=32, weight=ft.FontWeight.BOLD)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=20,
                    bgcolor=ft.Colors.RED_50,
                    width=150,
                    height=100
                )
            )
        ], spacing=20)
        dashboard_content.controls.append(stats_row)
        
        dashboard_content.controls.append(
            ft.Container(
                content=ft.Text("Fortschritt pro Modul", size=18, weight=ft.FontWeight.BOLD),
                margin=ft.margin.only(top=10, bottom=10)
            )
        )

        for modul in app.module:
            fortschritt = modul.get_fortschritt()
            aufgaben_anzahl = len(modul.aufgaben)
            erledigte_anzahl = sum(1 for a in modul.aufgaben if a.erledigt)
            
            modul_progress = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(modul.name, size=16, weight=ft.FontWeight.BOLD, expand=True),
                            ft.Text(f"{erledigte_anzahl}/{aufgaben_anzahl} ({int(fortschritt*100)}%)", size=14)
                        ]),
                        ft.ProgressBar(value=fortschritt, color=modul.farbe, height=12)
                    ], spacing=10),
                    padding=15
                )
            )
            dashboard_content.controls.append(modul_progress)
        
        page.update()
    
    def ansicht_wechseln(neue_ansicht: str):
        app.aktuelle_ansicht = neue_ansicht
        
        if neue_ansicht == "module":
            content_area.content = ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Module", size=24, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton("Neues Modul", icon=ft.Icons.ADD, on_click=modul_hinzufuegen_dialog)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Container(module_list, expand=True)
                    ]),
                    width=400,
                    padding=10
                ),
                ft.VerticalDivider(),
                ft.Container(
                    content=aufgaben_list,
                    expand=True,
                    padding=10
                )
            ], expand=True)
        elif neue_ansicht == "kalender":
            aktualisiere_kalender()
            content_area.content = kalender_content
        elif neue_ansicht == "dashboard":
            aktualisiere_dashboard()
            content_area.content = dashboard_content
        
        page.update()
    
    def csv_exportieren(e):
        datei_name = app.export_csv()
        if datei_name:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Daten erfolgreich exportiert nach: {datei_name}"))
            page.snack_bar.open = True
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Fehler beim Export"))
            page.snack_bar.open = True
 
        page.overlay.append(page.snack_bar)        
        page.snack_bar.open = True
        page.update()

    # Block 6: Keyboard Shortcuts
    def handle_keyboard(e: ft.KeyboardEvent):
        if e.ctrl:
            if e.key == "N":  # Ctrl+N für neues Modul
                modul_hinzufuegen_dialog()
            elif e.key == "E":  # Ctrl+E für Export
                csv_exportieren(e)
            elif e.key == "S":  # Ctrl+S für Speichern
                app.daten_speichern()
                page.snack_bar = ft.SnackBar(ft.Text("Daten gespeichert"))
                page.overlay.append(page.snack_bar)
                page.snack_bar.open = True
                page.update()
    
    page.on_keyboard_event = handle_keyboard
    
    # Navigation Tabs (Block 4: Zwischen Ansichten wechseln)
    tabs = ft.Tabs(
        selected_index=0,
        on_change=lambda e: ansicht_wechseln(["module", "kalender", "dashboard"][e.control.selected_index]),
        tabs=[
            ft.Tab(text="Module", icon=ft.Icons.SCHOOL),
            ft.Tab(text="Kalender", icon=ft.Icons.CALENDAR_MONTH),
            ft.Tab(text="Dashboard", icon=ft.Icons.DASHBOARD)
        ]
    )
    
    # Block 6: Menüleiste mit Export
    menubar = ft.Row([
        tabs,
        ft.ElevatedButton(
            "CSV Export",
            icon=ft.Icons.DOWNLOAD,
            on_click=csv_exportieren
        )
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    # Hauptinhalt
    content_area = ft.Container(expand=True)
    
    # Hauptlayout
    page.add(
        ft.Column([
            menubar,
            ft.Divider(),
            content_area
        ], expand=True)
    )
    
    # Initiale Ansicht laden
    aktualisiere_module_liste()
    ansicht_wechseln("module")


if __name__ == "__main__":
    #ft.app(target=main)                                 # startet als Desktop App (getestet auf MacOS)
    #ft.app(target=main, view=ft.AppView.FLET_APP)       # startet als Desktop App (getestet auf MacOS)
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)    # Startet im System-Webbrowser (getestet auf MacOS)
