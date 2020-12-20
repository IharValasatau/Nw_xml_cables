import os
import sys
from xml.etree import ElementTree

# открытие файла и парсинг кабельного журнала NC Электро
if len(sys.argv) > 1:
    file_path1 = sys.argv[1]
    print('Файл кабельного журнала nanoCAD Электро: ', file_path1)
else:
    print('Ошибка! Введите путь к файлу *.xml кабельного журнала nanoCAD Электро')
    sys.exit(1)
tree = ElementTree.parse(file_path1)
root = tree.getroot()

# все записи кабельного журнала
records = root.findall('.//*[@TypeName="DocRecordItem"]')
print('Записей найдено: ', len(records))

# перечень кабелей и их путей в список
cables = []
for record in records:
    cablePathValue = record.find('./Children/Child[4]//Value')
    cablePath = cablePathValue.text.replace('\n', ',').split(',') if cablePathValue is not None else []
    if cablePath:
        cableId = record.find('./Children/Child[1]//Value')
        cables.append([cableId.text, list(filter(None, cablePath))])
print('Записей с путями кабеля: ', len(cables))
for cable in cables:
    print('Кабель: ', cable[0], '; путь: ', cable[1])

# папка для вывода xml файлов поисковых запросов
out_folder = r'.\Наборы поиска xml'

# xml-шаблон поискового запроса
searchTemplate = '''
    <exchange
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xsi:noNamespaceSchemaLocation="http://download.autodesk.com/us/navisworks/schemas/nw-exchange-12.0.xsd"
    units="ft"
    filename=""
    filepath="">
      <findspec mode="all" disjoint="0">
        <conditions>      
        </conditions>
        <locator>/</locator>
      </findspec>
    </exchange>
    '''

# xml-шаблон условия поискового запроса
conditionTemplate = '''
    <condition test="equals" flags="74">
        <property>
            <name internal="LcOaSceneBaseUserName">Имя</name>
        </property>
        <value>
            <data type="wstring"></data>
        </value>
    </condition>    
'''

for cable in cables:  # для каждого кабеля из списка
    #  создание поискового запроса xml
    xmlSearch = ElementTree.fromstring(searchTemplate)
    conditions = xmlSearch.find('./findspec/conditions')
    #  создание условий поиска
    for t in cable[1]:
        condition = ElementTree.fromstring(conditionTemplate)
        conditionValueData = condition.find('./value/data')
        conditionValueData.text = t
        conditions.append(condition)
    #  создание файла поискового запроса
    file_name = cable[0] + '.xml'
    out_file_path = os.path.join(out_folder, file_name)
    ElementTree.ElementTree(xmlSearch).write(out_file_path)
    print('Создаю: ', out_file_path)
