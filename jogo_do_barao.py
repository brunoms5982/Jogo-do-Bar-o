import pygame
import random
import time
from publish import p_publish
from paho.mqtt import client as mqtt_client

#Inicializa as constantes
pygame.init()
screen_width = 1600
screen_height = 900    
screen = pygame.display.set_mode((screen_width, screen_height))
font = pygame.font.Font('goudy_bookletter_1911.otf',36)
title_font = pygame.font.Font('AquilineTwo.ttf', 72)
blue = (0, 0, 255)
white = (255,255,255)
dark = (255,255,255)
green = (0,255,0)
brown = (150,75,0)
broker = 'labdigi.wiseful.com.br'
port = 80
topic = "grupo1-bancadaB4/Q1" # Questão
topic_B4 = "grupo1-bancadaB4/B4" #Publica as informações para ESP (Errou/Acertou)
topic_R1 = "grupo1-bancadaB4/R1" #Recebe resposta da ESP
# Gera ID do cliente
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'grupo1-bancadaB4'
password = 'digi#@1B4'
#Variáveis do jogo
question_number = 0 #Numero da questão
score = 0 # Placar/Numero da questão
help = 1 #Ajudas
bg = pygame.image.load("bg.png")
lastMsg = ""
#messages = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","32"]
messages = [1]
answered = 0
first = 1
lost = 0
win = 0
from questions import questions
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client
def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        global lastMsg
        global messages
        lastMsg = msg.payload.decode()
        #p_publish(client,"R",topic_B4) #Sinal de Reset do Jogo
        #p_publish(client,"I",topic_B4) #Sinal de Inicia do Jogo
        if (msg.topic == topic):
            q_number = int(lastMsg,2)
            if (messages.count(q_number)==0):
                    p_publish(client,"11",topic_B4) # Testada e Aprovada
                    messages.append(q_number)
            else:
                    p_publish(client,"10",topic_B4) # Testada e não aprovada
                    #p_publish(client,"R",topic_B4) #Sinal de Reset do Jogo
                    #p_publish(client,"I",topic_B4) #Sinal de Inicia do Jogos
                    
        if (msg.topic == topic_R1 and lastMsg!="-1"):
            check_answer(questions[int(messages[question_number])], int(lastMsg))
        print(messages)
    client.subscribe([(topic,0),(topic_R1,0)])
    client.on_message = on_message
client = connect_mqtt()
subscribe(client)
client.loop_start()

# Mostra as perguntas
def display_question(question):
    # Mostra a questão
    global score
    question_alt = str(score+1)+ ") " + question["question"]
    question_text = font.render(question_alt, True, white)
    question_rect = question_text.get_rect(center=(screen_width/2, screen_height/3))
    screen.blit(question_text, question_rect)

    # Mostra as respostas
    for i, answer in enumerate(question["answers"]):
        if (i == 0):
            answer_alt = "A) "+answer
        if (i == 1):
            answer_alt = "B) "+answer
        if (i == 2):
            answer_alt = "C) "+answer
        if (i == 3):
            answer_alt = "D) "+answer
        answer_text = font.render(answer_alt, True, white)
        answer_rect = answer_text.get_rect(center=(screen_width/2, screen_height/3 + 50 + i*50))
        screen.blit(answer_text, answer_rect)
        
running = True
# Checa se a questão está correta
def check_answer(question, answer):
    global score
    global question_number
    if answer == question["correct"]:
        score += 1
        if score == 8: #Acerta 8 e ganha o Jogo 
                print("Ganhou!")
                global win
                win = 1
        question_number += 1
        p_publish(client,"A",topic_B4) # Trocar por 1 (Sinaliza que Acertou )
        screen.blit(bg, (0, 0))
        title_text = title_font.render(f"Jogo do Barão", True, brown)
        title_rect = title_text.get_rect(center=(screen_width/2, 160))
        screen.blit(title_text, title_rect)
        return True
    else:
        p_publish(client,"E",topic_B4) # Sinaliza que Errou 
        #p_publish(client,"Reset",topic_B4) #  Sinaliza o Reset (depois do Errou)
        global lost
        lost = 1
        return False
    

# Início do Jogo
p_publish(client,"R",topic_B4) #Sinal de Reset do Jogo
p_publish(client,"I",topic_B4) #Sinal de Inicia do Jogopygame.mixer.init()
pygame.mixer.music.load("bach.mp3")
pygame.mixer.music.play(-1,0.0)
start_ticks=pygame.time.get_ticks() #starter tick
while running:
    #Menu de Inicializacao do Jogo
    while (first == 1):
        screen.blit(bg, (0, 0))
        pygame.display.flip()
        title_text = title_font.render(f"Jogo do Barão", True, brown)
        title_rect = title_text.get_rect(center=(screen_width/2, 150))
        screen.blit(title_text, title_rect)
        exp_text = font.render(f"Bem-vindo ao Jogo Do Barão!", True, dark)
        exp_rect = exp_text.get_rect(center=(screen_width/2, 370))
        screen.blit(exp_text, exp_rect) 
        exp1_text = font.render(f"O Barão concederá para aquele que acertar as suas 8 perguntas todo o seu poder e fortuna", True, dark)
        exp1_rect = exp1_text.get_rect(center=(screen_width/2, 410))
        screen.blit(exp1_text, exp1_rect)
        exp2_text = font.render(f"Será que você conseguirá impressioná-lo ?", True, dark)
        exp2_rect = exp2_text.get_rect(center=(screen_width/2, 450))
        screen.blit(exp2_text, exp2_rect)        
        pygame.display.flip()
        pygame.time.wait(8000)
        screen.blit(bg, (0, 0))
        pygame.display.flip()
        first = 0
        screen.blit(bg, (0, 0))
    # Checa se o jogo foi fechado
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    for i, answer in enumerate(questions[int(messages[question_number])]["answers"]):
        answer_text = font.render(answer, True, white)
        answer_rect = answer_text.get_rect(center=(screen_width/2, screen_height/3 + 50 + i*50))
    # Mostra o Placar
    seconds=(pygame.time.get_ticks()-start_ticks)/1000 #calculate how many seconds        
    if lost != 1 and win == 0:
        score_text = font.render(f"Placar: {score}", True, white)
        score_rect = score_text.get_rect(center=(screen_width/2, screen_height-50))
        timer_text = font.render(f"Tempo: {seconds}", True, white)
        timer_rect = timer_text.get_rect(center=(screen_width/2, screen_height-85))
        title_text = title_font.render(f"Jogo do Barão", True, brown)
        title_rect = title_text.get_rect(center=(screen_width/2, 160))
        screen.blit(bg, (0, 0))
        if (running == True):
            display_question(questions[int(messages[question_number])])
        screen.blit(score_text, score_rect)
        screen.blit(title_text, title_rect)
        screen.blit(timer_text, timer_rect)
        pygame.display.flip()
    if ((lost == 1 and win ==0) or seconds>180):
        print("Perdeu!")
        fim_chute= pygame.image.load("fim_chute.jpeg")
        screen.blit(fim_chute, (0, 0))
        lose_text = title_font.render(f"Você Perdeu !", True, brown)
        lose_rect = lose_text.get_rect(center=(screen_width/2, 200))
        screen.blit(lose_text, lose_rect)
        pygame.display.flip()
        pygame.time.wait(4000)
        running = False
    if win == 1:
        print("Ganhou!")
        fim_chute= pygame.image.load("bg.png")
        screen.blit(fim_chute, (0, 0))
        win_text = title_font.render(f"Você ganhou !", True, brown)
        win_rect = win_text.get_rect(center=(screen_width/2, 200))
        screen.blit(win_text, win_rect)
        pygame.display.flip()
        pygame.time.wait(4000)
        running = False
    # Atualiza o display
    pygame.display.flip()

