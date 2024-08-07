import requests
from mwrogue.esports_client import EsportsClient
import urllib.request
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
from matplotlib.colors import Normalize
from io import BytesIO
import pkg_resources
site = EsportsClient("lol")
# Création des fonctions (moches) pour pouvoir tout faire (balec en gros)
def separe_role(liste_string):
    top, jng, mid, adc , supp = liste_string.split(",")
    return top, jng, mid, adc, supp

def heatmap_player(role, kill_x, kill_y, death_x, death_y, assist_x, assist_y, pos_x, pos_y):
    #img_filename = "assets/map_lolt.png"
    img_filename = pkg_resources.resource_filename('lol_analysis', 'assets/map_lolt.png')
    # Valeurs minimales et maximales pour les axes X et Y
    xmin, xmax = 0, 15000
    ymin, ymax = 0, 15000

    # Ajustez la résolution de la heatmap selon vos besoins
    heatmap_res = 30  # Résolution de la heatmap

    # Création d'une grille de points pour la heatmap
    heatmap_x = np.linspace(xmin, xmax, heatmap_res)
    heatmap_y = np.linspace(ymin, ymax, heatmap_res)
    heatmap_data = np.zeros((heatmap_res, heatmap_res))

    # Remplissage de la heatmap avec les valeurs de vos données
    for x, y in zip(kill_x[role] + death_x[role] + assist_x[role] + pos_x[role],
                    kill_y[role] + death_y[role] + assist_y[role] + pos_y[role]):
        x_idx = int(np.searchsorted(heatmap_x, x, side='left'))
        y_idx = int(np.searchsorted(heatmap_y, y, side='left'))
        if 0 <= x_idx < heatmap_res and 0 <= y_idx < heatmap_res:
            heatmap_data[y_idx, x_idx] += 1

    # Normaliser les valeurs de la heatmap entre 0 et 1
    norm = Normalize(vmin=0, vmax=np.max(heatmap_data))

    # Création du tracé avec une heatmap en fond
    fig, ax = plt.subplots()
    # response = requests.get(img_url)
    # img = plt.imread(BytesIO(response.content))
    # # Charger l'image depuis le répertoire courant
    img = plt.imread(cbook.get_sample_data(img_filename))

    # Afficher l'image en fond avec les limites spécifiées
    ax.imshow(img, extent=[xmin, xmax, ymin, ymax], aspect='auto', zorder=0)

    # Spécifier les couleurs manuellement pour les valeurs basses et hautes
    low_color = (0, 1, 0, 0)  # Noir transparent pour les valeurs basses
    high_color = (5, 0, 0, 5)  # Rouge opaque pour les valeurs hautes
    # Créer une colormap linéaire entre les couleurs spécifiées
    cmap = plt.matplotlib.colors.LinearSegmentedColormap.from_list('custom_colormap', [low_color, high_color], N=256)

    # Afficher la heatmap avec la colormap spécifiée et une interpolation bilinéaire
    cax = ax.imshow(heatmap_data, cmap=cmap, extent=[xmin, xmax, ymin, ymax], alpha=0.5, origin='lower', zorder=1, norm=norm, interpolation='bilinear')
    # Afficher les points des kill, des morts et des assist
    ax.scatter(kill_x[role], kill_y[role], color='red', label='Kill', s = 10)
    ax.scatter(death_x[role], death_y[role], color='black', label='Mort',s = 10)
    ax.scatter(assist_x[role], assist_y[role], color='green', label='Assist',s = 10)
    # Ajout de titres et d'étiquettes d'axes
    ax.set_title('Heatmap ' + str(role).lower())

    # Ajout d'une barre de couleur pour la heatmap
    cbar = fig.colorbar(cax, ax=ax, label='Fréquence')

    # Ajout de la légende en dehors du cadre en haut à gauche
    ax.legend(title='Statistiques', loc='upper left', bbox_to_anchor=(-0.5, 1))
    return plt

def search_game(team, side_hm, time, role_to_show):
  # Game Blue side
  response_blue = site.cargo_client.query(
      limit=100,
      tables="ScoreboardGames",
      fields = "Tournament, Team1 , Team2,RiotPlatformGameId,VOD,DateTime_UTC, GameId, Team1Dragons, Team1VoidGrubs, Team1RiftHeralds, Team1Barons, Team1Picks , Team1Bans, Team2Bans",
      where =  f"Team1 = '{team}' AND DateTime_UTC >= '2024-01-01 00:00:00'",
      order_by = "RiotGameId ASC"
  )
  #Game red side
  response_red = site.cargo_client.query(
      limit=100,
      tables="ScoreboardGames",
      fields = "Tournament, Team1 , Team2,RiotPlatformGameId,VOD,DateTime_UTC, GameId, Team2Dragons, Team2VoidGrubs, Team2RiftHeralds, Team2Barons, Team2Picks , Team2Bans, Team1Bans",
      where =  f"Team2 = '{team}' AND DateTime_UTC >= '2024-01-01 00:00:00'",
      order_by = "RiotGameId ASC"
  )
  # Mise en forme des données blueside
  game_blueside = pd.DataFrame(response_blue)
  game_blueside[["Team1Dragons","Team1VoidGrubs",'Team1Barons', 'Team1RiftHeralds']] = game_blueside[["Team1Dragons","Team1VoidGrubs",'Team1Barons', 'Team1RiftHeralds']].apply(pd.to_numeric)
  dragon_blueside = round(game_blueside["Team1Dragons"].mean(),2)
  grubs_blueside = round(game_blueside["Team1VoidGrubs"].mean(),2)
  herald_blueside = round(game_blueside["Team1RiftHeralds"].mean(),2)
  nashor_blueside = round(game_blueside["Team1Barons"].mean(),2)
  game_blueside[['TOP', 'JUNGLE', 'MID', 'ADC', 'SUPP']] = game_blueside['Team1Picks'].apply(separe_role).apply(pd.Series)
  # Mise en forme des données redside
  game_redside = pd.DataFrame(response_red)
  game_redside[["Team2Dragons","Team2VoidGrubs",'Team2Barons', 'Team2RiftHeralds']] = game_redside[["Team2Dragons","Team2VoidGrubs",'Team2Barons', 'Team2RiftHeralds']].apply(pd.to_numeric)
  dragon_redside = round(game_redside["Team2Dragons"].mean(),2)
  grubs_redside = round(game_redside["Team2VoidGrubs"].mean(),2)
  herald_redside = round(game_redside["Team2RiftHeralds"].mean(),2)
  nashor_redside = round(game_redside["Team2Barons"].mean(),2)
  game_redside[['TOP', 'JUNGLE', 'MID', 'ADC', 'SUPP']] = game_redside['Team2Picks'].apply(separe_role).apply(pd.Series)
  # Liste des matchs
  rgId = []
  side = []
  for game in response_red:
        rgId.append(game["RiotPlatformGameId"])
        side.append("red")
  for game in response_blue:
        rgId.append(game["RiotPlatformGameId"])
        side.append("blue")
  heatmap_1_x = []
  heatmap_1_y = []
  kill_x = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  kill_y = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  death_x = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  death_y = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  assist_x = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  assist_y = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  list_x_pos = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  list_y_pos = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  r_kill_x = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  r_kill_y = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  r_death_x = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  r_death_y = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  r_assist_x = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  r_assist_y = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  r_list_x_pos = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  r_list_y_pos = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  # Red side dict
  kill_x_15 = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  kill_y_15 = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  death_x_15 = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  death_y_15 = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  assist_x_15 = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  assist_y_15 = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  list_x_pos_15 = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  list_y_pos_15 = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  r_kill_x_15 = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  r_kill_y_15 = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  r_death_x_15 = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  r_death_y_15 = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  r_assist_x_15 = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  r_assist_y_15 = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  r_list_x_pos_15 = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  r_list_y_pos_15 = {"TOP" : [], "JUNGLE" : [], "MID" : [], "ADC" : [], "SUPP" : []}
  r_heatmap_1_x = []
  r_heatmap_1_y = []
  for game in range(len(rgId)):
      objectif = []
      monster_type = []
      data, timeline = site.get_data_and_timeline(rgId[game], version=5)
      blue_side = False
      for joueur in range(5):
          if side[game] == "blue":
              start = 1
          else:
              start = 6
          if joueur == 0:
              role = "TOP"
          if joueur == 1:
              role = "JUNGLE"
          if joueur == 2:
              role = "MID"
          if joueur == 3:
              role = "ADC"
          if joueur == 4:
              role = "SUPP"
          index_player = start + joueur
          timing_kill = []
          timing_death = []
          timing_assist = []
          match_detail_json = timeline
          if "frames" in match_detail_json:
              for frames in range(len(match_detail_json["frames"])):
                  if frames == 1:
                      if side[game] == "blue":
                          heatmap_1_x.append(match_detail_json["frames"][1]["participantFrames"][str(index_player)]["position"]["x"])
                          heatmap_1_y.append(match_detail_json["frames"][1]["participantFrames"][str(index_player)]["position"]["y"])
                      else:
                          r_heatmap_1_x.append(match_detail_json["frames"][1]["participantFrames"][str(index_player)]["position"]["x"])
                          r_heatmap_1_y.append(match_detail_json["frames"][1]["participantFrames"][str(index_player)]["position"]["y"])
                  if side[game] == "blue":
                      list_x_pos[role].append(match_detail_json["frames"][frames]["participantFrames"][str(index_player)]["position"]["x"])
                      list_y_pos[role].append(match_detail_json["frames"][frames]["participantFrames"][str(index_player)]["position"]["y"])
                      if frames < 16 :
                          list_x_pos_15[role].append(match_detail_json["frames"][frames]["participantFrames"][str(index_player)]["position"]["x"])
                          list_y_pos_15[role].append(match_detail_json["frames"][frames]["participantFrames"][str(index_player)]["position"]["y"])
                  else:
                      r_list_x_pos[role].append(match_detail_json["frames"][frames]["participantFrames"][str(index_player)]["position"]["x"])
                      r_list_y_pos[role].append(match_detail_json["frames"][frames]["participantFrames"][str(index_player)]["position"]["y"])
                      if frames < 16 :
                          r_list_x_pos_15[role].append(match_detail_json["frames"][frames]["participantFrames"][str(index_player)]["position"]["x"])
                          r_list_y_pos_15[role].append(match_detail_json["frames"][frames]["participantFrames"][str(index_player)]["position"]["y"])
                  for event in match_detail_json["frames"][frames]["events"]:
                      if "position" in event:
                          if event["type"] == "CHAMPION_KILL":
                              if "killerId" in event:
                                  if event["killerId"] == index_player:
                                      timing_kill.append(event["timestamp"]/1000)
                                      if side[game] == "blue":
                                          kill_x[role].append(event["position"]["x"])
                                          kill_y[role].append(event["position"]["y"])
                                      else:
                                          r_kill_x[role].append(event["position"]["x"])
                                          r_kill_y[role].append(event["position"]["y"])
                                      if frames < 16 :
                                          if side[game] == "blue":
                                              kill_x_15[role].append(event["position"]["x"])
                                              kill_y_15[role].append(event["position"]["y"])
                                          else:
                                              r_kill_x_15[role].append(event["position"]["x"])
                                              r_kill_y_15[role].append(event["position"]["y"])
                              if "victimId" in event:
                                  if event["victimId"] == index_player:
                                      timing_death.append(event["timestamp"]/1000)
                                      if side[game] == "blue":
                                          death_x[role].append(event["position"]["x"])
                                          death_y[role].append(event["position"]["y"])
                                      else:
                                          r_death_x[role].append(event["position"]["x"])
                                          r_death_y[role].append(event["position"]["y"])
                                      if frames < 16 :
                                          if side[game] == "blue":
                                              death_x_15[role].append(event["position"]["x"])
                                              death_y_15[role].append(event["position"]["y"])
                                          else:
                                              r_death_x_15[role].append(event["position"]["x"])
                                              r_death_y_15[role].append(event["position"]["y"])
                              if "assistingParticipantIds" in event:
                                  if index_player in event["assistingParticipantIds"]:
                                      timing_assist.append(event["timestamp"]/1000)
                                      if side[game] == "blue":
                                          assist_x[role].append(event["position"]["x"])
                                          assist_y[role].append(event["position"]["y"])
                                      else:
                                          r_assist_x[role].append(event["position"]["x"])
                                          r_assist_y[role].append(event["position"]["y"])
                                      if frames < 16 :
                                          if side[game] == "blue":
                                              assist_x_15[role].append(event["position"]["x"])
                                              assist_y_15[role].append(event["position"]["y"])
                                          else:
                                              r_assist_x_15[role].append(event["position"]["x"])
                                              r_assist_y_15[role].append(event["position"]["y"])
  if side_hm == "blue":
    if time == "15":
      plot = heatmap_player(role_to_show, kill_x_15, kill_y_15, death_x_15, death_y_15, assist_x_15, assist_y_15, list_x_pos_15, list_y_pos_15)
    if time == "all":
      plot = heatmap_player(role_to_show, kill_x, kill_y, death_x, death_y, assist_x, assist_y, list_x_pos, list_y_pos)
  if side_hm == "red":
    if time == "15":
      plot = heatmap_player(role_to_show, r_kill_x_15, r_kill_y_15, r_death_x_15, r_death_y_15, r_assist_x_15, r_assist_y_15, r_list_x_pos_15, r_list_y_pos_15)
    if time == "all":
      plot = heatmap_player(role_to_show, r_kill_x, r_kill_y, r_death_x, r_death_y, r_assist_x, r_assist_y, r_list_x_pos, r_list_y_pos)
  return plot, game_blueside[role_to_show].value_counts(), game_redside[role_to_show].value_counts()
# Exemple de données (remplir avec vos propres données)

# Affichage du plot
#plt.show()
#b_list_x_pos_15
