#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Framework SPHY - Interface de Ingestão Visual
Script: Seletor e Conversor Gráfico de Datasets SPARC
Autor: Deywe Okabe
Organização: Black Swan Research / Harpia Quantum
Ambiente: Windows Local (UI Nativa)
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import pandas as pd

def processar_e_salvar(caminho_arquivo):
    """
    Executa o motor de parsing do SPARC e exporta o payload SPHY plano.
    """
    try:
        nome_arquivo = os.path.basename(caminho_arquivo)
        # Extrai o nome da galáxia isolando o sufixo _rotmod.dat
        nome_galaxia = nome_arquivo.replace("_rotmod.dat", "").replace(".dat", "")
        
        col_raio, col_vobs, col_vgas, col_vdisk, col_vbulge = [], [], [], [], []
        
        with open(caminho_arquivo, 'r') as f:
            for linha in f:
                linha_limpa = linha.strip()
                if linha_limpa.startswith('#') or not linha_limpa:
                    continue
                
                partes = linha_limpa.split()
                if len(partes) >= 5:
                    col_raio.append(float(partes[0]))
                    col_vobs.append(float(partes[1]))
                    col_vgas.append(float(partes[3]))
                    col_vdisk.append(float(partes[4]))
                    
                    if len(partes) >= 6:
                        col_vbulge.append(float(partes[5]))
                    else:
                        col_vbulge.append(0.0)

        # Matrizes do espaço de fase
        r = np.array(col_raio)
        v_obs = np.array(col_vobs)
        v_gas = np.array(col_vgas)
        v_disk = np.array(col_vdisk)
        v_bulge = np.array(col_vbulge)

        # Filtro de ruído clássico negativo
        v_gas[v_gas < 0] = 0.0
        v_disk[v_disk < 0] = 0.0
        v_bulge[v_bulge < 0] = 0.0

        # Composição do tensor bariônico visível
        v_barionica = np.sqrt(v_gas**2 + v_disk**2 + v_bulge**2)

        # Criação do DataFrame padrão SPHY
        df_csv = pd.DataFrame({
            'raio': r,
            'v_barionica': v_barionica,
            'v_observada': v_obs
        })

        # Define a pasta de saída como a mesma onde a API procura os arquivos
        diretorio_saida = os.path.dirname(caminho_arquivo)
        caminho_saida = os.path.join(diretorio_saida, f"{nome_galaxia}_pronto_sphy.csv")
        
        df_csv.to_csv(caminho_saida, index=False)
        
        messagebox.showinfo(
            "Sucesso Cosmológico", 
            f"Galáxia: {nome_galaxia}\n\n"
            f"✓ CSV gerado com {len(df_csv)} pontos de dados!\n"
            f"Saved em: {caminho_saida}\n\n"
            f"Pronto para arrastar para a API do Streamlit."
        )
        
    except Exception as e:
        messagebox.showerror("Erro de Tensor", f"Falha crítica ao processar o arquivo:\n{str(e)}")

def abrir_janela_selecao():
    """
    Instancia a interface gráfica oculta do Tkinter e abre o seletor de arquivos do Windows.
    """
    root = tk.Tk()
    root.withdraw() # Oculta a janela principal vazia do Tkinter
    
    # Configura os filtros de arquivos na janela do Windows
    tipos_arquivos = [("Arquivos SPARC Dat", "*_rotmod.dat"), ("Todos os Arquivos Dat", "*.dat"), ("Arquivos de Texto", "*.txt")]
    
    caminho_selecionado = filedialog.askopenfilename(
        title="SPHY Core - Selecionar Galáxia do Catálogo SPARC",
        filetypes=tipos_arquivos
    )
    
    if caminho_selecionado:
        processar_e_salvar(caminho_selecionado)
    else:
        print("[*] Operação cancelada pelo usuário.")

if __name__ == "__main__":
    abrir_janela_selecao()