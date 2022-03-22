#!/usr/bin/python3
import os
import gi
import re
import sqlite3
import subprocess

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk, AppIndicator3 as appindicator



titleSettingsWindow = "Settings"
iconWindow = "/home/ilya/aapanel/phalcon_forum/public/assets/img/favicon.png"
workDir = "/home/ilya/python/tray"

# Подключаемся к базе
conn = sqlite3.connect("sqlite3database.db")
cursor = conn.cursor()
# Создание таблицы
cursor.execute("""CREATE TABLE IF NOT EXISTS domians ('id' INTEGER PRIMARY KEY AUTOINCREMENT, 'name' TEXT NOT NULL UNIQUE, 'soft' TEXT NOT NULL, 'dir' TEXT NOT NULL)""")


# Вариант с сокетом, nginx пишет "no files" не разрбрался.
#nginx
#sudo docker build -t open_web_server_nginx:1.20 /home/ilya/python/tray/nginx/
#sudo docker run -d -p 80:80 -v "/home/ilya/python/tray/nginx/http.d:/etc/nginx/http.d" -v "/home/ilya/python/tray/domians:/var/www" -v phpsocket:/var/run --rm --name open_web_server_nginx open_web_server_nginx:1.20
#php-fpm7
#sudo docker build -t open_web_server_php-fpm:all /home/ilya/python/tray/php-fpm/
#sudo docker run -d -v "/home/ilya/python/tray/php-fpm/php-fpm.d:/etc/php7/php-fpm.d" -v phpsocket:/var/run --rm --name open_web_server_php-fpm open_web_server_php-fpm:all

#Вариант c портом 
# попробовать имя контейнера "phpfpm"
#sudo docker run -d -p 9000:9000 -v "/home/ilya/python/tray/php-fpm/php-fpm.d:/etc/php7/php-fpm.d" -v "/home/ilya/python/tray/domians:/var/www" --rm --name open_web_server_php-fpm open_web_server_php-fpm:all

#sudo docker run -d -p 80:80 -v "/home/ilya/python/tray/nginx/http.d:/etc/nginx/http.d" -v "/home/ilya/python/tray/domians:/var/www" --link open_web_server_php-fpm --rm --name open_web_server_nginx open_web_server_nginx:1.20

startServer = gtk.MenuItem(label='Start')
stopServer = gtk.MenuItem(label='Stop')

def menu():
  menu = gtk.Menu()

  startServer.connect('activate', startServerF)
  menu.append(startServer)

  stopServer.connect('activate', stopServerF)
  stopServer.set_sensitive(False)
  menu.append(stopServer)

  controlcenter = gtk.MenuItem(label='Settings')
  controlcenter.connect('activate', SettingsWindow)
  menu.append(controlcenter)

  Separator = gtk.SeparatorMenuItem()
  menu.append(Separator)

  exittray = gtk.MenuItem(label='Quit')
  exittray.connect('activate', quit)
  menu.append(exittray)

  menu.show_all()
  return menu




class Handler:

  def __init__(self):
    self.window_is_hidden = False

  def btnAdd_clicked(self, button):
    regex = r"[a-z0-9.-]{0,}"
    chekDomianName = re.search(regex, inputDomianName.get_text())
    if chekDomianName.end() > 0 and str(inputFolderPath.get_filename()) != "None":
      add_domian_to_list(chekDomianName.group(), selectDomianSoft.get_active_id(), inputFolderPath.get_filename())
      update_domians_list()
    else:
      print("error: input Domian name and path")
    
  def btnDel_clicked(self, button):
    if domiansListView.get_selection().count_selected_rows() > 0:
      model, iter = domiansListView.get_selection().get_selected()
      domianName = model.get_value(iter, 0) #получем имя домена для удаления из sqlite
      cursor.execute("DELETE FROM domians WHERE name=?", (domianName,))
      conn.commit()
      update_domians_list()
  def btnSave_clicked(self, button):
    print("save")

def closeWindow(w,e):
  w.hide()
  return True






builder = gtk.Builder()
builder.add_from_file('mainWindow.glade')
builder.connect_signals(Handler())
win = builder.get_object('windowSettings')
win.connect('delete-event', closeWindow)

inputDomianName = builder.get_object('inputDomianName')
selectDomianSoft = builder.get_object('selectDomianSoft')
inputFolderPath = builder.get_object('inputFolderPath')
domiansListView = builder.get_object('domiansListView')

domiansListStore = gtk.ListStore(str, str, str)
domiansListView.set_model(domiansListStore)



def startServerF(_):
  startDockerContainers()
  clear_hosts_file()
  push_in_hosts_file()
  stopServer.set_sensitive(True)
  startServer.set_sensitive(False)
  

def stopServerF(_):
  stopDockerContainers()
  clear_hosts_file()
  stopServer.set_sensitive(False)
  startServer.set_sensitive(True)



def SettingsWindow(_):
  createWindow = False
  window_list = gtk.Window.list_toplevels()
  if len(window_list) == 0:
    print("No Windows Found")
  else:
    for windows in window_list:
      if windows.get_title() == titleSettingsWindow:
        windows.show()
        windows.deiconify()
        createWindow = True
        #print("Есть такое окно",windows.get_title())
        #print("get_size =", windows.get_size())

  if createWindow == False:
    win.set_title(titleSettingsWindow)
    win.set_keep_above(True)
    win.set_default_icon_from_file(iconWindow)
    win.show()
    #os.system("systemsettings5")


def add_domian_to_list(name,soft,dir):
  domian = [(name, soft, dir)]
  cursor.executemany("INSERT INTO domians (name,soft,dir) VALUES (?,?,?)", domian)
  conn.commit()
  inputDomianName.set_text('')
#[(1, 'name', 'soft', 'dir'), (2, 'ya.ru', 'apache', '/var/www')]

def get_all_domians_from_sqlite():
  cursor.execute("SELECT * FROM domians")
  domiansListStore.clear()
  return cursor.fetchall()
  

def update_domians_list():
  domiansFromSqlite = get_all_domians_from_sqlite()
  for row in domiansFromSqlite:
    domiansListStore.append((row[1],row[2],row[3]))

update_domians_list()


def chekInstallDoker():
  output = subprocess.check_output(['docker','--version'])
  output = str(output).split(',')
  if output[0].find("version") < 0:
    print("Не найден установленный Docker, проверьте вывод docker --version")
    exit()
  print("Docker установлен, версия", output[0].split(' ')[-1])

def checkInstallNginxDocker():
  output = subprocess.check_output(['sudo','docker','images'])
  output = output.splitlines()
  nginxInstalled = False
  for nginx in output:
    if str(nginx).find("open_web_server_nginx") > 0:
      nginxInstalled = True
  if nginxInstalled == False:
    print("Образ с Nginx НЕ установлен")
    print("Пробую установить docker push open_web_server_nginx:1.20")
    exit()
  print("Образ Nginx установлен")
  # Если запущены open_web_server_php-fpm open_web_server_nginx то перевести в сервер start




def push_in_hosts_file():
  domians = "\\n"
  # берем из списка доменов в окне
  domiansFromSqlite = get_all_domians_from_sqlite()
  for row in domiansFromSqlite:
    domians = domians + "127.0.0.1 " +row[1] + "\\n"
  # Меняем в hosts 
  os.system("sed 's/#---OpenWebServer_No_edit_this_strings---start/#---OpenWebServer_No_edit_this_strings---start"+domians+"/g' /etc/hosts > tmp")
  os.system("sudo mv tmp /etc/hosts")
  print('Push in Hosts done')

def clear_hosts_file():
  os.system("sed '/#---OpenWebServer_No_edit_this_strings---start/,/#---OpenWebServer_No_edit_this_strings---end/d' /etc/hosts > tmp")
  os.system("echo '#---OpenWebServer_No_edit_this_strings---start' >> tmp")
  os.system("echo '#---OpenWebServer_No_edit_this_strings---end' >> tmp")
  os.system("sudo mv tmp /etc/hosts")
  print('Hosts clear done')


def startDockerContainers():
  os.system('sudo docker run -d -p 9000:9000 -v "'+workDir+'/php-fpm/php-fpm.d:/etc/php7/php-fpm.d" -v "'+workDir+'/domians:/var/www" --rm --name open_web_server_php-fpm open_web_server_php-fpm:all')
  os.system('sudo docker run -d -p 80:80 -v "'+workDir+'/nginx/http.d:/etc/nginx/http.d" -v "'+workDir+'/domians:/var/www" --link open_web_server_php-fpm --rm --name open_web_server_nginx open_web_server_nginx:1.20')

def stopDockerContainers():
  print("Starting stop server")
  os.system("sudo docker stop open_web_server_php-fpm open_web_server_nginx")
  print("Server stoped")

def quit(_):
  gtk.main_quit()


def main():
  chekInstallDoker()
  checkInstallNginxDocker()
  #exit()
  indicator = appindicator.Indicator.new("customtray", iconWindow, appindicator.IndicatorCategory.APPLICATION_STATUS)
  indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
  indicator.set_menu(menu())
  gtk.main()


if __name__ == "__main__":
  main()




  