#include <ESP8266WiFi.h> 
#include <PubSubClient.h> 

String user = "grupo1-bancadaB4";
String passwd = "digi#@1B4";
const char* ssid = "LAB_DIGITAL";                                
const char* password = "C1-17*2018@labdig";                                    
const char* mqtt_server = "labdigi.wiseful.com.br";                  
int count = 0;
WiFiClient espClient;                                                   
PubSubClient client(espClient);                                         
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE (50)
char msg[MSG_BUFFER_SIZE];
int value = 0;
int questao = 0;
String bits;
char ultima_questao [20];
int ultimo_botao;
int botao;
char bits_char [20];

void setup() {                                                          
  pinMode(4, OUTPUT);   // GPIO 4   - Inicia
  pinMode(15, OUTPUT);  // GPIO 15  - Reset
  pinMode(0, OUTPUT);   // GPIO 0   - Tem Jogada
  pinMode(2, OUTPUT);   // GPIO 2   - Erro na Resposta
  pinMode(14, OUTPUT);  // GPIO 14  - Questão Testada
  pinMode(12, OUTPUT);  // GPIO 12  - Questão Aprovada
  pinMode(16, INPUT);   // GPIO 16  - Bit 0 (Questão Escolhida)
  pinMode(5, INPUT);    // GPIO 5   - Bit 1 (Questão Escolhida)
  pinMode(13, INPUT);   // GPIO 4   - Bit 2 (Questão Escolhida)
  pinMode(10, INPUT);   // GPIO 16  - Bit 3 (Questão Escolhida)
  pinMode(9, INPUT);    // GPIO 9   - Bit 4 (Questão Escolhida) 
  pinMode(A0, INPUT);   // AnalogRead para a escolha dos botões.
  digitalWrite(0, LOW);
  digitalWrite(2, LOW);
                                                                                        
  setup_wifi();                                                         
  client.setServer(mqtt_server, 80);                                  
  client.setCallback(callback);                                         
}

void setup_wifi() {                                                     

  delay(10);                                                            
  Serial.println();                                                     
  Serial.print("Conectando com ");                                       
  Serial.println(ssid);                                                 
             
  WiFi.begin(ssid, password);                                           
 
  while (WiFi.status() != WL_CONNECTED) {                               
    delay(500);                                                         
    Serial.print(".");                                                  
  }
  randomSeed(micros());
  Serial.println();                                                     
  Serial.println("WiFi conectado");                                     
  Serial.println("Endereço de IP: ");                                   
  Serial.println(WiFi.localIP());                                       
}

void callback(char* topic, byte* payload, unsigned int length) {        
  Serial.print("Mensagem recebida [");                                  
  Serial.print(topic);                                                  
  Serial.print("] ");   

  for (int i = 0; i < length; i++) {                                    
    Serial.print((char)payload[i]);                                     
  }
  Serial.println();                                                     
  int count = 0;
  
  if((char)payload[1] == '1' && (char)payload[0] == '1'){
    Serial.println("TestAprov");  
    digitalWrite(14, HIGH);
    digitalWrite(12, HIGH);
    Serial.println("HIGH");
    delay(50);
    digitalWrite(14, LOW);
    digitalWrite(12, LOW);
  }

   if((char)payload[1] == '0' && (char)payload[0] == '1'){
    Serial.println("TestReprov");
    digitalWrite(14, HIGH);
    digitalWrite(12, LOW);
    Serial.println("LOW");
    delay(50);
    digitalWrite(14, LOW);
  }

  if((char)payload[0] == 'I') {
    Serial.println("I");
    digitalWrite(4, HIGH);
    delay(50);
    digitalWrite(4, LOW);
  }

  if((char)payload[0] == 'R') {
    Serial.println("R");
    digitalWrite(15, HIGH);
    delay(50);
    digitalWrite(15, LOW);
  }

  if((char)payload[0] == 'A') {
    Serial.println("A");
    digitalWrite(0, HIGH);
    digitalWrite(2, LOW);
    delay(50);
    botao = analogRead(A0);
    client.publish("grupo1-bancadaB4/Q1", bits_char);
    digitalWrite(0, LOW);
  }

  if((char)payload[0] == 'E') {
    Serial.println("E");
    digitalWrite(0, HIGH);
    digitalWrite(2, HIGH);
    delay(50);
    digitalWrite(0, LOW);
    digitalWrite(2, LOW);
  }

  
}

void reconnect() {                                                       
  while (!client.connected()) {                                          
    Serial.print("Aguardando conexão MQTT...");   
    String clientId = user;             
    clientId += String(random(0xffff), HEX);         
    if (client.connect(clientId.c_str(), user.c_str(), passwd.c_str())) {                               
      Serial.println("conectado");                                       
      client.publish("grupo1-bancadaB4/1", "Reconectado");    
      client.subscribe("grupo1-bancadaB4/2");                         
    } else {                                                             
      Serial.print("falhou, rc=");                                       
      Serial.print(client.state());                                      
      Serial.println(" tente novamente em 5s");                          
      delay(5000);                                                       
    }
  }
}

void loop() {
  int bit0 = digitalRead(16);
  int bit1 = digitalRead(5);
  int bit2 = digitalRead(13);
  int bit3 = digitalRead(10);
  int bit4 = digitalRead(9);
  botao = analogRead(A0);
  int questao_testada;
  int questao_aprovada;
  int botao_escolhido;

  bits = String(bit4) + String(bit3) +String(bit2) + String(bit1) + String(bit0);
  
  if(botao > 480 && botao < 570) botao_escolhido = 0;
  else if(botao < 70 && botao > 35) botao_escolhido = 1;
  else if(botao > 75 && botao < 120) botao_escolhido = 2;
  else if(botao > 880) botao_escolhido = 3;
  else botao_escolhido = -1;

  if(botao_escolhido != -1){
    Serial.println(botao_escolhido);
  }                                     

  if (!client.connected()) {                                             
    reconnect();
  }
  client.loop();                                                         
  count = 0;
  long now = millis();                                                                                             
  lastMsg = now;
  char resposta [10];
  itoa(botao_escolhido, resposta, 10);
  bits.toCharArray(bits_char, 20);
  
  if(String(ultima_questao) != String(bits_char)) {
    Serial.print("Publica mensagem: ");
    char bits_comp [20];
    for(int i = 0; i < 5; i++){
      bits_comp[i] = bits_char[i];
    }
    char new_char [10];
    char new_char2 [10];
    itoa(random(0,2), new_char, 10);
    itoa(random(0,2), new_char2, 10);
    Serial.println(new_char);
    bits_comp[1] = new_char[0];
    bits_comp[4] = new_char2[0];
    Serial.println(bits_comp);
    client.publish("grupo1-bancadaB4/Q1", bits_comp);
    for(int i = 0; i < 5; i++){
      ultima_questao[i] = bits_char[i];
    }
  }
  
  if(ultimo_botao != botao_escolhido) {
    Serial.print("Publica mensagem: ");                                  
    Serial.println(resposta);
    client.publish("grupo1-bancadaB4/R1", resposta);
    ultimo_botao = botao_escolhido;                            
  }

  client.subscribe("grupo1-bancadaB4/B4");                   
}


/************************ FIM DO PROGRAMA***************************/
