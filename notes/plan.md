# Story
## Intro - Learn controls while finding panko

Panko has high health and automatically attacks and distracts targeted enemies. If he runs out of health, he returns and recharges 50% of his health quickly (he has slow health regenerationat all times)

The player starts by waking up at our house, asks "where is everyone?", and hears panko borking in the causeway. Auto pick up bow and machete (print small notification)

Panko is in causeway, borking at 3 zombies. Get them with bow to unlock panko and unlimited ammo slingshot

Panko says (yes he can talk) that cato ran in the direction of the rules club.

## 1st mission - Find Cato at the rules club

Cato is invulnerable to damage. His attack inflicts strong damage but takes a little while to recharge

The player has to clear glenfield road as they progress along it.

At the rules club, cato is atop a flag pole, hiding from 5 zombies and one rock throwing zombie.

Once the rock throwing zombie gets attacked by the player, it targets them, taking small damage for each hit

Once the area is cleared, cato informs the player that Oxie was travelling with him but was taken by a mysterious group of hooded figures to BBP

## 2nd mission - Find Oxie at BBP

Oxie has a spinning attack that blasts enemies back and inflicts moderate damage to all, with moderate recharge time

Oxie is at BBP. Fight more zombies to get there.

BBP itself is surrounded by a few hooded figures. They have more health and move around a little bit.

Once the hooded figures are defeated, Oxie comes out and the player has to chase him

Once the player catches him, he tells them he was trying to catch find udon, who was zooming to the city, with skoopi holding onto his head. They were heading to Larry's to try to find me

## 3rd mission - Find udon & skoopi at Larry's



# Development requirements
## Graphics
### Maps
Need to take multiple high resolution screenshots of google maps.

300m

Likely need corresponding PNG masks (lossless compression is important) to designate:
- walls
- doors
- entranceways to buildings
- enemy starting points (before an area has been cleared)
- enemy spawn points (for after an area has been cleared)
- area boundaries

### Spaces (stretch goal)
It would be nice to be able to enter and leave buildings, e.g. for boss battles
- Home
- Maccas
- Rules club
- Bunnings

### Vehicles (stretch goal)
It would also be nice to be able to use vehicles (which should probably respawn)

### Sprites
Each sprite will need a front view (for when you unlock them) and a top view for in-game. Where possible, sprites should come from open repositories
- Player (Em)
- Panko
- Cato
- Zombies
  - Regular
  - Rock-throwing (and rock)

## Software
### UI/HUD
- Conversation mechanism
- Thought bubbles (maybe same as above)
- Current objective (preferrably hideable)
- Area cleared notification

### 