import os
import sys
import time
import json

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.animation import Animation

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider


a = 0

#--------------------------------------------------------
# MQTT --------------------------------------------------
import paho.mqtt.client as mqtt
import sys

Broker = "broker.hivemq.com"
PortaBroker = 1883
KeepAliveBroker = 60
Topico = "DYRL-Topic-"
clientId = ""

# Connect Callback --------------------------------
def on_connect(client, userdata, flags, rc):
    print("[STATUS] Conectado ao Broker. Resultado de conexao: "+str(rc))
 
    client.subscribe(Topico)
 
# Broker Callback ---------------------------------
def on_message(client, userdata, msg):
    MensagemRecebida = str(msg.payload)
    print(":", str(MensagemRecebida),"  -- Topico: "+msg.topic)

    print('\n')
    if str(msg.payload) == 'b\'p_aberta\'':
         sensores(1)
    elif MensagemRecebida == 'b\'p_fechada\'':
        sensores(0)
        
    
# ---------------------------------------------------------
# MQTT PUB ------------------------------------------------
def publish(swc, tmr, sld):
	global mqttClient, clientId
	
	
	msg = dict([('switch', str(swc)),
				('timer', str(tmr)),
				('slider', str(sld))])


	msg = "{\"data\":" + str(json.dumps(msg)) + "}"
	
	mqttClient.publish(Topico+clientId,  str(msg))
	time.sleep(.1)
	print('\n')


#--------------------------------------------------------
# Comandos ----------------------------------------------

# Sw status
def comandos(cmd):
    if cmd == 1:
        print('COMANDO ABRIR')
    elif cmd == 0:
        print('COMANDO FECHAR')

# Sensores
def sensores(s):
    if s == 1:
        print('PORTA ABERTA')
    elif s == 0:
        print('PORTA FECHADA')





# ---------------------------------------------------------
# App -----------------------------------------------------

# ---------------------------------------------------------
# Home ----------------------------------------------------
class MainWindow(Screen):
	Window.size = (800, 600)
	Window.fullscreen = 1
	Window.set_title('SwApp')


	#------------------------------------------
	def timer_callback(self):

		if self.ids.chk_timer.active == True:
			#print('Timer On')
			
			anim = Animation(pos=(0, 225), duration = .6)
			anim.start(self.ids.slider)
			
			anim = Animation(pos=(0, 200), duration = .6)
			anim.start(self.ids.slider_label)
			
		elif self.ids.chk_timer.active == False:
			#print('Timer Off');

			anim = Animation(pos=(-600, 225), duration = .6)
			anim.start(self.ids.slider)
			anim.start(self.ids.slider_label)

		publish(self.ids.sw.active, self.ids.chk_timer.active, self.ids.slider.value)


	#------------------------------------------
	def slider_callback(self, widg, value):
		publish(self.ids.sw.active, self.ids.chk_timer.active, self.ids.slider.value)


	#------------------------------------------
	def sw_callback(self, x):
		global a
		if a % 2 == 0: #true
			a = 1
			publish(True, self.ids.chk_timer.active, self.ids.slider.value)
		elif a % 2 != 0:
			a = 0
			publish(False, self.ids.chk_timer.active, self.ids.slider.value)


	
	
	def exit_(self):
		App.get_running_app().stop()

	

		
# ---------------------------------------------------------
# Settings ------------------------------------------------
class SecondWindow(Screen):
	
	Window.size = (240, 426)
	Window.fullscreen = 1
	

	def sett_callback(self):
		global mqttClient, clientId
		
		config = dict([('ssid',  self.ids.ssid.text),
					('ssid_pw',  self.ids.ssid_pw.text),
					('broker', 	 self.ids.broker.text),
					('port', 	 self.ids.port.text),
					('client_id', self.ids.client_id.text),
					('username', self.ids.username.text),
					('broker_pw', self.ids.broker_pw.text)])



		
		config = "{\"sett\":" + str(json.dumps(config)) + "}"
		
		clientId = self.ids.client_id.text		
		mqttClient.subscribe(Topico+clientId) #Inscreve no topico do client_id
		mqttClient.publish(Topico+clientId,  str(config))
	pass


# ---------------------------------------------------------
# W. Manager ----------------------------------------------
class WindowManager(ScreenManager):
	pass
	


# ---------------------------------------------------------       
# APP Class -----------------------------------------------
class MyMainApp(App):
	def build(self):
		
		return Builder.load_file("SwApp.kv")


# ---------------------------------------------------------       
# Main ---- -----------------------------------------------
def main():
	global mqttClient, exit_flag
	mqttClient = mqtt.Client()
	mqttClient.on_connect = on_connect
	mqttClient.connect(Broker, PortaBroker, KeepAliveBroker)
	mqttClient.on_message = on_message

	mqttClient.loop_start()

	MyMainApp().run()

    
# ----------------------------------
if __name__ == "__main__": 
    main()
