import random
import time
import sys

class OregonTrail:
    def __init__(self):
        # Core inventory and stats
        self.cash = 700
        self.oxen = 0
        self.food = 0
        self.bullets = 0
        self.clothing = 0
        self.misc_supplies = 0
        
        # Game progress
        self.miles = 0
        self.turn = 0
        self.marksman_level = 0
        
        # Status flags
        self.injured = False
        self.illness = False
        self.blizzard = False
        self.cleared_south_pass = False
        self.cleared_blue_mountains = False
        self.fort_available = True
        
        # Dates correspond to 2-week intervals starting March 29, 1847
        self.dates = [
            "April 12", "April 26", "May 10", "May 24", "June 7", "June 21",
            "July 5", "July 19", "August 2", "August 16", "August 31",
            "September 13", "September 27", "October 11", "October 25",
            "November 8", "November 22", "December 6", "December 20"
        ]

    def play(self):
        """Main game initialization and loop."""
        self.print_instructions()
        self.set_marksman_level()
        self.initial_purchases()
        self.game_loop()

    def print_instructions(self):
        """Displays the original 1978 game instructions."""
        print("THIS PROGRAM SIMULATES A TRIP OVER THE OREGON TRAIL FROM")
        print("INDEPENDENCE, MISSOURI TO OREGON CITY, OREGON IN 1847.")
        print("YOUR FAMILY OF FIVE WILL COVER THE 2040 MILE OREGON TRAIL")
        print("IN 5-6 MONTHS --- IF YOU MAKE IT ALIVE.\n")

    def set_marksman_level(self):
        """Shooting skill determines the time handicap during shooting events."""
        print("HOW GOOD A SHOT ARE YOU WITH YOUR RIFLE?")
        print(" (1) ACE MARKSMAN, (2) GOOD SHOT, (3) FAIR TO MIDDLIN'")
        print(" (4) NEED MORE PRACTICE, (5) SHAKY KNEES")
        
        while True:
            try:
                choice = int(input("ENTER ONE OF THE ABOVE: "))
                if 1 <= choice <= 5:
                    self.marksman_level = choice
                    break
            except ValueError:
                pass
            print("Invalid input. Please enter 1-5.")

    def initial_purchases(self):
        """Handles the allocation of the starting $700 budget."""
        print("\nYOU HAD SAVED $900 TO SPEND FOR THE TRIP, AND YOU'VE JUST PAID $200 FOR A WAGON.")
        print("YOU WILL NEED TO SPEND THE REST OF YOUR MONEY ON THE FOLLOWING ITEMS:\n")
        
        while True:
            try:
                self.oxen = float(input("HOW MUCH DO YOU WANT TO SPEND ON YOUR OXEN TEAM ($200-$300)? "))
                if self.oxen < 200:
                    print("NOT ENOUGH")
                    continue
                if self.oxen > 300:
                    print("TOO MUCH")
                    continue
                
                self.food = float(input("HOW MUCH DO YOU WANT TO SPEND ON FOOD? "))
                ammo_cash = float(input("HOW MUCH DO YOU WANT TO SPEND ON AMMUNITION? "))
                self.clothing = float(input("HOW MUCH DO YOU WANT TO SPEND ON CLOTHING? "))
                self.misc_supplies = float(input("HOW MUCH DO YOU WANT TO SPEND ON MISCELLANEOUS SUPPLIES? "))
                
                total_spent = self.oxen + self.food + ammo_cash + self.clothing + self.misc_supplies
                if total_spent <= 700:
                    self.cash = 700 - total_spent
                    self.bullets = ammo_cash * 50  # $1 = 50 bullets
                    print(f"AFTER ALL YOUR PURCHASES, YOU NOW HAVE ${int(self.cash)} DOLLARS LEFT.\n")
                    break
                else:
                    print("YOU OVERSPENT--YOU ONLY HAD $700 TO SPEND. BUY AGAIN.\n")
            except ValueError:
                print("Please enter numeric values.\n")

    def game_loop(self):
        """The core turn-by-turn simulation loop."""
        while self.miles < 2040:
            if self.food < 0:
                self.food = 0
            if self.bullets < 0:
                self.bullets = 0
            if self.clothing < 0:
                self.clothing = 0
            if self.misc_supplies < 0:
                self.misc_supplies = 0

            # Check starvation
            if self.food <= 13:
                print("YOU'D BETTER DO SOME HUNTING OR BUY FOOD AND SOON!!!!")
            if self.food <= 0:
                self.die("STARVED TO DEATH")
                
            # Date progression
            if self.turn >= len(self.dates):
                print("YOU HAVE BEEN ON THE TRAIL TOO LONG ------")
                self.die("IN THE FIRST BLIZZARD OF WINTER")
                
            print(f"\nMONDAY {self.dates[self.turn]} 1847")
            self.turn += 1

            # Medical bills
            if self.illness or self.injured:
                self.cash -= 20
                if self.cash < 0:
                    self.cash = 0
                    print("YOU CAN'T AFFORD A DOCTOR")
                    self.die("PNEUMONIA" if self.illness else "INJURIES")
                print("DOCTOR'S BILL IS $20")
                self.illness = False
                self.injured = False

            print(f"TOTAL MILEAGE IS {int(self.miles)}")
            print(f"FOOD: {int(self.food)}  BULLETS: {int(self.bullets)}  CLOTHING: {int(self.clothing)}  MISC: {int(self.misc_supplies)}  CASH: ${int(self.cash)}")

            # Turn Action Selection
            self.take_turn_action()
            
            # Eating Phase
            self.eat()
            
            # Calculate distance based on oxen quality and RNG
            self.miles += 200 + (self.oxen - 220) / 5 + random.random() * 10
            
            # Events and environment triggers
            self.check_riders()
            self.random_events()
            self.check_mountains()
            self.check_illness()

        self.win()

    def take_turn_action(self):
        """Prompts the player for their primary action (Fort, Hunt, Continue)."""
        while True:
            if self.fort_available:
                action = input("DO YOU WANT TO (1) STOP AT THE NEXT FORT, (2) HUNT, OR (3) CONTINUE? ")
            else:
                action = input("DO YOU WANT TO (1) HUNT, OR (2) CONTINUE? ")
                if action == '1': action = '2'
                elif action == '2': action = '3'
                else: continue
                
            if action == '1' and self.fort_available:
                self.visit_fort()
                self.fort_available = False # Forts alternate availability
                break
            elif action == '2':
                if self.bullets > 39:
                    self.hunt()
                    self.fort_available = not self.fort_available
                    break
                else:
                    print("TOUGH---YOU NEED MORE BULLETS TO GO HUNTING")
            elif action == '3':
                self.fort_available = not self.fort_available
                break

    def visit_fort(self):
        """Shopping at a fort. Prices are effectively 50% higher (you get 2/3 of what you pay for)."""
        print("ENTER WHAT YOU WISH TO SPEND ON THE FOLLOWING")
        
        def buy(item_name, conversion_rate=1.0):
            try:
                spend = float(input(f"{item_name}: "))
                if spend <= self.cash:
                    self.cash -= spend
                    return spend * (2/3) * conversion_rate # Original game math applies a 2/3 penalty
                else:
                    print("YOU DON'T HAVE THAT MUCH--KEEP YOUR SPENDING DOWN")
            except ValueError:
                pass
            return 0

        self.food += buy("FOOD")
        self.bullets += int(buy("AMMUNITION", 50))
        self.clothing += buy("CLOTHING")
        self.misc_supplies += buy("MISCELLANEOUS SUPPLIES")
        self.miles -= 45 # Time cost to visit fort

    def hunt(self):
        """Triggers the typing-based hunting minigame."""
        self.miles -= 45
        shoot_time = self.shoot()
        
        if shoot_time <= 1:
            print("RIGHT BETWEEN THE EYES---YOU GOT A BIG ONE!!!!")
            self.food += 52 + random.random() * 6
            self.bullets -= 10 + random.random() * 4
        elif random.random() * 100 < 13 * shoot_time:
            print("YOU MISSED---AND YOUR DINNER GOT AWAY.....")
        else:
            print("NICE SHOT--RIGHT ON TARGET--GOOD EATIN' TONIGHT!!")
            self.food += 48 - 2 * shoot_time
            self.bullets -= 10 + 3 * shoot_time

    def eat(self):
        """Determines food consumption and baseline health resilience."""
        while True:
            try:
                self.eat_level = int(input("DO YOU WANT TO EAT (1) POORLY  (2) MODERATELY OR (3) WELL? "))
                if 1 <= self.eat_level <= 3:
                    self.food -= 8 + 5 * self.eat_level
                    if self.food < 0:
                        self.food += 8 + 5 * self.eat_level
                        print("YOU CAN'T EAT THAT WELL")
                        continue
                    break
            except ValueError:
                pass

    def check_riders(self):
        """Hostile or friendly rider encounter using the original proximity formula."""
        # Probability formula based on distance from the original basic source
        prob = ((self.miles / 100 - 4) ** 2 + 72) / ((self.miles / 100 - 4) ** 2 + 12) - 1
        if random.random() * 10 > prob:
            return

        is_hostile = random.random() < 0.2
        print("RIDERS AHEAD. THEY " + ("LOOK HOSTILE" if is_hostile else "DON'T LOOK HOSTILE"))
        print("TACTICS: (1) RUN  (2) ATTACK  (3) CONTINUE  (4) CIRCLE WAGONS")
        
        try:
            tactic = int(input("> "))
        except ValueError:
            tactic = 3

        if not is_hostile:
            print("RIDERS WERE FRIENDLY, BUT CHECK FOR POSSIBLE LOSSES")
            if tactic == 1:
                self.miles += 15
                self.oxen -= 10
            elif tactic == 2:
                self.miles -= 5
                self.bullets -= 100
            elif tactic == 4:
                self.miles -= 20
        else:
            print("RIDERS WERE HOSTILE--CHECK FOR LOSSES")
            if tactic == 1:
                self.miles += 20
                self.misc_supplies -= 15
                self.bullets -= 150
                self.oxen -= 40
            elif tactic == 2:
                shoot_time = self.shoot()
                self.bullets -= shoot_time * 40 + 80
                if shoot_time <= 1:
                    print("NICE SHOOTING---YOU DROVE THEM OFF")
                elif shoot_time <= 4:
                    print("LOUSY SHOT---YOU GOT KNIFED")
                    self.injured = True
                else:
                    print("KINDA SLOW WITH YOUR COLT .45")
            elif tactic == 3:
                if random.random() > 0.8:
                    print("THEY DID NOT ATTACK")
                else:
                    self.bullets -= 150
                    self.misc_supplies -= 15
            elif tactic == 4:
                shoot_time = self.shoot()
                self.bullets -= shoot_time * 30 + 80
                self.miles -= 25
                
            if self.bullets < 0:
                self.die("RAN OUT OF BULLETS AND GOT MASSACRED BY THE RIDERS")

    def random_events(self):
        """Selects from 15 possible negative events based on original RNG thresholds."""
        r = random.random() * 100
        
        if r <= 6:
            print("WAGON BREAKS DOWN--LOSE TIME AND SUPPLIES FIXING IT")
            self.miles -= 15 + 5 * random.random()
            self.misc_supplies -= 8
        elif r <= 11:
            print("OX INJURES LEG---SLOWS YOU DOWN REST OF TRIP")
            self.miles -= 25
            self.oxen -= 20
        elif r <= 13:
            print("BAD LUCK---YOUR DAUGHTER BROKE HER ARM")
            self.miles -= 5 + 4 * random.random()
            self.misc_supplies -= 2 + 3 * random.random()
        elif r <= 15:
            print("OX WANDERS OFF---SPEND TIME LOOKING FOR IT")
            self.miles -= 17
        elif r <= 17:
            print("YOUR SON GETS LOST---SPEND HALF THE DAY LOOKING FOR HIM")
            self.miles -= 10
        elif r <= 22:
            print("UNSAFE WATER--LOSE TIME LOOKING FOR CLEAN SPRING")
            self.miles -= 10 * random.random() + 2
        elif r <= 32:
            if self.miles > 950:
                print("COLD WEATHER---BRRRRRRR!---YOU " + ("DON'T " if self.clothing <= 22 + 4 * random.random() else "") + "HAVE ENOUGH CLOTHING")
                if self.clothing <= 22 + 4 * random.random():
                    self.illness = True
            else:
                print("HEAVY RAINS---TIME AND SUPPLIES LOST")
                self.food -= 10
                self.bullets -= 500
                self.misc_supplies -= 15
                self.miles -= 10 * random.random() + 5
        elif r <= 35:
            print("BANDITS ATTACK")
            shoot_time = self.shoot()
            self.bullets -= 20 * shoot_time
            if self.bullets < 0:
                print("YOU RAN OUT OF BULLETS---THEY GET LOTS OF CASH")
                self.cash /= 3
            elif shoot_time > 1:
                print("YOU GOT SHOT IN THE LEG AND THEY TOOK ONE OF YOUR OXEN")
                self.injured = True
                self.misc_supplies -= 5
                self.oxen -= 20
            else:
                print("QUICKEST DRAW OUTSIDE OF DODGE CITY!!! YOU GOT 'EM!")
        elif r <= 37:
            print("THERE WAS A FIRE IN YOUR WAGON--FOOD AND SUPPLIES DAMAGED")
            self.food -= 40
            self.bullets -= 400
            self.misc_supplies -= random.random() * 8 + 3
            self.miles -= 15
        elif r <= 42:
            print("LOSE YOUR WAY IN HEAVY FOG---TIME IS LOST")
            self.miles -= 10 + 5 * random.random()
        elif r <= 44:
            print("YOU KILLED A POISONOUS SNAKE AFTER IT BIT YOU")
            self.bullets -= 10
            self.misc_supplies -= 5
            if self.misc_supplies < 0:
                self.die("SNAKEBITE SINCE YOU HAVE NO MEDICINE")
        elif r <= 54:
            print("WAGON GETS SWAMPED FORDING RIVER--LOSE FOOD AND CLOTHES")
            self.food -= 30
            self.clothing -= 20
            self.miles -= 20 + 20 * random.random()
        elif r <= 64:
            print("WILD ANIMALS ATTACK!")
            if self.bullets <= 39:
                self.die("TOO LOW ON BULLETS--THE WOLVES OVERPOWERED YOU")
            shoot_time = self.shoot()
            if shoot_time <= 2:
                print("NICE SHOOTIN' PARDNER---THEY DIDN'T GET MUCH")
            else:
                print("SLOW ON THE DRAW---THEY GOT AT YOUR FOOD AND CLOTHES")
            self.bullets -= 20 * shoot_time
            self.clothing -= shoot_time * 4
            self.food -= shoot_time * 8
        elif r <= 69:
            print("HAIL STORM---SUPPLIES DAMAGED")
            self.miles -= 5 + random.random() * 10
            self.bullets -= 200
            self.misc_supplies -= 4 + random.random() * 3
        else:
            print("HELPFUL INDIANS SHOW YOU WHERE TO FIND MORE FOOD")
            self.food += 14

    def check_mountains(self):
        """Handles rugged terrain delays and blizzard mechanics at specific milestones."""
        if self.miles <= 950:
            return
            
        prob = 9 - ((self.miles / 100 - 15) ** 2 + 72) / ((self.miles / 100 - 15) ** 2 + 12)
        if random.random() * 10 <= prob:
            print("RUGGED MOUNTAINS")
            if random.random() <= 0.1:
                print("YOU GOT LOST---LOSE VALUABLE TIME TRYING TO FIND TRAIL!")
                self.miles -= 60
            elif random.random() <= 0.11:
                print("WAGON DAMAGED!---LOSE TIME AND SUPPLIES")
                self.misc_supplies -= 5
                self.bullets -= 200
                self.miles -= 20 + 30 * random.random()
            else:
                print("THE GOING GETS SLOW")
                self.miles -= 45 + random.random() / 0.02
                
        if not self.cleared_south_pass:
            self.cleared_south_pass = True
            if random.random() < 0.8:
                print("BLIZZARD IN MOUNTAIN PASS--TIME AND SUPPLIES LOST")
                self.blizzard = True
                self.food -= 25
                self.misc_supplies -= 10
                self.bullets -= 300
                self.miles -= 30 + 40 * random.random()
                if self.clothing < 18 + 2 * random.random():
                    self.illness = True
            else:
                print("YOU MADE IT SAFELY THROUGH SOUTH PASS--NO SNOW")

    def check_illness(self):
        """Probability of illness increases if players eat poorly."""
        if random.random() * 100 < 10 + 35 * (self.eat_level - 1):
            if random.random() * 100 < 100 - (40 / 4 ** (self.eat_level - 1)):
                print("MILD ILLNESS---MEDICINE USED")
                self.miles -= 5
                self.misc_supplies -= 2
            else:
                print("SERIOUS ILLNESS---YOU MUST STOP FOR MEDICAL ATTENTION")
                self.misc_supplies -= 10
                self.illness = True
                
        if self.misc_supplies < 0:
            print("YOU RAN OUT OF MEDICAL SUPPLIES")
            self.die("ILLNESS")

    def shoot(self):
        """The typing minigame. Measures reaction time modified by marksman level."""
        words = ["BANG", "BLAM", "POW", "WHAM"]
        word = random.choice(words)
        print(f"TYPE: {word}")
        
        start_time = time.time()
        typed = input("> ").strip().upper()
        end_time = time.time()
        
        # Reaction time minus player handicap
        reaction_time = (end_time - start_time) - (self.marksman_level - 1)
        if reaction_time < 0:
            reaction_time = 0
            
        if typed != word:
            return 9 # Severe penalty for typing the wrong word
        return reaction_time

    def die(self, cause):
        """Terminal state handler."""
        print(f"\nYOU DIED OF {cause}")
        print("DUE TO YOUR UNFORTUNATE SITUATION, THERE ARE A FEW FORMALITIES WE MUST GO THROUGH")
        input("WOULD YOU LIKE A MINISTER? ")
        input("WOULD YOU LIKE A FANCY FUNERAL? ")
        input("WOULD YOU LIKE US TO INFORM YOUR NEXT OF KIN? ")
        print("WE THANK YOU FOR THIS INFORMATION AND WE ARE SORRY YOU DIDN'T MAKE IT TO THE GREAT TERRITORY OF OREGON")
        sys.exit()

    def win(self):
        """Victory state handler."""
        print("\nYOU FINALLY ARRIVED AT OREGON CITY")
        print("AFTER 2040 LONG MILES---HOORAY!!!!! A REAL PIONEER!")
        print("\nPRESIDENT JAMES K. POLK SENDS YOU HIS HEARTIEST CONGRATULATIONS")
        sys.exit()

if __name__ == "__main__":
    game = OregonTrail()
    game.play()