import os
import threading
import urllib.parse
import webbrowser
from tkinter import messagebox
import customtkinter as ctk

from src.config import caminho_recurso, carregar_token, salvar_token
from src.tunnel import TunnelManager


class TokenModal(ctk.CTkToplevel):
    """Janela flutuante para configurar e salvar o AuthToken do Ngrok."""

    def __init__(self, parent, token_atual: str, callback_salvar):
        super().__init__(parent)
        self.title("Configurar AuthToken")
        self.geometry("400x210")
        self.resizable(False, False)
        self.configure(fg_color="#0F172A")
        self.callback_salvar = callback_salvar

        self.transient(parent)
        self.grab_set()

        caminho_ico = caminho_recurso(os.path.join("assets", "icone.ico"))
        if os.path.exists(caminho_ico):
            self.after(200, lambda: self.iconbitmap(caminho_ico))

        ctk.CTkLabel(
            self,
            text="Ngrok AuthToken",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#F8FAFC",
        ).pack(anchor="w", padx=24, pady=(20, 4))

        ctk.CTkLabel(
            self,
            text="Cole seu token obtido em dashboard.ngrok.com:",
            font=ctk.CTkFont(size=12),
            text_color="#94A3B8",
        ).pack(anchor="w", padx=24, pady=(0, 12))

        self.entry_token = ctk.CTkEntry(
            self,
            placeholder_text="2xYz...",
            height=38,
            fg_color="#1E293B",
            border_color="#334155",
            font=ctk.CTkFont(family="Consolas", size=13),
            show="*",
        )
        if token_atual:
            self.entry_token.insert(0, token_atual)
        self.entry_token.pack(fill="x", padx=24, pady=(0, 16))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24)

        self.btn_mostrar = ctk.CTkButton(
            btn_frame,
            text="Mostrar",
            width=80,
            height=34,
            fg_color="#334155",
            hover_color="#475569",
            command=self.alternar_visibilidade,
        )
        self.btn_mostrar.pack(side="left")

        ctk.CTkButton(
            btn_frame,
            text="Salvar Token",
            width=120,
            height=34,
            fg_color="#10B981",
            hover_color="#059669",
            font=ctk.CTkFont(weight="bold"),
            command=self.salvar,
        ).pack(side="right")

    def alternar_visibilidade(self):
        if self.entry_token.cget("show") == "*":
            self.entry_token.configure(show="")
            self.btn_mostrar.configure(text="Ocultar")
        else:
            self.entry_token.configure(show="*")
            self.btn_mostrar.configure(text="Mostrar")

    def salvar(self):
        novo_token = self.entry_token.get().strip()
        self.callback_salvar(novo_token)
        self.destroy()


class NgrokDarkApp(ctk.CTk):
    """Janela principal do gerenciador de túneis."""

    def __init__(self):
        super().__init__()

        self.title("WELLCATech • Ngrok Tunnel Manager")
        self.geometry("470x500")
        self.resizable(False, False)
        self.configure(fg_color="#0F172A")

        caminho_ico = caminho_recurso(os.path.join("assets", "icone.ico"))
        if os.path.exists(caminho_ico):
            self.iconbitmap(caminho_ico)

        self.tunnel_manager = TunnelManager()
        self.auth_token = carregar_token()

        self._construir_interface()
        self._atualizar_cor_botao_token()

    def _construir_interface(self):
        # --- Cabeçalho ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=25, pady=(20, 10))

        self.lbl_titulo = ctk.CTkLabel(
            self.header_frame,
            text="Ngrok Remote Bridge",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#F8FAFC",
        )
        self.lbl_titulo.pack(side="left")

        right_header = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        right_header.pack(side="right")

        self.btn_token = ctk.CTkButton(
            right_header,
            text="⚙ Token",
            width=72,
            height=26,
            corner_radius=13,
            fg_color="#1E293B",
            hover_color="#334155",
            border_width=1,
            border_color="#334155",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.abrir_modal_token,
        )
        self.btn_token.pack(side="left", padx=(0, 8))

        self.status_badge = ctk.CTkFrame(
            right_header, fg_color="#1E293B", corner_radius=20
        )
        self.status_badge.pack(side="right")

        self.lbl_status_dot = ctk.CTkLabel(
            self.status_badge,
            text="●",
            font=ctk.CTkFont(size=14),
            text_color="#64748B",
        )
        self.lbl_status_dot.pack(side="left", padx=(10, 4), pady=2)

        self.lbl_status_text = ctk.CTkLabel(
            self.status_badge,
            text="OFFLINE",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94A3B8",
        )
        self.lbl_status_text.pack(side="right", padx=(0, 12), pady=2)

        # --- Card de Configuração ---
        self.card_config = ctk.CTkFrame(
            self,
            fg_color="#1E293B",
            corner_radius=12,
            border_width=1,
            border_color="#334155",
        )
        self.card_config.pack(fill="x", padx=25, pady=8)

        self.card_config.grid_columnconfigure(0, weight=1)
        self.card_config.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.card_config,
            text="PROTOCOLO",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94A3B8",
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(14, 4))

        ctk.CTkLabel(
            self.card_config,
            text="PORTA LOCAL",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94A3B8",
        ).grid(row=0, column=1, sticky="w", padx=18, pady=(14, 4))

        self.combo_proto = ctk.CTkSegmentedButton(
            self.card_config,
            values=["tcp", "http"],
            selected_color="#2563EB",
            selected_hover_color="#1D4ED8",
            unselected_color="#0F172A",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.combo_proto.set("tcp")
        self.combo_proto.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 16))

        self.entry_porta = ctk.CTkEntry(
            self.card_config,
            placeholder_text="37840",
            height=32,
            fg_color="#0F172A",
            border_color="#334155",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            justify="center",
        )
        self.entry_porta.insert(0, "37840")
        self.entry_porta.grid(row=1, column=1, sticky="ew", padx=18, pady=(0, 16))

        # --- Botão Principal ---
        self.btn_acao = ctk.CTkButton(
            self,
            text="INICIAR CONEXÃO",
            height=44,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.alternar_conexao,
        )
        self.btn_acao.pack(fill="x", padx=25, pady=(6, 12))

        # --- Card de Saída e Compartilhamento ---
        self.card_output = ctk.CTkFrame(
            self,
            fg_color="#1E293B",
            corner_radius=12,
            border_width=1,
            border_color="#334155",
        )
        self.card_output.pack(fill="x", padx=25, pady=(0, 20))

        ctk.CTkLabel(
            self.card_output,
            text="ENDEREÇO PARA O CLIENTE",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94A3B8",
        ).pack(anchor="w", padx=18, pady=(14, 6))

        self.entry_endereco = ctk.CTkEntry(
            self.card_output,
            height=40,
            fg_color="#0F172A",
            border_color="#334155",
            text_color="#64748B",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            justify="center",
        )
        self.entry_endereco.insert(0, "Aguardando ativação do túnel...")
        self.entry_endereco.configure(state="readonly")
        self.entry_endereco.pack(fill="x", padx=18, pady=(0, 12))

        ctk.CTkLabel(
            self.card_output,
            text="WHATSAPP DO CLIENTE (OPCIONAL - COM DDD)",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#94A3B8",
        ).pack(anchor="w", padx=18, pady=(2, 4))

        self.entry_whatsapp = ctk.CTkEntry(
            self.card_output,
            placeholder_text="Ex: 21999998888 (deixe vazio para escolher na hora)",
            height=34,
            fg_color="#0F172A",
            border_color="#334155",
            font=ctk.CTkFont(size=12),
        )
        self.entry_whatsapp.pack(fill="x", padx=18, pady=(0, 14))

        actions_frame = ctk.CTkFrame(self.card_output, fg_color="transparent")
        actions_frame.pack(fill="x", padx=18, pady=(0, 16))
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)

        self.btn_copiar = ctk.CTkButton(
            actions_frame,
            text="Copiar Endereço",
            height=38,
            corner_radius=8,
            fg_color="#334155",
            hover_color="#475569",
            state="disabled",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.copiar_endereco,
        )
        self.btn_copiar.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.btn_zap = ctk.CTkButton(
            actions_frame,
            text="Enviar WhatsApp",
            height=38,
            corner_radius=8,
            fg_color="#334155",
            hover_color="#475569",
            state="disabled",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.enviar_whatsapp,
        )
        self.btn_zap.grid(row=0, column=1, sticky="ew", padx=(6, 0))

    # --- Gerenciamento do Token ---
    def _ao_salvar_token(self, token: str):
        self.auth_token = token
        salvar_token(token)
        self.tunnel_manager.definir_token(token)
        self._atualizar_cor_botao_token()

    def _atualizar_cor_botao_token(self):
        if self.auth_token:
            self.btn_token.configure(text="⚙ Token ✓", text_color="#10B981")
        else:
            self.btn_token.configure(text="⚙ Token !", text_color="#F59E0B")

    def abrir_modal_token(self):
        TokenModal(self, self.auth_token, self._ao_salvar_token)

    # --- Controle de Conexão ---
    def alternar_conexao(self):
        if self.tunnel_manager.tunel_ativo is None:
            porta = self.entry_porta.get().strip()
            if not porta.isdigit():
                messagebox.showerror(
                    "Porta Inválida", "Digite apenas números na porta local."
                )
                return

            self.btn_acao.configure(state="disabled", text="CONECTANDO...")
            self.lbl_status_dot.configure(text_color="#F59E0B")
            self.lbl_status_text.configure(
                text="CONECTANDO", text_color="#F59E0B"
            )

            threading.Thread(
                target=self._thread_conectar,
                args=(int(porta), self.combo_proto.get()),
                daemon=True,
            ).start()
        else:
            self.parar_conexao()

    def _thread_conectar(self, porta: int, protocolo: str):
        try:
            endereco = self.tunnel_manager.conectar(
                porta=porta, protocolo=protocolo, token=self.auth_token
            )
            self.after(0, self._atualizar_ui_conectado, endereco)
        except Exception as e:
            self.after(0, self._atualizar_ui_erro, str(e))

    def _atualizar_ui_conectado(self, endereco: str):
        self.entry_endereco.configure(
            state="normal", text_color="#10B981", border_color="#10B981"
        )
        self.entry_endereco.delete(0, "end")
        self.entry_endereco.insert(0, endereco)
        self.entry_endereco.configure(state="readonly")

        self.lbl_status_dot.configure(text_color="#10B981")
        self.lbl_status_text.configure(text="ONLINE", text_color="#10B981")

        self.btn_acao.configure(
            state="normal",
            text="ENCERRAR CONEXÃO",
            fg_color="#DC2626",
            hover_color="#B91C1C",
        )
        self.btn_copiar.configure(
            state="normal", fg_color="#2563EB", hover_color="#1D4ED8"
        )
        self.btn_zap.configure(
            state="normal", fg_color="#16A34A", hover_color="#15803D"
        )

        self.entry_porta.configure(state="disabled")
        self.combo_proto.configure(state="disabled")
        self.copiar_endereco()

    def _atualizar_ui_erro(self, erro: str):
        messagebox.showerror(
            "Erro no Ngrok",
            f"Falha ao abrir túnel:\n{erro}\n\nVerifique seu AuthToken no botão '⚙ Token'.",
        )
        self.parar_conexao()

    def parar_conexao(self):
        self.tunnel_manager.desconectar()

        self.entry_endereco.configure(
            state="normal", text_color="#64748B", border_color="#334155"
        )
        self.entry_endereco.delete(0, "end")
        self.entry_endereco.insert(0, "Conexão encerrada.")
        self.entry_endereco.configure(state="readonly")

        self.lbl_status_dot.configure(text_color="#64748B")
        self.lbl_status_text.configure(text="OFFLINE", text_color="#94A3B8")

        self.btn_acao.configure(
            state="normal",
            text="INICIAR CONEXÃO",
            fg_color="#2563EB",
            hover_color="#1D4ED8",
        )
        self.btn_copiar.configure(
            state="disabled",
            text="Copiar Endereço",
            fg_color="#334155",
            hover_color="#475569",
        )
        self.btn_zap.configure(
            state="disabled",
            fg_color="#334155",
            hover_color="#475569",
        )
        self.entry_porta.configure(state="normal")
        self.combo_proto.configure(state="normal")

    # --- Ações de Compartilhamento ---
    def copiar_endereco(self):
        endereco = self.entry_endereco.get()
        if (
            endereco
            and "Aguardando" not in endereco
            and "encerrada" not in endereco
        ):
            self.clipboard_clear()
            self.clipboard_append(endereco)
            self.update()
            self.btn_copiar.configure(text="✓ Copiado!")
            self.after(
                2000, lambda: self.btn_copiar.configure(text="Copiar Endereço")
            )

    def enviar_whatsapp(self):
        endereco = self.entry_endereco.get()
        if (
            not endereco
            or "Aguardando" in endereco
            or "encerrada" in endereco
        ):
            return

        mensagem = (
            "Olá! Segue o endereço para conexão remota:\n\n"
            f"*{endereco}*\n\n"
            "Basta colar no programa e clicar em conectar."
        )
        texto_codificado = urllib.parse.quote(mensagem)

        telefone = "".join(filter(str.isdigit, self.entry_whatsapp.get()))

        if telefone:
            if len(telefone) in (10, 11):
                telefone = "55" + telefone
            url = f"https://api.whatsapp.com/send?phone={telefone}&text={texto_codificado}"
        else:
            url = f"https://api.whatsapp.com/send?text={texto_codificado}"

        webbrowser.open(url)