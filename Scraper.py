# -*- coding: utf-8 -*-
import base64
import json
#Pour traiter l'image du clavier random
from PIL import Image
from pytesseract import image_to_string

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from weboob.core.ouiboube import Weboob
from weboob.exceptions import BrowserIncorrectPassword

import time

def test(bank):
    driver = webdriver.Chrome()
    driver.get(bank['URL_Login'])
    print ((driver.find_element_by_xpath("//div[@class='newIdent']//h1").get_attribute('innerHTML')))
    driver.close()


def getGrilleDecodee(imageGrilleRecu, grilleNbCol,grilleNbLigne):
    grilleApresOCR = []
    #Modification de l'image pour la rendre lisible
    traitementImage = Image.open(imageGrilleRecu)
    #imagePropre = Image.new("RGB", traitementImage.size, (0, 0, 0))
    #imagePropre.paste(traitementImage, mask=traitementImage.split()[3]) # 3 is the alpha channel
    traitementImage = traitementImage.convert('L') #transformer en nuance de gris
    traitementImage = traitementImage.point(lambda x: 255 if x>150 else 0, '1') #garder que le noir et le blanc
    traitementImage.save(imageGrilleRecu+'.conv.png', dpi=(600,600))

    stepW = traitementImage.width/5
    stepH = traitementImage.height/2

    #On fera des crop que si il y a plus de 2 lignes dans la grille
    #Car ca veut dire qu'il y a des cases vides !!
    #Premiere Ligne
    if grilleNbLigne > 2:
        for numLigne in range(0, grilleNbLigne):
            for numCol in range(0, grilleNbCol):
                grilleApresOCR.append(
                    image_to_string(traitementImage.crop((stepW*numCol,numLigne,stepW+stepW*numCol,stepH*numLigne+stepH)),config='-psm 6 digits')
                )
    else:
        tmp = image_to_string(traitementImage,config='-psm 6 digits').replace("\n","")
        for chiffre in tmp:
            grilleApresOCR.append(chiffre)

    traitementImage.close()
    return grilleApresOCR


def LCL_getSolde(bank, userID, userPassword):
    #driver = webdriver.PhantomJS()
    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    driver = webdriver.Chrome(chrome_options=options)
    driver.get(bank['URL_Login'])

    champs_identifiant = driver.find_element_by_name(bank['HTML_ID_Identifiant'])
    imageClavier = driver.find_element_by_id(bank['HTML_ID_Clavier'])

    champs_identifiant.send_keys(userID)
    imageClavier_base64 = driver.execute_async_script("""
    var ele = arguments[0], callback = arguments[1];
    ele.addEventListener('load', function fn(){
      ele.removeEventListener('load', fn, false);
      var cnv = document.createElement('canvas');
      cnv.width = this.width; cnv.height = this.height;
      cnv.getContext('2d').drawImage(this, 0, 0);
      callback(cnv.toDataURL('image/jpeg').substring(22));
    }, false);
    ele.dispatchEvent(new Event('load'));
    """, imageClavier)

    # save the captcha to a file
    with open(r"drawClavier.png", 'wb') as f:
        f.write(base64.b64decode(imageClavier_base64))
    #On recupere la version apres OCR de la grille
    grilleApresOCR = getGrilleDecodee('drawClavier.png', bank['GRILLE_nb_Col'], bank['GRILLE_nb_Ligne'])

    keysToClick = []
    for chiffre in userPassword:
        keysToClick.append(bank['HTML_ID_TouchesClavier'][grilleApresOCR.index(chiffre)])

    for keyID in keysToClick:
        key = driver.find_element_by_id(keyID)
        driver.execute_script("document.getElementById('"+keyID+"').click()")
        print ('click sur '+ keyID)
    #petite verif pour debugging
    print ('combinaison postClavier: '+ driver.find_element_by_id('postClavier').get_attribute('value'))

    driver.execute_script("document.getElementById('"+bank['HTML_ID_BoutonSubmit']+"').click()")
    #driver.find_element_by_id(bank['HTML_ID_BoutonSubmit']).click()
    driver.get(bank['URL_Solde'])

    details_labels=driver.find_elements_by_xpath("//div[@class='libelleCompte']")
    details_soldes=driver.find_elements_by_xpath("//td[@class='right']")

    i=0
    details=[]
    while i<len(details_labels):
        tmp = details_soldes[i].get_attribute('innerHTML').replace('+', '').replace(' ','').replace(',','.').replace('&nbsp;', '').replace("\n", '').replace("\t", '')
        tmp = tmp[:-1]
        #details[details_labels[i].get_attribute('innerHTML')] = float(tmp)
        test = {"libelle":details_labels[i].get_attribute('innerHTML'), "solde":float(tmp)}
        details.append(test)
        i=i+1

    solde = driver.find_element_by_xpath("//div[@class='t_datatop']//td[contains(@class, 'right')]/strong").get_attribute('innerHTML')
    solde = solde.replace('&nbsp;', '')

    print ('MON SOLDE TOTAL: '+ solde)
    driver.close()
    solde = solde[:-1] #retirer le dernier caractere, euros
    solde = float(solde.replace('+', '').replace(' ','').replace(',','.'))

    datas = {
        "solde":solde,
        "details":details
    }
    return json.dumps(datas)



def LCL_getSoldeMobile(bank, userID, userPassword):
    driver = webdriver.Chrome()
    driver.get("https://ios.particuliers.secure.lcl.fr/?env=prod")

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "codeId0")))

    champs_identifiant = driver.find_element_by_id('idUnique')
    champs_identifiant.send_keys(userID)

    for key in userPassword:
        driver.execute_script("document.getElementById('codeId"+key+"').click()")

    driver.find_element_by_id('btnLoginPar').click()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "syntheseComptesDash")))
    time.sleep(0.3) # chelou, il click des fois sur le mauvais bouton :(
    driver.find_element_by_id('syntheseComptesDash').click()

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".liChevron")))

    soldes = driver.find_elements_by_xpath("//div[contains(@class,'liChevron')]/a/div/div[contains(@class, 'soldCptRight')]")
    #soldes = driver.find_element_by_xpath("//div[contains(@class,'liChevron')]/a/div[contains(@class, 'soldCptRight')]")

    for solde in soldes:
        print (solde.get_attribute('innerHTML').replace('&nbsp;', ''))

    driver.close()


def getSolde(bankSettings,id,mdp):
    if bankSettings['NOM_Banque'] == 'LCL':
        return LCL_getSolde(bankSettings,id,mdp)
    elif bank == 'BNP':
        print ('BNP')
        return(False)
    else:
        print ('Banque non reconnu')
        return(False)
"""
startTime=time.time()
with open('bankSettings.json') as json_data:
    bankSettings = json.load(json_data)
#test(bankSettings['LCL'])
print (getSolde(bankSettings['LCL'], '5769408937', '934522'))
endTime=time.time()
tempsTotal = round(endTime - startTime , 2)
print (tempsTotal , " sec")
"""

def getDatas(bank,login,mdp,website):

    w = Weboob('workDir','dataDir','mesBackends')
    b = w.load_backend(bank,bank,{'login':login, 'password':mdp, 'website':website})

    details=[]
    soldeTotal = 0.0
    status = "OK"
    try:
        for element in w.iter_accounts():
            print(element.label, element.balance)
            tmp = {"libelle":element.label, "solde":float(element.balance)}
            details.append(tmp)
            soldeTotal = soldeTotal + float(element.balance)
    except:
        status = "NOK identifiant incorrect"
        pass

    datas = {
        "solde":soldeTotal,
        "details":details,
        "status":status
    }
    return json.dumps(datas)
