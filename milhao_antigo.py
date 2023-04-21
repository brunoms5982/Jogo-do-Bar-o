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
font = pygame.font.SysFont(None, 36)
blue = (0, 0, 255)
white = (255, 255, 255)
green = (0,255,0)
brown = (150,75,0)
broker = 'labdigi.wiseful.com.br'
port = 80
topic = "grupo1-bancadaB4/1" #Recebe as informações da ESP
topic_p = "grupo1-bancadaB4/P1" #Publica as informações para ESP 
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'grupo1-bancadaB4'
password = 'digi#@1B4'
#Variáveis do jogo
question_number = 0 #Numero da questão
score = 0 # Placar/Numero da questão
help = 1 #Ajudas
bg = pygame.image.load("bg.png")
lastMsg = ""
messages = []
answered = 0
first = 1
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
        if (messages.count(lastMsg)==0):
            messages.append(lastMsg)
        print(messages)
    client.subscribe(topic)
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

# Checa se a questão está correta
def check_answer(question, answer):
    global score
    if answer == question["correct"]:
        score += 1
        return True
    else:
        return False
# Início do Jogo
p_publish(client,"Inicia",topic_p) #Sinal de Inicia do Jogo
time.sleep(5)#Delay Antes de iniciar o jogo (tempo para receber dados MQTT)
running = True
while running:
    screen.blit(bg, (0, 0))
    # Checa se o botão esquerdo do mouse foi pressionado
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # clicou em uma resposta ?
            mouse_pos = pygame.mouse.get_pos()
            for i, answer in enumerate(questions[int(messages[question_number])]["answers"]):
                answer_text = font.render(answer, True, white)
                answer_rect = answer_text.get_rect(center=(screen_width/2, screen_height/3 + 50 + i*50))
                if answer_rect.collidepoint(mouse_pos):
                    # Checa se a resposta está correta
                    if check_answer(questions[int(messages[question_number])], i):
                        answered = 1
                        question_number += 1
                        p_publish(client,"Acertou",topic_p) # Trocar por 1 (Sinaliza que Acertou )
                        if question_number == 8: #Acerta 8 e ganha o Jogo 
                            print("Ganhou!")
                            running = False
                    else:
                        #Se errado, para o jogo (adicionar menu de Game Over)
                            p_publish(client,"Errou",topic_p) # Sinaliza que Errou 
                            p_publish(client,"Reset",topic_p) #  Sinaliza o Reset (depois do Errou)
                            print("Perdeu!")
                            running = False


    # Preenche a tela com o background
    #screen.fill(blue)

    # Renderiza as questões e respostas
    if (running == True):
        display_question(questions[int(messages[question_number])])
    # Mostra o Placar
    score_text = font.render(f"Placar: {score}", True, white)
    score_rect = score_text.get_rect(center=(screen_width/2, screen_height-50))
    help_text = font.render(f"Ajudas: {help}", True, white)
    help_rect = help_text.get_rect(center=(screen_width/2, screen_height-85))
    title_text = font.render(f"Jogo do Barão", True, brown)
    title_rect = title_text.get_rect(center=(screen_width/2, 200))
    screen.blit(score_text, score_rect)
    screen.blit(title_text, title_rect)
    #screen.blit(help_text, help_rect)
    #screen.blit(help_text, help_rect)
    # Atualiza o display
    pygame.display.flip()
