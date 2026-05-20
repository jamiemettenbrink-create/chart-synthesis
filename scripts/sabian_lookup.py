"""
sabian_lookup.py
----------------
Sabian Symbol lookup for natal chart synthesis.
Integrate this into run_full_chart.py (see instructions at bottom).

Usage:
    from sabian_lookup import get_sabian

    symbol = get_sabian(sign="Taurus", degree=4, minute=11)
    # Returns: {"degree": 5, "sign": "Taurus", "symbol": "A widow at an open grave",
    #           "keyword": "Reorientation", "label": "Taurus 5°"}
"""

SABIAN_SYMBOLS = {
    "Aries": [
        ("A woman just risen from the sea, a seal embracing her", "Emergence"),
        ("A comedian entertaining a group", "Release"),
        ("A cameo profile of a man, suggesting the outline of his country", "Exploitation"),
        ("Two lovers strolling through a secluded walk", "Enjoyment"),
        ("A triangle with wings", "Zeal"),
        ("A square with one of its sides brightly illuminated", "Structural integrity"),
        ("A man successfully expressing himself in two realms at once", "Facility"),
        ("A large hat with streamers flying, facing east", "Aspiration"),
        ("A seer gazes intently into a crystal ball before them", "Revelation"),
        ("A scholar reads in his library, surrounded by ancient tomes", "Profundity"),
        ("The ruler of a nation", "Effectiveness"),
        ("A flock of wild geese", "Serenity"),
        ("An unsuccessful bomb explosion", "Protection"),
        ("A serpent coiling near a man and woman", "Polarization"),
        ("An Indian weaving a blanket", "Realization"),
        ("Brownies dancing in the setting sun", "Invigoration"),
        ("Two prim spinsters", "Fastidiousness"),
        ("An empty hammock hung between two trees", "Repose"),
        ("The magic carpet", "Panorama"),
        ("A young girl feeding birds in winter", "Tenderness"),
        ("A pugilist entering the ring", "Exertion"),
        ("The gate to the garden of desire", "Prospect"),
        ("A woman in pastel colors carrying a heavy and valuable, but veiled, load", "Reticence"),
        ("An open window and a net curtain blowing into a cornucopia", "Munificence"),
        ("A double promise", "Covenanting"),
        ("A person possessed of more gifts than they can hold", "Opulence"),
        ("Through imagination a lost opportunity is regained", "Recovery"),
        ("A large audience confronts the performer who disappoints its expectations", "Appraisal"),
        ("A celestial choir singing", "Veneration"),
        ("A duck pond and its brood", "Reliability"),
    ],
    "Taurus": [
        ("A clear mountain stream", "Endowment"),
        ("An electrical storm", "Transformation"),
        ("Natural stepping stones across a brook", "Adequacy"),
        ("The pot of gold at the end of the rainbow", "Promise"),
        ("A widow at an open grave", "Reorientation"),
        ("A bridge being built across a gorge", "Channeling"),
        ("The woman of Samaria at the ancestral well", "Regeneration"),
        ("A sleigh without snow", "Sustainment"),
        ("A fully decorated Christmas tree", "Commemoration"),
        ("A red cross nurse", "Enlistment"),
        ("A woman watering flowers in her garden", "Cultivation"),
        ("A young couple window-shopping", "Acquisition"),
        ("A man handling baggage", "Duty"),
        ("On the beach, children play while shellfish grope along the bottom", "Utterness"),
        ("A man muffled up, with a rakish silk hat", "Sophistication"),
        ("An old man attempting vainly to reveal the Mysteries", "Pertinacity"),
        ("A symbolical battle between swords and torches", "Resolution"),
        ("A woman holding a bag out of a window", "Facilitation"),
        ("A newly formed continent", "Originality"),
        ("Wisps of cloud, like wings, are seen on either side of the sun's disk", "Fineness"),
        ("A finger pointing in an open book", "Indication"),
        ("White dove over troubled waters", "Mediation"),
        ("A jewelry shop", "Preservation"),
        ("An Indian girl introduces her white lover to her assembled tribe", "Justification"),
        ("A large well-kept public park", "Recreation"),
        ("A Spaniard serenading his seniorita", "Constancy"),
        ("A squaw selling beads", "Detachment"),
        ("A woman pursued by mature romance", "Persuasion"),
        ("Two cobblers working at a table", "Subdivision"),
        ("A peacock parading on an ancient lawn", "Aloofness"),
    ],
    "Gemini": [
        ("A glass-bottomed boat reveals undersea wonders", "Curiosity"),
        ("Santa Claus furtively filling Christmas stockings", "Anticipation"),
        ("The garden of the Tuileries", "Luxury"),
        ("Holly and mistletoe reawaken old memories of Christmas", "Recollection"),
        ("A revolutionary magazine asking for action", "Representation"),
        ("Drilling for oil", "Penetration"),
        ("An old-fashioned well with the handle", "Attraction"),
        ("Aroused strikers surround a factory", "Intensification"),
        ("A quiver filled with arrows", "Preparation"),
        ("An airplane dives toward the earth as if to land", "Decisiveness"),
        ("Newly opened lands offer the pioneer new opportunities", "Crossing"),
        ("A topsy saucy lass", "Impertinence"),
        ("A great musician at his piano", "Achievement"),
        ("A conversation by telepathy", "Intimacy"),
        ("Two Dutch children talking", "Understanding"),
        ("A woman activist in an emotional speech, dramatizing her cause", "Indignation"),
        ("The head of a robust youth changes into that of a mature thinker", "Expansion"),
        ("Two Chinese men talk Chinese in a western crowd", "Insulation"),
        ("A large archaic volume reveals a traditional wisdom", "Erudition"),
        ("A modern cafeteria displays an abundance of food, products of various regions", "Assimilation"),
        ("A labor demonstration", "Representation"),
        ("A barn dance", "Festivity"),
        ("Three fledglings in a nest high in a tree", "Elevation"),
        ("Children skating over a frozen village pond", "Gliding"),
        ("A man trimming palms", "Diligence"),
        ("Winter frost in the woods", "Crystallization"),
        ("A gypsy emerging from the forest where her tribe is encamped", "Exoticism"),
        ("A crowd upon the beach", "Exhilaration"),
        ("The first mockingbird in spring", "Promise"),
        ("Bathing beauties", "Artlessness"),
    ],
    "Cancer": [
        ("On a ship the sailors lower an old flag and raise a new one", "Allegiance"),
        ("A man suspended over a vast level place", "Contemplation"),
        ("A man all bundled up in fur leading a shaggy horse", "Circumspection"),
        ("A cat arguing with a mouse", "Justification"),
        ("An automobile wrecked by a train", "Dispersion"),
        ("Gamebirds feathering their nests", "Preparation"),
        ("Two fairies dancing on a moonlit night", "Ascendancy"),
        ("Rabbits dressed in clothes and on parade", "Appropriation"),
        ("A tiny nude miss reaching in the water for a fish", "Inclination"),
        ("A large diamond in the first stages of the cutting process", "Latency"),
        ("A clown caricaturing well-known personalities", "Sophistication"),
        ("A Chinese woman nursing a baby whose aura reveals him to be the reincarnation of a great teacher", "Investiture"),
        ("One hand slightly flexed with a very prominent thumb", "Determination"),
        ("A very old man facing a vast dark space to the northeast", "Sanction"),
        ("In a sumptuous dining hall, guests relax after a huge feast", "Opportunity"),
        ("A man before a square with a manuscript scroll before him", "Profundity"),
        ("The germ grows into knowledge and life", "Unfoldment"),
        ("A hen scratching the ground to find nourishment for her progeny", "Industriousness"),
        ("A priest performing a marriage ceremony", "Continuity"),
        ("Venetian gondoliers in a serenade", "Sentiment"),
        ("A prima donna singing", "Projection"),
        ("A woman awaiting a sailboat", "Quickening"),
        ("Meeting of a literary society", "Communion"),
        ("A woman and two men castaways on a small island of the south seas", "Adequateness"),
        ("A dark shadow or mantle thrown suddenly over the right shoulder", "Destiny"),
        ("Contentment and happiness in luxury, people reading on davenports", "Sumptuousness"),
        ("A violent storm in a canyon filled with expensive homes", "Exposure"),
        ("A modern Pocahontas", "Nativeness"),
        ("A Muse weighing twins", "Approbation"),
        ("A daughter of the American Revolution", "Inheritance"),
    ],
    "Leo": [
        ("Blood rushes to a man's head as his vital energies are mobilized under the spur of ambition", "Ambition"),
        ("An epidemic of mumps", "Infection"),
        ("A woman having her hair bobbed", "Transformation"),
        ("A ham actor", "Pretension"),
        ("Rock formations at the edge of a precipice", "Endurance"),
        ("A conservative, old-fashioned lady is confronted by a hippie girl", "Contrast"),
        ("The constellations of stars shine brilliantly in the night sky", "Surety"),
        ("A Bolshevist propagandist", "Fanaticism"),
        ("Glass blowers shape beautiful vases with their controlled breathing", "Skillfulness"),
        ("Early morning dew sparkling on grass and flowers", "Refreshment"),
        ("Children play on a swing hanging from the branches of a huge oak tree", "Delight"),
        ("An evening lawn party of adults", "Cultivation"),
        ("An old sea captain rocking on the porch of his cottage", "Retrospection"),
        ("A human soul seeking opportunities for outward manifestation", "Ingenuity"),
        ("A pageant moves along a street, packed with people", "Demonstration"),
        ("Brilliant sunshine just after a storm", "Restoration"),
        ("A volunteer church choir makes a social event of rehearsal", "Cooperation"),
        ("A teacher of chemistry", "Instruction"),
        ("A houseboat party", "Congeniality"),
        ("The Zuni sun worshippers", "Fidelity"),
        ("Chickens intoxicated", "Bliss"),
        ("A carrier pigeon fulfilling its mission", "Conviction"),
        ("A bareback rider in a circus displays her dangerous skill", "Audacity"),
        ("Totally concentrated upon inner spiritual attainment, a man is sitting in a state of complete neglect of bodily appearance and cleanliness", "Purification"),
        ("A large camel crossing a vast and forbidding desert", "Adequacy"),
        ("After the heavy storm, a rainbow", "Assurance"),
        ("Daybreak — the luminescence of dawn in the eastern sky", "Illumination"),
        ("Many little birds on a limb of a big tree", "Congeniality"),
        ("A mermaid emerges from the ocean waves ready for rebirth in human form", "Emergence"),
        ("An unsealed letter", "Confidence"),
    ],
    "Virgo": [
        ("In a portrait, the best of a man's features and traits are idealized", "Perfectibility"),
        ("A large white cross upraised", "Glorification"),
        ("Two guardian angels bringing protection", "Invigoration"),
        ("Black and white children play together happily", "Communion"),
        ("A man dreaming of fairies", "Sensitivity"),
        ("A merry-go-round", "Diversion"),
        ("A harem", "Restraint"),
        ("First dancing instruction", "Discipline"),
        ("An expressionist painter making a futuristic drawing", "Daring"),
        ("Two heads looking out and beyond the shadows", "Acuity"),
        ("A boy molded in his mother's aspirations for him", "Aspiration"),
        ("A bride with her veil snatched away", "Exposure"),
        ("A strong hand supplanting political hysteria", "Legality"),
        ("A family tree", "Nobility"),
        ("A fine lace ornamental handkerchief", "Gracefulness"),
        ("In the zoo, children are brought face to face with an orangutan", "Innate nature"),
        ("A volcano in eruption", "Explosion"),
        ("Two girls playing with a ouija board", "Acuity"),
        ("A swimming race", "Stamina"),
        ("A caravan of cars headed to the west coast", "Foresight"),
        ("A girls' basketball team", "Ambition"),
        ("A royal coat of arms", "Prerogative"),
        ("A lion tamer rushes fearlessly into the circus arena", "Daring"),
        ("Mary and her white lamb", "Artlessness"),
        ("A flag at half-mast in front of a large public building", "Respect"),
        ("A boy with a censer serves the priest near the altar", "Refinement"),
        ("Grande dames at a tea party", "Gentility"),
        ("A bald-headed man who has seized power", "Dominance"),
        ("A man gaining secret knowledge from an ancient scroll he is reading", "Perseverance"),
        ("Having an urgent task to complete, a man doesn't look to distractions", "Concentration"),
    ],
    "Libra": [
        ("A butterfly made perfect by a dart through it", "Articulation"),
        ("The light of the sixth race transmuted to the seventh", "Threshold"),
        ("The dawn of a new day reveals everything changed", "Innovations"),
        ("A group around a campfire", "Communion"),
        ("A man teaching the true inner knowledge", "Affinity"),
        ("A strand of brilliant new gems", "Desirability"),
        ("A woman feeding chickens and protecting them from the hawks", "Guardianship"),
        ("A blazing fireplace in a deserted home", "Permanence"),
        ("Three old masters hanging in an art gallery", "Accord"),
        ("A canoe approaching safety through dangerous waters", "Competency"),
        ("A professor peering over his glasses at his students", "Dominance"),
        ("Miners are surfacing from a deep coalmine", "Extrication"),
        ("Children blowing soap bubbles", "Enchantment"),
        ("A noon siesta", "Recuperation"),
        ("Circular paths", "Cycling"),
        ("After a storm, a boat landing stands in need of reconstruction", "Repair"),
        ("A retired sea captain watches ships entering and leaving the harbor", "Command"),
        ("Two men placed under arrest", "Consequence"),
        ("A gang of robbers in hiding", "Divergence"),
        ("A Jewish rabbi performing his duties", "Fidelity"),
        ("A crowd upon the beach", "Exhilaration"),
        ("A child giving birds a drink at a fountain", "Solicitude"),
        ("Chanticleer's proud and vigilant crowing", "Anticipation"),
        ("A butterfly with the right wing more perfectly formed", "Uniqueness"),
        ("The sight of an autumn leaf brings to a pilgrim the sudden revelation of the mystery of life and death", "Initiation"),
        ("An eagle and a large white dove turning one into the other", "Adeptness"),
        ("An airplane hovering overhead", "Surveillance"),
        ("A man in the midst of brightening influences", "Responsiveness"),
        ("Humanity seeking to span the bridge of knowledge", "Rationality"),
        ("Three mounds of knowledge on a philosopher's head", "Prescience"),
    ],
    "Scorpio": [
        ("A sight-seeing bus filled with tourists", "Friendliness"),
        ("A broken bottle and spilled perfume", "Permeation"),
        ("A house-raising", "Helpfulness"),
        ("A youth holding a lighted candle", "Reliance"),
        ("A massive rocky shore resists the pounding of the sea", "Durability"),
        ("A gold rush tears men away from their native soil", "Ambition"),
        ("Mature woman keeps ideals while accepting social compromises", "Compromise"),
        ("The silvery moon shining across a lake", "Quietescence"),
        ("Dental work", "Practicality"),
        ("A fellowship supper reunites old comrades", "Fraternity"),
        ("A drowning man is being rescued", "Resurgence"),
        ("An embassy ball", "Allurement"),
        ("An inventor performs a laboratory experiment", "Conjecture"),
        ("Telephone linemen at work installing new connections", "Technique"),
        ("Children playing around five mounds of sand", "Fascination"),
        ("A girl's face breaking into a smile", "Acquiescence"),
        ("A woman, fecundated by her own spirit, is great with child", "Fecundation"),
        ("A woods rich in autumn coloring", "Fulfillment"),
        ("A parrot listening and then talking, filled with chatter", "Conventionality"),
        ("A woman drawing two dark curtains aside", "Daring"),
        ("A soldier derelict in duty", "Relinquishment"),
        ("Hunters starting out for ducks", "Anticipation"),
        ("A rabbit metamorphoses into a nature spirit", "Transition"),
        ("Crowds coming down the mountain to listen to one inspired man", "Channeling"),
        ("An X-ray photograph helps with the diagnosis", "Penetration"),
        ("Indians making camp in new territory", "Hardihood"),
        ("A military band marches noisily through the city streets", "Intrepidity"),
        ("The king of the fairies approaching his domain", "Regality"),
        ("An Indian woman pleading to the chief for the lives of her children", "Effectiveness"),
        ("The Halloween jester", "Spontaneousness"),
    ],
    "Sagittarius": [
        ("Retired army veterans gather to reawaken old memories", "Reminiscence"),
        ("The ocean covered with whitecaps", "Irrepressibility"),
        ("Two men playing chess", "Profundity"),
        ("A little child learning to walk with the encouragement of his parents", "Assistance"),
        ("An old owl sits alone on the branch of a large tree", "Wisdom"),
        ("A game of cricket", "Fitness"),
        ("Cupid knocking at the door", "Enticement"),
        ("Within the depths of the earth, new elements of life are being formed", "Germination"),
        ("A mother with her children on the stairs", "Adequateness"),
        ("A golden-haired goddess of opportunity", "Reward"),
        ("The lamp of physical enlightenment at the left temple", "Transcendence"),
        ("A flag turns into an eagle, the eagle into a chanticleer", "Progressiveness"),
        ("A widow's past brought to light", "Karma"),
        ("The pyramid and the sphinx", "Conventionalization"),
        ("The groundhog looking for its shadow on Ground Hog's Day", "Reassurance"),
        ("Sea gulls watching a ship", "Alertness"),
        ("An Easter sunrise service draws a large crowd", "Rebirth"),
        ("Tiny children are playing on swings in the shade of a huge oak tree", "Delight"),
        ("Pelicans menaced by the behavior and refuse of men seek safer areas", "Survival"),
        ("In an old-fashioned northern village, men cut the ice of a frozen pond for use in summer", "Provision"),
        ("A child and a dog wearing borrowed eyeglasses", "Curiosity"),
        ("A Chinese laundry", "Unremittingness"),
        ("Immigrants entering a new country", "Entrance"),
        ("A bluebird standing at the door of the house", "Happiness"),
        ("A chubby boy on a hobby-horse", "Emulation"),
        ("A flag bearer in a battle", "Inspiration"),
        ("A sculptor's vision is slowly taking form", "Externalization"),
        ("An old bridge over a beautiful stream is still in constant use", "Persistence"),
        ("A fat boy mowing the lawn of his house on an elegant suburban street", "Normalness"),
        ("The Pope blessing the faithful", "Sanction"),
    ],
    "Capricorn": [
        ("An Indian chief claims power from the assembled tribe", "Leadership"),
        ("Three stained-glass windows in a gothic church, one damaged by war", "Commemoration"),
        ("The human soul, in its eagerness for new experiences, seeks embodiment", "Daring"),
        ("A party entering a large canoe", "Co-adventuring"),
        ("Indians — some rowing a canoe while others are dancing a war dance", "Mobilization"),
        ("Ten logs lie under an archway leading to darker woods", "Thoroughness"),
        ("A veiled prophet speaks, seized by the power of a god", "Mediatorship"),
        ("In a sunlit home, domesticated birds sing joyously", "Contentment"),
        ("An angel carrying a harp", "Attunement"),
        ("An albatross feeding from the hand of a sailor", "Thanksgiving"),
        ("Pheasants display their brilliant colors on a private estate", "Aristocracy"),
        ("An illustrated lecture on natural science reveals little-known aspects of life", "Instructiveness"),
        ("A fire worshipper", "Aspiration"),
        ("An ancient bas-relief carved in granite remains a witness to a long-forgotten culture", "Imperishability"),
        ("Many toys in the children's ward of a hospital", "Abundance"),
        ("School grounds filled with boys and girls in gym suits", "Exercise"),
        ("A girl, surreptitiously bathing in the nude", "Daring"),
        ("The Union Jack flies from a new British warship", "Seapower"),
        ("A child of about five with a huge shopping bag", "Expectation"),
        ("A hidden choir singing during a religious service", "Communion"),
        ("A relay race", "Sportsmanship"),
        ("A general accepting defeat gracefully", "Resignation"),
        ("A soldier receiving two awards for bravery in combat", "Recognition"),
        ("A woman entering a convent", "Consecration"),
        ("An oriental rug dealer in a store filled with precious ornamental rugs", "Sumptuousness"),
        ("A water sprite", "Affinity"),
        ("Pilgrims climbing the steep steps leading to a mountain shrine", "Perseverance"),
        ("A large aviary", "Companionship"),
        ("A woman reading tea leaves", "Divination"),
        ("A secret business conference", "Opportunity"),
    ],
    "Aquarius": [
        ("An old adobe mission in California", "Establishment"),
        ("An unexpected thunderstorm", "Accident"),
        ("A deserter from the navy", "Defiance"),
        ("A Hindu healer glows with a mystic healing force", "Therapy"),
        ("A council of ancestors is seen implementing the efforts of a young leader", "Empowerment"),
        ("During a silent hour, a man receives a new inspiration which may change his life", "Receptiveness"),
        ("A child is seen being born out of an egg", "Emergence"),
        ("Beautifully gowned wax figures on display", "Idealization"),
        ("A flag is seen turning into an eagle", "Ritualization"),
        ("A man who had for a time become the embodiment of a popular ideal awakens to the confusion of his life", "Disillusionment"),
        ("During a silent hour, a man receives a new inspiration", "Receptiveness"),
        ("People on stairs graduated upwards", "Progression"),
        ("A barometer", "Indication"),
        ("A train entering a tunnel", "Penetration"),
        ("Two lovebirds sitting on a fence and singing happily", "Contentment"),
        ("A big businessman at his desk", "Authority"),
        ("A watchdog stands guard, protecting his master and his possessions", "Vigilance"),
        ("A man unmasked", "Disillusionment"),
        ("A forest fire is being subdued by the use of water, chemicals and the creation of new disinfected earth", "Effectiveness"),
        ("A large white dove bearing a message", "Conviction"),
        ("A woman disappointed and disillusioned, courageously faces a seemingly empty life", "Resilience"),
        ("A rug placed on a floor for children to play", "Comfort"),
        ("A big bear sitting down and waving all its paws", "Aptitude"),
        ("A man turning his back on his passions and teaching from his experience", "Counseling"),
        ("A butterfly with the right wing more perfectly formed", "Growth"),
        ("A garage man testing a car's battery with a hydrometer", "Efficiency"),
        ("An ancient pottery bowl filled with violets", "Conservation"),
        ("A tree felled and sawed to ensure a supply of wood for the winter", "Foresight"),
        ("A butterfly emerging from a chrysalis", "Metamorphosis"),
        ("Moonlit fields, once Babylon, are now bathed in the moon-light", "Cancellation"),
    ],
    "Pisces": [
        ("A public market", "Commerce"),
        ("A squirrel hiding from hunters", "Protection"),
        ("Petrified forest, an eternal record of a life lived long ago", "Stability"),
        ("Heavy car traffic on a narrow isthmus linking two seashore resorts", "Convergence"),
        ("A church bazaar", "Fundraising"),
        ("Officers on dress parade", "Discipline"),
        ("Illumined by a shaft of light, a large cross lies on rocks surrounded by sea", "Martyrdom"),
        ("A girl blowing a bugle", "Summons"),
        ("A jockey", "Emulation"),
        ("An aviator pursues his journey, flying through ground-obscuring clouds", "Perseverance"),
        ("Men traveling a narrow path, seeking illumination, are guided into a sanctuary", "Transcendence"),
        ("In the sanctuary of an occult brotherhood, newly initiated members are being examined and their character tested", "Qualification"),
        ("A sword, used in many battles, is now in a museum", "Collective inheritance"),
        ("A lady wrapped in a large stole of fur", "Luxury"),
        ("An officer instructing his men before a simulated assault under a barrage of live shells", "Toughening"),
        ("In the quiet of his study, a creative individual experiences a flow of inspiration", "Transcendence"),
        ("An Easter promenade", "Celebration"),
        ("In a gigantic tent, thousands of people watch the performance of a spectacular pageant", "Ritualization"),
        ("A master instructing his disciple", "Discipleship"),
        ("A table set for an evening meal", "Abundance"),
        ("Under the watchful and kind eye of a Chinese servant, a girl fondles a little white lamb", "Gentleness"),
        ("A man bringing down the new law from Sinai", "Mandate"),
        ("Spiritist phenomena are at work", "Sensitivity"),
        ("On a small island surrounded by the vast expanse of the sea, people are seen living in close interaction", "Community"),
        ("The purging of the priesthood", "Reformation"),
        ("Watching the very thin crescent of a new moon, people realize the end of a particular cycle", "Finality"),
        ("The harvest moon illumines a clear autumnal sky", "Benediction"),
        ("A fertile garden under the full moon reveals a variety of full-grown vegetables", "Fulfillment"),
        ("Light breaking into many colors as it passes through a prism", "Revelation"),
        ("The Great Stone Face", "Manifestation"),
    ],
}

SIGN_ORDER = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]


def get_sabian(sign: str, degree: int, minute: int = 0) -> dict:
    """
    Return the Sabian Symbol for a given sign and degree.

    Args:
        sign: Zodiac sign name (e.g. "Taurus")
        degree: Degree within the sign, 0–29 (integer part of position)
        minute: Arcminutes, 0–59

    Returns:
        dict with keys: degree (rounded), sign, symbol, keyword, label

    Degree rounding convention (Marc Edmund Jones):
        - 0°00'–0°59' → degree 1
        - 1°00'–1°59' → degree 2
        - ...
        - 29°00'–29°59' → degree 30
        i.e., always use math.ceil(degree + minute/60) with min result of 1
    """
    import math

    # Convert to 1-based degree (round up)
    raw = degree + minute / 60.0
    rounded = max(1, math.ceil(raw)) if minute > 0 or degree == 0 else degree if degree > 0 else 1
    # Simpler: always ceil from fractional; if exactly integer, it stays that integer (already at that degree)
    # but Jones convention: 0°00' = degree 1, 1°00' = degree 2, etc. → use degree + 1 for exact integers
    # Standard interpretation: position at N°00' uses symbol N+1; position at N°01' uses symbol N+1
    # So: rounded_degree = floor(raw) + 1, capped at 30
    rounded = min(30, int(raw) + 1)

    signs = SABIAN_SYMBOLS.get(sign)
    if not signs:
        return {"error": f"Sign '{sign}' not found"}

    idx = rounded - 1  # 0-indexed list
    symbol, keyword = signs[idx]

    return {
        "degree": rounded,
        "sign": sign,
        "symbol": symbol,
        "keyword": keyword,
        "label": f"{sign} {rounded}°",
        "formatted": f'"{symbol}" — Keyword: {keyword}',
        "blueprint_line": f"Sabian Symbol ({sign} {rounded}°): \"{symbol}\" · {keyword}"
    }


def get_sabian_from_longitude(longitude: float) -> dict:
    """
    Convenience wrapper: accepts absolute ecliptic longitude (0–360°).

    0–29.99° = Aries, 30–59.99° = Taurus, etc.
    """
    sign_idx = int(longitude / 30)
    sign = SIGN_ORDER[sign_idx]
    pos_in_sign = longitude % 30
    degree = int(pos_in_sign)
    minute = int((pos_in_sign - degree) * 60)
    return get_sabian(sign, degree, minute)


# ─────────────────────────────────────────────
# INTEGRATION INSTRUCTIONS FOR run_full_chart.py
# ─────────────────────────────────────────────
#
# 1. Copy this file to scripts/sabian_lookup.py
#
# 2. At the top of run_full_chart.py, add:
#    from sabian_lookup import get_sabian_from_longitude
#
# 3. After the Western chart calculation block (where sun_longitude is computed),
#    add:
#
#    sabian_sun = get_sabian_from_longitude(sun_longitude)
#    sabian_asc = get_sabian_from_longitude(asc_longitude)  # if birth time known
#
# 4. Add to the output dict:
#
#    "sabian": {
#        "sun": sabian_sun,
#        "ascendant": sabian_asc,
#    }
#
# 5. In the printed output section, add:
#
#    print(f"\n── SABIAN SYMBOLS ──────────────────────────")
#    print(f"Sun:       {sabian_sun['blueprint_line']}")
#    print(f"Ascendant: {sabian_asc['blueprint_line']}")
#
# ─────────────────────────────────────────────
# TEST (Jamie Mettenbrink: Sun ~4°11' Taurus = Taurus 5°)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # Jamie's Sun: ~4°11' Taurus
    result = get_sabian("Taurus", 4, 11)
    print(result)
    # Expected: Taurus 5° — "A widow at an open grave" — Keyword: Reorientation

    # Test via longitude (Taurus = 30–60°, 4°11' in Taurus = 34.18°)
    result2 = get_sabian_from_longitude(34.18)
    print(result2)
    # Expected: same as above

    # Test Aries 29°59' (should give Aries 30°)
    result3 = get_sabian("Aries", 29, 59)
    print(result3)
