
import time
import urllib.request
import os
import base64
import colorsys
import sys
import math
import difflib
import pytesseract as tess
from urllib.request import urlopen
from utility_methods.utility_methods import *
from selenium import webdriver
from functools import reduce
from PIL import Image
from PIL import ImageGrab
from pytesseract import Output
tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import os
from selenium.webdriver.chrome.options import Options
import threading


version = "9"
totalCrownsEarned = 0
headless = False
wordList = []

def isVersionOutdated():
    newestVersion = urlopen("https://raw.githubusercontent.com/TempJannik/Wizard101-Trivia-Bot/master/version.txt").read().decode('utf-8')
    if newestVersion != version:
        print("Your Bot seems to be outdated. Please visit https://github.com/TempJannik/Wizard101-Trivia-Bot for the newest version")
        input("Press any keys to continue with the old version...")

class TriviaBot:
    def __init__(self, accounts):
        global headless
        self.login_url = "https://www.freekigames.com/trivia"
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--enable-automation")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-browser-side-navigation")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        path = os.path.dirname(os.path.realpath(__file__))
        self.driver = webdriver.Chrome(path+"/chromedriver.exe", options=chrome_options)
        self.earnedCrowns = 0
        self.activeAccount = ""
        self.accounts = accounts

    def start(self):
        global headless
        for account in self.accounts:
            try:
                print("Starting login for " +account[0])
                self.login(account[0], account[1])
                self.driver.switch_to.default_content()
                while len(self.driver.find_elements_by_xpath("//a[contains(@class, 'logout button orange')]")) == 0:
                    print("Login failed, retrying...")
                    self.driver.get("https://www.freekigames.com/auth/logout/freekigames?redirectUrl=https://www.freekigames.com")
                    self.login(account[0], account[1])
                    time.sleep(2)
                self.activeAccount = account[0]
                self.activeAccountCrowns = 0
                #print("Finished login for " +account[0])
                
                self.doQuiz("Magical", "https://www.freekigames.com/wizard101-magical-trivia")
                #print("Switching Quiz")
                self.doQuiz("Adventuring", "https://www.freekigames.com/wizard101-adventuring-trivia")
                #print("Switching Quiz")
                self.doQuiz("Conjuring", "https://www.freekigames.com/wizard101-conjuring-trivia")
                #print("Switching Quiz")
                self.doQuiz("Marleybone", "https://www.freekigames.com/wizard101-marleybone-trivia")
                #print("Switching Quiz")
                self.doQuiz("Mystical", "https://www.freekigames.com/wizard101-mystical-trivia")
                #print("Switching Quiz")
                self.doQuiz("Spellbinding", "https://www.freekigames.com/wizard101-spellbinding-trivia")
                #print("Switching Quiz")
                self.doQuiz("Spells", "https://www.freekigames.com/wizard101-spells-trivia")
                #print("Switching Quiz")
                self.doQuiz("Valencia", "https://www.freekigames.com/pirate101-valencia-trivia")
                #print("Switching Quiz")
                self.doQuiz("Wizard", "https://www.freekigames.com/wizard101-wizard-city-trivia")
                #print("Switching Quiz")
                self.doQuiz("Zafaria", "https://www.freekigames.com/wizard101-zafaria-trivia")
                print("Earned a total of " + str(self.activeAccountCrowns) + " crowns on account: " + self.activeAccount)
                self.driver.get("https://www.freekigames.com/auth/logout/freekigames?redirectUrl=https://www.freekigames.com")
            except Exception as e:
                print("An error occured while doing Trivia for "+account[0]+", this account will be skipped. If you want to do trivia on this account please restart the bot after completion.")
                print("Following Exception occured while trying to process an account:\n"+str(e))
                self.driver.quit()
                chrome_options = Options()
                if headless:
                    chrome_options.add_argument("--headless")
                chrome_options.add_argument("--log-level=3")
                chrome_options.add_argument("--enable-automation")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-infobars")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-browser-side-navigation")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
                path = os.path.dirname(os.path.realpath(__file__))
                self.driver = webdriver.Chrome(path+"/chromedriver.exe", options=chrome_options)

        print("\n\nThread Summary\nEarned " + str(self.earnedCrowns)+" crowns on " + str(len(self.accounts)) + " accounts.")
        self.driver.quit()

    def doQuiz(self, quizName, quizUrl, numAttempts = 1):
        global totalCrownsEarned
        try:
            self.driver.get(quizUrl)
            while len(self.driver.find_elements_by_xpath("//*[contains(text(), 'YOU PASSED THE')]")) == 0 and len(self.driver.find_elements_by_xpath("//*[contains(text(), 'YOU FINISHED THE')]")) == 0:
                #print("Not finished, sleeping...")
                if len(self.driver.find_elements_by_xpath("//*[contains(text(), 'Too Many Requests')]")) != 0: #Error 429 handling
                    print("Too many requests, waiting 45 seconds for a retry.")
                    time.sleep(45)
                    self.doQuiz(quizName, quizUrl)
                    return
                if len(self.driver.find_elements_by_xpath("//*[contains(text(), 'Come Back Tomorrow!')]")) != 0: #Quiz throttle handling
                    print("Quiz throttled, skipping quiz.")
                    return

                while len(self.driver.find_elements_by_class_name("quizQuestion")) == 0:
                    time.sleep(0.01)
                self.driver.execute_script("""for (let index = 0; index < 4; index++) { document.getElementsByClassName('answer')[index].style.visibility = "visible"; }""")
                question = ""
                while question == "":
                    #print("Looking for question")
                    question = self.driver.find_element_by_class_name("quizQuestion").text
               # print("Found question: "+question)
                correctAnswer = self.getAnswer(quizName, question)
                #print("Found answer: "+correctAnswer)
                if correctAnswer == "Invalid":
                    print(question+" was not recognized as a question.")
                    return

                self.driver.execute_script("""
                    var choices = []
                    for (i = 0; i < 4; i++) {
                        choices.push(document.getElementsByClassName('answerText')[i].innerText);
                    }

                    //click on the correct answer, then hit the next quiz button
                    for (i = 0; i < 4; i++) {
                        if (arguments[0] == choices[i]) {
                            document.getElementsByName('checkboxtag')[i].click();
                            document.getElementById('nextQuestion').click();
                            break;
                        }
                    }""", correctAnswer)
                time.sleep(0.5)
            
            #print("Quiz is over, clicking on see your score button")
            self.driver.find_element_by_xpath("//a[contains(@class, 'login button purple')]").click()
            #print("Switching to frame for captcha")
            iframe = self.driver.find_element_by_xpath("//iframe")
            self.driver.switch_to.frame(iframe)
            #print("Attemping to solve captcha")
            self.solveCaptcha("//a[contains(@class, 'buttonsubmit')]")
            #print("Solved captcha")
            self.driver.switch_to.default_content()
            #Need to find out if success, then add to total crowns earned
            #print("Did we win?")
            time.sleep(0.3)
            if len(self.driver.find_elements_by_xpath("//*[contains(text(), 'Transferrable Crowns')]")) != 0:
                self.earnedCrowns += 10
                self.activeAccountCrowns += 10
                totalCrownsEarned += 10
                print("Earned 10 Crowns on Account "+self.activeAccount+" with Quiz: "+quizName)
            #print("Quiz finished")
        except Exception as e:
            if numAttempts == 3:
                print("Following Exception occured while trying to complete the "+quizName+ " quiz. Skipping quiz.\n"+str(e))
                return
            else:
                print("Following Exception occured while trying to complete the "+quizName+ " quiz. Restarting quiz.\n"+str(e))
                self.doQuiz(quizName, quizUrl, numAttempts = numAttempts+1)

    def getAnswer(self, category, question):
        if category == "Magical":
            switcher = {
                "Zafaria is home to what cultures?":"Gorillas, Zebras, Lions",
                "Which of these locations is not in Wizard City?":"Digmore Station",
                "What book does Professor Drake send you to the library to check out?":"Book on the Wumpus",
                "What is the title of the book that is floating around the Wizard City Library?":"Basic Wizarding & Proper Care of Familiars",
                "How many worlds of The Spiral are unlocked as of May 21st, 2014?":"12",
                "Why are the Gobblers so afraid to go home?":"Witches",
                "Merle Ambrose is originally from which world?":"Avalon",
                "Who sells Valentine's Day items in Wizard City?":"Valentina Heartsong",
                "Who is the Registrar of Pigswick Academy?":"Mrs. Dowager",
                "Who guards the entrance to Unicorn Way?":"Private Stillson",
                "What's the name of the balance tree?":"Niles",
                "What can be used to diminish the Nirini's powers in Krokotopia?":"Flame Gems",
                "Why are the pixies and faeries on Unicorn Way evil?":"Rattlebones corrupted them.",
                "Which below are NOT a type of Oni in MooShu?":"Ruby",
                'Who prophesizes this? "The mirror will break, The horn will call, From the shadows I strike , And the skies will fall..."':"Morganthe",
                "Who is the Nameless Knight?":"Sir Malory",
                "What color is the door inside the boys dormroom?":"Red",
                "What is the shape of the pink piece in potion motion?":"Heart",
                "Which one of these are not a symbol on the battle sigil?":"Wand",
                "What did Prospector Zeke lose track of in MooShu?":"Blue Oysters",
                "Which is the only school left standing in Dragonspyre?":"Fire",
            }
            return switcher.get(question, "Invalid")
        if category == "Adventuring":
            switcher = {
                "What is Professor Falmea's favorite food?":"Pasta Arrabiata",
                "What hand does Lady Oriel hold her wand in?":"Trick question, she has a sword.",
                "What determines the colors of the manders in Krok?":"Where they come from and their school of focus.",
                "What school is the spell Dark Nova":"Shadow",
                "How long do you have to wait to join a new match after fleeing in PVP?":"5 minutes",
                "Who is in the top level of the Tower of the Helephant?":"Lyon Lorestriker",
                "What type of rank 8 spell is granted to Death students at level 58?":"Damage + DoT",
                "Which of these are not a lore spell?":"Fire Dragon",
                "An unmodified Sun Serpent does what?":"900 � 1000 Fire Damage + 300 Fire Damage to entire team",
                "Which of these is NOT a Zafaria Anchor Stone?":"Rasik Anchor Stone",
                "Who is the Bear King of Grizzleheim?":"Valgard Goldenblade",
                "What is the name of the secret society in Krokotopia":"Order of the Fang",
                "What is unique about Falmea's Classroom?":"There are scorch marks on the ceiling",
                "In Grizzleheim, the Ravens want to bring about:":"The Everwinter, to cover the world in ice:",
                "What is the name of the new dance added with Khrysalis?":"The bee dance",
                "What is the name of the book stolen from the Royal Museum?":"The Krokonomicon",
                "Which Aztecan ponders the Great Questions of Life?":"Philosoraptor",
                "What does the Time Ribbon Protect against?":"Time Flux",
                "What school is the Gurtok Demon focused on?":"Balance",
                "Shaka Zebu is known best as:":"The Greatest Living Zebra Warrior",
            }
            return switcher.get(question, "Invalid")
        if category == "Conjuring":
            switcher = {
                "Who is Bill Tanner's sister?":"Sarah Tanner",
                "What is the shape on the weather vanes in the Shopping District?":"Half moon/moon",
                "What book was Anna Flameright accused of stealing?":"Advanced Flameology",
                "What level must you be to wear Dragonspyre crafted clothing?":"33",
                "What did Abigail Dolittle accuse Wadsworth of stealing?":"Genuine Imitation Golden Ruby",
                "What was the name of the powerful Grendel Shaman who sealed the runic doors?":"Thulinn",
                "Who Is NOT a member of the Council of Light?":"Cyrus Drake",
                "Sir Edward Halley is the Spiral's most famous:":"Aztecosaurologist",
                "Who is the King of the Burrowers?":"Pyat MourningSword",
                'Which Queen is mentioned in the Marleybone book "The Golden Age"?':"Ellen",
                "How many portal summoning candles are in the Burial Mound?":"Three",
                "Kirby Longspear was once a student of which school of magic?":"Death",
                "The Swordsman Destreza was killed by:":"A Gorgon",
            }
            return switcher.get(question, "Invalid")
        if category == "Marleybone":
            switcher = {
                "Arthur Wethersfield is A:..":"Dog",
                "What course did Herold Digmoore study?":"Ancient Myths for Parliament",
                "What is flying around in Regent's Square?":"Newspapers",
                "What time of day is it always in Marleybone?":"Night",
                "What two names are on the Statues in the Marleybone cathedral?":"Saint Bernard and Saint Hubert",
                "What event is Abigail Doolittle sending out invitations for?":"Policeman's Ball",
                "What sort of beverage is served in Air Dales Hideaway?":"Root Beer",
                "What is a very common last name of the cats in Marleybone?":"O'Leary",
                "Who is not an officer you'll find around Marleybone?":"Officer Digmore",
                "What style of artifacts are in the Royal Museum?":"Krokotopian",
                "What initials were on the doctor's glove?":"XX",
                "Who is the dangerous criminal that is locked up, but escapes from Newgate Prison?":"Meowiarty",
                "What color are the Marleybone mailboxes?":"Red",
                "Which of these folks can you find in the Royal Museum?":"Clancy Pembroke",
                "Which is not a street in Regent's Square?":"Fleabitten Ave",
                "What is Sgt. Major Talbot's full name?":"Sylvester Quimby Talbot III",
                "What time does the clock always read in Marleybone?":"1:55",
                "Which symbol is not on the stained glass window in Regent's Square?":"A Tennis Ball",
                "What transports you from place to place in Marleybone?":"Hot Air Balloons",
                "What did Prospector Zeke lose in Marleybone?":"The Stray Cats",
            }
            return switcher.get(question, "Invalid")
        if category == "Mystical":
            switcher = {
                "Who is the Emperor of Mooshu's Royal Guard?":"Noboru Akitame",
                "In what world would you find the Spider Temple":"Zafaria",
                "Where is the only pure fire in the Spiral found?":"Wizard City",
                "King Neza is Zenzen Seven Star's:?":"Grandfather",
                "What was Ponce de Gibbon looking for in Azteca?":"The Water of Life",
                "In Reagent's Square, the Professor is standing in front of a:":"Telegraph Box",
                "Hrundle Fjord is part of what section of Grizzleheim?":"Wintertusk",
                "King Axaya Knifemoon needs what to unify the people around him?":"The Badge of Leadership",
                "Which villain terrorizes the fair maidens of Marleybone?":"Jaques the Scatcher",
                "Who gives you permission to ride the boat to the Krokosphinx?":"Sergent Major Talbot",
                "Who is the only person who knows how to enter the Tomb of Storms?":"Hetch Al'Dim",
                "Who was ordered to guard the Sword of Kings?":"The Knights of the Silver Rose",
                "Who did Falynn Greensleeves fall in love with?":"Sir Malick de Logres",
                "Who was the greatest Aquilan Gladiator of all time?":"Dimachaerus",
                "Who haunts the Night Warrens?":"Nosferabbit",
                "Who tells you how to get to Aquila?":"Harold Argleston",
                "Who takes you across the River of Souls?":"Charon",
                "Thaddeus Price is the Pigswick Academy Professor of what school?":"Tempest",
                "Who asks you to find Khrysanthemums?":"Eloise Merryweather",
                "What is used to travel to the Isle of Arachnis?":"Ice Archway",
            }
            return switcher.get(question, "Invalid")
        if category == "Spellbinding":
            switcher = {
                "Who makes the harpsicord for Shelus?":"Gretta Darkkettle",
                "Morganthe got the Horned Crown from the Spriggan:":"Gisela",
                "Sumner Fieldgold twice asks you to recover what for him?":"Shrubberies",
                "Who needs the healing potion from Master Yip?":"Binh Hoa",
                "Who is Haraku Yip's apprentice?":"Binh Hoa",
                'Who taunts you with: "Prepare to be broken, kid!"':"Clanker",
                "What badge do you earn by defeating 100 Samoorai?":"Yojimbo",
                "Who thinks you are there to take their precious feathers?":"Takeda Kanryu",
                "The Swallows of Caliburn migrate to Avalon from where each year?":"Zafaria and Marleybone",
                'Who tells you: "A shield is just as much a weapon as the sword."':"Mavra Flamewing",
                'Who tells you to speak these words only unto your mentor: "Meena Korio Jajuka!"':"Priya the Dryad",
                "Who tries to raise a Gorgon Army?":"Phorcys",
                'Who taunts you with: "Wizard, you will know the meaning of the word pain after we battle!"':"Aiuchi",
                "What special plant was Barley developing in his Garden?":"Cultivated Woodsmen",
                "Who helps Morganthe find the Horn of Huracan?":"Belloq",
                "Who taunts: Why I oughta knock you to the moon, you pesky little creep!":"Mugsy",
                "What does Silenus name you once you've defeated Hades?":"Glorious Golden Archon",
                "In Azteca, Morganthe enlisted the help of the:":"The Black Sun Necromancers",
                "Where has Pharenor been imprisoned?":"Skythorn Tower",
                "Who grants the first Shadow Magic spell?":"Sophia DarkSide",
            }
            return switcher.get(question, "Invalid")
        if category == "Spells":
            switcher = {
               "Mortis can teach you this.":"Tranquilize",
                "What term best fits Sun Magic Spells?":"Enchantment",
                "What type of spells are Ice, Fire, and Storm?":"Elemental",
                "Who can teach you the Life Shield Spell?":"Sabrina Greenstar",
                "Mildred Farseer teaches you what kind of spell?":"Dispels",
                "What term best fits Star Magic Spells?":"Auras",
                "Who teaches you balance magic?":"Alhazred",
                "What isn't a shadow magic spell?":"Ebon Ribbons",
                "Which spell can't be cast while polymorphed as a Gobbler?":"Pie in the sky",
                "If you can cast Storm Trap, Wild Bolt, Catalan, and the Tempest spell, what are you polymorphed as?":"Ptera",
                "How many pips does it cost to cast Stormzilla?":"5",
                "Which spell would not be very effective when going for the elixir vitae Badge?":"Entangle",
                "Cassie the Ponycorn teaches this kind of spell:":"Prism",
                "What level of spell does Enya Firemoon Teach?":"80",
                "If you're a storm wizard with 4 power pips and 3 regular pips, how powerful would your supercharge charm be?":"110%",
                "How many pips does it cost to cast Dr. Von's Monster?":"9",
                "What does Forsaken Banshee do?":"375 damage plus a hex trap",
                "Which Fire spell both damages and heals over time?":"Power Link",
                "Ether Shield protects against what?":"Life and Death attacks",
                "Tish'Mah specializes in spells that mostly affect these:":"Minions",
            }
            return switcher.get(question, "Invalid")
        if category == "Valencia":
            switcher = {
                "Historian Gonzago is on a stage, who isn't in the audience?":"Giafra",
                'Historian Gonzago sends you on a "Paper Chase," who do you talk to during that quest?':"Magdalena",
                "How many Mechanical Birds do you collect in Sivella?":"5",
                "The Mooshu Tower in Sivella is a replica of what?":"Tower of Serenity",
                "What are Albus and Carbo?":"Armada Commanders",
                "What color of Windstone do you find in Marco Pollo's Tomb?":"Blue",
                "What kind of disguise do you wear in Sivella?":"Clockwork",
                "What shows Steed you're part of the Resistence?":"Amulet",
                "What type of boat do you use to get from the docks to Sivella?":"Gondola",
                "What type of item does Prospector Zeke want you to find in Valencia?":"Birds",
                "What's the name of a librarian in Sivella?":"Grassi",
                "Where do you find the Tomb of Marco Pollo?":"Granchia",
                "Which one isn't a Scholar by name?":"Caresini",
                "Which world doesn't have a pillar in Sivella?":"Monquista",
                "Who do you find in the Lecture Hall of Sivella?":"Ridolfo",
                "Who does Steed send you to speak to in Sivella?":"Thaddeus",
                "Who reads the inscription on Marleybone's Tower?":"Ratbeard",
                "Why does Steed want you to attack Armada Ships?":"Make a Disguise",
                "You need a good eye to save these in Granchia...":"Art Objects",
                "You won't find this kind of Armada Troop in Sivella!":"Battle Angel",
            }
            return switcher.get(question, "Invalid")
        if category == "Wizard":
            switcher = {
                "Who is the Fire School professor?":"Dalia Falmea",
                "What school does Malorn Ashthorn think is the best?":"Death",
                "What is the name of the bridge in front of the Cave to Nightside?":"Rainbow Bridge",
                "What does every Rotting Fodder in the Dark Caves carry with them?":"A spade",
                "Who is the Wizard City mill foreman?":"Sohomer Sunblade",
                "What is Diego's full name?":"Diego Santiago Quariquez Ramirez the Third",
                "What is something that the Gobblers are NOT stockpiling in Colossus Way?":"Broccoli",
                "Where is Sabrina Greenstar?":"Fairegrounds",
                "Who sang the Dragons, Tritons and Giants into existance?":"Bartleby",
                "What are the school colors of Balance?":"Tan and Maroon",
                "What are the main colors for the Myth School?":"Blue and Gold",
                "What school is all about Creativity?":"Storm",
                "What is the gemstone for Balance?":"Citrine",
                "Who resides in the Hedge Maze?":"Lady Oriel",
                "Who taught Life Magic before Moolinda Wu?":"Sylvia Drake",
                "Who is the Princess of the Seraphs?":"Lady Oriel",
                "What is the name of the school newspaper? Boris Tallstaff knows...":"Ravenwood Bulletin",
                "What is the name of the grandfather tree?":"Bartleby",
                "What is Mindy's last name (she's on Colossus Blvd)?":"Pixiecrown",
                "What is the name of the Ice Tree in Ravenwood?":"Kelvin",
            }
            return switcher.get(question, "Invalid")
        if category == "Zafaria":
            switcher = {
                "What does Lethu Blunthoof says about Ghostmanes?":"You never can tell with them!",
                "Sir Reginal Baxby's cousin is:":"Mondli Greenhoof",
                "Baobab is governed by:":"A Council of three councilors.",
                "Who is the missing prince?":"Tiziri Silvertusk",
                "Umlilo Sunchaser hired who as a local guide?":"Msizi Redband",
                "Inyanga calls Umlio a:":"Fire feather",
                "The Fire Lion Ravagers are led by:":"Nergal the Burned Lion",
                "Unathi Nightrunner is:":"A councilor of Baobab.",
                "Who is not one of the Zebu Kings:":"Zaffe Zoffer",
                "Rasik Pridefall is:":"An Olyphant from Stone Town.",
                "Esop Thornpaw gives you a magic:":"Djembe Drum",
                "The Inzinzebu Bandits are harassing the good merchants in:":"Baobab Market",
                "Vir Goodheart is an assistant to:":"Rasik Pridefall",
                "Belloq is first found in:":"The Sook",
                "Zebu Blackstripes legendary blade was called:":"The Sword of the Duelist",
                "Jambo means:":"Hello.",
                "Zebu Blackstripes legendary blade was forged:":"In the halls of Valencia",
                "Koyate Ghostmane accuses the player of:":"Being a thief",
                "Who are Hannibal Onetusk's brother and co-pilot?":"Mago and Sobaka",
                "Zamunda's great assassin is known as:":"Karl the Jackal",
            }
            return switcher.get(question, "Invalid")

    def solveCaptcha(self, submitXPath): # submitXPath = the XPath of the element needed to submit the captcha
        global wordList
        retryLimit = 20
        currentTry = 0
        img_base64 = self.driver.execute_script("""
        var ele = arguments[0];
        var cnv = document.createElement('canvas');
        cnv.width = 230; cnv.height = 50;
        cnv.getContext('2d').drawImage(ele, 0, 0);
        return cnv.toDataURL('image/jpeg').substring(22);    
        """, self.driver.find_element_by_id("captchaImage"))   #"/html/body/form/div[2]/div[3]/span[3]/div[1]/img"))
        with open(r"image.png", 'wb') as f:
            f.write(base64.b64decode(img_base64))
        origImg = Image.open(r'image.png')
        img = origImg.load()

        self.removeYellowLine(origImg, img)
        captchaResult = tess.image_to_string(origImg, lang="eng", config="-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ").lower()
        captchaResult = captchaResult.replace(" ","")
        closestMatches = difflib.get_close_matches(captchaResult, wordList)
        if len(closestMatches) > 0:
            captchaResult = closestMatches[0]
        captchaResult = captchaResult.replace("\n","")
        if captchaResult == "":
                self.driver.find_element_by_id("captchaImage").click()
       # print("Captcha Result: "+captchaResult)
        self.driver.execute_script("document.getElementById(\"captcha\").value = arguments[0]", captchaResult)
        submitBtns = self.driver.find_elements_by_xpath(submitXPath)
        for btn in submitBtns:
            if btn.is_enabled() and btn.is_displayed():
                btn.click()
                break
        #print("Submitted Captcha")
        while len(self.driver.find_elements_by_xpath("//*[contains(text(), 'You must correct')]")) > 0: # Failed captcha
            currentTry = currentTry + 1
            if currentTry >= retryLimit: #To Prevent getting stuck for whatever reason, add a retry limit, if the captcha isnt solved the following code should have it
                return
            self.driver.find_element_by_id("captcha").clear()
            #self.driver.find_element_by_id("captchaImage").click()
            time.sleep(1)
            #print("Downloading Image")
            img_base64 = self.driver.execute_script("""
            var ele = arguments[0];
            var cnv = document.createElement('canvas');
            cnv.width = 230; cnv.height = 50;
            cnv.getContext('2d').drawImage(ele, 0, 0);
            return cnv.toDataURL('image/jpeg').substring(22);    
            """, self.driver.find_element_by_id("captchaImage"))
            with open(r"image.png", 'wb') as f:
                f.write(base64.b64decode(img_base64))
            origImg = Image.open(r'image.png')
            img = origImg.load()
            #print("Processing image")
            self.removeYellowLine(origImg, img)
            #print("Tesseracting...")
            captchaResult = tess.image_to_string(origImg, lang="eng", config="-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ").lower()
            captchaResult = captchaResult.replace(" ","")
            closestMatches = difflib.get_close_matches(captchaResult, wordList)
            if len(closestMatches) > 0:
                captchaResult = closestMatches[0]
            captchaResult = captchaResult.replace("\n","")
            if captchaResult == "":
                self.driver.find_element_by_id("captchaImage").click()
            #print("Captcha Result: "+captchaResult)
            self.driver.execute_script("document.getElementById(\"captcha\").value = arguments[0]", captchaResult)
            submitBtns = self.driver.find_elements_by_xpath(submitXPath)
            for btn in submitBtns:
                if btn.is_enabled() and btn.is_displayed():
                    btn.click()
                    break

    def login(self, username, password):
        self.driver.get(self.login_url)
        time.sleep(1.5)
        if len(self.driver.find_elements_by_xpath("//*[contains(text(), 'Too Many Requests')]")) != 0: #Error 429 handling
            print("Too many requests, waiting 45 seconds for a retry.")
            time.sleep(45)
            self.login(username, password)
            return
        login_btn = self.driver.find_element_by_xpath("//*[contains(text(), 'Login / SignUp')]")
        login_btn.click()
        iframe = self.driver.find_elements_by_xpath("//iframe")
        while len(iframe) == 0:
            iframe = self.driver.find_elements_by_xpath("//iframe")
        self.driver.switch_to.frame(iframe[0])
        time.sleep(1.5)

        username_input = self.driver.find_element_by_class_name('userNameField')
        password_input = self.driver.find_element_by_class_name('passwordField')

        username_input.send_keys(username)
        password_input.send_keys(password)
        login_btns = self.driver.find_elements_by_xpath("//*[contains(text(), 'Login')]")
        for btn in login_btns:
                if btn.is_enabled() and btn.is_displayed():
                    btn.click()
                    break

        if len(self.driver.find_elements_by_xpath("//*[contains(text(), 'captcha')]")) > 0:
            #print("Found captcha")
            self.solveCaptcha("//*[contains(text(), 'Login')]")
        else:
            print("No Captcha! Login successful")

    def isYellow(self, color):
        hsv = self.rgb_to_hsv(color[0], color[1], color[2])
        if hsv[0] > 31 and hsv[0] < 80:
            return True
        else:
            return False

    def rgb_to_hsv(self, r, g, b):
        r, g, b = r/255.0, g/255.0, b/255.0
        mx = max(r, g, b)
        mn = min(r, g, b)
        df = mx-mn
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g-b)/df) + 360) % 360
        elif mx == g:
            h = (60 * ((b-r)/df) + 120) % 360
        elif mx == b:
            h = (60 * ((r-g)/df) + 240) % 360
        if mx == 0:
            s = 0
        else:
            s = (df/mx)*100
        v = mx*100
        return h, s, v

    def getRGB(self, img, i, j):
        try:
            return img[i, j]
        except:
            return (0, 0, 0)

    def getNeighborPixels(self, img, i, j):
        arr = []
        arr.append(self.getRGB(img, i, j + 1))
        arr.append(self.getRGB(img, i + 1, j))
        arr.append(self.getRGB(img, i - 1, j))
        arr.append(self.getRGB(img, i, j - 1))
        return arr

    def removeColorFromImg(self, origImage, img):
        for i in range(origImage.size[0]):
            for j in range(origImage.size[1]):
                hue = self.rgb_to_hsv(img[i,j][0], img[i,j][1], img[i,j][2])[0]
                if hue < 50:
                    img[i,j] = (0, 0, 0)
                else:
                    img[i,j] = (255, 255, 255)

    def removeYellowLine(self, origImage, img):
        ok = True
        for i in range(origImage.size[0]):
            for j in range(origImage.size[1]):
                if self.isYellow(img[i, j]):
                    ok = False
                    
                    neighborPixels = self.getNeighborPixels(img, i, j)
                    notYellowPixels = list(filter((lambda x: not self.isYellow(x)), neighborPixels))
                    
                    if len(notYellowPixels) > 1:
                        avgPixel = reduce((lambda  x, y: (x[0] + y[0], x[1] + y[1], x[2] + y[2])), notYellowPixels)
                        avgPixel = list(map(lambda x:  math.floor(x/len(notYellowPixels)), avgPixel))
                        if self.isYellow(avgPixel):
                            img[i, j] = (255, 255, 255)
                            continue
                        else:   
                            img[i, j] = (avgPixel[0], avgPixel[1], avgPixel[2])

        if not ok:
            self.removeYellowLine(origImage, img)


def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

if __name__ == '__main__':
    print("--------  Wizard101 Trivia Bot v"+version+" --------\n\n")
    print("If you encounter any issues and are on the newest version, have any suggestions or wishes for the bot feel free to contact me via Discord: ToxOver#9831")
    print("To change the amount of parallel answering of Trivias change the number in threads.txt. Default: 1")
    print("To run the bot in headless mode (Chrome will be invisible in background) change the number in headless.txt from 0 to 1")
    isVersionOutdated()

    path = os.path.dirname(os.path.realpath(__file__))
    with open(path+"/wordlist.txt") as f:
        for line in f:
            wordList.append(line)
            wordList.append(line + "s")
    with open(path+'/threads.txt', 'r') as threadFile:
        chunksAmount = int(threadFile.read())
    with open(path+'/headless.txt', 'r') as headlessFile:
        if int(headlessFile.read()) == 1:
            headless = True
    accounts = []
    path = os.path.dirname(os.path.realpath(__file__))
    with open(path+"/accounts.txt") as f:
        for line in f:
            data = line.split(':')
            accounts.append((data[0], data[1]))
    accountChunks = split(accounts, chunksAmount)
    threads = []
    for chunk in accountChunks:
        bot = TriviaBot(chunk)
        t = threading.Thread(target=bot.start)
        threads.append(t)
    for x in threads:
        x.start()
    for x in threads:
        x.join()

    print("\n\nSummary\nEarned " + str(totalCrownsEarned)+" crowns on " + str(len(accounts)) + " accounts.")
    input()

    

