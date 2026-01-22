import flet as ft
import logging
import re

# --- 1. CONFIGURAÇÃO DE LOGS ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def main(page: ft.Page):
    # --- CONFIGURAÇÕES DA TELA ---
    page.title = "Resultadoreal Player Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0 
    page.spacing = 0
    page.bgcolor = "#000000"
    page.window_width = 390
    page.window_height = 844

    # --- 2. PALETA DE CORES ---
    COR_ROSA = "#FF007F"
    COR_BRANCA = "#FFFFFF"
    COR_CINZA_ESCURO = "#1C1C1C"
    COR_AZUL_TREINO = ft.colors.BLUE_GREY_700 
    
    # --- 3. DADOS E LINKS ---
    def converter_link_google(url_original):
        if "drive.google.com" in url_original:
            padrao_id = r"/d/([a-zA-Z0-9_-]+)"
            match = re.search(padrao_id, url_original)
            if match:
                file_id = match.group(1)
                return f"https://drive.google.com/uc?export=download&id={file_id}"
        return url_original

    # ==============================================================================
    # SEUS LINKS
    # ==============================================================================
    lista_cardio_bruta = [
        {"titulo": "AQUECIMENTO CARDIO", "url": "https://drive.google.com/file/d/1Y5riqZmYZLOJLMDrnKw0DeyEptcBIhH4/view?usp=sharing"}, 
        {"titulo": "CORRIDA RITMADA", "url": "https://drive.google.com/file/d/123zFR0UL-EI-RCBLsh5uaqbzwXa5PYzQ/view?usp=drive_link"},
    ]

    lista_treino_bruta = [
        {"titulo": "TREINO PESADO 1", "url": "https://drive.google.com/file/d/1afJvd4PK0x1D6uKR6MsZoGb_J8QTla6R/view?usp=drive_link"},
        {"titulo": "FOCO TOTAL", "url": "https://drive.google.com/file/d/1CF0m5HcD-N0t1qyPfS48KrF5impe-Qm2/view?usp=drive_link"},
    ]

    def preparar_playlist(lista_bruta, nome_modo):
        lista_pronta = []
        for item in lista_bruta:
            lista_pronta.append({
                "titulo": item['titulo'],
                "artista": nome_modo,
                "src": converter_link_google(item['url'])
            })
        return lista_pronta

    playlist_cardio = preparar_playlist(lista_cardio_bruta, "MODO CARDIO")
    playlist_treino = preparar_playlist(lista_treino_bruta, "MODO TREINO")

    state = {
        "playlist": playlist_cardio,
        "index": 0,
        "tocando": False,
        "duracao": 0,
        "posicao": 0,
        "modo": "cardio"
    }

    # --- 4. ENGINE DE ÁUDIO ---
    audio_player = ft.Audio(src=state["playlist"][0]["src"], autoplay=False)
    page.overlay.append(audio_player)

    # --- 5. VISUAL UI ---

    # Badge
    txt_modo_badge = ft.Text("CARDIO", size=12, weight="bold", color=COR_ROSA)
    container_badge = ft.Container(
        content=txt_modo_badge,
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
        border=ft.border.all(1, COR_ROSA),
        border_radius=20
    )

    # Header OTIMIZADO (Logo maior)
    img_logo = ft.Image(src="/img/logo.png", height=100, fit=ft.ImageFit.CONTAIN) # Aumentei para 100
    
    header = ft.Container(
        content=ft.Column([
            ft.Container(height=10), # Espaço topo
            img_logo, 
            ft.Container(height=5),
            container_badge
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
        alignment=ft.alignment.center
    )

    # Capa
    icone_capa = ft.Icon(ft.icons.DIRECTIONS_RUN, size=80, color=COR_BRANCA)
    container_capa = ft.Container(
        content=icone_capa,
        width=220, height=220, # Levemente maior
        bgcolor=COR_ROSA,
        border_radius=20,
        alignment=ft.alignment.center,
        shadow=ft.BoxShadow(blur_radius=40, color=COR_ROSA),
        animate=ft.animation.Animation(400, "easeOut")
    )

    # Info
    txt_titulo = ft.Text(state["playlist"][0]["titulo"], size=24, weight="bold", color=COR_BRANCA, text_align="center", no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS)
    txt_artista = ft.Text(state["playlist"][0]["artista"], size=16, color=ft.colors.GREY_500)

    # Displays
    txt_min = ft.Text("00", size=20, weight="bold", color=COR_BRANCA)
    txt_seg = ft.Text("00", size=20, weight="bold", color=COR_BRANCA)

    slider = ft.Slider(min=0, max=1000, value=0, active_color=COR_ROSA, thumb_color=COR_ROSA, inactive_color=ft.colors.GREY_800, expand=True)

    # --- 6. FUNÇÕES LÓGICAS (MANTIDAS IGUAIS) ---
    def safe_convert(ms):
        try: return max(0, int(float(ms)))
        except: return 0

    def formatar_display(ms):
        seg_total = safe_convert(ms) // 1000
        txt_min.value = f"{seg_total // 60:02d}"
        txt_seg.value = f"{seg_total % 60:02d}"

    def update_ui(): page.update()

    def play_track(index_override=None):
        if index_override is not None: state["index"] = index_override
        track = state["playlist"][state["index"]]
        audio_player.src = track["src"]
        audio_player.autoplay = True
        audio_player.update()
        state["tocando"] = True
        txt_titulo.value = track["titulo"]
        txt_artista.value = track["artista"]
        btn_play.icon = ft.icons.PAUSE_CIRCLE_FILLED
        update_ui()

    def toggle_play_pause(e):
        if state["tocando"]:
            audio_player.pause()
            state["tocando"] = False
            btn_play.icon = ft.icons.PLAY_CIRCLE_FILL
        else:
            audio_player.resume()
            state["tocando"] = True
            btn_play.icon = ft.icons.PAUSE_CIRCLE_FILLED
        update_ui()

    def mudar_faixa(delta):
        audio_player.pause()
        novo_index = (state["index"] + delta) % len(state["playlist"])
        play_track(novo_index)

    def seek_audio(ms):
        ms = safe_convert(ms)
        if state["duracao"] > 0 and ms > state["duracao"]: ms = state["duracao"]
        state["posicao"] = ms
        audio_player.seek(ms)
        slider.value = ms
        formatar_display(ms)
        update_ui()

    def ajuste_fino(tipo, delta):
        atual = safe_convert(state["posicao"])
        novo = atual + (delta * 60 * 1000) if tipo == 'min' else atual + (delta * 1000)
        seek_audio(novo)

    # Eventos
    def on_duration(e):
        state["duracao"] = safe_convert(e.data)
        slider.max = state["duracao"]
        update_ui()

    def on_position(e):
        state["posicao"] = safe_convert(e.data)
        if state["posicao"] <= slider.max:
            slider.value = state["posicao"]
            formatar_display(state["posicao"])
            update_ui()

    audio_player.on_duration_changed = on_duration
    audio_player.on_position_changed = on_position
    slider.on_change = lambda e: formatar_display(e.control.value) or update_ui()
    slider.on_change_end = lambda e: seek_audio(e.control.value)

    def set_modo(e, modo_alvo):
        audio_player.pause()
        state["tocando"] = False
        state["index"] = 0
        state["posicao"] = 0
        btn_play.icon = ft.icons.PLAY_CIRCLE_FILL
        slider.value = 0
        formatar_display(0)

        if modo_alvo == "cardio":
            state["playlist"] = playlist_cardio
            state["modo"] = "cardio"
            tema, icone = COR_ROSA, ft.icons.DIRECTIONS_RUN
            btn_cardio.style = style_btn_ativo_rosa
            btn_treino.style = style_btn_inativo_branco
        else:
            state["playlist"] = playlist_treino
            state["modo"] = "treino"
            tema, icone = COR_AZUL_TREINO, ft.icons.FITNESS_CENTER
            btn_cardio.style = style_btn_inativo_rosa
            btn_treino.style = style_btn_ativo_branco

        container_capa.bgcolor = tema
        container_capa.shadow.color = tema
        icone_capa.name = icone
        slider.active_color = tema
        slider.thumb_color = tema
        txt_modo_badge.value = modo_alvo.upper()
        txt_modo_badge.color = tema
        container_badge.border.color = tema

        track = state["playlist"][0]
        audio_player.src = track["src"]
        audio_player.update()
        txt_titulo.value = track["titulo"]
        txt_artista.value = track["artista"]
        update_ui()

    # --- 7. BOTÕES ---
    def btn_ajuste_factory(texto, func):
        return ft.Container(
            content=ft.Text(texto, size=18, weight="bold", color=COR_ROSA),
            width=40, height=40, bgcolor=ft.colors.WHITE10, # Aumentei um pouco o tamanho do toque
            border_radius=10, alignment=ft.alignment.center,
            on_click=func, ink=True
        )

    painel_precisao = ft.Row([
        ft.Row([btn_ajuste_factory("-", lambda e: ajuste_fino('min', -1)), txt_min, btn_ajuste_factory("+", lambda e: ajuste_fino('min', 1))], spacing=8),
        ft.Text(":", size=20, color=COR_BRANCA, weight="bold"),
        ft.Row([btn_ajuste_factory("-", lambda e: ajuste_fino('seg', -10)), txt_seg, btn_ajuste_factory("+", lambda e: ajuste_fino('seg', 10))], spacing=8),
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

    btn_prev = ft.IconButton(ft.icons.SKIP_PREVIOUS, icon_size=45, icon_color=COR_BRANCA, on_click=lambda e: mudar_faixa(-1))
    btn_play = ft.IconButton(ft.icons.PLAY_CIRCLE_FILL, icon_size=90, icon_color=COR_BRANCA, on_click=toggle_play_pause) # Play maior
    btn_next = ft.IconButton(ft.icons.SKIP_NEXT, icon_size=45, icon_color=COR_BRANCA, on_click=lambda e: mudar_faixa(1))

    style_btn_ativo_rosa = ft.ButtonStyle(bgcolor=COR_ROSA, color=COR_BRANCA, shape=ft.RoundedRectangleBorder(radius=10))
    style_btn_inativo_branco = ft.ButtonStyle(bgcolor=COR_BRANCA, color=COR_ROSA, shape=ft.RoundedRectangleBorder(radius=10))
    style_btn_ativo_branco = ft.ButtonStyle(bgcolor=COR_BRANCA, color=COR_AZUL_TREINO, shape=ft.RoundedRectangleBorder(radius=10))
    style_btn_inativo_rosa = ft.ButtonStyle(bgcolor=COR_ROSA, color=COR_BRANCA, shape=ft.RoundedRectangleBorder(radius=10))

    btn_cardio = ft.ElevatedButton("CARDIO", width=140, height=55, style=style_btn_ativo_rosa, on_click=lambda e: set_modo(e, "cardio"))
    btn_treino = ft.ElevatedButton("TREINO", width=140, height=55, style=style_btn_inativo_branco, on_click=lambda e: set_modo(e, "treino"))

    # --- 8. LAYOUT HARMÔNICO ---
    
    # Bloco Central: Agrupa tudo que é controle visual
    center_section = ft.Column([
        ft.Container(height=10), # Respiro logo x capa
        container_capa,
        ft.Container(height=15),
        txt_titulo,
        txt_artista,
        ft.Container(height=20),
        
        # Barra de Progresso
        ft.Container(content=slider, padding=ft.padding.symmetric(horizontal=25)),
        
        ft.Container(height=10),
        
        # Painel de Precisão
        painel_precisao,
        
        ft.Container(height=20), # Separação entre precisão e play
        
        # Botões de Play (BEM ALINHADOS)
        ft.Row([btn_prev, btn_play, btn_next], alignment=ft.MainAxisAlignment.CENTER),
        
        # --- AQUI ESTÁ O SEGREDO DA HARMONIA ---
        # Este Container "Expand" empurra tudo pra cima e deixa o espaço embaixo vazio
        ft.Container(expand=True), 
        
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0, expand=True)

    # Layout Principal
    main_layout = ft.Container(
        content=ft.Column([
            header,
            # O center section agora expande e ocupa o meio da tela, empurrando os botões de modo pro final
            ft.Container(content=center_section, expand=True, padding=ft.padding.only(bottom=20)),
            
            # Botões de Modo fixos lá embaixo
            ft.Container(
                content=ft.Row([btn_cardio, btn_treino], alignment=ft.MainAxisAlignment.CENTER), 
                padding=ft.padding.only(bottom=40, top=10)
            )
        ], spacing=0),
        gradient=ft.LinearGradient(begin=ft.alignment.top_center, end=ft.alignment.bottom_center, colors=[COR_CINZA_ESCURO, "#000000"]),
        expand=True
    )

    page.add(main_layout)

if __name__ == "__main__":
    # O segredo é o web_renderer=ft.WebRenderer.HTML
    ft.app(target=main, assets_dir="assets", web_renderer=ft.WebRenderer.HTML)